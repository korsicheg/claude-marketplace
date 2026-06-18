// Tests for the reusable engine. Run after compiling: node --test <out>/engine.test.js
// Covers multi-field aggregation + corpus validation. Pure, no deps.

import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { aggregate, validateCorpus, type ScenarioResult, type CorpusEntry, type ValidateConfig } from "./engine.js";

function entry(over: Partial<CorpusEntry>): CorpusEntry {
  return {
    id: "s1|technical|en", scenarioId: "s1", persona: "technical", lang: "en",
    opening: "hello", expected: { caseType: "complaint", category: "Cards" }, ...over,
  };
}
function sr(over: Partial<ScenarioResult>): ScenarioResult {
  return {
    entry: entry({}),
    turns: [{ role: "customer", text: "a" }, { role: "agent", text: "b" }, { role: "agent", text: "c" }],
    observed: { caseType: "complaint", category: "Cards" },
    outcome: "ok", ...over,
  };
}

describe("aggregate (multi-field)", () => {
  const results: ScenarioResult[] = [
    sr({ entry: entry({ id: "s1|technical|en" }) }), // ok, both hit
    sr({ entry: entry({ id: "s1|rude|el", persona: "rude", lang: "el" }), observed: { caseType: "complaint", category: "Other" } }), // caseType hit, category miss
    sr({ entry: entry({ id: "s2|rude|en", scenarioId: "s2", persona: "rude" }), observed: { caseType: "suggestion", category: "Other" } }), // caseType miss
    sr({ entry: entry({ id: "s3|nervous|en", scenarioId: "s3", persona: "nervous" }), observed: { caseType: null, category: null }, outcome: "deferred", turns: [{ role: "customer", text: "a" }] }),
    sr({ entry: entry({ id: "s4|clueless|el", scenarioId: "s4", persona: "clueless", lang: "el" }), observed: { caseType: null, category: null }, outcome: "error" }),
  ];
  const { json, markdown } = aggregate(results);

  test("overall counts", () => {
    assert.equal(json.total, 5);
    assert.equal(json.scored, 3);
    assert.equal(json.deferred, 1);
    assert.equal(json.errors, 1);
  });

  test("per-field accuracy over total (deferred/error = miss)", () => {
    const f = (name: string) => json.fields.find((x) => x.field === name)!;
    assert.equal(f("caseType").accuracy, 2 / 5);
    assert.equal(f("category").accuracy, 1 / 5);
  });

  test("confusion matrix for caseType", () => {
    const c = json.fields.find((x) => x.field === "caseType")!.confusion;
    assert.equal(c["complaint"]["complaint"], 2);
    assert.equal(c["complaint"]["suggestion"], 1);
    assert.equal(c["complaint"]["deferred"], 1);
    assert.equal(c["complaint"]["error"], 1);
  });

  test("misses = every scenario not fully correct", () => {
    assert.deepEqual(json.misses.map((m) => m.id).sort(), ["s1|rude|el", "s2|rude|en", "s3|nervous|en", "s4|clueless|el"]);
  });

  test("dialog metrics", () => {
    assert.equal(json.deferredRateByPersona["nervous"], 1);
    assert.equal(json.deferredRateByPersona["technical"], 0);
    assert.equal(json.avgTurnsToClassify, 2); // r1,r2,r3 each have 2 agent turns
  });

  test("markdown renders sections", () => {
    assert.match(markdown, /# Persona-Dialog Eval Report/);
    assert.match(markdown, /By persona/);
    assert.match(markdown, /expected → what the agent produced/);
    assert.match(markdown, /## Misses/);
  });

  test("markdown tables aren't broken by pipes in ids/values", () => {
    // The cell-table separator must have one column per header cell, and any
    // pipe in cell content must be escaped — else GitHub mis-renders the table.
    const persRows = markdown.split("\n").filter((l) => l.startsWith("| technical |") || l.startsWith("| rude |"));
    // header: key, n, full-hit, <2 fields>, deferred, errors = 7 cols -> 7 separator groups
    assert.match(markdown, /\| key \| n \| full-hit \| caseType \| category \| deferred \| errors \|\n\|---\|---\|---\|---\|---\|---\|---\|/);
    // misses carry scenario id (no raw pipe leakage into extra columns)
    assert.ok(persRows.length > 0);
  });
});

describe("validateCorpus", () => {
  const cfg: ValidateConfig = {
    personaIds: ["p1"], langs: ["en"], scenarioIds: ["s1"],
    expectedFor: (id) => (id === "s1" ? { team: "Billing" } : undefined),
    labelOk: (field, v) => field === "team" && ["Billing", "Tech"].includes(v),
  };
  const good: CorpusEntry = { id: "s1|p1|en", scenarioId: "s1", persona: "p1", lang: "en", opening: "hi", expected: { team: "Billing" } };

  test("a complete, correct corpus has no problems", () => {
    assert.deepEqual(validateCorpus([good], cfg), []);
  });
  test("flags label disagreeing with the scenario", () => {
    assert.ok(validateCorpus([{ ...good, expected: { team: "Tech" } }], cfg).some((m) => /team mismatch/.test(m)));
  });
  test("flags a label outside the label space", () => {
    assert.ok(validateCorpus([{ ...good, expected: { team: "Nope" } }], cfg).some((m) => /not in the label space/.test(m)));
  });
  test("flags an id that doesn't match its fields", () => {
    assert.ok(validateCorpus([{ ...good, id: "wrong" }], cfg).some((m) => /id should be/.test(m)));
  });
  test("flags missing cells", () => {
    assert.ok(validateCorpus([], cfg).some((m) => /missing cell s1\|p1\|en/.test(m)));
  });
});
