// Base scenarios — authored from the business case by the scaffolder.
//
// Each scenario FIXES the ground-truth label(s) and a fact sheet (everything the
// simulated customer knows, so they can answer the agent's intake questions).
// Personas and languages never change `expected` — that gap is what you measure.
//
// Rules the scaffolder follows:
//   • `expected` keys == EVAL_CONFIG.scoredFields; values are REAL labels the
//     agent can emit (validated by labels.ts / `npm run eval:validate`).
//   • Cover each label with >= 1 scenario; the signal comes from clear-home cases.
//   • `factSheet` holds identity + the facts the customer reveals when asked
//     (include optional/unscored fields here too, just don't score them).
//   • `problem` is a neutral description of what happened — it seeds the openings.

export interface Scenario {
  id: string;
  expected: Record<string, string>;
  factSheet: Record<string, unknown>;
  problem: string;
}

export const SCENARIOS: Scenario[] = [
  // EXAMPLE (replace with your business case):
  // {
  //   id: "double-charge",
  //   expected: { category: "Billing" },
  //   factSheet: { firstName: "Alex", accountId: "...", amount: "12.99", month: "May" },
  //   problem: "The monthly subscription fee was charged twice in the same month.",
  // },
];
