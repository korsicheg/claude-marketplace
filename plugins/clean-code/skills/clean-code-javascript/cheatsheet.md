# Cheatsheet — clean-code-javascript

## Thresholds & Defaults

| Thing | Commitment |
|---|---|
| Function arguments | 0–2 ideal · 3 avoid · **4+ consolidate into a destructured object** |
| Things a function does | **One.** "By far the most important rule in software engineering" |
| Levels of abstraction per function | One |
| Test coverage target | **100%** of statements **and branches** |
| Concepts per test | One `it`, one behavior, one reason to fail |
| Boolean parameters | **Zero** — a flag means two functions |
| Vertical distance caller→callee | ~0 lines; caller directly above |
| Comments per function | As close to zero as the code allows |
| Default class choice | No class. Small functions until objects get large and complex |
| Default over inheritance | Composition |

## Decision Rules

- **If you can only describe a function using "and", split it.** That is the one-thing test.
- **If a parameter is a boolean that picks a branch, write two functions instead.** The flag is the admission.
- **If you're passing 4+ arguments, pass one object and destructure it in the signature** — but know only *primitives* get cloned; nested objects/arrays stay shared.
- **If you're about to write `x || default`, use a default parameter — then check the falsy cases.** `||` replaces `''`, `0`, `false`, `null`, `NaN`; a default parameter replaces only `undefined`. If callers pass `""` meaningfully, the refactor is a regression.
- **If a function receives an object or array, return a new one — never mutate it.** `[...cart, item]`, not `cart.push(item)`.
- **If you need a side effect, give it exactly one owner service.** "One and only one."
- **If you're extending a built-in prototype, stop and `extends` the global instead.**
- **If you're deduplicating and the abstraction feels forced, keep the duplication.** "Bad abstractions can be worse than duplicate code."
- **If you must override a method to preserve the subclass's own invariant, it isn't a subtype** — make both siblings under a shared parent (LSP).
- **If a constructor calls `new` on its collaborator, inject it instead** (DIP).
- **If adding a variant means editing an existing `if`/`switch`, move the behavior onto the variant** (OCP).
- **If a `try/catch` has no plan for the failure, delete the `try/catch`** — let it propagate. An empty catch deletes the error.
- **If you're about to argue about formatting, install a formatter instead.** "DO NOT ARGUE."
- **If a comment restates the code, delete the comment. If it's load-bearing because a name is bad, fix the name.**

## Removing a Conditional — escalation ladder

Work down until one fits:

- Compound condition in an `if` → **extract a named predicate** (`shouldShowSpinner(...)`)
- `!isNotPresent(x)` → **invert to a positive predicate** (`isPresent(x)`)
- `switch (this.type)` inside a class → **one subclass per case**
- `instanceof` chain → **consistent API**: give every type the same method, just call it
- `typeof` guards on primitives → **adopt TypeScript**; hand-rolled checks cost more readability than they buy safety

## Async — a one-way ladder

Callbacks → Promises → **async/await**. Never climb back down.

| | Nesting | Error handling | Cost of one more step |
|---|---|---|---|
| Callbacks | grows per operation | one `if (err)` per level | +1 level, +1 branch |
| Promises | flat | one `.catch()` | +1 `.then()` |
| **async/await** | none | `try/catch` | **+1 line** |

Swaps that make it mechanical: `request` → `request-promise`, `fs` → `fs-extra`. Don't forget to *call* the async function.

## Inheritance Gate — all three must hold

1. Genuine **"is-a"**, not "has-a" — Human→Animal ✅, User→UserDetails ❌
2. The subclass **reuses base-class code**
3. You **want** base-class changes to propagate to every derived class

Any "no" → composition.

## Error Handler Adequacy

| Handler | Verdict |
|---|---|
| `catch (e) {}` | Worst — error erased |
| `catch (e) { console.log(e) }` | Bad — lost in console noise |
| `catch (e) { console.error(e) }` | Minimum acceptable |
| `console.error` + `notifyUserOfError` + `reportErrorToService` | Recommended — "OR do all three!" |
| No `.catch()` on a chain | Unhandled rejection |

Ask: *does a developer need this now? is a human waiting? would I want this at 3am?* → log / notify / report.

## Tells & Smells

| If you see… | You're probably… | Go to |
|---|---|---|
| A magic number | hiding intent nobody can grep | Ch 2 |
| `getUserInfo` + `getClientData` + `getCustomerRecord` | growing three near-duplicate implementations | Ch 2 |
| `forEach(l => ...)` with a long body | forcing mental mapping | Ch 2 |
| `car.carColor` | repeating context that's already in scope | Ch 2 |
| A 4th argument | about to violate "do one thing" | Ch 3 |
| `cart.push(...)` on a parameter | writing the retry-purchase bug | Ch 3 |
| `Array.prototype.x = ...` | shipping a collision into someone's production | Ch 3 |
| `class X extends Y` where X *has* a Y | modeling has-a as is-a | Ch 5 |
| A setter returning `undefined` | blocking chaining | Ch 5 |
| `if (adapter.name === "...")` | violating OCP with a name tag | Ch 6 |
| A subclass overriding a setter to stay consistent | violating LSP (Square/Rectangle) | Ch 6 |
| `new Requester()` in a constructor | hard-wiring a dependency | Ch 6 |
| One `it` with five assertions | masking later failures behind the first | Ch 7 |
| `.catch(e => console.log(e))` | discarding an error with a receipt nobody reads | Ch 9 |
| `restore_database()` beside `eraseDatabase()` | losing case as a type signal | Ch 10 |
| `////////` banners | decorating a file that should be split | Ch 11 |
| A dated changelog above a function | duplicating `git log`, badly | Ch 11 |
| Commented-out code | keeping dead code nobody dares delete | Ch 11 |
