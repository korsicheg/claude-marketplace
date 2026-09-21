# Cheatsheet — clean-code-typescript

## Thresholds & defaults
| Thing | Commit to |
|---|---|
| Function arguments | **≤2** ideal · 3 avoid · 4+ → options object |
| Asserts per test | **1** (one concept) |
| Test coverage | **100%** statements *and* branches, before shipping or refactoring |
| Access modifier | **`private readonly`** by default (`public` is TS's default and usually wrong) |
| Field mutability | **`readonly`** unless you intend to change it |
| Async style | **`async`/`await`** (chain acceptable, callbacks not) |
| Throw/reject payload | **always `new Error(...)`**, never a string |
| Casing | `PascalCase` types · `camelCase` values/members · `SNAKE_CASE` constants |
| Import groups | **6**, blank-line separated, alphabetized within |
| Endorsed comment forms | **1** — `// TODO` |

## Decision rules — if X, do Y, because Z
- **If a signature has 3+ params** → options object with a `type` alias, because arg count blows up the test matrix combinatorially.
- **If a param is a boolean** → split the function, because a flag advertises that it does two things.
- **If you're writing `instanceof`** → union type with a shared method (local) or `abstract` method (OCP), because each new variant otherwise edits a class that isn't about variants.
- **If you're writing `switch` on a type field** → subclass + override, because that's one function doing many things.
- **If a function mutates its argument** → clone, edit, return the clone, because every other holder of that object silently sees the change.
- **If two consecutive `await`s don't consume each other's results** → one `Promise.all`, because you've serialized by accident: latency is the sum, not the max.
- **If a `catch` block is empty or only `console.log`s** → real logger **+ a code path**, because writing the `try` was a claim that this can fail.
- **If an implementer must `throw new Error('… not supported')`** → split the interface (ISP), because the interface is fatter than its clients.
- **If a class field is used by only one method group** → split the class, because the other callers are being forced to supply a dependency they never use.
- **If you'd say "X *has* a Y" out loud** → compose, don't `extend`.
- **If a comment explains *what* the code does** → extract a named boolean/function; the comment's text is the name. **If it explains *why*** → keep it (and see `clean-code-java` ch04).
- **If a file needs `////// section //////` banners to navigate** → the class is too big; IDE folding already does signage.
- **If imports contain `../../../`** → path alias, and ask whether the module is in the wrong place.
- **If an import is types-only** → `import type`, because it's erased at runtime and therefore breaks dependency cycles.
- **If the team is arguing about formatting** → commit an ESLint+Prettier config; it's "a waste of time and money."

## Decision trees
**`type` or `interface`?** → need a union/intersection → **`type`** · need `extends`/`implements` → **`interface`** · neither → either; be consistent (the source states there is *no strict rule*).

**How immutable?** → one property → `readonly` · whole shape → `Readonly<T>` · array must not grow → `ReadonlyArray<T>` / `readonly T[]` · **literal you return** → `as const` (plain `readonly` will *not* protect it) · need a runtime guarantee → **none of these; all are erased**.

**`throw` or `Failable<R, E>`?** → failure is unexpected / must propagate up layers / you want a stack → **`throw new Error`** · failure is expected, caller must branch, you want the compiler to force it → **`Failable`** (costs unwrap/rewrap at every layer, no stack).

**`extend` or compose?** → all three of (1) is-a, (2) real base-class reuse, (3) you want base changes to propagate → **inherit** · any missing → **compose**.

**Deduplicate?** → same domain, one shared reason to change → **extract** · different modules, different domains, coincidental resemblance → **keep both copies** (extraction creates an indirect dependency; *"bad abstractions can be worse than duplicate code"*).

## Tells & smells
| You see | It means | Go to |
|---|---|---|
| 3+ params, or a boolean param | function does >1 thing | Ch 3 |
| `instanceof` chain | type system underused / OCP violation | Ch 3, Ch 6 |
| Two altitudes of code in one body | mixed abstraction | Ch 3 |
| `let subject` reassigned inside `it()` | multiple concepts in one test | Ch 7 |
| `it('2/29/2020')` | test named after data, not behaviour | Ch 7 |
| `throw new Error('… not supported')` | fat interface | Ch 6 |
| `private readonly x = new Concrete()` | DIP violation; untestable | Ch 6 |
| Override maintains a private invariant | LSP violation (25, not 20) | Ch 6 |
| Class name needs "and" | SRP violation | Ch 5, Ch 6 |
| Caller constructs a dep it never uses | low cohesion | Ch 5 |
| `void` setters then `build()` | missing `this` return | Ch 5 |
| `array.push()` compiles on a `const` | needs `ReadonlyArray<T>` | Ch 4 |
| `result.value = 200` compiles | returned literal needs `as const` | Ch 4 |
| Nested callbacks; `if (error)` per level | callback hell | Ch 8 |
| Dated changelog / commented-out code | git already has it | Ch 11 |
| Comment restates the next line | extract a name, delete the comment | Ch 11 |
| `car.carMake` | unneeded context | Ch 2 |
| Bare literal like `86400000` | needs a `SNAKE_CASE` named constant | Ch 2 |

## F.I.R.S.T. as a diagnostic
Slow → **F** · order-dependent → **I** · green locally red in CI → **R** · needs a human to read output → **S** · hard to write at all → **T** *(that's a design problem — inject dependencies)*.

## Judgment calls the source explicitly allows
Formatting (*"subjective… your team can choose whatever they want"*) · `type` vs `interface` (*no strict rule*) · cross-domain duplication · maximal cohesion (*"not always possible, nor even advisable"*) · TDD itself (*coverage is the requirement; TDD is one route*) · and the whole guide (*"not every principle herein has to be strictly followed, and even fewer will be universally agreed upon"*).
