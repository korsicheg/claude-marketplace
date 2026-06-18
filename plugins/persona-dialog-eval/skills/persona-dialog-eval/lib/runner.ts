// Reusable dialog-loop skeleton. PURE — you inject the two effects:
//   • agentTurn   — runs ONE real turn of YOUR agent (the system under test)
//   • customerReply — produces the customer's next line (played by an LLM)
//
// Two ways to drive it:
//   1. Claude-Code-in-session: a subagent IS `customerReply` — it reads the
//      agent's question and writes the reply inline. Use this skeleton as the
//      contract; the subagent follows the same loop by hand (file in, file out).
//   2. Fully automated: wire `customerReply` to an LLM API (e.g. Anthropic) and
//      call runScenario() directly.

import type { CorpusEntry, ScenarioResult, TurnRecord } from "./engine.js";

export type HistMsg = { role: "user" | "assistant"; content: string };

export interface AgentTurnResult {
  agentText: string;
  /** The scored fields the agent emitted THIS turn, or null if it didn't classify. */
  classified: Record<string, string> | null;
  /** True if some executed action other than the classification fired → "error". */
  otherAction?: boolean;
  /** Optional unscored context to surface in the report (confidence, optional fields…). */
  surfaced?: Record<string, unknown>;
}

/** Run one real turn of the agent under test over the full history.
 *  MUST stop at the classification step (don't execute past it → no side effects).
 *  If implemented as a CLI: write ONLY this result as JSON to stdout; send all
 *  diagnostics to stderr so callers can parse stdout directly. */
export type AgentTurn = (history: HistMsg[]) => Promise<AgentTurnResult>;

export type CustomerReply = (ctx: {
  entry: CorpusEntry;
  factSheet: Record<string, unknown>;
  history: HistMsg[];
  agentText: string;
}) => Promise<string>;

export async function runScenario(opts: {
  entry: CorpusEntry;
  factSheet: Record<string, unknown>;
  agentTurn: AgentTurn;
  customerReply: CustomerReply;
  maxTurns?: number;
}): Promise<ScenarioResult> {
  const { entry, factSheet, agentTurn, customerReply } = opts;
  // Default cap sized for a multi-field intake. Set it ABOVE the turns a
  // cooperative user needs to reach a decision (+ margin) or "deferred" measures
  // your cap, not the agent. See config.maxTurns.
  const maxTurns = opts.maxTurns ?? 12;

  const history: HistMsg[] = [{ role: "user", content: entry.opening }];
  const turns: TurnRecord[] = [{ role: "customer", text: entry.opening }];
  let classified: Record<string, string> | null = null;
  let surfaced: Record<string, unknown> | undefined;
  let outcome: ScenarioResult["outcome"] = "deferred";

  for (let i = 0; i < maxTurns; i++) {
    let res: AgentTurnResult;
    try {
      res = await agentTurn(history);
    } catch {
      outcome = "error";
      break;
    }
    history.push({ role: "assistant", content: res.agentText });
    turns.push({ role: "agent", text: res.agentText });

    if (res.classified) {
      classified = res.classified;
      surfaced = res.surfaced;
      outcome = "ok";
      break;
    }
    if (res.otherAction) {
      outcome = "error";
      break;
    }

    const reply = await customerReply({ entry, factSheet, history, agentText: res.agentText });
    history.push({ role: "user", content: reply });
    turns.push({ role: "customer", text: reply });
  }

  // Normalize: every expected field present in observed (null when unclassified).
  const observed: Record<string, string | null> = {};
  for (const f of Object.keys(entry.expected)) observed[f] = classified?.[f] ?? null;

  return { entry, turns, observed, surfaced, outcome };
}
