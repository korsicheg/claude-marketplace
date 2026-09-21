# Chapter 2: Variables

## Core Idea
A variable name must carry the meaning that would otherwise live in a comment, a lookup table, or the reader's short-term memory — make names **meaningful, pronounceable, searchable, and free of redundant context**.

## Frameworks Introduced
- **Use meaningful and pronounceable variable names**: if you cannot say it out loud in a code review, rename it.
  - When to use: every declaration.
  - How: expand encodings into words — `yyyymmdstr` → `currentDate`.
- **Use the same vocabulary for the same type of variable**: one concept, one word, across the whole codebase.
  - When to use: when naming a second accessor for a thing you already named once.
  - How: pick one term (`User`) and ban the synonyms (`Info`, `Data`, `Record`, `Client`, `Customer`) for that same entity. `getUserInfo/getClientData/getCustomerRecord` → `getUser`.
- **Use searchable names**: "We will read more code than we will ever write" — a value you cannot grep for is a value you cannot maintain.
  - When to use: any literal that carries meaning, especially numbers.
  - How: hoist to a capitalized named constant; let **buddy.js** or the ESLint **`no-magic-numbers`** rule find the ones you missed.
- **Use explanatory variables**: name the intermediate result instead of re-deriving or re-indexing it.
  - When to use: when a subexpression is used twice, or indexed positionally (`match[1]`, `match[2]`).
  - How: destructure or assign to a named const before passing it on.
- **Avoid Mental Mapping**: "Explicit is better than implicit."
  - When to use: loop and callback parameters.
  - How: name the element for what it is (`location`), never a single letter the reader must hold in their head.
- **Don't add unneeded context**: if the class/object name says it, the property must not repeat it.
  - When to use: object literals and class fields.
  - How: `Car.carMake` → `Car.make`.
- **Use default parameters instead of short circuiting or conditionals**: prefer `function f(name = "x")` over `const n = name || "x"`.
  - When to use: any optional argument.
  - How: put the default in the signature — but know the semantics (see Anti-patterns).

## Key Concepts
- **Pronounceable name** — a name you can read aloud unambiguously in discussion.
- **Searchable name** — a name/constant you can grep, as opposed to a bare literal like `86400000`.
- **Magic number** — an unnamed numeric literal whose meaning lives only in the author's head.
- **Explanatory variable** — a named const introduced purely to give a subexpression a meaning.
- **Mental mapping** — forcing the reader to remember that `l` means `location`.
- **Unneeded context** — repeating the container's name inside its members (`carColor` on `Car`).
- **Short-circuiting default** — `x || fallback`, which fires on *every* falsy value, not just `undefined`.
- **Default parameter** — an ES6 signature default, which fires on `undefined` only.

## Mental Models
- **Think of a name as the comment you don't have to write.** `MILLISECONDS_PER_DAY` retires the comment `// What the heck is 86400000 for?`.
- **Use the read/write ratio as the tiebreaker.** You will read this far more often than you wrote it; optimize the name for the reader, not for your typing speed.
- **Think of one concept, one word.** Vocabulary drift (`Info`/`Data`/`Record`) is how a codebase grows three functions that do the same job.
- **Use the container to carry the context.** The name of the object is already in scope for the reader — don't pay for it twice in every field.

## Anti-patterns
- **Encoded / abbreviated names** (`yyyymmdstr`): unpronounceable, unsearchable, and the encoding is never quite complete.
- **Synonym drift** (`getUserInfo`, `getClientData`, `getCustomerRecord`): three names for one entity guarantees three near-duplicate implementations.
- **Magic numbers** (`setTimeout(blastOff, 86400000)`): the reader must do arithmetic to recover intent, and nobody can grep the value's uses.
- **Positional regex indexing** (`address.match(re)[1]`, `[2]`): re-runs the match *and* hides what each slot means.
- **Single-letter callback params** (`l`, `e`, `x`) in bodies longer than a line: the classic "wait, what is `l` for again?" defect.
- **Redundant prefixes** (`car.carColor`): noise that scales with every field added.
- **`||` as a default**: silently replaces `''`, `""`, `false`, `null`, `0`, and `NaN` — so `createMicrobrewery("")` and `count || 10` are bugs waiting to happen. A default parameter only replaces `undefined`.

## Code Examples
The searchable-names rule, which subsumes the magic-number problem:

