# Chapter 11: Comments

## Core Idea
**"The use of a comment is an indication of failure to express without them. Code should be the
only source of truth."** Comments are *"an apology, not a requirement"* — so the default is to
delete the comment by improving the code, and the only endorsed survivor is a **`// TODO`**.

> *"Don't comment bad code—rewrite it."* — **Brian W. Kernighan and P. J. Plaugher**

## Frameworks Introduced

- **The apology test.** Before writing a comment, ask what the code failed to say — then fix
  *that*. *"Good code mostly documents itself."*
  - How: extract the commented expression into a **named boolean** or a named function. The
    comment's content becomes the name.
  - This is the chapter's one constructive technique; everything else is a prohibition.

- **Delete commented-out code.** *"Version control exists for a reason. Leave old code in your
  history."*
  - Applies to commented-out *type members* too — the source's example is two commented fields
    inside a `type User`, which is exactly where it hides best.

- **No journal comments.** *"Remember, use version control! There's no need for dead code,
  commented code, and especially journal comments. Use `git log` to get history!"*
  - The tell: a dated changelog block above a function (`2016-12-20: Removed monads…`).

- **Avoid positional markers.** They *"usually just add noise."*
  - The stated replacement: *"Let the functions and variable names along with the proper
    indentation and formatting give the visual structure to your code."*
  - And the tooling answer: **most IDEs support code folding** — VS Code's *folding regions* is
    the cited example — so the banner buys nothing an editor doesn't already give you.

- **`// TODO` comments — the one endorsed comment.** When you need to leave a note for a later
  improvement, *"do that using `// TODO` comments. Most IDEs have special support for those kinds
  of comments so that you can quickly go over the entire list of todos."*
  - The stated limit: ***"a TODO comment is not an excuse for bad code."***
  - How: the marker is what makes it findable. A bare `// ensure dueDate is indexed.` is
    invisible to tooling; `// TODO: ensure dueDate is indexed.` appears in the IDE's TODO list
    and in a `grep`.

## Key Concepts
- **Comment as apology** — the chapter's framing: a comment admits the code didn't express
  itself.
- **Self-documenting code** — code whose names carry the intent a comment would have.
- **Commented-out code** — disabled code left in the file; superseded by version control.
- **Journal comment** — a dated change log in the source; superseded by `git log`.
- **Positional marker / banner comment** — `////////` separators labelling sections
  (`// public methods`); noise, replaced by names, indentation, and IDE folding.
- **`// TODO`** — a machine-findable note about future work; the one comment form the chapter
  endorses.
- **Folding region** — an editor feature that collapses code blocks, making section banners
  redundant.

## Mental Models
- **Read every comment as a question: "what should this code have been called?"** In the
  worked example the comment literally contains the answer (`// Check if subscription is
  active.` → `isSubscriptionActive`). That is usually true.
- **Treat "code should be the only source of truth" literally.** A comment can drift out of
  sync with the code and nothing will fail. Two sources of truth means one of them is lying and
  you don't know which.
- **`git log` and `git blame` are the comment you don't write.** Journal comments and
  commented-out code are both attempts to do version control inside the source file.
- **A section banner is a class waiting to be split.** If a file needs `// private methods`
  signposting to be navigable, the problem is size (ch05), not signage.
- **`// TODO` is a marker, not a licence.** The prefix makes the note findable; it does not make
  the shortcut acceptable.
- **Read the author's hedge as deliberate.** *"Good code **mostly** documents itself"* — the
  emphasis on **mostly** is the source's own, and "comments are an **apology**, not a
  requirement" is not "comments are forbidden." Every prohibition here names a *specific* bad
  kind: what-restatements, commented-out code, journal comments, banners. `// TODO` is
  positively endorsed. Nothing here says a comment is never warranted.
- **What this chapter doesn't do is enumerate the good kinds.** Its only named endorsement is
  `// TODO`, so it gives you no vocabulary for a **why**-comment. `clean-code-java` ch04 names
  them — intent, warning of consequences, amplification, legal headers, public-API docs — and
  is the better reference when you're deciding whether a *why*-comment should survive.

## Code Examples

The apology test — the comment becomes the name:

```ts
// Bad — the comment says what the condition means, because the code doesn't.
// Check if subscription is active.
if (subscription.endDate > Date.now) {  }

// Good — the name says it; the comment is now redundant and deleted.
const isSubscriptionActive = subscription.endDate > Date.now;
if (isSubscriptionActive) { /* ... */ }
```
- **What it demonstrates**: the extracted boolean is the same lever as ch03's "encapsulate
  conditionals" and ch02's "explanatory variables" — one technique, three chapters.
- *(Reproduced as written in the source, including `Date.now` without call parentheses. In real
  code that compares a `Date` to a function object; you want `Date.now()`.)*

Commented-out code, including the easy-to-miss type-member case:

```ts
// Bad
type User = {
  name: string;
  email: string;
  // age: number;
  // jobPosition: string;
}

// Good
type User = {
  name: string;
  email: string;
}
```

Journal comments:

```ts
// Bad
/**
 * 2016-12-20: Removed monads, didn't understand them (RM)
 * 2016-10-01: Improved using special monads (JP)
 * 2016-02-03: Added type-checking (LI)
 * 2015-03-14: Implemented combine (JR)
 */
function combine(a: number, b: number): number {
  return a + b;
}

// Good
function combine(a: number, b: number): number {
  return a + b;
}
```

Positional markers:

