// Acceptance tests for the local stack (A1, A2, A3, A20 and the namespace collision row of the
// plan). They drive `make up`, `make down` and `make ns-clean` against Docker on this machine and
// talk to localhost only. The order matters: the last test leaves the stack up for the CI steps
// that follow.
//
// The make down test (A2) wipes every container and volume of the one stack that all worktrees
// share, so it runs only when TEST_STACK_RESET=1: CI's check job sets it; on a workstation, set it
// only when no other worktree is running its tests.
import { randomBytes } from "node:crypto";
import { describe, expect, it } from "vitest";
import {
  bucketExists,
  clickhouse,
  containerHealth,
  createBucket,
  createTopic,
  deleteBucket,
  getObject,
  listTopics,
  make,
  namespaceEnv,
  objectExists,
  postgres,
  produceAndConsume,
  putObject,
  stackContainers,
  stackEnv,
  stackVolumes,
  supabaseStatus,
} from "../helpers/stack.js";

const MINUTES = 60_000;
const suffix = (): string => randomBytes(4).toString("hex");

async function createNamespaceResources(ns: string): Promise<Record<string, string>> {
  const env = { ...stackEnv(), ...namespaceEnv(ns) };
  const names = {
    topic: `${env.TEST_TOPIC_PREFIX ?? ""}events`,
    schema: env.TEST_PG_SCHEMA ?? "",
    database: env.TEST_PG_DATABASE ?? "",
    chDatabase: env.TEST_CH_DATABASE ?? "",
    bucket: env.TEST_S3_BUCKET ?? "",
  };
  await createTopic(env, names.topic);
  await postgres(env, `create schema if not exists "${names.schema}"`);
  await postgres(env, `create database "${names.database}"`);
  await clickhouse(env, `CREATE DATABASE IF NOT EXISTS "${names.chDatabase}"`);
  await createBucket(env, names.bucket);
  await putObject(env, names.bucket, "probe.txt", "x");
  return names;
}

async function namespaceResourcesPresent(
  names: Record<string, string>,
): Promise<Record<string, boolean>> {
  const env = stackEnv();
  const topics = await listTopics(env);
  const schemas = await postgres<{ n: string }>(
    env,
    "select count(*)::text as n from pg_namespace where nspname = $1",
    [names.schema],
  );
  const databases = await postgres<{ n: string }>(
    env,
    "select count(*)::text as n from pg_database where datname = $1",
    [names.database],
  );
  const chDatabases = await clickhouse(
    env,
    `SELECT count() FROM system.databases WHERE name = '${names.chDatabase ?? ""}'`,
  );
  return {
    topic: topics.includes(names.topic ?? ""),
    schema: schemas[0]?.n === "1",
    database: databases[0]?.n === "1",
    chDatabase: chDatabases === "1",
    bucket: await bucketExists(env, names.bucket ?? ""),
  };
}