```javascript
// Bad
// What the heck is 86400000 for?
setTimeout(blastOff, 86400000);

// Good — declare them as capitalized named constants.
const MILLISECONDS_PER_DAY = 60 * 60 * 24 * 1000; //86400000;

setTimeout(blastOff, MILLISECONDS_PER_DAY);
```
- **What it demonstrates**: the constant is simultaneously the name, the documentation, and the derivation — `60 * 60 * 24 * 1000` shows its own arithmetic.

Explanatory variables via destructuring:

```javascript
// Bad — match runs twice, [1] and [2] mean nothing
const cityZipCodeRegex = /^[^,\\]+[,\\\s]+(.+?)\s*(\d{5})?$/;
saveCityZipCode(
  address.match(cityZipCodeRegex)[1],
  address.match(cityZipCodeRegex)[2]
);

// Good — one match, named slots
const [_, city, zipCode] = address.match(cityZipCodeRegex) || [];
saveCityZipCode(city, zipCode);
```
- **What it demonstrates**: destructuring is JavaScript's native way to buy explanatory names for free; `|| []` keeps a failed match from throwing.

## Reference Tables

| Rule | Bad | Good |
|---|---|---|
| Meaningful & pronounceable | `yyyymmdstr` | `currentDate` |
| Same vocabulary | `getUserInfo` / `getClientData` / `getCustomerRecord` | `getUser` |
| Searchable | `86400000` | `MILLISECONDS_PER_DAY` |
| Explanatory variable | `match(re)[1]`, `match(re)[2]` | `const [_, city, zipCode] = ...` |
| No mental mapping | `locations.forEach(l => ...)` | `locations.forEach(location => ...)` |
| No unneeded context | `Car.carMake`, `car.carColor` | `Car.make`, `car.color` |
| Default parameters | `name \|\| "Hipster Brew Co."` | `function f(name = "Hipster Brew Co.")` |

Falsy-value trap — which values each default mechanism replaces:

| Argument value | `name \|\| "default"` | `name = "default"` |
|---|---|---|
| `undefined` | replaced | replaced |
| `null` | replaced | **kept** |
| `0` | replaced | **kept** |
| `''` / `""` | replaced | **kept** |
| `false` | replaced | **kept** |
| `NaN` | replaced | **kept** |

## Worked Example
The guide's brewery case, walked end to end.

Starting point — short-circuit default:

```javascript
function createMicrobrewery(name) {
  const breweryName = name || "Hipster Brew Co.";
  // ...
}
```

The refactor is mechanical — lift the default into the signature:

```javascript
function createMicrobrewery(name = "Hipster Brew Co.") {
  // ...
}
```

But the two are **not equivalent**, and the guide flags exactly this: default parameters only fire for `undefined`. Trace three calls:

| Call | Old (`\|\|`) | New (default param) |
|---|---|---|
| `createMicrobrewery()` | `"Hipster Brew Co."` | `"Hipster Brew Co."` |
| `createMicrobrewery("")` | `"Hipster Brew Co."` | `""` ← behavior change |
| `createMicrobrewery(null)` | `"Hipster Brew Co."` | `null` ← behavior change |

**How to decide:** if empty string and `null` are invalid inputs, the new behavior is *better* — it surfaces a caller bug instead of papering over it. If callers legitimately pass `""` to mean "unnamed", the refactor introduces a regression and you need explicit handling. Make that call consciously; don't let the rule make it for you.

## Key Takeaways
1. Name things so the name replaces a comment — pronounceable, searchable, unabbreviated.
2. One concept gets **one word** across the codebase; synonym drift breeds duplicate functions.
3. Hoist every meaningful literal into a capitalized named constant; enforce with `no-magic-numbers` or buddy.js.
4. Introduce explanatory variables (often via destructuring) rather than positional indexes or repeated subexpressions.
5. Name loop/callback parameters for what they hold — never make the reader map `l` → `location`.
6. Don't repeat the container's name in its members.
7. Prefer default parameters to `||`, and know that they only catch `undefined` — verify the falsy cases before refactoring.

## Connects To
- **Ch 3 (Functions)**: "Function names should say what they do" is the same naming discipline applied to callables; the object-argument rule reuses destructuring from here.
- **Ch 10 (Formatting)**: "Use consistent capitalization" governs the `SCREAMING_SNAKE_CASE` convention these constants rely on.
- **Ch 11 (Comments)**: good names are why most comments are unnecessary — "Comments are an apology, not a requirement."
- **ESLint `no-magic-numbers` / buddy.js**: the tooling that mechanizes the searchable-names rule.
