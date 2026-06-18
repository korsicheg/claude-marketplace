// Score raw subagent results against the labeled corpus and write a report folder.
// Raw results carry NO labels (id + turns + observed + outcome); this script joins
// them to corpus.json by id to attach `expected`, then aggregates.
// Usage: tsx eval/cli/aggregate.ts
import { readFileSync, writeFileSync, mkdirSync, readdirSync, existsSync } from "node:fs";
import { aggregate, type CorpusEntry, type ScenarioResult } from "../engine.js";
import { EVAL_CONFIG } from "../config.js";

const corpus = JSON.parse(
  readFileSync(new URL("../corpus.json", import.meta.url), "utf8"),
) as CorpusEntry[];
const byId = new Map(corpus.map((e) => [e.id, e]));

const rawDir = new URL("../reports/_work/raw/", import.meta.url);
if (!existsSync(rawDir)) {
  console.error("no raw results — run `eval:build-slice` and drive the dialog groups (write reports/_work/raw/group-NN.json) before aggregating");
  process.exit(1);
}
const rawFiles = readdirSync(rawDir).filter((f) => f.endsWith(".json"));
if (!rawFiles.length) {
  console.error("reports/_work/raw/ is empty — drive the dialog groups (write group-NN.json) before aggregating");
  process.exit(1);
}
const results: ScenarioResult[] = [];
for (const f of rawFiles) {
  const raw = JSON.parse(readFileSync(new URL(f, rawDir), "utf8")) as {
    id: string; turns: ScenarioResult["turns"]; observed: Record<string, string | null>;
    surfaced?: Record<string, unknown>; outcome: ScenarioResult["outcome"];
  }[];
  for (const r of raw) {
    const entry = byId.get(r.id);
    if (!entry) throw new Error(`raw result for unknown id "${r.id}"`);
    results.push({ entry, turns: r.turns, observed: r.observed, surfaced: r.surfaced, outcome: r.outcome });
  }
}

const { json, markdown } = aggregate(results, { fields: EVAL_CONFIG.scoredFields });
const ts = new Date().toISOString().replace(/[:.]/g, "-");
const dir = new URL(`../reports/${ts}/`, import.meta.url);
mkdirSync(dir, { recursive: true });
writeFileSync(new URL("report.md", dir), markdown);
writeFileSync(new URL("report.json", dir), JSON.stringify(json, null, 2));
writeFileSync(new URL("transcripts.jsonl", dir), results.map((r) => JSON.stringify(r)).join("\n") + "\n");
console.log(`scored ${results.length} scenarios -> ${decodeURIComponent(new URL(".", dir).pathname)}`);
