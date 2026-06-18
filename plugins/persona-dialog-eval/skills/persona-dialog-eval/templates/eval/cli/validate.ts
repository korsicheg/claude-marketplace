// Validate corpus.json against scenarios, the label space, and completeness.
// Usage: tsx eval/cli/validate.ts
import { readFileSync } from "node:fs";
import { validateCorpus, type CorpusEntry } from "../engine.js";
import { SCENARIOS } from "../scenarios.js";
import { EVAL_CONFIG } from "../config.js";
import { labelOk } from "../labels.js";

const corpus = JSON.parse(
  readFileSync(new URL("../corpus.json", import.meta.url), "utf8"),
) as CorpusEntry[];
const expectedById = new Map(SCENARIOS.map((s) => [s.id, s.expected]));

const problems = validateCorpus(corpus, {
  personaIds: EVAL_CONFIG.personaIds,
  langs: EVAL_CONFIG.langs,
  scenarioIds: SCENARIOS.map((s) => s.id),
  expectedFor: (id) => expectedById.get(id),
  labelOk,
});

if (problems.length) {
  console.error(`✗ corpus has ${problems.length} problem(s):`);
  for (const p of problems) console.error("  - " + p);
  process.exit(1);
}
console.log(`✓ corpus valid (${corpus.length} entries)`);
