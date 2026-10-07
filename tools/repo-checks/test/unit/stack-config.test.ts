import { describe, expect, it } from "vitest";
import { parse } from "yaml";
import { readEnvFile, readText } from "../helpers/pins.js";
import { cleanEnv, parseExports, ROOT, script } from "../helpers/repo.js";

describe("local stack configuration", () => {
  const compose = parse(readText("compose.yaml")) as {
    name: string;
    services: Record<
      string,
      {
        ports?: string[];
        volumes?: string[];
        command?: string[];
        configs?: { source: string; target: string }[];
        labels?: Record<string, string>;
      }
    >;
    volumes: Record<string, unknown>;
    configs?: Record<string, { content?: string }>;
  };

  it("uses one fixed compose project name, so every worktree shares one stack", () => {
    expect(compose.name).toBe("securebrand");
    expect(readText("supabase/config.toml")).toMatch(/^project_id = "securebrand"$/m);
  });

  it("publishes every port on localhost only", () => {
    for (const [name, service] of Object.entries(compose.services)) {
      for (const port of service.ports ?? []) {
        expect(port, name).toMatch(/^127\.0\.0\.1:\d+:\d+$/);
      }
    }
  });

  it("keeps data in named volumes that make down removes", () => {
    for (const name of ["redpanda", "clickhouse", "seaweedfs"]) {
      const volumes = compose.services[name]?.volumes ?? [];
      expect(
        volumes.some((v) => /^[a-z-]+-data:/.test(v)),
        name,
      ).toBe(true);
    }
    expect(Object.keys(compose.volumes).length).toBeGreaterThanOrEqual(3);
  });

  it("mounts no file of the checkout, so a make up from any worktree finds the stack unchanged", () => {
    // A bind mount names a path inside one worktree: from another worktree it changes the
    // service's definition, and make up recreates the container under every other worktree.
    for (const [name, service] of Object.entries(compose.services)) {
      for (const volume of service.volumes ?? []) {
        expect(Object.keys(compose.volumes), `${name}: ${volume}`).toContain(volume.split(":")[0]);
      }
    }
  });

  it("writes the ClickHouse and SeaweedFS configuration from compose.yaml, and recreates a service when its configuration changes", () => {
    const targets = (name: string): string[] =>
      (compose.services[name]?.configs ?? []).map((config) => config.target);
    expect(targets("clickhouse").sort()).toEqual([
      "/etc/clickhouse-server/config.d/local.xml",
      "/etc/clickhouse-server/users.d/listening.xml",
    ]);
    expect(targets("seaweedfs")).toEqual(["/etc/seaweedfs/s3.json"]);
    // Compose recreates a container when its service definition changes, and a config's content
    // is not part of it: each service carries the content of its configs in a label.
    for (const [name, service] of Object.entries(compose.services)) {
      for (const { source } of service.configs ?? []) {
        const content = compose.configs?.[source]?.content ?? "";
        expect(content, `${name}: config ${source}`).not.toBe("");
        expect(service.labels?.[`securebrand.config.${source}`], `${name}: ${source}`).toBe(
          content,
        );
      }
    }
  });

  it("gives SeaweedFS a fixed number of volume slots, enough for a test bucket per worktree", () => {
    // Each bucket is a collection that takes seven volume slots. Left at 0, the number of slots is
    // the free disk divided by the volume size limit (21 on a 22 GB disk): three buckets.
    const command = compose.services.seaweedfs?.command ?? [];
    const max = Number(
      /^-volume\.max=(\d+)$/.exec(command.find((a) => a.startsWith("-volume.max=")) ?? "")?.[1],
    );
    expect(max).toBeGreaterThanOrEqual(7 * 20);
  });

  it("stack-env.sh prints the ports and the credentials the stack config defines", () => {
    const result = script("stack-env.sh", ["--no-supabase"], { cwd: ROOT, env: cleanEnv() });
    expect(result.code, result.output).toBe(0);
    const vars = parseExports(result.stdout);
    const local = readEnvFile("stack/local.env");
    expect(vars).toMatchObject({
      KAFKA_BROKERS: "127.0.0.1:19092",
      SCHEMA_REGISTRY_URL: "http://127.0.0.1:18081",
      REDPANDA_ADMIN_URL: "http://127.0.0.1:9644",
      CLICKHOUSE_URL: "http://127.0.0.1:8123",
      S3_ENDPOINT: "http://127.0.0.1:8333",
      S3_FORCE_PATH_STYLE: "true",
      S3_BUCKET: "listening-local",
    });
    for (const key of [
      "CLICKHOUSE_USER",
      "CLICKHOUSE_PASSWORD",
      "S3_ACCESS_KEY_ID",
      "S3_SECRET_ACCESS_KEY",
      "S3_REGION",
    ]) {
      expect(vars[key], key).toBe(local[key]);
    }
    const users = compose.configs?.["clickhouse-users"]?.content ?? "";
    expect(users).toContain(`<${local.CLICKHOUSE_USER ?? "?"}>`);
    expect(users).toContain(`<password>${local.CLICKHOUSE_PASSWORD ?? "?"}</password>`);
    const s3 = JSON.parse(compose.configs?.["seaweedfs-s3"]?.content ?? "") as {
      identities: { credentials: { accessKey: string; secretKey: string }[] }[];
    };
    expect(s3.identities[0]?.credentials[0]).toEqual({
      accessKey: local.S3_ACCESS_KEY_ID,
      secretKey: local.S3_SECRET_ACCESS_KEY,
    });
  });

  it("resolves images from stack/versions.env, or from the publishers' registries with IMAGE_REGISTRY=upstream", () => {
    const versions = readEnvFile("stack/versions.env");
    const byDefault = parseExports(
      script("stack-images.sh", [], { cwd: ROOT, env: cleanEnv() }).stdout,
    );
    const upstream = parseExports(
      script("stack-images.sh", [], { cwd: ROOT, env: cleanEnv({ IMAGE_REGISTRY: "upstream" }) })
        .stdout,
    );
    for (const key of ["REDPANDA", "CLICKHOUSE", "SEAWEEDFS"]) {
      const tag = versions[`${key}_TAG`] ?? "";
      expect(byDefault[`${key}_IMAGE`]).toBe(`${versions[`${key}_REPO`] ?? ""}:${tag}`);
      expect(upstream[`${key}_IMAGE`]).toBe(`${versions[`${key}_UPSTREAM`] ?? ""}:${tag}`);
    }
  });

  it("rejects an unknown IMAGE_REGISTRY value", () => {
    const result = script("stack-images.sh", [], {
      cwd: ROOT,
      env: cleanEnv({ IMAGE_REGISTRY: "dockerhub" }),
    });
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("IMAGE_REGISTRY");
  });
});
