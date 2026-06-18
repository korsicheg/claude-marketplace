# Persona-Dialog Eval

Measures whether this agent classifies/routes correctly across user personalities
and languages. The **customer** is played by an LLM (your in-session coding agent,
or an API model); the **agent under test is the real system**. Scaffolded by the
`persona-dialog-eval` skill.

> Run all CLIs **from the project root** (`tsx eval/cli/<x>.ts`). The work dir is
> resolved relative to the CLI files, so root vs. subdir doesn't matter — but the
> npm scripts assume root.

## Layout

- `engine.ts` / `runner.ts` / `personas.ts` — the reusable engine (don't edit casually).
- `config.ts` — scored fields, personas, langs, **turn cap** (size it above your intake).
- `scenarios.ts` — base scenarios: fixed ground-truth labels + fact sheets.
- `labels.ts` — the agent's real label space (used for validation).
- `agent-turn.ts` — the adapter to this agent (one real turn).
- `customer-reply.ts` — optional Path-A customer (API-backed); delete if unused.
- `corpus.json` — generated openings (scenario × persona × lang) + labels.
- `cli/` — `build-corpus`, `validate`, `build-slice`, `aggregate` (corpus + scoring);
  `drive-turn`, `finalize`, `scenario-state`, `assemble` (enforced driving); `run-turn` (ad-hoc).

## Commands

```bash
npm run eval:build-corpus    # openings parts -> corpus.json (labels from scenarios)
npm run eval:validate        # corpus invariants (complete grid, real labels)
npm run eval:build-slice -- --persona rude,clueless --lang el   # -> reports/_work/payloads/group-NN.json (NO labels)
npm run eval:aggregate       # reports/_work/raw/group-NN.json -> reports/<timestamp>/report.{md,json} + transcripts.jsonl
```

## Why driving is enforced (read this)

If a subagent both role-plays the customer **and** writes its own result file, under
normal laziness it will **fabricate** the dialog (no real agent calls) or **script** it
(real calls, canned non-persona replies). The fake data looks plausible. So results are
**assembled by scripts from a transcript that only real agent turns can write** — the
driver never authors results. Two ways to drive:

### Path A — fully automated (if you can call a customer model via API)
Fill in `customer-reply.ts`, then drive `runScenario()` over the **full corpus** in a
small script (the loop is code → fabrication impossible; keep the customer a different
model family from the agent; never pass `expected` into the prompt). No subagents.

### Path B — enforced in-session subagents (no API key) — default
1. `eval:build-slice` for your filter → `reports/_work/payloads/group-NN.json` (opening + fact sheet + persona voice, **no labels**).
2. Dispatch one subagent per group. For each scenario it drives the loop **but never writes results**:
   - resume check: `tsx eval/cli/scenario-state.ts <id>` — if `complete`, skip; else continue from its `history`.
   - per turn: write the full history to a temp file, run
     `tsx eval/cli/drive-turn.ts <id> <histIn.json> <histOut.json>` (real agent turn → appends to the transcript), read `histOut`.
   - after a turn where a tool ran: `tsx eval/cli/finalize.ts <id>` — exit 0 = scenario done; "INCOMPLETE" (exit 3) = keep driving.
   - otherwise compose the customer's next line **fully in persona + language from the fact sheet** — reveal only what this persona would, the way they would (rude/arrogant push back and give one, clueless misunderstands, nervous rambles; never a clean checklist); never name a label; append, repeat.
   - cap at `config.maxTurns` → `finalize <id> <cap>` records `deferred`.
3. `tsx eval/cli/assemble.ts reports/_work/payloads/group-NN.json` → `reports/_work/raw/group-NN.json`.
4. **Audit each group before trusting it:** transcript real-turn count == recorded turns; subagent `tool_uses` (genuine ≈ 3–4/turn, not ~5–11 total); turn-count variance (not all identical); skim a difficult-persona reply. Reject + re-dispatch (it resumes) anything that fails.
5. `eval:aggregate` joins raw results to the labeled corpus and writes the report.

## Rules (don't break these)

- **The driver never authors results** — only real turns, captured by `drive-turn`, count. Don't hand-write `raw/*.json`.
- **Never trust a `12 ok` self-report** — verify against the transcripts on disk.
- Score the **mandatory** field(s) in `config.scoredFields`; surface optional fields, don't score them.
- Labels in `scenarios.ts` must be real (from the agent's code path) — `eval:validate` enforces it.
- If the agent resolves differently than your label, that's a **miss / finding** — don't relabel to match.
- Personas change voice only; never the facts or the label.
- Size `config.maxTurns` **above** the agent's full intake length, or `deferred` measures your cap.
