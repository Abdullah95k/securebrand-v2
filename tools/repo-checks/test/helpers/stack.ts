// Clients for the local stack, configured only from the variables scripts/stack-env.sh prints
// and the names scripts/test-namespace.sh derives. Everything here talks to localhost.
import {
  CreateBucketCommand,
  DeleteBucketCommand,
  DeleteObjectCommand,
  GetObjectCommand,
  HeadBucketCommand,
  ListObjectsV2Command,
  PutObjectCommand,
  S3Client,
} from "@aws-sdk/client-s3";
import kafkaModule from "@confluentinc/kafka-javascript";
import pg from "pg";
import { cleanEnv, parseExports, ROOT, run, script } from "./repo.js";

const { Kafka, logLevel } = kafkaModule.KafkaJS;

export type StackEnv = Record<string, string>;

export function stackEnv(extra: NodeJS.ProcessEnv = {}): StackEnv {
  const result = script("stack-env.sh", [], { cwd: ROOT, env: cleanEnv(extra) });
  if (result.code !== 0) {
    throw new Error(`stack-env.sh failed:\n${result.output}`);
  }
  return parseExports(result.stdout);
}

export function namespaceEnv(namespace: string): StackEnv {
  const result = script("test-namespace.sh", [], {
    cwd: ROOT,
    env: cleanEnv({ TEST_NAMESPACE: namespace }),
  });
  if (result.code !== 0) {
    throw new Error(`test-namespace.sh failed:\n${result.output}`);
  }
  return parseExports(result.stdout);
}

function need(env: StackEnv, key: string): string {
  const value = env[key];
  if (value === undefined || value === "") {
    throw new Error(`${key} is not set by scripts/stack-env.sh`);
  }
  return value;
}

export function make(
  args: string[],
  extra: NodeJS.ProcessEnv = {},
  timeoutMs = 600_000,
): ReturnType<typeof run> {
  return run("make", ["--no-print-directory", ...args], {
    cwd: ROOT,
    env: cleanEnv(extra),
    timeoutMs,
  });
}

// Kafka (Redpanda) through KAFKA_BROKERS.
function kafka(env: StackEnv): InstanceType<typeof Kafka> {
  return new Kafka({
    kafkaJS: {
      brokers: need(env, "KAFKA_BROKERS").split(","),
      clientId: "repo-checks",
      logLevel: logLevel.ERROR,
    },
  });
}

export async function createTopic(env: StackEnv, topic: string): Promise<void> {
  const admin = kafka(env).admin();
  await admin.connect();
  try {
    await admin.createTopics({ topics: [{ topic, numPartitions: 1 }] });
  } finally {
    await admin.disconnect();
  }
}

export async function listTopics(env: StackEnv): Promise<string[]> {
  const admin = kafka(env).admin();
  await admin.connect();
  try {
    return await admin.listTopics();
  } finally {
    await admin.disconnect();
  }
}

export async function produceAndConsume(
  env: StackEnv,
  topic: string,
  value: string,
): Promise<string> {
  const client = kafka(env);
  const producer = client.producer();
  await producer.connect();
  await producer.send({ topic, messages: [{ key: "k", value }] });
  await producer.disconnect();

  const consumer = client.consumer({
    kafkaJS: { groupId: `repo-checks-${topic}`, fromBeginning: true },
  });
  await consumer.connect();
  try {
    await consumer.subscribe({ topics: [topic] });
    return await new Promise<string>((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`no message on ${topic} within 30 s`));
      }, 30_000);
      void consumer.run({
        eachMessage: ({ message }) => {
          clearTimeout(timer);
          resolve(message.value?.toString() ?? "");
          return Promise.resolve();
        },
      });
    });
  } finally {
    await consumer.disconnect();
  }
}

// ClickHouse over HTTP through CLICKHOUSE_URL, CLICKHOUSE_USER and CLICKHOUSE_PASSWORD.
export async function clickhouse(env: StackEnv, query: string): Promise<string> {
  const response = await fetch(need(env, "CLICKHOUSE_URL"), {
    method: "POST",
    body: query,
    headers: {
      "X-ClickHouse-User": need(env, "CLICKHOUSE_USER"),
      "X-ClickHouse-Key": need(env, "CLICKHOUSE_PASSWORD"),
    },
  });
  const text = await response.text();
  if (!response.ok) {
    throw new Error(`ClickHouse ${String(response.status)}: ${text}`);
  }
  return text.trim();
}

