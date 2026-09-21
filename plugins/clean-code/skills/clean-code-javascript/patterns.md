# Patterns & Techniques — clean-code-javascript

Concrete, repeatable techniques from the guide. Each is a refactor you can apply mechanically once you've recognized the trigger.

## Named Constant Extraction
**When to use**: any literal — especially a number — whose meaning isn't self-evident at the call site.
**How**: hoist to a `SCREAMING_SNAKE_CASE` const and keep the derivation visible: `const MILLISECONDS_PER_DAY = 60 * 60 * 24 * 1000;`. Enforce with ESLint `no-magic-numbers` or buddy.js.
**Trade-offs**: none of substance. Keep the arithmetic form rather than the computed value — it documents itself. (Ch 2)

## Explanatory Variable via Destructuring
**When to use**: a subexpression used twice, or positional indexing like `match[1]` / `match[2]`.
**How**: `const [_, city, zipCode] = address.match(re) || [];` — one evaluation, named slots.
**Trade-offs**: `|| []` is required to keep a failed match from throwing. (Ch 2)

## Object Parameter with Signature Destructuring
**When to use**: a function needs three or more arguments.
**How**: `function createMenu({ title, body, buttonText, cancellable })`, called with an object literal.
**Trade-offs**: destructuring clones **primitives** only — nested objects and arrays are still shared references. (Ch 3)

## Predicate Extraction
**When to use**: a loop body that filters before acting, or a compound condition inside `if`.
**How**: name the boolean expression as its own function — `clients.filter(isActiveClient).forEach(email)`; `if (shouldShowSpinner(fsm, listNode))`.
**Trade-offs**: one more named function, independently testable. Almost always worth it. (Ch 3)

## Flag Parameter Split
**When to use**: any boolean parameter that selects a code path.
**How**: two functions with real names — `createFile(name)` and `createTempFile(name)`, the second delegating to the first.
**Trade-offs**: more entry points, each doing one thing. That's the goal. (Ch 3)

## Clone-and-Return (Immutable Argument Handling)
**When to use**: a function receives an object or array that callers still hold.
**How**: `return [...cart, item]` instead of `cart.push(item)`.
**Trade-offs**: cloning large structures costs memory/time — use Immutable.js for hot paths. Occasionally you genuinely want to mutate the input, but "those cases are pretty rare". (Ch 3)

## Extend the Global, Don't Patch It
**When to use**: you want a helper method on a built-in type.
**How**: `class SuperArray extends Array { diff(other) { ... } }` instead of `Array.prototype.diff = ...`.
**Trade-offs**: callers must construct your subclass. The alternative is a production collision in *your user's* app. (Ch 3)

## Functional Aggregation
**When to use**: an accumulator loop building a total, a mapped list, or a filtered list.
**How**: `reduce` / `map` / `filter`.
**Trade-offs**: JS "isn't a functional language in the way that Haskell is" — apply where it reads better, not universally. (Ch 3)

## Polymorphic Dispatch (Replace Conditional)
**When to use**: a `switch`/`if` branching on a type discriminator inside a class, or an `instanceof` chain.
**How**: one subclass per case, each overriding the method; or give every accepted type the same method name and just call it (`vehicle.move(...)`).
**Trade-offs**: more classes; the payoff is that new variants are purely additive (OCP). (Ch 3, Ch 6)

## Object.assign Defaults
**When to use**: a config object with several optional keys.
**How**: `Object.assign({ title: "Foo", body: "Bar", ... }, config)` — defaults first, caller config second.
**Trade-offs**: shallow merge only; nested config needs deeper handling. (Ch 3)

## Closure Privacy (Factory Function)
**When to use**: state that external code must not reach, overwrite, or `delete`.
**How**: declare state as a local in a factory and return only the methods closing over it — `makeEmployee(name)` returning `{ getName() { return name } }`.
**Trade-offs**: methods are per-instance rather than shared on a prototype. Irrelevant at ordinary object counts; measure before worrying. (Ch 4)

