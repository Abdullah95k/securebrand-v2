#!/usr/bin/env node
// Scaffolds a service from services/_template (TypeScript) or services/_template-py (Python).
//
//   pnpm new:service <name> [--lang ts|python] [--root <repo>] [--no-install]
//
// The name follows CONVENTIONS "Naming, repository, deployment": <source>-<action> for a
// per-source service (sources fb, ig, tt, x, li, tg, yt, news, web) or <action> for a shared one,
// in lowercase kebab case. The templates carry the placeholders service-template (the name) and
// service_template (the Python package); both are replaced in file contents and paths. Then the
// service is installed, offline, unless --no-install is given: a TypeScript one joins
// pnpm-lock.yaml with the template's entry and installs from pnpm's store, a Python one from its
// copied uv.lock and uv's cache (make bootstrap fills both). Nothing is resolved, so nothing needs
// the registry; when a package is missing, the generator stops and says what to run.
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
// The TypeScript template's key under importers in pnpm-lock.yaml.
const TEMPLATE_IMPORTER = "services/_template";

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

// Adds the importer `to` to pnpm-lock.yaml as a copy of the importer `from`. A generated service
// declares the template's dependencies, so its entry is the one pnpm would resolve, and pnpm then
// installs from the frozen lockfile without registry metadata. Only lines are inserted; the rest of
// the file stays as pnpm wrote it. Returns false when the lockfile has no `from` entry.
function addToLockfile(root, from, to) {
  const file = join(root, "pnpm-lock.yaml");
  if (!existsSync(file)) {
    return false;
  }
  const lines = readFileSync(file, "utf8").split("\n");
  const section = lines.indexOf("importers:");
  if (section === -1) {
    return false;
  }
  const next = lines.findIndex((line, i) => i > section && /^\S/.test(line));
  const end = next === -1 ? lines.length : next;
  const entries = [];
  for (let i = section + 1; i < end; i += 1) {
    const key = /^ {2}([^\s:]\S*?):(?: \{\})?$/.exec(lines[i])?.[1];
    if (key !== undefined) {
      entries.push({ key, at: i });
    }
  }
  // An entry runs from its key line to the next entry, less the blank lines between them.
  const span = (n) => {
    let stop = n + 1 < entries.length ? entries[n + 1].at : end;
    while (stop > entries[n].at + 1 && lines[stop - 1] === "") {
      stop -= 1;
    }
    return { at: entries[n].at, length: stop - entries[n].at };
  };
  const source = entries.findIndex((entry) => entry.key === from);
  if (source === -1) {
    return false;
  }
  const { at, length } = span(source);
  const copy = [lines[at].replace(`  ${from}:`, `  ${to}:`), ...lines.slice(at + 1, at + length)];
  const existing = entries.findIndex((entry) => entry.key === to);
  if (existing !== -1) {
    const old = span(existing);
    lines.splice(old.at, old.length, ...copy);
  } else {
    // pnpm keeps the importers sorted.
    const after = entries.find((entry) => entry.key > to);
    lines.splice(after === undefined ? end : after.at, 0, ...copy, "");
  }
  writeFileSync(file, lines.join("\n"));
  return true;
}

function install(cmd, args, cwd) {
  return spawnSync(cmd, args, { cwd, stdio: "inherit" }).status === 0;
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

  if (args.install && args.lang === "ts") {
    if (!addToLockfile(root, TEMPLATE_IMPORTER, rel)) {
      fail(
        `${rel} was created, but pnpm-lock.yaml has no ${TEMPLATE_IMPORTER} entry to copy; run pnpm install`,
      );
    }
    if (!install("pnpm", ["install", "--offline", "--frozen-lockfile"], root)) {
      fail(
        `${rel} was created and added to pnpm-lock.yaml, but pnpm could not install it offline: ` +
          "run pnpm install (or make bootstrap), which fetches what pnpm's store lacks",
      );
    }
  } else if (args.install && !install("uv", ["sync", "--locked", "--offline"], target)) {
    fail(
      `${rel} was created, but uv could not install it offline: run uv sync --locked in ${rel} ` +
        "(or make bootstrap), which fetches what uv's cache lacks",
    );
  }

  console.log("Next:");
  console.log(`  make test SERVICE=${name}   # unit and acceptance suites`);
  console.log("  make check                  # lint, types and tests of what changed");
  console.log(`  read ${rel}/README.md for what to fill in`);
}

main();
