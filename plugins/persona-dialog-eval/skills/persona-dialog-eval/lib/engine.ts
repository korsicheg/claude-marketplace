// Reusable, project-agnostic engine for a persona-dialog eval.
//
// PURE — no I/O, no framework, no external deps. Generalizes the cmt-agent
// implementation: it scores an arbitrary set of MANDATORY scored fields
// (`expected`/`observed` keyed by field name), surfaces optional context
// unscored, and renders a report (accuracy per field, a per-expected-value
// breakdown, per-persona / per-language / per-scenario breakdowns, dialog
// metrics, misses).
//
// You provide: ScenarioResult[] (built by your runner — see runner.ts) and,
// for validation, predicates over your label space.

export type Outcome = "ok" | "deferred" | "error";

export interface TurnRecord {
  role: "customer" | "agent";
  text: string;
}

/** One committed scenario seed: scenario × persona × lang + its opening line.
 *  `expected` holds the scored ground-truth fields, copied from the base
 *  scenario and NEVER re-derived. */
export interface CorpusEntry {
  id: string; // canonical: `${scenarioId}|${persona}|${lang}`
  scenarioId: string;
  persona: string;
  lang: string;
  opening: string;
  expected: Record<string, string>;
}

/** Result of running one scenario's dialog and scoring it. `observed` carries
 *  the scored fields the agent emitted (null when it never classified);
 *  `surfaced` carries unscored context (confidence, optional fields, …). */
export interface ScenarioResult {
  entry: CorpusEntry;
  turns: TurnRecord[];
  observed: Record<string, string | null>;
  surfaced?: Record<string, unknown>;
  outcome: Outcome;
}

export interface FieldStats {
  field: string;
  total: number;
  hits: number;
  accuracy: number; // hits / total (deferred & error count as a miss)
  confusion: Record<string, Record<string, number>>; // expected -> observed|deferred|error -> n
}

export interface CellStats {
  n: number;
  fullHits: number; // every scored field correct
  deferred: number;
  errors: number;
  perField: Record<string, number>; // field -> hits within this cell
}

export interface MissRecord {
  id: string;
  persona: string;
  lang: string;
  scenarioId: string;
  outcome: Outcome;
  expected: Record<string, string>;
  observed: Record<string, string | null>;
  opening: string;
}

export interface ReportData {
  total: number;
  scored: number; // outcome === "ok"
  deferred: number;
  errors: number;
  fields: FieldStats[];
  byPersona: Record<string, CellStats>;
  byLanguage: Record<string, CellStats>;
  byScenario: Record<string, CellStats>;
  avgTurnsToClassify: number;
  avgTurnsByPersona: Record<string, number>;
  deferredRateByPersona: Record<string, number>;
  misses: MissRecord[];
}

function fieldNames(results: ScenarioResult[], explicit?: string[]): string[] {
  if (explicit) return explicit;
  const s = new Set<string>();
  for (const r of results) for (const k of Object.keys(r.entry.expected)) s.add(k);
  return [...s].sort();
}

function hit(r: ScenarioResult, f: string): boolean {
  return r.observed[f] != null && r.observed[f] === r.entry.expected[f];
}

function fullHit(r: ScenarioResult, fields: string[]): boolean {
  return fields.every((f) => hit(r, f));
}

function agentTurns(r: ScenarioResult): number {
  return r.turns.filter((t) => t.role === "agent").length;
}

function emptyCell(fields: string[]): CellStats {
  const perField: Record<string, number> = {};
  for (const f of fields) perField[f] = 0;
  return { n: 0, fullHits: 0, deferred: 0, errors: 0, perField };
}

function bump(map: Record<string, CellStats>, key: string, r: ScenarioResult, fields: string[]): void {
  const c = (map[key] ??= emptyCell(fields));
  c.n++;
  if (fullHit(r, fields)) c.fullHits++;
  if (r.outcome === "deferred") c.deferred++;
  if (r.outcome === "error") c.errors++;
  for (const f of fields) if (hit(r, f)) c.perField[f]++;
}

