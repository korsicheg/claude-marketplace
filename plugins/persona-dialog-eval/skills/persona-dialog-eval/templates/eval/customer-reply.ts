// OPTIONAL — Path A (fully-automated) customer.
//
// Wire this to an LLM API to play the customer entirely in code, then drive
// scenarios with runScenario() — NO subagents. This is the strongest
// anti-fabrication setup: the loop lives in code, so the model is only ever
// asked for ONE reply per call and can never skip turns or invent the agent's
// side. Use it WHEN you can call a customer model programmatically (i.e. you
// have an API key). If you can't (e.g. the customer must be your in-session
// coding agent), use the enforced subagent path instead — see SKILL.md.
//
// Two rules:
//   1. Keep the customer a DIFFERENT model/family from the agent under test, for
//      genuine cross-model diversity (that's the point of the eval).
//   2. NEVER put entry.expected (the ground-truth label) into the prompt — this
//      template deliberately ignores it.
//
// Example uses the Anthropic SDK; swap for any provider.  npm i @anthropic-ai/sdk
import Anthropic from "@anthropic-ai/sdk";
import type { CustomerReply } from "./runner.js";
import { PERSONAS } from "./personas.js";

const client = new Anthropic(); // reads ANTHROPIC_API_KEY

export const customerReply: CustomerReply = async ({ entry, factSheet, history, agentText }) => {
  const persona = PERSONAS.find((p) => p.id === entry.persona);
  const system = [
    `You are role-playing a customer contacting a support chatbot.`,
    `Persona: ${persona?.label ?? entry.persona} — ${persona?.guidance ?? ""}.`,
    `Reply ONLY in this language code: ${entry.lang}.`,
    `The ONLY facts you know are this fact sheet: ${JSON.stringify(factSheet)}.`,
    `Reply to the agent's latest message FULLY in character. Reveal only what this`,
    `persona would, the way they would — do not be more cooperative, organised, or`,
    `complete than they would be. Never mention any internal label or category.`,
  ].join("\n");
  // From the customer's POV the agent's lines are the "user" turns it answers.
  const messages = history.map((m) => ({
    role: (m.role === "assistant" ? "user" : "assistant") as "user" | "assistant",
    content: m.content,
  }));
  const res = await client.messages.create({
    model: "claude-haiku-4-5-20251001", // a cheaper model is fine for the customer
    max_tokens: 400,
    system,
    messages: messages.length ? messages : [{ role: "user", content: agentText }],
  });
  const part = res.content.find((c) => c.type === "text");
  return part && "text" in part ? part.text : "";
};