describe("local stack (make up, make down, make ns-clean)", () => {
  it(
    "makes every stack service healthy and a second make up changes nothing",
    () => {
      const first = make(["up"]);
      expect(first.code, first.output).toBe(0);
      const before = stackContainers();
      for (const service of ["redpanda", "clickhouse", "seaweedfs"]) {
        expect(containerHealth(`securebrand-${service}-1`), service).toBe("healthy");
      }
      for (const name of [
        "supabase_db_securebrand",
        "supabase_kong_securebrand",
        "supabase_auth_securebrand",
        "supabase_rest_securebrand",
      ]) {
        expect([...before.keys()], name).toContain(`/${name}`);
        expect(containerHealth(name), name).toMatch(/healthy|running/);
      }
      expect(first.output).toMatch(/IMAGE_REGISTRY/);

      const second = make(["up"]);
      expect(second.code, second.output).toBe(0);
      expect(stackContainers()).toEqual(before);
    },
    20 * MINUTES,
  );

  it(
    "every stack service answers through the variables stack-env.sh prints",
    async () => {
      const env = stackEnv();
      const topic = `repo_checks_a3_${suffix()}`;
      await createTopic(env, topic);
      expect(await produceAndConsume(env, topic, "hello redpanda")).toBe("hello redpanda");

      expect(await clickhouse(env, "SELECT 1")).toBe("1");

      const rows = await postgres<{ one: number }>(env, "select 1 as one");
      expect(rows[0]?.one).toBe(1);
      expect(await supabaseStatus(env, "/auth/v1/health")).toBe(200);
      expect(await supabaseStatus(env, "/rest/v1/")).toBe(200);

      const key = `repo-checks/a3-${suffix()}.txt`;
      await putObject(env, env.S3_BUCKET ?? "", key, "hello s3");
      expect(await getObject(env, env.S3_BUCKET ?? "", key)).toBe("hello s3");
    },
    5 * MINUTES,
  );

  it(
    "make ns-clean removes the namespace's topics, schema, database and bucket",
    async () => {
      const ns = `t_${suffix()}`;
      const names = await createNamespaceResources(ns);
      expect(Object.values(await namespaceResourcesPresent(names)).every(Boolean)).toBe(true);

      const clean = make(["ns-clean"], { TEST_NAMESPACE: ns });
      expect(clean.code, clean.output).toBe(0);
      expect(await namespaceResourcesPresent(names)).toEqual({
        topic: false,
        schema: false,
        database: false,
        chDatabase: false,
        bucket: false,
      });
    },
    5 * MINUTES,
  );

  it(
    "two namespaces create disjoint topics, schemas, databases and buckets",
    async () => {
      const one = await createNamespaceResources(`t_${suffix()}`);
      const twoNs = `t_${suffix()}`;
      const two = await createNamespaceResources(twoNs);
      // A namespace's schema and databases share one name (test_<ns>); two namespaces share none.
      const taken = new Set(Object.values(one));
      expect(Object.values(two).filter((name) => taken.has(name))).toEqual([]);

      const clean = make(["ns-clean"], { TEST_NAMESPACE: twoNs });
      expect(clean.code, clean.output).toBe(0);
      expect(Object.values(await namespaceResourcesPresent(one)).every(Boolean)).toBe(true);
      expect(Object.values(await namespaceResourcesPresent(two)).some(Boolean)).toBe(false);

      const oneNs = one.topic?.split(".")[0] ?? "";
      expect(make(["ns-clean"], { TEST_NAMESPACE: oneNs }).code).toBe(0);
    },
    5 * MINUTES,
  );

  it(
    "holds a test bucket with data for each of eight parallel worktrees at once",
    async () => {
      const env = stackEnv();
      const id = suffix();
      const buckets = Array.from(
        { length: 8 },
        (_, i) => namespaceEnv(`t_${id}_${i}`).TEST_S3_BUCKET ?? "",
      );
      const created: string[] = [];
      try {
        for (const [i, bucket] of buckets.entries()) {
          await createBucket(env, bucket);
          created.push(bucket);
          await putObject(env, bucket, "probe.txt", `worktree ${i}`);
        }
        for (const [i, bucket] of buckets.entries()) {
          expect(await getObject(env, bucket, "probe.txt")).toBe(`worktree ${i}`);
        }
      } finally {
        for (const bucket of created) {
          await deleteBucket(env, bucket);
        }
      }
    },
    5 * MINUTES,
  );

  it.runIf(process.env.TEST_STACK_RESET === "1")(
    "make down removes the volumes so the next make up starts empty",
    async () => {
      const env = stackEnv();
      const id = suffix();
      const marker = {
        topic: `repo_checks_marker_${id}`,
        chDatabase: `marker_${id}`,
        table: `marker_${id}`,
        object: `repo-checks/marker-${id}.txt`,
      };
      await createTopic(env, marker.topic);
      await clickhouse(env, `CREATE DATABASE ${marker.chDatabase}`);
      await postgres(env, `create table public.${marker.table} (id int)`);
      await putObject(env, env.S3_BUCKET ?? "", marker.object, "marker");

      const down = make(["down"]);
      expect(down.code, down.output).toBe(0);
      expect(stackContainers().size).toBe(0);
      expect(stackVolumes()).toEqual([]);

      const up = make(["up"]);
      expect(up.code, up.output).toBe(0);
      const fresh = stackEnv();
      expect(await listTopics(fresh)).not.toContain(marker.topic);
      expect(
        await clickhouse(
          fresh,
          `SELECT count() FROM system.databases WHERE name = '${marker.chDatabase}'`,
        ),
      ).toBe("0");
      const tables = await postgres<{ n: string }>(
        fresh,
        "select count(*)::text as n from pg_tables where tablename = $1",
        [marker.table],
      );
      expect(tables[0]?.n).toBe("0");
      expect(await objectExists(fresh, fresh.S3_BUCKET ?? "", marker.object)).toBe(false);
    },
    25 * MINUTES,
  );
});
