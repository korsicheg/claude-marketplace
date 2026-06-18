// One real agent turn: reads {history} JSON on stdin, writes the result JSON on
// stdout. Diagnostics MUST go to stderr (callers parse stdout directly).
// Usage: echo '{"history":[...]}' | tsx eval/cli/run-turn.ts
import { agentTurn } from "../agent-turn.js";

let raw = "";
process.stdin.setEncoding("utf8");
for await (const chunk of process.stdin) raw += chunk;

let history: { role: "user" | "assistant"; content: string }[];
try {
  history = JSON.parse(raw).history ?? [];
} catch (e) {
  console.error("run-turn: invalid JSON on stdin: " + (e as Error).message);
  process.exit(1);
}

const res = await agentTurn(history);
process.stdout.write(JSON.stringify(res));