export function aggregate(
  results: ScenarioResult[],
  opts: { fields?: string[] } = {},
): { json: ReportData; markdown: string } {
  const fields = fieldNames(results, opts.fields);
  const total = results.length;
  const ok = results.filter((r) => r.outcome === "ok");
  const scored = ok.length;
  const deferred = results.filter((r) => r.outcome === "deferred").length;
  const errors = results.filter((r) => r.outcome === "error").length;

  const fieldStats: FieldStats[] = fields.map((f) => {
    const hits = results.filter((r) => hit(r, f)).length;
    const confusion: Record<string, Record<string, number>> = {};
    for (const r of results) {
      const row = (confusion[r.entry.expected[f] ?? "(none)"] ??= {});
      const col = r.outcome === "ok" ? (r.observed[f] ?? "none") : r.outcome;
      row[col] = (row[col] ?? 0) + 1;
    }
    return { field: f, total, hits, accuracy: total ? hits / total : 0, confusion };
  });

  const byPersona: Record<string, CellStats> = {};
  const byLanguage: Record<string, CellStats> = {};
  const byScenario: Record<string, CellStats> = {};
  for (const r of results) {
    bump(byPersona, r.entry.persona, r, fields);
    bump(byLanguage, r.entry.lang, r, fields);
    bump(byScenario, r.entry.scenarioId, r, fields);
  }

  const avgTurnsToClassify = scored ? ok.reduce((a, r) => a + agentTurns(r), 0) / scored : 0;
  const avgTurnsByPersona: Record<string, number> = {};
  const deferredRateByPersona: Record<string, number> = {};
  for (const [p, c] of Object.entries(byPersona)) {
    const okP = ok.filter((r) => r.entry.persona === p);
    avgTurnsByPersona[p] = okP.length ? okP.reduce((a, r) => a + agentTurns(r), 0) / okP.length : 0;
    deferredRateByPersona[p] = c.n ? c.deferred / c.n : 0;
  }

  const misses: MissRecord[] = results
    .filter((r) => !fullHit(r, fields))
    .map((r) => ({
      id: r.entry.id,
      persona: r.entry.persona,
      lang: r.entry.lang,
      scenarioId: r.entry.scenarioId,
      outcome: r.outcome,
      expected: r.entry.expected,
      observed: r.observed,
      opening: r.entry.opening,
    }));

  const json: ReportData = {
    total, scored, deferred, errors,
    fields: fieldStats,
    byPersona, byLanguage, byScenario,
    avgTurnsToClassify, avgTurnsByPersona, deferredRateByPersona, misses,
  };
  return { json, markdown: renderMarkdown(json) };
}

const pct = (x: number): string => (x * 100).toFixed(1) + "%";

/** Escape `|` so cell content (e.g. a corpus id "scenario|persona|lang", or a
 *  value containing a pipe) doesn't split into extra Markdown table columns. */
const esc = (s: unknown): string => String(s).replace(/\|/g, "\\|");

