import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { parse } from "yaml";
import { ROOT } from "../helpers/repo.js";

interface Step {
  name?: string;
  uses?: string;
  run?: string;
  if?: string;
  with?: Record<string, unknown>;
  env?: Record<string, string>;
}

interface Job {
  "runs-on"?: string;
  "timeout-minutes"?: number;
  permissions?: Record<string, string>;
  env?: Record<string, string>;
  steps: Step[];
}

interface Workflow {
  on: Record<string, unknown> | null;
  permissions?: Record<string, string>;
  concurrency?: { group: string; "cancel-in-progress"?: boolean };
  jobs: Record<string, Job>;
}

function workflow(name: string): Workflow {
  const text = readFileSync(join(ROOT, ".github", "workflows", name), "utf8");
  return parse(text) as Workflow;
}

function runText(job: Job): string {
  return job.steps.map((s) => s.run ?? "").join("\n");
}

const PINNED = /^[\w.-]+\/[\w.-]+(\/[\w./-]+)?@[0-9a-f]{40}$/;

describe("GitHub workflows", () => {
  const ci = workflow("ci.yml");
  const policy = workflow("policy.yml");
  const mirror = workflow("mirror-images.yml");

  it("the CI workflows define check, policy and template-smoke with every action pinned by SHA", () => {
    expect(Object.keys(ci.jobs)).toEqual(expect.arrayContaining(["check", "template-smoke"]));
    expect(Object.keys(policy.jobs)).toContain("policy");

    for (const wf of [ci, policy, mirror]) {
      expect(wf.permissions).toMatchObject({ contents: "read" });
      for (const [name, job] of Object.entries(wf.jobs)) {
        expect(job["runs-on"], name).toBe("ubuntu-24.04");
        expect(job["timeout-minutes"], name).toBeGreaterThan(0);
        for (const step of job.steps) {
          if (step.uses !== undefined && !step.uses.startsWith("./")) {
            expect(step.uses, `${name}: ${step.uses}`).toMatch(PINNED);
          }
        }
      }
    }

    const check = runText(ci.jobs.check ?? { steps: [] });
    for (const command of [
      "pnpm install --frozen-lockfile",
      "make up",
      "make check",
      "make smoke",
      "make down",
    ]) {
      expect(check).toContain(command);
    }
    const smoke = runText(ci.jobs["template-smoke"] ?? { steps: [] });
    expect(smoke).toContain("pnpm new:service demo && make check");
    expect(smoke).toMatch(/pnpm new:service \S+ --lang python && make check/);

    const policyRun = runText(policy.jobs.policy ?? { steps: [] });
    for (const command of [
      '"$POLICY_SCRIPTS/policy/check-contract-paths.sh"',
      '"$POLICY_SCRIPTS/policy/check-handoff-review.sh"',
      '"$POLICY_SCRIPTS/policy/check-dependencies.sh"',
      '"$POLICY_SCRIPTS/check-fixtures.sh"',
    ]) {
      expect(policyRun).toContain(command);
    }
  });

  it("the policy job runs the base branch's copy of the policy scripts, so a pull request cannot loosen its own checks", () => {
    const steps = policy.jobs.policy?.steps ?? [];
    const kit = steps.findIndex((s) => (s.run ?? "").includes("git archive"));
    expect(kit).toBeGreaterThan(-1);
    const extract = steps[kit]?.run ?? "";
    expect(extract).toContain('git archive "$POLICY_BASE" scripts');
    expect(extract).toContain("POLICY_SCRIPTS=");
    expect(extract).toContain("$GITHUB_ENV");
    // Every check runs after the extraction, from the extracted copy only.
    for (const step of steps.slice(0, kit)) {
      expect(step.run ?? "").not.toContain("check-");
    }
    for (const step of steps.slice(kit + 1)) {
      expect(step.run ?? "").not.toMatch(/(^|\s)scripts\//);
    }
  });

  it("on a push to main, make check compares with the commit before the push", () => {
    const step = (ci.jobs.check?.steps ?? []).find((s) => (s.run ?? "").includes("make check"));
    expect(step).toBeDefined();
    const base = step?.env?.CHECK_BASE ?? "";
    expect(base).toContain("github.event_name == 'push'");
    expect(base).toContain("github.event.before");
  });

  it("only CI's check job opts in to the acceptance test that resets the shared stack", () => {
    const step = (ci.jobs.check?.steps ?? []).find((s) => (s.run ?? "").includes("make check"));
    expect(step?.env?.TEST_STACK_RESET).toBe("1");
    const smoke = ci.jobs["template-smoke"]?.steps ?? [];
    for (const s of smoke) {
      expect(s.env?.TEST_STACK_RESET).toBeUndefined();
    }
  });

  it("runs CI on every pull request and on pushes to main, cancelling superseded runs", () => {
    expect(ci.on).toHaveProperty("pull_request");
    expect((ci.on?.push as { branches?: string[] }).branches).toEqual(["main"]);
    expect(ci.concurrency?.group).toContain("github.ref");
    expect(ci.concurrency?.["cancel-in-progress"]).toBe(true);
  });

  it("the check job still runs on docs-only pull requests so the required status exists", () => {
    const pr = (ci.on?.pull_request ?? {}) as Record<string, unknown>;
    expect(pr).not.toHaveProperty("paths");
    expect(pr).not.toHaveProperty("paths-ignore");
    const policyPr = (policy.on?.pull_request ?? {}) as Record<string, unknown>;
    expect(policyPr).not.toHaveProperty("paths");
    expect(policyPr).not.toHaveProperty("paths-ignore");
  });

  it("re-runs the policy job when labels change, and passes untrusted values through env only", () => {
    const types = (policy.on?.pull_request as { types: string[] }).types;
    expect(types).toEqual(
      expect.arrayContaining(["opened", "synchronize", "reopened", "labeled", "unlabeled"]),
    );
    for (const wf of [ci, policy, mirror]) {
      for (const job of Object.values(wf.jobs)) {
        for (const step of job.steps) {
          expect(step.run ?? "").not.toMatch(/\$\{\{\s*github\.(head_ref|event)/);
        }
      }
    }
  });

  it("the mirror workflow runs on demand and on pushes to any branch that change stack/versions.env", () => {
    expect(mirror.on).toHaveProperty("workflow_dispatch");
    const push = mirror.on?.push as { paths: string[]; branches?: string[] };
    expect(push.paths).toContain("stack/versions.env");
    expect(push.branches).toBeUndefined();
    expect(mirror.permissions).toMatchObject({ packages: "write" });
    const job = Object.values(mirror.jobs)[0];
    expect(job).toBeDefined();
    const steps = job?.steps ?? [];
    const dockerHub = steps.find(
      (s) => s.uses?.startsWith("docker/login-action") && s.with?.registry === undefined,
    );
    expect(dockerHub?.if).toMatch(/DOCKERHUB_USERNAME/);
    expect(runText(job ?? { steps: [] })).toContain("scripts/mirror-images.sh");
    // Only main may replace a mirrored tag whose digest no longer matches its upstream.
    const copy = steps.find((s) => (s.run ?? "").includes("scripts/mirror-images.sh"));
    expect(copy?.env?.MIRROR_REPLACE).toBe("${{ github.ref == 'refs/heads/main' && '1' || '' }}");
  });

  it("dependabot covers npm, uv, docker and github-actions weekly and grouped with a low limit", () => {
    const config = parse(readFileSync(join(ROOT, ".github", "dependabot.yml"), "utf8")) as {
      updates: {
        "package-ecosystem": string;
        schedule: { interval: string };
        "open-pull-requests-limit": number;
        groups?: Record<string, unknown>;
      }[];
    };
    const ecosystems = config.updates.map((u) => u["package-ecosystem"]).sort();
    expect(ecosystems).toEqual(["docker", "github-actions", "npm", "uv"]);
    for (const update of config.updates) {
      expect(update.schedule.interval).toBe("weekly");
      expect(update["open-pull-requests-limit"]).toBeLessThanOrEqual(3);
      expect(update.groups).toBeDefined();
    }
  });
});
