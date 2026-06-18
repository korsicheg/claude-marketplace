// Build payload files for a slice: filter corpus, STRIP labels, group for subagents.
// Each payload carries the opening + fact sheet + persona voice — never `expected`.
// Usage: tsx eval/cli/build-slice.ts [--persona a,b] [--lang en,el] [--story id,id] [--group N]
import { readFileSync, writeFileSync, mkdirSync, rmSync } from "node:fs";
import { SCENARIOS } from "../scenarios.js";
import { PERSONAS } from "../personas.js";
import { EVAL_CONFIG } from "../config.js";
import type { CorpusEntry } from "../engine.js";

const arg = (k: string): string[] | null => {
  const i = process.argv.indexOf("--" + k);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1].split(",") : null;
};
const fPersona = arg("persona"), fLang = arg("lang"), fStory = arg("story");
const groupSize = Number(arg("group")?.[0] ?? EVAL_CONFIG.groupSize);

const corpus = JSON.parse(
  readFileSync(new URL("../corpus.json", import.meta.url), "utf8"),
) as CorpusEntry[];
const scen = new Map(SCENARIOS.map((s) => [s.id, s]));
const voice = new Map(PERSONAS.map((p) => [p.id, p.guidance]));

const selected = corpus.filter(
  (e) =>
    (!fPersona || fPersona.includes(e.persona)) &&
    (!fLang || fLang.includes(e.lang)) &&
    (!fStory || fStory.includes(e.scenarioId)),
);

const payloads = selected.map((e) => ({
  id: e.id, scenarioId: e.scenarioId, persona: e.persona, lang: e.lang,
  opening: e.opening,
  voice: voice.get(e.persona),
  factSheet: scen.get(e.scenarioId)?.factSheet,
  problem: scen.get(e.scenarioId)?.problem,
  // NO `expected` — labels never reach the subagents.
}));

const workDir = new URL("../reports/_work/", import.meta.url);
rmSync(workDir, { recursive: true, force: true });
const payloadDir = new URL("payloads/", workDir);
mkdirSync(payloadDir, { recursive: true });
mkdirSync(new URL("raw/", workDir), { recursive: true });

const groups: typeof payloads[] = [];
for (let i = 0; i < payloads.length; i += groupSize) groups.push(payloads.slice(i, i + groupSize));
groups.forEach((g, i) =>
  writeFileSync(new URL(`group-${String(i).padStart(2, "0")}.json`, payloadDir), JSON.stringify(g, null, 2)),
);
writeFileSync(new URL("manifest.json", workDir), JSON.stringify({ groups: groups.length, total: payloads.length }, null, 2));
console.log(`built ${groups.length} group(s), ${payloads.length} scenarios (no labels). Drive each group-NN.json -> reports/_work/raw/group-NN.json`);
