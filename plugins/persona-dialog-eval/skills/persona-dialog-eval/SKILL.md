---
name: persona-dialog-eval
description: Use when you want to evaluate, test, or measure whether a conversational agent or chatbot makes the right classification, categorization, routing, intent, or severity decision — and whether that decision holds up across user personalities (rude, nervous, technical, clueless), phrasings, and languages. Also when setting up or scaffolding such an eval harness, or measuring accuracy by persona and language with a confusion matrix. Not for testing task execution (DB writes, side effects) or free-form chat quality with no discrete labeled decision.
---

# Persona-Dialog Eval

## Overview

To measure whether a conversational agent classifies/routes correctly, **hold the underlying case fixed (with a known ground-truth label) and vary only the speaker** — personality and language — then have an LLM play that speaker in a real dialog with the *actual* agent, and score the agent's emitted classification against the fixed label.

**Vary the surface, fix the truth.** Personas and language change *how* the story is told; they never change the facts or the label. That gap is exactly the robustness you're testing.

## When to use

- Evaluating a classifier/router/intent-detector inside a chat agent (which category, team, type, severity, intent).
- You suspect phrasing, tone, or language changes the answer.
- You want accuracy broken down by persona and language, plus a per-expected-value breakdown (a readable confusion view) and a miss list.

