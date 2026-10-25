// The paths the schema's tools and tests read, from this workspace's place in the repository.
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export const SUPABASE_DIR = resolve(dirname(fileURLToPath(import.meta.url)), "..");
export const REPO_DIR = resolve(SUPABASE_DIR, "..");
export const MIGRATIONS_DIR = join(SUPABASE_DIR, "migrations");
export const SEEDS_DIR = join(SUPABASE_DIR, "seeds");
export const SERVICES_DIR = join(REPO_DIR, "services");
export const SUPABASE_CLI = join(REPO_DIR, "node_modules/.bin/supabase");
export const CONVENTIONS_FILE = join(REPO_DIR, "docs/prds/_shared/CONVENTIONS.md");
export const TABLE_OWNERS_FILE = join(REPO_DIR, "docs/contracts/TABLE-OWNERS.md");
export const CONTRACTS_DIR = join(REPO_DIR, "packages/contracts");
export const DATABASE_TYPES_FILE = join(CONTRACTS_DIR, "src/db/database.types.ts");
