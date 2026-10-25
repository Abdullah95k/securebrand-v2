// make test SERVICE=text runs vitest directly, without turbo's ^build, and text imports contracts
// from its compiled dist/ (F2's handoff). Build it when a fresh checkout lacks it; under turbo it is
// built first, so this never writes while another task reads it.
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

const CONTRACTS_DIR = fileURLToPath(new URL("../../../contracts/", import.meta.url));

export default function setup(): void {
  if (existsSync(`${CONTRACTS_DIR}dist/index.js`)) return;
  execFileSync("pnpm", ["run", "build"], { cwd: CONTRACTS_DIR, stdio: "inherit" });
}
