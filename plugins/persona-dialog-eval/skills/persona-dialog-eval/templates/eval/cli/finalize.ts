// Assembles ONE scenario's result FROM the script-written transcript — never
// from a driver's prose. This is the ENFORCEMENT GATE: it exits 3 ("keep
// driving") if the scenario has no classification, no other-action result, and
// hasn't hit the turn cap. So a fabricated/short dialog cannot be turned into an
// accepted result; only a real conversation that actually reached a decision
// (or genuinely ran out the cap) produces one.
//
//   tsx eval/cli/finalize.ts <corpusId> [maxTurns]
//
// Writes <WORK>/scenarios/<safeKey>.json = { id, turns, observed, surfaced?, outcome }
// (the same shape the aggregator joins to the labeled corpus by id — NO labels here).
// Exit codes: 0 finalized, 2 no transcript, 3 incomplete (keep driving).
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const WORK = process.env.EVAL_WORK_DIR ?? fileURLToPath(new URL("../reports/_work", import.meta.url));
const safeKey = (id: string) => id.replace(/[^a-zA-Z0-9._-]/g, "_");

const [corpusId, maxArg] = process.argv.slice(2);
const maxTurns = Number(maxArg ?? 12);
if (!corpusId) {
  console.error("usage: tsx eval/cli/finalize.ts <corpusId> [maxTurns]");
  process.exit(1);
}

const tpath = join(WORK, "transcripts", `${safeKey(corpusId)}.jsonl`);
if (!existsSync(tpath)) {
  console.error(`NO TRANSCRIPT for ${corpusId} — scenario never driven`);
  process.exit(2);
}
const lines = readFileSync(tpath, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));

const turns: { role: "customer" | "agent"; text: string }[] = [];
for (const ln of lines) {
  if (ln.customer != null) turns.push({ role: "customer", text: ln.customer });
  turns.push({ role: "agent", text: ln.agentText ?? "" });
}

let outcome: "ok" | "error" | "deferred";
let observed: Record<string, string> = {};
let surfaced: Record<string, unknown> | undefined;

const cls = lines.find((ln) => ln.classified);
if (cls) {
  outcome = "ok";
  observed = cls.classified;
  surfaced = cls.surfaced;
} else if (lines.some((ln) => ln.otherAction)) {
  outcome = "error";
} else if (lines.length >= maxTurns) {
  outcome = "deferred";
} else {
  console.error(
    `INCOMPLETE: ${corpusId} has ${lines.length} real turn(s), no classification, cap ${maxTurns} not reached — keep driving`,
  );
  process.exit(3);
}

const result = { id: corpusId, turns, observed, surfaced, outcome };
const outDir = join(WORK, "scenarios");
mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, `${safeKey(corpusId)}.json`), JSON.stringify(result));
console.log(`finalized ${corpusId}: ${outcome}, ${lines.length} real turns`);