function renderMarkdown(d: ReportData): string {
  const L: string[] = [];
  L.push(`# Persona-Dialog Eval Report`, ``);
  L.push(`- Scenarios: **${d.total}** (scored ${d.scored}, deferred ${d.deferred}, errors ${d.errors})`);
  for (const f of d.fields) L.push(`- ${f.field} accuracy: **${pct(f.accuracy)}** (${f.hits}/${f.total})`);
  L.push(`- avg agent turns to classify: ${d.avgTurnsToClassify.toFixed(2)}`, ``);

  // For each scored field, break down — per EXPECTED value — what the agent
  // actually produced. (Same information as a confusion matrix, but rendered as
  // a readable list: long values + sparse rows make a wide grid unreadable.)
  // ✓ marks the correct output, ✗ a miss; `deferred`/`error` = it produced none.
  for (const f of d.fields) {
    L.push(`## ${f.field}: expected → what the agent produced`, ``);
    for (const [exp, row] of Object.entries(f.confusion)) {
      const total = Object.values(row).reduce((a, b) => a + b, 0);
      const correct = row[exp] ?? 0;
      L.push(`- **${exp}** — ${correct}/${total} correct (${pct(total ? correct / total : 0)})`);
      for (const [obs, n] of Object.entries(row).sort((a, b) => b[1] - a[1])) {
        L.push(`  - ${obs === exp ? "✓" : "✗"} ${obs} ×${n}`);
      }
    }
    L.push(``);
  }

  const cellTable = (title: string, m: Record<string, CellStats>) => {
    L.push(`## ${title}`, ``);
    const fields = d.fields.map((f) => f.field);
    L.push(`| key | n | full-hit | ${fields.join(" | ")} | deferred | errors |`);
    // Columns = key, n, full-hit (3) + one per field + deferred, errors (2).
    L.push(`|${"---|".repeat(fields.length + 5)}`);
    for (const [k, c] of Object.entries(m)) {
      const fcols = fields.map((f) => (c.n ? pct(c.perField[f] / c.n) : "-"));
      L.push(`| ${esc(k)} | ${c.n} | ${c.n ? pct(c.fullHits / c.n) : "-"} | ${fcols.join(" | ")} | ${c.deferred} | ${c.errors} |`);
    }
    L.push(``);
  };
  cellTable("By persona", d.byPersona);
  cellTable("By language", d.byLanguage);
  cellTable("By scenario", d.byScenario);

  L.push(`## Dialog metrics by persona`, ``);
  L.push(`| persona | avg turns | deferred rate |`, `|---|---|---|`);
  for (const p of Object.keys(d.avgTurnsByPersona)) {
    L.push(`| ${p} | ${d.avgTurnsByPersona[p].toFixed(2)} | ${pct(d.deferredRateByPersona[p] ?? 0)} |`);
  }
  L.push(``);

  L.push(`## Misses (${d.misses.length})`, ``);
  if (!d.misses.length) {
    L.push(`_none_`, ``);
  } else {
    L.push(
      "A miss = the agent's output differs from the expected value on ≥1 scored field. **miss on** = which field(s) differed (or `both`/`all`); **expected** = the ground truth; **agent** = what the agent produced (`—` if it produced none, i.e. the dialog deferred/errored).",
      "",
    );
    L.push(
      `| scenario | persona | lang | miss on | expected | agent |`,
      `|---|---|---|---|---|---|`,
    );
    for (const m of d.misses) {
      const allFields = Object.keys(m.expected);
      const missed = allFields.filter((k) => m.observed[k] !== m.expected[k]);
      const missOn =
        missed.length === allFields.length
          ? allFields.length === 2
            ? "both"
            : "all"
          : missed.join(", ") || "—";
      const e = Object.entries(m.expected).map(([k, v]) => `${k}=${v}`).join(", ");
      const o = Object.entries(m.observed).map(([k, v]) => `${k}=${v ?? "—"}`).join(", ");
      L.push(`| ${esc(m.scenarioId)} | ${m.persona} | ${m.lang} | ${missOn} | ${esc(e)} | ${esc(o)} |`);
    }
    L.push(``);
  }
  return L.join("\n");
}

// ─── Corpus validation ───────────────────────────────────────────────────────
// Domain-agnostic via injected predicates. `personaIds`/`langs`/`scenarioIds`
// define the expected grid; `labelOk(field, value)` checks a label is in the
// real label space (enumerate it via your system's runtime code path, NOT docs);
// `expectedFor(scenarioId)` returns the frozen ground truth for a scenario.

export interface ValidateConfig {
  personaIds: string[];
  langs: string[];
  scenarioIds: string[];
  expectedFor: (scenarioId: string) => Record<string, string> | undefined;
  labelOk: (field: string, value: string) => boolean;
}

export function validateCorpus(corpus: CorpusEntry[], cfg: ValidateConfig): string[] {
  const problems: string[] = [];
  const personas = new Set(cfg.personaIds);
  const langs = new Set(cfg.langs);
  const seen = new Set<string>();

  for (const e of corpus) {
    const truth = cfg.expectedFor(e.scenarioId);
    if (!truth) {
      problems.push(`${e.id}: unknown scenarioId "${e.scenarioId}"`);
      continue;
    }
    for (const [f, v] of Object.entries(truth)) {
      if (e.expected[f] !== v) problems.push(`${e.id}: ${f} mismatch (entry "${e.expected[f]}" vs scenario "${v}")`);
    }
    for (const [f, v] of Object.entries(e.expected)) {
      if (!cfg.labelOk(f, v)) problems.push(`${e.id}: ${f}="${v}" not in the label space`);
    }
    if (!e.opening || !e.opening.trim()) problems.push(`${e.id}: empty opening`);
    if (!personas.has(e.persona)) problems.push(`${e.id}: unknown persona "${e.persona}"`);
    if (!langs.has(e.lang)) problems.push(`${e.id}: unknown lang "${e.lang}"`);
    const key = `${e.scenarioId}|${e.persona}|${e.lang}`;
    if (e.id !== key) problems.push(`${e.id}: id should be "${key}"`);
    if (seen.has(key)) problems.push(`duplicate cell ${key}`);
    seen.add(key);
  }

  for (const s of cfg.scenarioIds)
    for (const p of cfg.personaIds)
      for (const l of cfg.langs) {
        const key = `${s}|${p}|${l}`;
        if (!seen.has(key)) problems.push(`missing cell ${key}`);
      }
  return problems;
}
