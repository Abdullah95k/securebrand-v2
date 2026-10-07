import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { ROOT } from "../helpers/repo.js";

// Each docs lane, the kit template its files follow (when the kit has one) and a session that
// writes into it.
const LANES: { lane: string; template: string | null; owner: RegExp }[] = [
  { lane: "plans", template: "PLAN.md", owner: /\/plan-session/ },
  { lane: "handoffs", template: "HANDOFF.md", owner: /\/build-session/ },
  { lane: "reviews", template: "REVIEW.md", owner: /\/review-session/ },
  { lane: "issues", template: "ISSUE.md", owner: /\/build-session/ },
  { lane: "proposals", template: "PROPOSAL.md", owner: /\/contract-change/ },
  { lane: "decisions", template: "ADR.md", owner: /\bD2\b/ },
  { lane: "contracts", template: null, owner: /\bD1\b.*\bF2\b|\bF2\b.*\bD1\b/s },
  { lane: "gates", template: null, owner: /\bG0\b/ },
  { lane: "patterns", template: null, owner: /\bC0\b/ },
  { lane: "probes", template: "PROBE-REPORT.md", owner: /\/probe-platform/ },
];

describe("docs tree", () => {
  it.each(LANES)("every docs lane folder has a README naming its template: $lane", (entry) => {
    const readme = join(ROOT, "docs", entry.lane, "README.md");
    expect(existsSync(readme), readme).toBe(true);
    const text = readFileSync(readme, "utf8");
    if (entry.template !== null) {
      expect(text).toContain(`build-plan/templates/${entry.template}`);
    }
    expect(text).toMatch(entry.owner);
  });

  it("each reserved top-level folder has a README naming its owning session", () => {
    const reserved: [string, RegExp][] = [
      ["tests/e2e/README.md", /\bE1\b/],
      ["tools/gates/README.md", /\bE2\b/],
      ["tools/probes/README.md", /\/probe-platform/],
      ["fixtures/README.md", /scripts\/check-fixtures\.sh/],
      ["infra/README.md", /\bI1\b/],
    ];
    for (const [file, owner] of reserved) {
      const path = join(ROOT, file);
      expect(existsSync(path), file).toBe(true);
      expect(readFileSync(path, "utf8")).toMatch(owner);
    }
  });
});
