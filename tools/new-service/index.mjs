#!/usr/bin/env node
// Scaffolds a service from services/_template (TypeScript) or services/_template-py (Python).
//
//   pnpm new:service <name> [--lang ts|python] [--root <repo>] [--no-install]
//
// The name follows CONVENTIONS "Naming, repository, deployment": <source>-<action> for a
// per-source service (sources fb, ig, tt, x, li, tg, yt, news, web) or <action> for a shared one,
// in lowercase kebab case. The templates carry the placeholders service-template (the name) and
// service_template (the Python package); both are replaced in file contents and paths. Then the
// workspace is installed (pnpm install, or uv sync for Python) unless --no-install is given.
// No dependencies: Node's standard library only.
import { spawnSync } from "node:child_process";
import {
  chmodSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const SOURCES = ["fb", "ig", "tt", "x", "li", "tg", "yt", "news", "web"];
const RESERVED = new Set(["service-template", "template"]);
const NAME = /^[a-z][a-z0-9]*(-[a-z0-9]+)*$/;
const SKIP = new Set([
  "node_modules",
  "dist",
  ".turbo",
  "coverage",
  ".venv",
  "__pycache__",
  ".pytest_cache",
  ".ruff_cache",
]);
const TEMPLATES = {
  ts: fileURLToPath(new URL("../../services/_template/", import.meta.url)),
  python: fileURLToPath(new URL("../../services/_template-py/", import.meta.url)),
};

function fail(message) {
  console.error(`new:service: ${message}`);
  process.exit(1);
}

function parseArgs(argv) {
  const args = { name: undefined, lang: "ts", root: undefined, install: true };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--lang") {
      args.lang = argv[++i];
    } else if (arg.startsWith("--lang=")) {
      args.lang = arg.slice("--lang=".length);
    } else if (arg === "--root") {
      args.root = argv[++i];
    } else if (arg === "--no-install") {
      args.install = false;
    } else if (arg === "--help" || arg === "-h") {
      console.log(
        "usage: pnpm new:service <name> [--lang ts|python] [--root <repo>] [--no-install]",
      );
      process.exit(0);
    } else if (args.name === undefined) {
      // A name such as "-poller" is still a name: validateName explains the convention.
      args.name = arg;
    } else {
      fail(`unexpected argument "${arg}"`);
    }
  }
  if (args.lang === "typescript") {
    args.lang = "ts";
  }
  if (args.lang === "py") {
    args.lang = "python";
  }
  return args;
}

function validateName(name) {
  const rule =
    "service names follow docs/prds/_shared/CONVENTIONS.md (Naming): <source>-<action> for a " +
    `per-source service (sources: ${SOURCES.join(", ")}) or <action> for a shared one, ` +
    "lowercase words joined by single hyphens, at most 63 characters";
  if (name === undefined || name === "") {
    return `give a name; ${rule}`;
  }
  if (!NAME.test(name) || name.length > 63) {
    return `"${name}" breaks the naming convention: ${rule}`;
  }
  if (SOURCES.includes(name)) {
    return `"${name}" is a source prefix, not a service: name it <source>-<action> (CONVENTIONS naming)`;
  }
  if (RESERVED.has(name)) {
    return `"${name}" is reserved for the templates (CONVENTIONS naming leaves the rest open)`;
  }
  return undefined;
}

function repoRoot(cwd) {
  const result = spawnSync("git", ["rev-parse", "--show-toplevel"], { cwd, encoding: "utf8" });
  return result.status === 0 ? result.stdout.trim() : cwd;
}

function copyTemplate(src, dest, replace) {
  mkdirSync(dest, { recursive: true });
  for (const entry of readdirSync(src)) {
    if (SKIP.has(entry) || entry.endsWith(".tsbuildinfo")) {
      continue;
    }
    const from = join(src, entry);
    const to = join(dest, replace(entry));
    const stat = statSync(from);
    if (stat.isDirectory()) {
      copyTemplate(from, to, replace);
    } else {
      writeFileSync(to, replace(readFileSync(from, "utf8")));
      chmodSync(to, stat.mode & 0o777);
    }
  }
}

function install(cmds, cwd) {
  for (const [cmd, args] of cmds) {
    const result = spawnSync(cmd, args, { cwd, stdio: "inherit" });
    if (result.status === 0) {
      return true;
    }
  }
  return false;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const problem = validateName(args.name);
  if (problem !== undefined) {
    fail(problem);
  }
  const template = TEMPLATES[args.lang];
  if (template === undefined) {
    fail(`--lang must be ts or python, not "${args.lang}"`);
  }
  const name = args.name;
  const pkg = name.replaceAll("-", "_");
  const root = args.root ?? repoRoot(process.cwd());
  const target = join(root, "services", name);
  if (existsSync(target)) {
    fail(`services/${name} already exists; pick another name or remove it first`);
  }

  copyTemplate(template, target, (text) =>
    text.replaceAll("service-template", name).replaceAll("service_template", pkg),
  );
  const rel = relative(root, target);
  console.log(`Created ${rel} from ${relative(root, template) || template} (${args.lang}).`);

  if (args.install) {
    const ok =
      args.lang === "ts"
        ? install(
            [
              ["pnpm", ["install", "--offline"]],
              ["pnpm", ["install"]],
            ],
            root,
          )
        : install(
            [
              ["uv", ["sync", "--locked", "--offline"]],
              ["uv", ["sync", "--locked"]],
            ],
            target,
          );
    if (!ok) {
      fail(`${rel} was created but the install failed; run it again by hand`);
    }
  }

  console.log("Next:");
  console.log(`  make test SERVICE=${name}   # unit and acceptance suites`);
  console.log("  make check                  # lint, types and tests of what changed");
  console.log(`  read ${rel}/README.md for what to fill in`);
}

main();
