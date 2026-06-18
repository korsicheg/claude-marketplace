// Reusable personas for a persona-dialog eval. Drop-in: copy into your project
// (or import). A persona is ONLY a voice instruction — it changes how the
// customer talks, never the facts or the ground-truth label. Add/trim to taste;
// the eval engine treats `id` as an opaque grouping key.

export interface Persona {
  id: string;
  label: string;
  guidance: string;
}

export const PERSONAS: Persona[] = [
  {
    id: "technical",
    label: "Technical",
    guidance:
      "Precise and competent. Uses correct terms, exact figures/dates/references. Answers directly — a clean, complete answer is in character here.",
  },
  {
    id: "non_technical",
    label: "Non-technical",
    guidance:
      "An ordinary user with no jargon. Plain, slightly vague wording; cooperative; answers what's asked, sometimes imprecisely.",
  },
  {
    id: "arrogant",
    label: "Arrogant",
    guidance:
      "Condescending and impatient. Implies the organisation is incompetent and questions why so much is needed; answers grudgingly and with sarcasm, pushing back on 'pointless' questions before giving in. Does NOT calmly provide a tidy list of fields.",
  },
  {
    id: "rude",
    label: "Rude",
    guidance:
      "Hostile and curt; one-line replies. Answers the MINIMUM and never volunteers extra. Asked for several things at once, gives only one or two and snaps at being asked for the rest. Complains; demands speed. Never dumps all the requested fields in one neat message.",
  },
  {
    id: "nervous",
    label: "Nervous",
    guidance:
      "Anxious and rambling. Over-explains, apologises, goes off on tangents; answers some questions while forgetting or muddling others; asks whether it'll be OK. Replies are messy and incomplete, not a clean checklist.",
  },
  {
    id: "clueless",
    label: "Clueless",
    guidance:
      "Knows almost nothing about the domain. Misunderstands the agent's questions and terms, asks it to explain, gives uncertain or partial answers ('I think it's…?'), describes symptoms not causes; does NOT reliably produce clean field values on request.",
  },
];
