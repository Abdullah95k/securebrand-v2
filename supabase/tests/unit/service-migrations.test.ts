// A40 (plan T19, Question 3): a service migration names only its own schema. The check the service
// runner applies before it runs a file refuses one that names public, auth, a Supabase schema or
// another service's schema, or that sets the search path or a role, creates or drops a schema, or
// grants; and every migration under services/*/migrations passes it, with a timestamped name.
import { describe, expect, it } from "vitest";
import { schemaProblems, serviceMigrations, serviceSchema } from "../../tools/migrate-services.ts";
import { SERVICES_DIR } from "../../tools/paths.ts";

describe("service migrations", () => {
  it("a service's schema is svc_ and its name with - as _", () => {
    expect(serviceSchema("fb-page-search")).toBe("svc_fb_page_search");
    expect(() => serviceSchema("Bad_Name")).toThrow(/not a service name/);
  });

  it("a service migration that stays in its own schema passes", () => {
    for (const sql of [
      "create table rows (row_id int primary key, note text);",
      "create table svc_demo_svc.rows (row_id int primary key);",
      "alter table rows add column seen_at timestamptz; create index on rows (seen_at);",
      "create function bump(r rows) returns int language sql as $$ select r.row_id + 1 $$;",
      "-- public.sources is read by the service, not by its migration\ncreate table rows (id int);",
      "insert into rows as t (row_id) values (1) on conflict (row_id) do update set row_id = excluded.row_id;",
    ])
      expect(schemaProblems("demo-svc", sql), sql).toEqual([]);
  });

  it("a service migration names only its own schema", () => {
    const cases: [string, RegExp][] = [
      ["create table public.leak (id int);", /names schema public/],
      [
        'insert into "public"."sources" (source_id) values (gen_random_uuid());',
        /names schema public/,
      ],
      ["select count(*) from auth.users;", /names schema auth/],
      ["create table svc_other_svc.rows (id int);", /names schema svc_other_svc/],
      [
        "create function f() returns bigint language sql as $$ select count(*) from public.cursors $$;",
        /names schema public/,
      ],
      ["do $$ begin execute 'delete from public.sources'; end $$;", /names schema public/],
      ["set search_path = public;", /sets the search path/],
      ["select set_config('search_path', 'public', true);", /sets the search path/],
      ["set role service_role;", /sets a role/],
      ["create schema extra;", /creates, changes or drops a schema/],
      ["grant select on rows to authenticated;", /grants or revokes/],
      ["alter default privileges grant select on tables to anon;", /grants or revokes/],
    ];
    for (const [sql, problem] of cases) {
      const problems = schemaProblems("demo-svc", sql);
      expect(
        problems.some((p) => problem.test(p)),
        `${sql}: ${problems.join("; ")}`,
      ).toBe(true);
    }
  });

  it("every service migration in the repository names only its own schema", () => {
    for (const m of serviceMigrations(SERVICES_DIR))
      expect(schemaProblems(m.service, m.sql), m.file).toEqual([]);
  });
});
