// The agent's REAL label space, per scored field.
//
// CRITICAL: enumerate these via your system's RUNTIME code path (the same enum /
// config / taxonomy loader the agent itself uses), NOT a docs page or a CSV. A
// label the agent can never emit makes every scenario using it a false miss.
//
// The scaffolder replaces the body of `allowedLabels` with the real enumeration.

export const allowedLabels: Record<string, Set<string>> = {
  // category: new Set([
  //   ...loadCategoriesFromYourSystem(),   // e.g. import the agent's category list
  // ]),
};

/** Used by validateCorpus to reject any ground-truth label outside the space. */
export function labelOk(field: string, value: string): boolean {
  const set = allowedLabels[field];
  return set ? set.has(value) : true; // field not enumerated -> not checked
}