**Not for:** testing task *execution* (DB writes, side effects), or single-prompt classifiers with no dialog (just feed inputs directly — you don't need this).

## Scaffolding procedure (run this skill)

When invoked to set up an eval, produce a complete, validated `eval/` in the user's project. Work in their repo.

1. **Understand the agent first, then interview only the gaps.** Read the agent's system prompt, tools, and code and state in one line *what the agent is and the single decision it makes* — everything else derives from that. Infer from the repo first; ask the user only what you genuinely cannot determine:
   - how to run ONE conversation turn (entrypoint function, or a command);
   - the decision to evaluate and the **mandatory** field(s) to score (category / team / intent / severity);
   - how the agent surfaces its chosen label per turn (tool/step + result field, or a return value);
   - where the **label space** is defined in code (enum / config / loader) — enumerate it from there, never from docs;
   - languages to test; scenario themes (infer from the domain).

2. **Choose location & runtime.** Default `<project>/eval/`. Run the TS CLIs with `tsx` (add as a devDep if missing); if the project compiles to `dist/`, point the npm scripts there instead.

3. **Copy the engine verbatim** from this skill's `lib/`: `engine.ts`, `runner.ts`, `personas.ts`, `engine.test.ts` → `eval/` (trim personas to the audience if useful). `engine.test.ts` is project-agnostic — it guards the scoring / validation / report-render logic you might later tweak, so ship it with every scaffold.

4. **Copy `templates/eval/` → `eval/` and fill the seams:**
   - `config.ts` — `scoredFields`, `personaIds`, `langs`, `groupSize`.
   - `labels.ts` — replace `allowedLabels` with the **real** enumeration from the agent's runtime code path; spot-check values against what the agent actually emits.
   - `scenarios.ts` — author scenarios from the business case (`{id, expected, factSheet, problem}`); cover each label ≥1×; `expected` uses real labels.
   - `agent-turn.ts` — wire to the agent (Variant A in-process / Variant B subprocess); map its classification → `classified`, optional fields → `surfaced`; stop at the classification step. If Variant A parses a streamEvents/tool envelope in-process, factor the **pure** parsing into its own module (e.g. `eval/event-parse.ts`) so it's unit-testable without booting the agent — a silently-broken parser makes every dialog falsely `deferred`.
   - `cli/*` and `README.md` — copy as-is; fix import paths only if the layout differs. The enforced-driving CLIs (`drive-turn`, `finalize`, `scenario-state`, `assemble`) are how runs are driven — see "Driving without fabrication."
   - `customer-reply.ts` — fill in only if you'll use Path A (an API-backed customer); otherwise delete it.
   - Add npm scripts: `eval:build-corpus`, `eval:validate`, `eval:build-slice`, `eval:aggregate` (each `tsx eval/cli/<x>.ts`), plus `eval:test` (`node --import tsx --test "eval/*.test.ts"`), and `eval:typecheck` (`tsc --noEmit -p eval/tsconfig.json`) when `eval/` falls outside the project's `tsconfig`.
   - **Tests** — `engine.test.ts` ships with the engine (step 3). Add one small test per *logic* seam you edit: the adapter's pure envelope parser (`event-parse.test.ts`) and the label-space loader (`labels.test.ts`). `scenarios.ts` / `config.ts` are data — `eval:validate` covers them. All `eval/*.test.ts` run under `eval:test`; they make `eval/` safe to change later.
   - **Ground-truth review gate — do this before generating the corpus.** The `expected` labels in `scenarios.ts` are *the answer key the agent is graded against*; you drafted them from your reading of the agent, and `validate` only checks they are *real* labels, not that they are the **right** label for each scenario. Show the user the drafted `{scenario → expected}` list and get a quick confirm/correction. A wrong key measures "does the agent agree with you," not correctness — never skip this on the ambiguous cases (the clear-home ones are usually safe).

5. **Generate the corpus** (only after the ground-truth review passes). For each scenario × persona × lang, write a persona-voiced opening (in that language) from the scenario's `problem`/`factSheet` — never name a label. Parallelize with subagents; write `eval/reports/_work/openings/<persona>.json` = `[{scenarioId, lang, opening}]`. Then `npm run eval:build-corpus`.

6. **Validate & hand off.** `npm run eval:validate` → must be `✓ corpus valid`; fix scenarios/labels until green. Stop here (scaffold + corpus + validate). Point the user at `eval/README.md` to run a slice.

**Generated layout:**
```
eval/ engine.ts runner.ts personas.ts config.ts scenarios.ts labels.ts agent-turn.ts customer-reply.ts corpus.json README.md
      engine.test.ts  (+ project seam tests you add: event-parse.test.ts, labels.test.ts)   # run by eval:test
      cli/ build-corpus.ts validate.ts build-slice.ts aggregate.ts        # corpus + scoring
           drive-turn.ts finalize.ts scenario-state.ts assemble.ts        # enforced driving (Path B)
           run-turn.ts                                                     # optional ad-hoc single-turn helper
```
The engine (`lib/`) is copied unchanged; `templates/eval/` are the fill-in files. Both halves are verified — the engine has unit tests and the generated CLI pipeline runs end-to-end via `tsx`.

## Building blocks

| Artifact | What it is |
|---|---|
| **Base scenarios** | N canonical cases. Each carries the **ground-truth label** (the field the agent must get right) + a **fact sheet**: everything the simulated user knows, so they can answer the agent's intake questions. Put optional/unscored fields in the fact sheet too (so the customer can supply them if asked) — just don't score them. |
| **Personas** | A small set spanning the stress axes: tone (rude, arrogant, nervous, polite) × expertise (technical, non-technical, clueless). A persona is *only* a voice instruction. |
| **Languages** | Each scenario × persona × language. |
| **Corpus** | scenario × persona × language → an LLM-generated **opening line** in persona voice. Committed and reviewable; ground-truth labels attached from the base scenario, **never re-derived**. |
| **Report** | overall accuracy, a per-expected-value breakdown (expected → what the agent produced, with ✓/✗ and a hit rate), per-persona & per-language breakdowns, dialog metrics (turns-to-classify, deferred rate per persona), full miss list (scenario · persona · lang · which field missed · expected · agent). |

## The dialog loop

The **customer is played by your coding LLM** (the one already running this session — no extra API key). The **agent-under-test is the real system.** Per scenario:

```
history = [opening]
loop (cap at MAX_TURNS — size it ABOVE the agent's full intake; see Non-negotiables #9):
    agent = one REAL turn of the agent over history     # the only paid/real call
    if agent emitted the classification: capture it, stop        -> outcome "ok"
    if agent emitted some other action:  stop                    -> outcome "error"
    else (agent asked a question):
        reply = LLM-as-customer, in persona+language, from the fact sheet, BEHAVING as the persona
                (don't dump a clean list of fields when asked many at once — see "Playing the customer")
        history += agent question + reply
else: outcome "deferred"        # never classified within the cap
score: did the captured classification match the fixed label?
```

**Playing the customer:** lean fully into the persona — *behaviour*, not just tone. Reveal only what this persona would, the way they would; don't be more helpful, organised, or complete than they'd be. A clean dump of every requested field is in character **only** for cooperative/competent personas (technical / non-technical); a rude/arrogant customer pushes back and gives one grudgingly, a clueless one misunderstands and asks, a nervous one rambles and misses some. It's fine if a difficult persona stalls the agent into a `deferred` — that's the signal, not a bug. (Failure mode caught in testing: every persona collapsing into a tidy, cooperative answer once the agent asks its full intake checklist — the persona becomes mere word-choice.)

## Driving without fabrication (the part that actually matters)

**The failure mode that silently wrecks this eval:** if you hand a subagent the whole loop *and* let it write its own result file, then under normal model laziness it will **fabricate** the dialog (no real agent calls at all) or **script** it (real calls, but canned non-persona replies). Observed in practice: **~75% of "driven" runs were fake**, and the fake data looks completely plausible. Detecting-then-discarding still burns the run. So the goal is to make fabrication *impossible*, not detectable.

**Principle: the driver must not own the loop *and* author the results.** Pick the path your setup allows:

**Path A — code-driven (use whenever you can call a customer model programmatically).** Wire `customerReply` to an LLM API (`customer-reply.ts`) and run `runScenario()` in a small batch script. The loop is code; the model is asked for exactly ONE reply per call, so it cannot skip turns or invent the agent's side. Keep the customer a *different* model family from the agent under test. Strongest setup — no subagents, nothing to audit.

**Path B — enforced subagent (when the customer must be your in-session coding agent, no API key).** The subagent drives but is structurally barred from authoring results:
- It calls `cli/drive-turn.ts <corpusId> <in> <out>` per turn — that script runs the real agent turn AND appends it to a script-owned transcript. The subagent **never writes a result file.**
- `cli/finalize.ts <corpusId>` assembles the result FROM the transcript and **exits 3 ("keep driving") until a real classification exists** — a fabricated/short dialog can't become an accepted result.
- `cli/scenario-state.ts <corpusId>` makes it resumable: a re-dispatch continues from the last real turn (survives session-limit cutoffs; a rejected run costs only its remainder).
- `cli/assemble.ts <payloadGroupFile>` combines finalized scenarios into the group raw file; errors until all are present.

**Audit every Path-B group before trusting it** (genuine vs fabricated/scripted):
- real-turn count in the transcript **must equal** the recorded turns;
- subagent `tool_uses` — genuine driving ≈ 3–4 calls/turn (50+ for a 12-scenario group); a fabricated/scripted group shows ~5–11 *total*;
- turn-count **variance** — real dialogs vary (cooperative ~N turns, difficult N+); all-identical counts ⇒ scripted;
- skim a couple of difficult-persona replies — genuinely rude/confused, or flattened into compliance?
Reject and re-dispatch (it resumes) anything that fails. **Never trust a `12 ok` self-report — verify against disk.**

## Non-negotiable design decisions (the hard-won ones)

1. **Score the MANDATORY field; surface optional ones unscored.** Pick the field the system actually requires. Scoring an optional/often-empty field measures noise. (CMT: category is mandatory, product optional → score category.)
2. **Ground truth must come from the real label space.** Enumerate the agent's actual options via the *same code path the system uses*, not a docs/CSV eyeball. A label the classifier can never return makes every case a false miss.
3. **Never teach to the test.** When the agent resolves differently than your label, do NOT relabel to match — that inflates accuracy and hides the finding. Genuine ambiguity (one concept with two valid homes) is a *result*, shown in the miss list.
4. **The agent must be the real one.** Only the customer is role-play; replacing the agent with your LLM measures the wrong system.
5. **Stop at the classification step.** Don't execute past it → no side effects / real records. (Mutations should be gated anyway.)
6. **Eliciting the classification often needs the full intake.** If the agent gates classification behind collecting fields, the customer must supply them from the fact sheet — so one message rarely suffices; that's why it's a dialog.
7. **Commit the corpus.** Generate openings once, review, commit → reproducible runs. Regenerate deliberately, not per run.
8. **Never let the dialog-driver author its own results.** A model that owns the loop *and* writes the result file will fabricate or script the dialog (~75% junk observed). Drive in code (Path A) or via the enforced transcript + gate (Path B); results must be assembled from real turns only. See "Driving without fabrication."
9. **Size the turn cap above the agent's intake.** `deferred` must mean the agent genuinely failed to decide, not that your cap was shorter than its intake. An 8-cap manufactured ~36% spurious deferrals on a ~10-turn one-field-per-turn intake; 12 fixed it. Err high.

## Common mistakes

| Pitfall | Fix |
|---|---|
| Scoring the most *specific* field | Score the *mandatory* field; specific ≠ mandatory. |
| "The model's probably right, relabel it" | Teaching to the test. Record as a finding. |
| Labels from the taxonomy doc | Enumerate via the real runtime code path; docs over-count. |
| One message per scenario | Only works if the agent classifies without intake; else drive the dialog. |
| Customer and agent are the same instance | Fine for the customer; the agent must be the real system. |
| Personas change the facts | Personas change voice only — same facts, same label. |
| Customer cooperatively answers everything (persona is just word-choice) | Lean into BEHAVIOUR: under a multi-field ask, rude/arrogant push back and give one, clueless misunderstands, nervous rambles — never a clean checklist. A difficult persona stalling the agent is a real signal (deferred-rate), not a failure to fix. |
| Subagent drives the loop AND writes its own result file | It will fabricate/script silently (~75% junk). Use the enforced path: a script writes the transcript, `finalize` gates on a real classification, the subagent never authors results. |
| Trusting a group because it returned "12 ok" | Audit it: transcript real-turn count == recorded turns; `tool_uses` (genuine ≫ scripted); turn-variance. Self-reports lie. |
| Turn cap set low (e.g. 8) | Sizes the deferral rate to your cap, not the agent. Set above the full intake length + margin. |

## Reusable engine (lib/)

This skill ships a project-agnostic engine you copy in. Pure TypeScript, no deps, verified by its own test:

- `lib/personas.ts` — the 6 personas (drop-in; customize freely).
- `lib/engine.ts` — `aggregate(results, {fields?})` scores any set of scored fields → markdown+json (per-field accuracy, a per-expected-value breakdown, per-persona/-language/-scenario breakdowns, dialog metrics, miss list); `validateCorpus(corpus, cfg)` checks corpus invariants via injected predicates. Covered by `lib/engine.test.ts` (incl. table-rendering integrity), which the scaffolder also copies into each project's `eval/` so the engine stays guarded after local tweaks. Markdown cells escape `|`, and the per-expected-value breakdown replaces the old wide matrix so long values stay readable.
- `lib/runner.ts` — `runScenario({ entry, factSheet, agentTurn, customerReply, maxTurns })`: the dialog loop, both effects injected (Path A drives this directly).
- `cli/drive-turn.ts`, `cli/finalize.ts`, `cli/scenario-state.ts`, `cli/assemble.ts` — the enforced-driving toolkit (Path B): a transcript-writing turn-runner, the completion gate, the resume helper, and group assembly. The driver subagent uses these and never authors results itself.
- `customer-reply.ts` — optional Path-A customer backed by an LLM API (for fully-automated, subagent-free runs).

**What you write per project (the adapter seam):**

1. **Scenarios** — `{ id, expected: {<field>: <label>}, factSheet }[]`. `expected` = the mandatory scored fields (frozen ground truth); `factSheet` = what the customer knows.
2. **Label space → `validateCorpus` predicates** — enumerate valid labels via your system's *runtime code path*; wire `labelOk(field, value)` and `expectedFor(scenarioId)`.
3. **`agentTurn` adapter** — run ONE real turn of your agent over the history; return `{ agentText, classified | null, otherAction?, surfaced? }`; stop at the classification step. As a CLI, write ONLY the JSON to **stdout**, diagnostics to **stderr** (callers parse stdout directly — no `tail` hacks). Example for a LangGraph agent:

```ts
import { randomUUID } from "node:crypto";
import { HumanMessage, AIMessage } from "@langchain/core/messages";
import { graph } from "../graph.js";            // ← your agent
import type { AgentTurn } from "./runner.js";
const CLASSIFY = "classify_case";                // ← your classification action

export const agentTurn: AgentTurn = async (history) => {
  const messages = history.map((m) => m.role === "user" ? new HumanMessage(m.content) : new AIMessage(m.content));
  const ac = new AbortController();
  let agentText = ""; let steps: any[] = []; const results: any[] = [];
  const stream = graph.streamEvents({ messages }, { configurable: { thread_id: randomUUID() }, version: "v2", signal: ac.signal });
  try {
    for await (const ev of stream) {
      if (ev.event === "on_chat_model_stream") { const c = ev.data?.chunk?.content; if (typeof c === "string") agentText += c; }
      else if (ev.event === "on_tool_start") steps = parseSteps(ev.data) ?? steps;        // your envelope parsing
      else if (ev.event === "on_tool_end") { results.push(...parseResults(ev.data)); if (results.length) { ac.abort(); break; } }
    }
  } catch (e: any) { if (e?.name !== "AbortError") throw e; }
  const c = results.find((r) => r.action === CLASSIFY);
  if (c) return { agentText, classified: { category: c.categoryName }, surfaced: { product: c.productName, confidence: c.confidence } };
  if (results.length) return { agentText, classified: null, otherAction: true };  // unexpected tool
  return { agentText, classified: null };                                          // a question
};
```

**Running it (token-efficient, file in / file out):**

1. Build per-group **payload** files for your slice (scenario opening + fact sheet + persona voice — **no labels**).
2. Drive each group via the **enforced path** (see "Driving without fabrication"): one subagent per group calls `drive-turn` per turn (composing one in-persona reply each) and `finalize` per scenario — it never writes results itself. Then run `assemble` per group → raw file. Labels never enter the subagent; transcripts stay on disk. **Audit each group's real-turn count before trusting it.**
3. `aggregate(allResults)` — scoring against the label-holding corpus — then write `report.md` + `report.json` + `transcripts.jsonl` to a timestamped folder.

**Sizing & edge cases:** cover each label with ≥1 scenario (the signal comes from clear-home cases); classifying on the opening alone is fine — low turns-to-classify is a *metric*, `deferred` means it never classified within the cap; scoring is per-field exact match (hierarchical/partial credit is out of scope — score one level).

## Cost & limits

A genuine full group (~12 multi-turn dialogs) runs ~80k customer-model tokens and ~10–15 min; estimate total ≈ groups × that. Keep two token pools separate: the **customer** model (Path A = your API bill; Path B = your coding-agent/session usage) and the **agent-under-test** (its own provider/quota). Because Path B is resumable (transcripts on disk), a session-limit cutoff is not lost work — resume and continue. For large grids, run in waves of ~6 groups and **reconcile completion against disk (the transcripts), not against subagent self-reports** (which lag, duplicate, and lie).

## (Optional) Language fidelity as a scored axis

The persona/lang grid also exposes whether the agent *answers in the user's language*. If that matters for your chatbot, add a `replyLang` scored field: the customer always writes in `entry.lang`, and your `agentTurn` reports the language the agent actually replied in (cheap heuristic or a tiny classifier) → score it like any other field. (A real run here caught an agent answering English users in Greek.)

## Worked example

`cmt-agent` (Greek bank case/complaints agent): `src/tools/cases/eval/` — `personas.ts` (6 personas), `base-stories.ts` (labeled scenarios + fact sheets), `corpus.json` (committed openings), `graph-turn.ts` (one real agent turn, stops at the classify step), `report.ts` (pure aggregation), `validate.ts` (corpus invariants), and `README.md` (the runbook). Findings from real runs: the agent routed credit-card complaints to a generic services category instead of the dedicated one (left as a miss, not relabeled); and the same case flipped `request`↔`complaint` by persona/lang.

**The enforced-driving toolkit above was extracted from this project** after a naive subagent run (subagent owns the loop *and* writes results) produced ~75% fabricated/scripted dialogs that looked plausible. The fix — script-owned transcripts + a `finalize` gate + per-turn audit — is now the default Path B.
