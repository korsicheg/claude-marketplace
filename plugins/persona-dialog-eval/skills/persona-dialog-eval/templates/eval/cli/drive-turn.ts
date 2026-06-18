// Enforced turn-runner (file in / file out) — the ANTI-FABRICATION spine.
//
// Runs ONE real agent turn over a history file AND appends that turn to a
// script-written, per-scenario transcript. The driving subagent NEVER writes
// results itself; `finalize.ts` assembles them from this transcript. So a lazy
// driver that skips real turns produces an empty/short transcript that the gate
// rejects — fabricated dialogue has nowhere to land.
//
// File-in/file-out (not stdin) on purpose: it is shell-agnostic (PowerShell
// cannot reliably redirect stdin), and the transcript is the only trusted record.
//
//   tsx eval/cli/drive-turn.ts <corpusId> <histIn.json> <histOut.json>
//
// <corpusId>      the scenario's corpus id, e.g. "atm-outage|rude|en" (verbatim).
// <histIn.json>   {"history":[{role,content},...]} — pass the FULL history each call.
// <histOut.json>  the AgentTurnResult {agentText, classified, otherAction?, surfaced?}.
// Transcript appended to <WORK>/transcripts/<safeKey>.jsonl (safeKey = id sanitized).
import { readFileSync, writeFileSync, appendFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { agentTurn } from "../agent-turn.js";

// Resolve the work dir relative to THIS file (matches aggregate.ts/build-slice.ts),
// so all CLIs agree regardless of cwd or a dist/ build. Override with EVAL_WORK_DIR.
const WORK = process.env.EVAL_WORK_DIR ?? fileURLToPath(new URL("../reports/_work", import.meta.url));
const safeKey = (id: string) => id.replace(/[^a-zA-Z0-9._-]/g, "_");

const [corpusId, inPath, outPath] = process.argv.slice(2);
if (!corpusId || !inPath || !outPath) {
  console.error("usage: tsx eval/cli/drive-turn.ts <corpusId> <histIn.json> <histOut.json>");
  process.exit(1);
}

let history: { role: "user" | "assistant"; content: string }[];
try {
  const parsed = JSON.parse(readFileSync(inPath, "utf8"));
  history = Array.isArray(parsed) ? parsed : (parsed.history ?? []);
} catch (e) {
  console.error(`drive-turn: invalid JSON in ${inPath}: ${(e as Error).message}`);
  process.exit(1);
}

const res = await agentTurn(history);
writeFileSync(outPath, JSON.stringify(res));

// Append the REAL turn to the script-owned transcript. This is the only record
// finalize trusts; the driver cannot write here except by running a real turn.
try {
  const tdir = join(WORK, "transcripts");
  mkdirSync(tdir, { recursive: true });
  const lastUser = [...history].reverse().find((m) => m.role === "user");
  appendFileSync(
    join(tdir, `${safeKey(corpusId)}.jsonl`),
    JSON.stringify({ customer: lastUser ? lastUser.content : null, ...res }) + "\n",
  );
} catch (e) {
  console.error(`drive-turn: transcript append failed: ${(e as Error).message}`);
}

const tag = res.classified ? "CLASSIFIED" : res.otherAction ? "OTHER-ACTION" : "question";
console.error(`drive-turn ${corpusId}: ${tag}`);