## Accessor Methods
**When to use**: a property needing validation, logging, lazy loading, or freedom to change representation.
**How**: `getBalance()` / `setBalance(amount)` over a bare `balance` field.
**Trade-offs**: indirection that pays for itself only when at least one of those five reasons applies. (Ch 4)

## Method Chaining
**When to use**: builder- and configuration-style APIs.
**How**: `return this;` at the end of **every** method, terminal ones included.
**Trade-offs**: only works when methods have nothing else to return; a method with a real return value should return it. (Ch 5)

## Composition over Inheritance
**When to use**: by default. Use `extends` only when all three hold — genuine "is-a", base-class code reuse, and you *want* base changes to propagate to all derived classes.
**How**: hold the collaborator as a field (`this.taxData = new EmployeeTaxData(...)`).
**Trade-offs**: slightly more wiring; avoids the `EmployeeTaxData extends Employee` class of mistake. (Ch 5)

## Responsibility Extraction (SRP)
**When to use**: a class you'd have to edit for two unrelated reasons.
**How**: split by *reason to change* — pull `UserAuth` out of `UserSettings` and hold it as a field.
**Trade-offs**: more classes, each with fewer reasons to change. (Ch 6)

## Constructor Injection (DIP)
**When to use**: any class that `new`s its own collaborator.
**How**: take the collaborator as a constructor parameter; construct it at the call site (`new InventoryTracker(items, new InventoryRequesterV2())`).
**Trade-offs**: wiring moves outward — which is what makes V1→V2 swaps and test doubles possible. (Ch 6)

## Sibling Classes Under a Shared Parent (Fix LSP)
**When to use**: a subclass must override a method to preserve its own invariant (Square overriding `setWidth`).
**How**: give both a common parent (`Shape`), move dimensions into constructors, let each own its `getArea()`.
**Trade-offs**: abandons a relationship that felt natural; restores substitutability. (Ch 6)

## Optional Options Bag (ISP)
**When to use**: a constructor demanding settings most clients don't need.
**How**: nest rare settings under `options` and guard with `if (this.options.x)`.
**Trade-offs**: one extra level of nesting; removes the fat interface. (Ch 6)

## Single-Concept Test Split
**When to use**: one `it` block asserting several behaviors.
**How**: one `it` per concept, each with a descriptive name and its own `const` fixture.
**Trade-offs**: more test blocks; failures become self-describing and stop masking each other. (Ch 7)

## Callback → Promise → async/await
**When to use**: any nested-callback async code.
**How**: swap to promise-returning modules (`request` → `request-promise`, `fs` → `fs-extra`), chain `.then()` with one `.catch()`, then convert to `async`/`await` with `try/catch`.
**Trade-offs**: none the guide endorses — it treats this as a one-way ladder. Remember to actually invoke the async function. (Ch 8)

## Three-Response Error Handling
**When to use**: every `catch` block and every `.catch()`.
**How**: `console.error(error)` (noisier than `console.log` on purpose), `notifyUserOfError(error)`, `reportErrorToService(error)` — "OR do all three!"
**Trade-offs**: if none of the three is warranted, you had no plan — delete the `try/catch` and let the error propagate. (Ch 9)

## Newspaper Ordering
**When to use**: any file or class whose reader must scroll to follow a call.
**How**: put each caller directly above its callee; entry point first, details descending.
**Trade-offs**: no tool does this for you — it's manual and worth the minute. (Ch 10)

## Comment Deletion Test
**When to use**: before writing or keeping any comment.
**How**: ask whether deleting it loses information the code can't express. `// Convert to 32-bit integer` above `hash &= hash` survives; narration doesn't. If a comment is load-bearing because a name is poor, fix the name.
**Trade-offs**: none — stale comments are a liability nothing checks. (Ch 11)
