// Project eval config. The scaffolder fills these from your business case.
import { PERSONAS } from "./personas.js";

export const EVAL_CONFIG = {
  /** The MANDATORY label field(s) the agent must get right — what gets scored.
   *  Must match the keys in each scenario's `expected`. Keep this to the
   *  field(s) the system actually requires; surface optional fields unscored. */
  scoredFields: ["category"] as string[],

  /** Persona ids to run (default: all from personas.ts). */
  personaIds: PERSONAS.map((p) => p.id),

  /** Languages to test. */
  langs: ["en"] as string[],

  /** Cap on agent turns per scenario before marking it "deferred".
   *  SIZE THIS TO YOUR AGENT'S INTAKE: it must exceed the number of turns a
   *  cooperative user needs to reach a decision, plus margin for difficult
   *  personas who stall. Too low and "deferred" measures your cap, not the agent
   *  (an 8-cap manufactured ~36% spurious deferrals on an agent whose one-field-
   *  per-turn intake needs ~10 turns; 12 fixed it). When unsure, err high. */
  maxTurns: 12,

  /** Subagents per slice = ceil(scenarios / groupSize). */
  groupSize: 6,
};
