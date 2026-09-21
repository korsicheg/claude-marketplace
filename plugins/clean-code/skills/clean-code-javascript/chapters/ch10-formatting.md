# Chapter 10: Formatting

## Core Idea
"Formatting is subjective… The main point is **DO NOT ARGUE over formatting**." Automate it with a tool, and spend human judgment only on the things tools can't decide: **consistent capitalization** and **vertical proximity of caller and callee**.

## Frameworks Introduced
- **Don't argue about formatting — automate it**: "There are tons of tools to automate this. Use one! It's a waste of time and money for engineers to argue over formatting."
  - When to use: as the first move on any new project, and as the answer to any formatting debate.
  - How: adopt an automatic formatter/linter (the guide links StandardJS's rule set) and let it settle indentation, tabs vs spaces, and quote style. The remaining rules cover only "things that don't fall under the purview of automatic formatting".
- **Use consistent capitalization**: "JavaScript is untyped, so capitalization tells you a lot about your variables, functions, etc."
  - When to use: every identifier.
  - How: the specific scheme is your team's to pick — "These rules are subjective, so your team can choose whatever they want. The point is, no matter what you all choose, **just be consistent**." The guide's own example settles on `SCREAMING_SNAKE_CASE` for constant data, `camelCase` for functions, `PascalCase` for classes.
- **Function callers and callees should be close** — the *newspaper* rule.
  - When to use: ordering methods within a class or functions within a module.
  - How: "If a function calls another, keep those functions vertically close in the source file. Ideally, keep the caller right above the callee."
  - Why it works: "We tend to read code from top-to-bottom, like a newspaper. Because of this, make your code read that way." The reader descends from summary to detail instead of scrolling to find each callee.

## Key Concepts
- **Automatic formatting** — indentation, tabs vs spaces, quote style: a tool's job, never a review comment.
- **The newspaper metaphor** — a source file should read top-to-bottom, headline first, details below.
- **Vertical proximity** — the distance in lines between a caller and what it calls; keep it near zero.
- **Capitalization as type signal** — in an untyped language, case is one of the few cues distinguishing a constant from a variable from a class.
- **Team consistency over correctness** — for subjective choices, agreement beats being right.
- **Stepdown order** — the resulting layout: each function appears just above the ones it calls, descending in abstraction.

## Mental Models
- **Think of formatting debates as billable hours burned.** "A waste of time and money" is the guide's actual framing — the cost is real and the payoff is zero.
- **Read your file like a newspaper.** Headline (`perfReview`), then sections (`getPeerReviews`), then details (`lookupPeers`). If the reader must scroll up to find the detail, the order is wrong.
- **Think of capitalization as the type annotation you don't have.** `DAYS_IN_WEEK` vs `daysInMonth` vs `Animal` each tell the reader something no declaration does.
- **Use "consistent" as the criterion, not "correct".** The guide refuses to pick a scheme for you and insists you pick one.

## Anti-patterns
- **Arguing over tabs vs spaces, quote style, or indentation**: the chapter's one emphatic prohibition, in capitals.
- **Mixed constant casing**: `const DAYS_IN_WEEK = 7;` next to `const daysInMonth = 30;` — two conventions for the same kind of value, in adjacent lines.
- **Mixed function casing**: `eraseDatabase()` beside `restore_database()`.
- **Mixed class casing**: `class animal {}` beside `class Alpaca {}` — the lowercase one reads as a variable.
- **Scattered helper methods**: `perfReview()` at the bottom of the class with `lookupPeers` and `lookupManager` above it in arbitrary order, forcing the reader to jump around to reconstruct the call graph.
- **Manual formatting discipline**: relying on humans to keep style consistent instead of a tool that can't forget.

## Code Examples
Consistent capitalization:

```javascript
// Bad
const DAYS_IN_WEEK = 7;
const daysInMonth = 30;

const songs = ["Back In Black", "Stairway to Heaven", "Hey Jude"];
const Artists = ["ACDC", "Led Zeppelin", "The Beatles"];

function eraseDatabase() {}
function restore_database() {}

class animal {}
class Alpaca {}

// Good
const DAYS_IN_WEEK = 7;
const DAYS_IN_MONTH = 30;

const SONGS = ["Back In Black", "Stairway to Heaven", "Hey Jude"];
const ARTISTS = ["ACDC", "Led Zeppelin", "The Beatles"];

function eraseDatabase() {}
function restoreDatabase() {}

class Animal {}
class Alpaca {}
```
- **What it demonstrates**: each pair in the bad block uses two conventions for one category — the fix isn't that `SCREAMING_SNAKE_CASE` is objectively right, it's that the file now applies one rule per category.

## Reference Tables

Who decides what:

| Concern | Decided by | Rule |
|---|---|---|
| Indentation, tabs vs spaces, quotes | A tool | Automate; do not discuss |
| Capitalization scheme | Your team, once | Any scheme — then be consistent |
| Caller/callee ordering | The author, per file | Caller directly above callee |

The guide's own capitalization example:

| Category | Convention | Example |
|---|---|---|
| Constant data | `SCREAMING_SNAKE_CASE` | `DAYS_IN_WEEK`, `SONGS`, `ARTISTS` |
| Functions | `camelCase` | `eraseDatabase`, `restoreDatabase` |
| Classes | `PascalCase` | `Animal`, `Alpaca` |

## Worked Example
**The newspaper rule**, applied to `PerformanceReview`.

Before — the entry point `perfReview()` sits fourth, and its three callees are scattered above and below it:

```javascript
class PerformanceReview {
  constructor(employee) { this.employee = employee; }

  lookupPeers() { return db.lookup(this.employee, "peers"); }
  lookupManager() { return db.lookup(this.employee, "manager"); }

  getPeerReviews() {
    const peers = this.lookupPeers();
  }

  perfReview() {
    this.getPeerReviews();
    this.getManagerReview();
    this.getSelfReview();
  }

  getManagerReview() {
    const manager = this.lookupManager();
  }

  getSelfReview() {}
}
```

To answer "what does a performance review consist of?", a reader must find `perfReview` in the middle, then scroll **up** for `getPeerReviews`, further **up** for `lookupPeers`, then **down** past the entry point for `getManagerReview`, then back up for `lookupManager`. Five jumps for a five-method class.

After — each function sits directly above what it calls:

```javascript
class PerformanceReview {
  constructor(employee) { this.employee = employee; }

  perfReview() {
    this.getPeerReviews();
    this.getManagerReview();
    this.getSelfReview();
  }

  getPeerReviews() {
    const peers = this.lookupPeers();
  }

  lookupPeers() { return db.lookup(this.employee, "peers"); }

  getManagerReview() {
    const manager = this.lookupManager();
  }

  lookupManager() { return db.lookup(this.employee, "manager"); }

  getSelfReview() {}
}
```

**Read it as a newspaper:** the headline is `perfReview` — three things happen. Each section follows immediately, and each section's supporting detail follows *it*. A reader who only wants the summary stops after the first method; one who wants peer-review mechanics reads two more and stops. Nobody scrolls backwards.

**Note what did *not* change:** no logic, no names, no signatures. The entire refactor is method order — which is exactly why no tool does it for you, and why it's one of only two formatting rules the chapter keeps for humans.

## Key Takeaways
1. **DO NOT ARGUE over formatting** — adopt a tool and move on; the argument costs time and money for nothing.
2. Indentation, tabs vs spaces, and quote style are automation's job, not a review topic.
3. Capitalization carries type information in an untyped language — pick a scheme as a team and apply it uniformly.
4. Consistency beats correctness for subjective choices; the guide deliberately declines to pick for you.
5. Keep callers **directly above** callees so files read top-to-bottom like a newspaper.
6. Ordering is one of the few formatting decisions a tool can't make — spend your judgment there.

## Connects To
- **Ch 1 (Introduction)**: "This is not a style guide" — this chapter is the explicit discharge of that claim.
- **Ch 2 (Variables)**: the `SCREAMING_SNAKE_CASE` convention is what makes hoisted constants like `MILLISECONDS_PER_DAY` recognizable at a glance.
- **Ch 3 (Functions)**: "Functions should only be one level of abstraction" produces the stepdown structure the newspaper rule then orders.
- **StandardJS / Prettier / ESLint**: the class of tool the chapter tells you to adopt.
