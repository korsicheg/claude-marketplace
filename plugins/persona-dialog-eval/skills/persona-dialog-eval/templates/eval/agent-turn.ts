// The adapter seam — wire this to YOUR agent. Implement AgentTurn: run ONE real
// turn of the agent over the conversation history, STOP at the classification
// step (don't execute past it -> no side effects), and map the emitted
// classification to `classified` (the scored fields) + optional unscored
// `surfaced` context. Return classified=null when the agent asked a question;
// set otherAction=true if some non-classification action fired.
//
// Pick ONE variant and delete the other.

import type { AgentTurn } from "./runner.js";

// ── Variant A — in-process (TypeScript agent, e.g. LangGraph) ─────────────────
// import { randomUUID } from "node:crypto";
// import { HumanMessage, AIMessage } from "@langchain/core/messages";
// import { graph } from "../graph.js";          // ← your agent
// const CLASSIFY = "classify_case";              // ← your classification action
//
// export const agentTurn: AgentTurn = async (history) => {
//   const messages = history.map((m) =>
//     m.role === "user" ? new HumanMessage(m.content) : new AIMessage(m.content));
//   const ac = new AbortController();
//   let agentText = ""; let steps: any[] = []; const results: any[] = [];
//   const stream = graph.streamEvents({ messages },
//     { configurable: { thread_id: randomUUID() }, version: "v2", signal: ac.signal });
//   try {
//     for await (const ev of stream) {
//       if (ev.event === "on_chat_model_stream") {
//         const c = ev.data?.chunk?.content; if (typeof c === "string") agentText += c;
//       } else if (ev.event === "on_tool_start") steps = parseSteps(ev.data) ?? steps;
//       else if (ev.event === "on_tool_end") {
//         results.push(...parseResults(ev.data));
//         if (results.length) { ac.abort(); break; }   // stop at the FIRST executed tool
//       }
//     }
//   } catch (e: any) { if (e?.name !== "AbortError") throw e; }
//   const c = results.find((r) => r.action === CLASSIFY);
//   if (c) return { agentText,
//     classified: { category: c.categoryName },                 // ← your scored fields
//     surfaced: { product: c.productName, confidence: c.confidence } };
//   if (results.length) return { agentText, classified: null, otherAction: true };
//   return { agentText, classified: null };
// };

// ── Variant B — subprocess (any language / stack) ─────────────────────────────
// Your agent exposes a command that reads {history} JSON on stdin and writes
// {agentText, classified|null, otherAction?, surfaced?} JSON on stdout.
import { spawn } from "node:child_process";

export const agentTurn: AgentTurn = (history) =>
  new Promise((resolve, reject) => {
    const proc = spawn("YOUR_AGENT_CMD", ["one-turn"], { stdio: ["pipe", "pipe", "inherit"] }); // ← edit
    let out = "";
    proc.stdout.on("data", (d) => (out += d));
    proc.on("error", reject);
    proc.on("close", () => {
      try { resolve(JSON.parse(out)); } catch (e) { reject(e); }
    });
    proc.stdin.end(JSON.stringify({ history }));
  });
