// Merge persona opening files into corpus.json, attaching ground-truth labels
// from scenarios.ts (labels are NEVER authored into the openings — they come
// from the scenario, so they can't drift). Run after the openings are generated.
//
//   reports/_work/openings/<persona>.json  =  [{ scenarioId, lang, opening }, ...]
//
// Usage: tsx eval/cli/build-corpus.ts
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { SCENARIOS } from "../scenarios.js";

const openingsDir = new URL("../reports/_work/openings/", import.meta.url);
const byId = new Map(SCENARIOS.map((s) => [s.id, s]));
const out: unknown[] = [];

for (const file of readdirSync(openingsDir).filter((f) => f.endsWith(".json"))) {
  const persona = file.replace(/\.json$/, "");
  const parts = JSON.parse(readFileSync(new URL(file, openingsDir), "utf8")) as {
    scenarioId: string; lang: string; opening: string;
  }[];
  for (const p of parts) {
    const s = byId.get(p.scenarioId);
    if (!s) throw new Error(`unknown scenarioId "${p.scenarioId}" in ${file}`);
    if (!p.opening?.trim()) throw new Error(`empty opening ${p.scenarioId}|${persona}|${p.lang}`);
    out.push({
      id: `${p.scenarioId}|${persona}|${p.lang}`,
      scenarioId: p.scenarioId, persona, lang: p.lang,
      opening: p.opening, expected: s.expected,
    });
  }
}

out.sort((a: any, b: any) => a.id.localeCompare(b.id));
writeFileSync(new URL("../corpus.json", import.meta.url), JSON.stringify(out, null, 2) + "\n");
console.log(`wrote corpus.json (${out.length} entries)`);
