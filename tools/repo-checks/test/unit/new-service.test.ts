import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { cleanEnv, ROOT, run, TempRepo } from "../helpers/repo.js";

const GENERATOR = join(ROOT, "tools", "new-service", "index.mjs");

function generate(target: TempRepo, args: string[]): ReturnType<typeof run> {
  return run("node", [GENERATOR, ...args, "--root", target.dir, "--no-install"], {
    cwd: target.dir,
    env: cleanEnv(),
  });
}

function files(dir: string): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      out.push(...files(full));
    } else {
      out.push(full);
    }
  }
  return out;
}

describe("pnpm new:service (tools/new-service)", () => {
  let target: TempRepo;

  beforeEach(() => {
    target = new TempRepo("new-service-");
  });

  afterEach(() => {
    target.cleanup();
  });

  it.each([
    "Fb-Poller",
    "fb",
    "news",
    "fb_page_feed_poller",
    "-poller",
    "poller-",
    "page--poller",
    "1poller",
    "_template",
    "service-template",
    "poller.v2",
    "a".repeat(64),
  ])("rejects %s, a name outside the naming convention", (name) => {
    const result = generate(target, [name]);
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/CONVENTIONS|naming/i);
    expect(target.exists(`services/${name}`)).toBe(false);
  });

  it.each(["fb-page-feed-poller", "news-article-extractor", "x-search", "normalize-item", "demo"])(
    "accepts %s, a per-source or shared name",
    (name) => {
      const result = generate(target, [name]);
      expect(result.code, result.output).toBe(0);
      expect(target.exists(`services/${name}/package.json`)).toBe(true);
    },
  );

  it("refuses to overwrite an existing service", () => {
    target.write("services/demo/keep.txt", "mine\n");
    const result = generate(target, ["demo"]);
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/already exists/i);
    expect(target.read("services/demo/keep.txt")).toBe("mine\n");
    expect(target.exists("services/demo/package.json")).toBe(false);
  });

  it("leaves no template placeholder behind in the generated tree", () => {
    expect(generate(target, ["fb-page-feed-poller"]).code).toBe(0);
    expect(generate(target, ["news-demo-extractor", "--lang", "python"]).code).toBe(0);
    for (const file of files(target.path("services"))) {
      const text = readFileSync(file, "utf8");
      expect(text, relative(target.dir, file)).not.toMatch(/service[-_]template/);
      expect(relative(target.dir, file)).not.toMatch(/service[-_]template/);
    }
    const pkg = JSON.parse(target.read("services/fb-page-feed-poller/package.json")) as {
      name: string;
    };
    expect(pkg.name).toBe("fb-page-feed-poller");
    expect(target.read("services/news-demo-extractor/pyproject.toml")).toContain(
      'name = "news-demo-extractor"',
    );
    expect(target.exists("services/news-demo-extractor/src/news_demo_extractor/__init__.py")).toBe(
      true,
    );
    expect(target.read("services/news-demo-extractor/uv.lock")).toContain(
      'name = "news-demo-extractor"',
    );
  });

  it("copies no dependencies, build output, virtualenv or cache from the template", () => {
    expect(generate(target, ["demo"]).code).toBe(0);
    expect(generate(target, ["demo-py", "--lang", "python"]).code).toBe(0);
    const generated = files(target.path("services")).map((f) => relative(target.dir, f));
    for (const forbidden of [
      "node_modules",
      "dist",
      ".turbo",
      ".venv",
      "__pycache__",
      ".pytest_cache",
      ".ruff_cache",
    ]) {
      expect(generated.filter((f) => f.split("/").includes(forbidden))).toEqual([]);
    }
  });

  it("rejects an unknown language", () => {
    const result = generate(target, ["demo", "--lang", "go"]);
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/--lang/);
  });

  it("prints the next commands", () => {
    const result = generate(target, ["demo"]);
    expect(result.output).toContain("make test SERVICE=demo");
  });
});
