import { describe, expect, it } from "vitest";
import { parse } from "yaml";
import { readEnvFile, readText } from "../helpers/pins.js";
import { cleanEnv, parseExports, ROOT, script } from "../helpers/repo.js";

describe("local stack configuration", () => {
  const compose = parse(readText("compose.yaml")) as {
    name: string;
    services: Record<string, { ports?: string[]; volumes?: string[] }>;
    volumes: Record<string, unknown>;
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

  it("stack-env.sh prints the ports and the credentials the stack config defines", () => {
    const result = script("stack-env.sh", ["--no-supabase"], { cwd: ROOT, env: cleanEnv() });
    expect(result.code, result.output).toBe(0);
    const vars = parseExports(result.stdout);
    const local = readEnvFile("stack/local.env");
    expect(vars).toMatchObject({
      KAFKA_BROKERS: "localhost:19092",
      SCHEMA_REGISTRY_URL: "http://localhost:18081",
      REDPANDA_ADMIN_URL: "http://localhost:9644",
      CLICKHOUSE_URL: "http://localhost:8123",
      S3_ENDPOINT: "http://localhost:8333",
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
    const users = readText("stack/clickhouse/users.d/listening.xml");
    expect(users).toContain(`<${local.CLICKHOUSE_USER ?? "?"}>`);
    expect(users).toContain(`<password>${local.CLICKHOUSE_PASSWORD ?? "?"}</password>`);
    const s3 = JSON.parse(readText("stack/seaweedfs/s3.json")) as {
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