```ts
// Bad — banners doing what indentation and names already do.
////////////////////////////////////////////////////////////////////////////////
// Client class
////////////////////////////////////////////////////////////////////////////////
class Client {
  id: number;
  name: string;

  ////////////////////////////////////////////////////////////////////////////////
  // public methods
  ////////////////////////////////////////////////////////////////////////////////
  public describe(): string { /* ... */ }

  ////////////////////////////////////////////////////////////////////////////////
  // private methods
  ////////////////////////////////////////////////////////////////////////////////
  private describeAddress(): string { /* ... */ }
}

// Good
class Client {
  id: number;
  name: string;
  address: Address;
  contact: Contact;

  public describe(): string { /* ... */ }
  private describeAddress(): string { /* ... */ }
  private describeContact(): string { /* ... */ }
}
```

`// TODO` — the marker is the whole point:

```ts
// Bad — a real note, but invisible to tooling.
function getActiveSubscriptions(): Promise<Subscription[]> {
  // ensure `dueDate` is indexed.
  return db.subscriptions.find({ dueDate: { $lte: new Date() } });
}

// Good
function getActiveSubscriptions(): Promise<Subscription[]> {
  // TODO: ensure `dueDate` is indexed.
  return db.subscriptions.find({ dueDate: { $lte: new Date() } });
}
```

## Reference Tables

| Comment you're about to write | Instead |
|---|---|
| Explains what a condition means | extract a named boolean |
| Explains what a block does | extract a named function |
| Disabled code kept "just in case" | delete it — git has it |
| Dated change log | delete it — `git log` has it |
| `////// public methods //////` | delete it — names, indentation, IDE folding |
| Note about future work | **`// TODO: <the note>`** ✓ the one endorsed form |
| Explains **why** a non-obvious decision was made | keep it — but this chapter names no such category, so see `clean-code-java` ch04 for the vocabulary (intent / warning of consequences / amplification / legal) |

## Worked Example
**The apology test applied to a real comment, step by step** — because "delete the comment by
improving the code" is easy to state and easy to skip.

Start with code that needs a comment:

```ts
// Check if subscription is active.
if (subscription.endDate > Date.now()) {
  grantAccess(user);
}
```

**Step 1 — read the comment as a naming suggestion.** It says "subscription is active". That is
a predicate, and it now has a name.

**Step 2 — give the expression that name.**

```ts
const isSubscriptionActive = subscription.endDate > Date.now();

if (isSubscriptionActive) {
  grantAccess(user);
}
```

**Step 3 — delete the comment.** It now restates the identifier on the line above it. Keeping it
would create the two-sources-of-truth problem: change the condition to include a grace period
and the comment silently becomes wrong.

**Step 4 — check whether the name wants to be a function.** If the same predicate appears
anywhere else, or if it grows a second clause, promote it (this is ch03's "encapsulate
conditionals"):

```ts
function isSubscriptionActive(subscription: Subscription): boolean {
  return subscription.endDate > Date.now();
}

if (isSubscriptionActive(subscription)) {
  grantAccess(user);
}
```

**Why it works**: the intent moved from a comment (unverified, driftable, invisible to the
compiler) into an identifier (checked, refactorable, greppable, and shown by the IDE at every
call site). The comment's information wasn't lost — it was **promoted**.

**Where the test comes back with something to keep.** The test tells you to try to delete the
comment by improving the code — it does not promise you always can. Consider:

```ts
// Stripe rounds half-up; our ledger rounds half-even. Converting here
// keeps the two reconcilable at month end. See FIN-4412.
const cents = roundHalfUp(amount * 100);
```

No name captures that. It's a *why* — an external constraint and its rationale — and renaming
`cents` cannot express it. This is what the italicized **mostly** in *"good code mostly documents
itself"* is making room for. The chapter simply doesn't give you a *name* for this kind;
**`clean-code-java` ch04 does** (intent, warning of consequences, amplification, legal). The
rule: run the apology test first, and if the surviving content is a *why* rather than a *what*,
keep the comment.

## Key Takeaways
1. **A comment is an apology for code that didn't express itself.** Code is the only source of
   truth.
2. **Delete the comment by improving the code** — the comment usually contains the name you need.
3. **Never leave commented-out code.** Version control remembers; check `type` members too.
4. **No journal comments.** `git log` is the changelog.
5. **No positional markers / banner comments** — names, indentation and IDE folding regions do
   that job. A file that needs signposting is too big (ch05).
6. **`// TODO` is the one endorsed comment form** — the prefix makes it findable by IDEs and
   grep. It is **not an excuse for bad code**.
7. The chapter targets *what*-comments; the *mostly* in "good code mostly documents itself" is
   the author's own room for the rest. It just never names those kinds — for that vocabulary
   (intent, warning of consequences, amplification, legal), go to `clean-code-java` ch04.

## Connects To
- **Ch 2 (Variables)**: "explanatory variables" is the same technique — naming a value instead of
  annotating it.
- **Ch 3 (Functions)**: "encapsulate conditionals" is step 4 of the worked example; a section
  banner marks a function waiting to be extracted.
- **Ch 5 (Classes)**: needing positional markers to navigate a class means the class is too big.
- **Ch 7 (Testing)**: "the name of the test should reveal its intention" is this rule applied to
  tests — a well-named test needs no comment.
- **Ch 9 (Error Handling)**: `Failable<R, E>` documents the failure mode in the type, which is a
  comment you don't write.
- **`clean-code-java` ch04 (Comments)**: the essential complement. *"Comments are always
  failures"* — but it also enumerates the **good** comments this chapter omits: legal headers,
  **intent**, **warning of consequences**, **amplification**, TODOs with a stated plan, and
  public-API docs. It also adds prohibitions this chapter lacks: closing-brace comments,
  mandated per-function docs, bylines, and *"commented-out code is an abomination."*
