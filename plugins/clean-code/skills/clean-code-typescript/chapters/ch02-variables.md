# Chapter 2: Variables

## Core Idea
A variable name is the cheapest documentation you will ever write: make names **meaningful,
pronounceable, searchable, and context-free**, and let TypeScript's `enum` and default
arguments carry intent that comments otherwise would.

## Frameworks Introduced
- **Distinguish names by what the difference *offers***: if two names differ, the reader must be
  able to tell *what the difference buys*.
  - When to use: any time you have sibling parameters or sibling variables (`a1, a2, a3`).
  - How: ask "what does the reader learn from this name that they don't learn from its
    neighbour?" `(a1, a2, a3)` → `(value, left, right)`.
- **The pronounceability test**: *"If you can't pronounce it, you can't discuss it without
  sounding like an idiot."*
  - When to use: on abbreviations and compressed names (`genymdhms`, `DtaRcrd102`, `pszqint`).
  - How: say the name out loud as if in a standup. If you would have to spell it, rename it.
- **The searchability test**: we read far more code than we write, so a name must be
  **greppable**.
  - When to use: on every literal that carries meaning — magic numbers and magic strings.
  - How: promote it to a capitalized named constant. ESLint can find the unnamed ones for you.
- **"Explicit is better than implicit. Clarity is king."** — the anti-mental-mapping rule.
  - When to use: whenever you have single-letter locals outside a trivial scope.
  - How: the reader should never have to hold a translation table (`u`→user, `s`→subscription)
    in their head while reading.
- **Don't repeat the container in the contained**: if the type name says `Car`, the field does
  not say `carMake`.
  - How: read the name at its *use site*, with the owner attached: `car.carMake` is stuttering;
    `car.make` is not.

## Key Concepts
- **Mental mapping** — the reader-side cost of translating a short name into the concept it
  stands for. Always paid by the reader, never by the writer.
- **Magic number / magic string** — an unnamed literal whose meaning lives only in the
  author's head (`setTimeout(restart, 86400000)`).
- **Named constant** — a `SCREAMING_SNAKE_CASE` binding that gives a literal a searchable name.
- **Unneeded context** — name segments already implied by the enclosing type, class, or module.
- **Explanatory variable** — a local (often from destructuring) introduced solely to name a
  value that was previously anonymous.
- **Short circuiting** — `count !== undefined ? count : 10` or `x || fallback`; the pattern
  default arguments replace.
- **Intent documentation via `enum`** — using a nominal set of members when you care that
  values are *distinct*, not what they literally are.

## Mental Models
- **Think of a name as a promise to the next reader**, and of an abbreviation as a debt they
  repay on every read.
- **Use `enum` when you care that values differ, not what they are.** That is the stated
  trigger: a `const` object of string literals leaks incidental strings into your domain; an
  `enum` says "these are the four genres" and nothing more.
- **Use a default argument, not a conditional, whenever the fallback is a constant.** The
  signature then documents the default — `loadPages(count: number = 10)` tells the caller the
  answer without opening the body.
- **Treat destructuring as naming.** `for (const keyValue of users)` names nothing;
  `for (const [id, user] of users)` names two things for free.
- **Read every field name with its owner prefixed.** The stutter is only visible at the use site.

## Code Examples

Searchable names — the rule that pays for itself in the diff:

```ts
// Bad — what the heck is 86400000 for?
setTimeout(restart, 86400000);

// Good — declare them as capitalized named constants.
const MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000; // 86400000
setTimeout(restart, MILLISECONDS_PER_DAY);
```
- **What it demonstrates**: the arithmetic form (`24 * 60 * 60 * 1000`) doubles as the
  derivation, and the name is now greppable across the repo.

`enum` to document intent:

```ts
// Bad — a const object; the switch matches incidental string values.
const GENRE = { ROMANTIC: 'romantic', DRAMA: 'drama', COMEDY: 'comedy' };

// Good — the members ARE the domain; no strings leak out.
enum GENRE { ROMANTIC, DRAMA, COMEDY, DOCUMENTARY }

projector.configureFilm(GENRE.COMEDY);
```
- **What it demonstrates**: intent ("these values are distinct") expressed in the type system
  rather than in a comment.

