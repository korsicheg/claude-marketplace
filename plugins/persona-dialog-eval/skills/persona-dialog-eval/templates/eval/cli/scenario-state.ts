// Resume helper. Given a scenario's corpus id, reads the script-written
// transcript and prints how far the dialog got, so a (re-)dispatched driver
// continues from the last REAL turn instead of restarting. Makes runs resumable
// across session limits and makes a rejected/killed run cost only its remainder.
//
//   tsx eval/cli/scenario-state.ts <corpusId>
//
// Prints JSON: { exists, turns, complete, lastAgentText, history }
//   history  — full accumulated [{role:"user"|"assistant",content}], ready to
//              feed straight back into drive-turn.ts.
//   complete — true once a classification or other-action turn was recorded.
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const WORK = process.env.EVAL_WORK_DIR ?? fileURLToPath(new URL("../reports/_work", import.meta.url));
const safeKey = (id: string) => id.replace(/[^a-zA-Z0-9._-]/g, "_");

const corpusId = process.argv[2];
if (!corpusId) {
  console.error("usage: tsx eval/cli/scenario-state.ts <corpusId>");
  process.exit(1);
}
const tpath = join(WORK, "transcripts", `${safeKey(corpusId)}.jsonl`);
if (!existsSync(tpath)) {
  console.log(JSON.stringify({ exists: false, turns: 0, complete: false, lastAgentText: "", history: [] }));
  process.exit(0);
}
const lines = readFileSync(tpath, "utf8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
const history: { role: "user" | "assistant"; content: string }[] = [];
for (const ln of lines) {
  if (ln.customer != null) history.push({ role: "user", content: ln.customer });
  if (ln.agentText) history.push({ role: "assistant", content: ln.agentText });
}
const complete = lines.some((ln) => ln.classified || ln.otherAction);
const lastAgentText = lines.length ? lines[lines.length - 1].agentText : "";
console.log(JSON.stringify({ exists: true, turns: lines.length, complete, lastAgentText, history }));
