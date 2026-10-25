// Once per acceptance run: this checkout's fresh database, test_<namespace>, built from the
// migrations and seeded. The stack's own Supabase database is migrated by make up or make migrate,
// never by the tests; the suites that read it check first that it holds this checkout's migrations.
import { freshDatabase } from "../helpers/fresh.ts";
import { testDatabaseName } from "../helpers/env.ts";

export default async function setup(): Promise<void> {
  await freshDatabase(testDatabaseName());
}
