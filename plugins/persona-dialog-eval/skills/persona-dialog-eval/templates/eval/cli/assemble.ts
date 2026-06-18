// Combines the per-scenario results (written by finalize.ts) for one payload
// group into the group raw file the aggregator consumes. REQUIRES every scenario
// in the payload to be finalized; otherwise it errors and lists exactly which
// ids are still missing (the group-level gate). A raw file is produced only when
// all its scenarios are backed by real, finalized transcripts.
//
//   tsx eval/cli/assemble.ts <payloadGroupFile>
//   e.g. tsx eval/cli/assemble.ts eval/reports/_work/payloads/group-03.json
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const WORK = process.env.EVAL_WORK_DIR ?? fileURLToPath(new URL("../reports/_work", import.meta.url));
const safeKey = (id: string) => id.replace(/[^a-zA-Z0-9._-]/g, "_");

const payloadPath = process.argv[2];
if (!payloadPath) {
  console.error("usage: tsx eval/cli/assemble.ts <payloadGroupFile>");
  process.exit(1);
}
const payload: { id: string }[] = JSON.parse(readFileSync(payloadPath, "utf8"));

const results: unknown[] = [];
const missing: string[] = [];
for (const s of payload) {
  const p = join(WORK, "scenarios", `${safeKey(s.id)}.json`);
  if (!existsSync(p)) {
    missing.push(s.id);
    continue;
  }
  const r = JSON.parse(readFileSync(p, "utf8"));
  r.id = s.id; // authoritative id from the payload
  results.push(r);
}
if (missing.length) {
  console.error(`${basename(payloadPath)}: MISSING ${missing.length}/${payload.length} — still need: ${missing.join(", ")}`);
  process.exit(2);
}
const rawDir = join(WORK, "raw");
mkdirSync(rawDir, { recursive: true });
const outPath = join(rawDir, basename(payloadPath));
writeFileSync(outPath, JSON.stringify(results, null, 2));
const tally = (results as { outcome: string }[]).reduce<Record<string, number>>(
  (a, r) => ((a[r.outcome] = (a[r.outcome] || 0) + 1), a),
  {},
);
console.log(`assembled ${outPath}: ${results.length} scenarios — ${JSON.stringify(tally)}`);