// Postgres through SUPABASE_DB_URL.
export async function postgres<T extends pg.QueryResultRow>(
  env: StackEnv,
  sql: string,
  params: unknown[] = [],
): Promise<T[]> {
  const client = new pg.Client({ connectionString: need(env, "SUPABASE_DB_URL") });
  await client.connect();
  try {
    const result = await client.query<T>(sql, params);
    return result.rows;
  } finally {
    await client.end();
  }
}

// The Supabase API gateway through SUPABASE_URL and SUPABASE_ANON_KEY.
export async function supabaseStatus(env: StackEnv, path: string): Promise<number> {
  const key = need(env, "SUPABASE_ANON_KEY");
  const response = await fetch(`${need(env, "SUPABASE_URL")}${path}`, {
    headers: { apikey: key, Authorization: `Bearer ${key}` },
  });
  await response.arrayBuffer();
  return response.status;
}

// S3 (SeaweedFS) through S3_ENDPOINT and the S3_* credentials.
export function s3(env: StackEnv): S3Client {
  return new S3Client({
    endpoint: need(env, "S3_ENDPOINT"),
    region: need(env, "S3_REGION"),
    forcePathStyle: need(env, "S3_FORCE_PATH_STYLE") === "true",
    credentials: {
      accessKeyId: need(env, "S3_ACCESS_KEY_ID"),
      secretAccessKey: need(env, "S3_SECRET_ACCESS_KEY"),
    },
  });
}

export async function putObject(
  env: StackEnv,
  bucket: string,
  key: string,
  body: string,
): Promise<void> {
  await s3(env).send(new PutObjectCommand({ Bucket: bucket, Key: key, Body: body }));
}

export async function getObject(env: StackEnv, bucket: string, key: string): Promise<string> {
  const out = await s3(env).send(new GetObjectCommand({ Bucket: bucket, Key: key }));
  return (await out.Body?.transformToString()) ?? "";
}

export async function objectExists(env: StackEnv, bucket: string, key: string): Promise<boolean> {
  const out = await s3(env).send(new ListObjectsV2Command({ Bucket: bucket, Prefix: key }));
  return (out.Contents ?? []).some((o) => o.Key === key);
}

export async function deleteObject(env: StackEnv, bucket: string, key: string): Promise<void> {
  await s3(env).send(new DeleteObjectCommand({ Bucket: bucket, Key: key }));
}

export async function createBucket(env: StackEnv, bucket: string): Promise<void> {
  await s3(env).send(new CreateBucketCommand({ Bucket: bucket }));
}

/** Deletes the bucket's objects (one listing page is enough for a test bucket), then the bucket. */
export async function deleteBucket(env: StackEnv, bucket: string): Promise<void> {
  const client = s3(env);
  const listed = await client.send(new ListObjectsV2Command({ Bucket: bucket }));
  for (const object of listed.Contents ?? []) {
    if (object.Key !== undefined) {
      await client.send(new DeleteObjectCommand({ Bucket: bucket, Key: object.Key }));
    }
  }
  await client.send(new DeleteBucketCommand({ Bucket: bucket }));
}

export async function bucketExists(env: StackEnv, bucket: string): Promise<boolean> {
  try {
    await s3(env).send(new HeadBucketCommand({ Bucket: bucket }));
    return true;
  } catch {
    return false;
  }
}

/** Containers of the stack (compose project and Supabase CLI project) with id and start time. */
export function stackContainers(): Map<string, string> {
  const containers = new Map<string, string>();
  for (const filter of [
    "label=com.docker.compose.project=securebrand",
    "label=com.supabase.cli.project=securebrand",
  ]) {
    const ids = run("docker", ["ps", "-q", "--filter", filter], { cwd: ROOT })
      .stdout.split("\n")
      .filter(Boolean);
    for (const id of ids) {
      const info = run("docker", ["inspect", "-f", "{{.Name}} {{.Id}} {{.State.StartedAt}}", id], {
        cwd: ROOT,
      });
      const [name, fullId, started] = info.stdout.trim().split(" ");
      if (name !== undefined && fullId !== undefined && started !== undefined) {
        containers.set(name, `${fullId} ${started}`);
      }
    }
  }
  return containers;
}

export function containerHealth(name: string): string {
  return run(
    "docker",
    [
      "inspect",
      "-f",
      "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}",
      name,
    ],
    {
      cwd: ROOT,
    },
  ).stdout.trim();
}

export function stackVolumes(): string[] {
  const volumes: string[] = [];
  for (const filter of [
    "label=com.docker.compose.project=securebrand",
    "label=com.supabase.cli.project=securebrand",
  ]) {
    volumes.push(
      ...run("docker", ["volume", "ls", "-q", "--filter", filter], { cwd: ROOT })
        .stdout.split("\n")
        .filter(Boolean),
    );
  }
  return volumes;
}
