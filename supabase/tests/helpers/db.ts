// Database helpers for the acceptance tests: one client per call, a role taken with `set local role`
// inside a transaction that is always rolled back, so nothing a test writes stays, and a statement's
// refusal read back as its SQLSTATE through a savepoint, so the session stays usable after it.
import pg from "pg";

export type Row = Record<string, unknown>;

/** The roles a session can take: Supabase's three API roles, the D3 servers' role and the owner. */
export type Role = "anon" | "authenticated" | "service_role" | "admin_api" | "postgres";

export interface Session {
  rows<R extends Row = Row>(sql: string, params?: unknown[]): Promise<R[]>;
  /** The SQLSTATE of the statement's error, or null when it succeeds. */
  failure(sql: string, params?: unknown[]): Promise<string | null>;
}

export async function withClient<T>(
  url: string,
  fn: (client: pg.Client) => Promise<T>,
): Promise<T> {
  const client = new pg.Client({ connectionString: url });
  await client.connect();
  try {
    return await fn(client);
  } finally {
    await client.end();
  }
}

function sqlState(error: unknown): string {
  if (error instanceof Error && "code" in error && typeof error.code === "string")
    return error.code;
  throw error;
}

export function session(client: pg.Client): Session {
  let savepoint = 0;
  return {
    async rows<R extends Row = Row>(sql: string, params: unknown[] = []): Promise<R[]> {
      return (await client.query<R>(sql, params)).rows;
    },
    async failure(sql: string, params: unknown[] = []): Promise<string | null> {
      const name = `attempt_${++savepoint}`;
      await client.query(`savepoint ${name}`);
      try {
        await client.query(sql, params);
        await client.query(`release savepoint ${name}`);
        return null;
      } catch (error) {
        await client.query(`rollback to savepoint ${name}`);
        return sqlState(error);
      }
    },
  };
}

/**
 * Runs `fn` as `role`, with the JWT claims Supabase's auth.uid() and auth.jwt() read (`sub` the
 * user's id, when given), inside a transaction that is rolled back whatever happens.
 */
export async function asRole<T>(
  url: string,
  role: Role,
  fn: (s: Session) => Promise<T>,
  sub?: string,
): Promise<T> {
  return withClient(url, async (client) => {
    await client.query("begin");
    try {
      const claims = JSON.stringify(sub === undefined ? { role } : { role, sub });
      await client.query("select set_config('request.jwt.claims', $1, true)", [claims]);
      if (role !== "postgres") await client.query(`set local role ${role}`);
      return await fn(session(client));
    } finally {
      await client.query("rollback");
    }
  });
}

/** Runs `fn` as the owner inside a transaction that is rolled back. */
export async function inRollback<T>(url: string, fn: (s: Session) => Promise<T>): Promise<T> {
  return asRole(url, "postgres", fn);
}

/** A quoted SQL identifier. */
export function ident(name: string): string {
  return `"${name.replaceAll('"', '""')}"`;
}