Default arguments over short circuiting:

```ts
// Bad
function loadPages(count?: number) {
  const loadCount = count !== undefined ? count : 10;
}

// Good — the default is now part of the signature.
function loadPages(count: number = 10) { }
```

## Reference Tables

| Rule | Bad | Good |
|---|---|---|
| Meaningful | `between<T>(a1, a2, a3)` | `between<T>(value, left, right)` |
| Pronounceable | `type DtaRcrd102 = { genymdhms, modymdhms, pszqint }` | `type Customer = { generationTimestamp, modificationTimestamp, recordId }` |
| One vocabulary | `getUserInfo()` / `getUserDetails()` / `getUserData()` | `getUser()` |
| Searchable | `setTimeout(restart, 86400000)` | `MILLISECONDS_PER_DAY` |
| Explanatory | `for (const keyValue of users)` | `for (const [id, user] of users)` |
| No mental map | `const u = getUser()` | `const user = getUser()` |
| No extra context | `car.carMake` | `car.make` |
| Default args | `count !== undefined ? count : 10` | `count: number = 10` |
| Intent via enum | `const GENRE = { ROMANTIC: 'romantic' }` | `enum GENRE { ROMANTIC }` |

## Worked Example
The "unneeded context" rule, walked end to end — because it is the one people under-apply, and
the payoff only shows up at the call sites.

**Before** — the type name is `Car`, and every field repeats it:

```ts
type Car = {
  carMake: string;
  carModel: string;
  carColor: string;
}

function print(car: Car): void {
  console.log(`${car.carMake} ${car.carModel} (${car.carColor})`);
}
```

Read the template literal aloud: *"car car-make, car car-model, car car-color."* The prefix is
pure noise — the type annotation `car: Car` already established it.

**After:**

```ts
type Car = {
  make: string;
  model: string;
  color: string;
}

function print(car: Car): void {
  console.log(`${car.make} ${car.model} (${car.color})`);
}
```

**Why it works**: the context now lives in exactly one place (the type), so it can be changed
in exactly one place. Rename `Car` → `Vehicle` and the `After` version needs no field edits at
all; the `Before` version needs three, plus every use site, or it silently starts lying.

**Failure mode of over-applying it**: strip context that the *use site* does not supply and the
name goes vague. A bare `make: string` sitting in a 400-line function that also handles
manufacturers and suppliers is worse than `carMake`. The test is not "is the word redundant in
the type declaration" but **"is the word redundant at the point of use"** — `car.make` passes,
a free-floating `const make = ...` does not.

## Key Takeaways
1. Names differ only to tell the reader **what the difference offers** — `(value, left, right)`,
   never `(a1, a2, a3)`.
2. If you can't pronounce it, rename it — you cannot discuss what you cannot say.
3. **One word per concept**: `getUser()`, not `getUserInfo`/`getUserDetails`/`getUserData`.
4. Every meaningful literal becomes a **capitalized named constant**; let ESLint find them.
5. Destructuring is free naming — take it.
6. Don't repeat the type's name inside its fields; test the name **at the use site**.
7. Default arguments beat short circuiting, and put the default in the signature where callers
   read it.
8. Reach for `enum` when distinctness is the point and the literal value is not.

## Connects To
- **Ch 3 (Functions)**: "Function names should say what they do" is this chapter's rules applied
  to the function itself; option objects (ch03) are where destructuring-as-naming pays most.
- **Ch 10 (Formatting)**: fixes the casing conventions these names are written in — `PascalCase`
  for types, `camelCase` for variables, `SNAKE_CASE` for the constants introduced here.
- **Ch 11 (Comments)**: "prefer self-explanatory code instead of comments" is the same lever —
  an explanatory variable is the comment you didn't have to write.
- **Ch 6 (SOLID)**: `enum` + `switch` is a known OCP pressure point; ch06 replaces it with
  polymorphism when the branch set keeps growing.
- **`clean-code-java` ch02 (Meaningful Names)**: fuller treatment — name length ∝ scope, no
  encodings/Hungarian, no puns, and the rule that **the name must include the side effects**.
