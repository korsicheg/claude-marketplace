# Chapter 3: Functions

## Core Idea
**Functions should do one thing** — called "by far the most important rule in software engineering" — and everything else in this chapter (argument count, abstraction level, flags, side effects) is a tell for whether that one rule is being kept.

## Frameworks Introduced
- **Function arguments (2 or fewer ideally)**: one or two is ideal, three should be avoided, more than three must be consolidated.
  - When to use: every signature.
  - How: pass a single object and **destructure it in the signature** — `createMenu({ title, body, buttonText, cancellable })`.
  - Why it works: more than three arguments causes a *combinatorial explosion* of test cases. Destructuring also (1) makes used properties visible at the signature, (2) simulates named parameters, (3) clones destructured **primitives**, limiting side effects — note objects and arrays destructured out are **not** cloned, (4) lets linters warn on unused properties.
- **Functions should do one thing**: "If you take nothing else away from this guide other than this, you'll be ahead of many developers."
  - When to use: always; it is the root rule.
  - How: if you can describe the function only with "and", split it. Extract the predicate, then compose (`clients.filter(isActiveClient).forEach(email)`).
  - Failure mode: multi-purpose functions are harder to compose, test, and reason about.
- **Function names should say what they do**: the name must disclose the effect, not just the subject.
  - When to use: any function whose call site is ambiguous.
  - How: `addToDate(date, 1)` → `addMonthToDate(1, date)` — add the missing noun.
- **Functions should only be one level of abstraction**: mixing levels means the function is doing too much.
  - When to use: any function that both orchestrates and implements.
  - How: name each level and extract it — `tokenize()`, `parse()`, then the orchestrator just calls them in sequence.
- **Remove duplicate code**: duplication means more than one place to change one behavior.
  - When to use: when two functions differ only in a detail.
  - How: create an abstraction covering the variation — but get it right, because **bad abstractions can be worse than duplicate code**. Follow SOLID (Ch 6) when abstracting.
- **Set default objects with `Object.assign`**: merge caller config onto a defaults literal.
  - When to use: config/options objects with several optional keys.
  - How: `Object.assign({ ...defaults }, config)` — defaults first, config second.
- **Don't use flags as function parameters**: "Flags tell your user that this function does more than one thing."
  - When to use: any boolean parameter that selects a code path.
  - How: split into two named functions — `createFile(name)` and `createTempFile(name)`.
- **Avoid Side Effects (part 1 — centralize them)**: a side effect is anything beyond taking a value and returning a value.
  - When to use: any write to a file, global, or shared state.
  - How: you *will* need side effects; have **one service** that performs each one. "One and only one." Don't scatter writers to the same file across classes.
- **Avoid Side Effects (part 2 — don't mutate arguments)**: objects and arrays are mutable and passed by reference.
  - When to use: any function receiving an object or array.
  - How: clone, edit the clone, return it — `return [...cart, item]`, not `cart.push(item)`.
  - Caveats the guide states: (1) occasionally you *do* want to mutate the input, but those cases are rare; (2) cloning big objects is expensive — libraries like Immutable.js make this fast.
- **Don't write to global functions**: never extend built-in prototypes.
  - When to use: when tempted by `Array.prototype.myHelper = ...`.
  - How: `class SuperArray extends Array { ... }`. Prototype patches clash with other libraries and surface as production exceptions your API's users can't explain.
- **Favor functional programming over imperative programming**: JS "has a functional flavor"; functional code is cleaner and easier to test.
  - When to use: aggregations, transformations, filters.
  - How: `reduce`/`map`/`filter` over accumulator loops.
- **Encapsulate conditionals**: give a boolean expression a name.
  - When to use: any compound condition in an `if`.
  - How: `if (shouldShowSpinner(fsm, listNode))`.
- **Avoid negative conditionals**: name the positive predicate.
  - How: `isDOMNodeNotPresent` + `!` → `isDOMNodePresent`.
- **Avoid conditionals (use polymorphism)**: a `switch` on a type field is a class hierarchy waiting to be written.
  - When to use: branching on `this.type` / a kind discriminator inside a class.
  - How: one subclass per case, each overriding the method. Rationale is the root rule again: "when you have classes and functions that have `if` statements, you are telling your user that your function does more than one thing."
- **Avoid type-checking (part 1)**: prefer **consistent APIs** over `instanceof` branching.
  - How: give every accepted type the same method name (`vehicle.move(...)`) and just call it.
- **Avoid type-checking (part 2)**: if you're type-checking primitives, **use TypeScript** instead.
  - Why: hand-rolled type-checking "requires so much extra verbiage that the faux 'type-safety' you get doesn't make up for the lost readability." Otherwise: clean JS + good tests + good code reviews.
- **Don't over-optimize**: modern engines optimize at runtime; hand-caching `list.length` is wasted effort.
- **Remove dead code**: "Dead code is just as bad as duplicate code." Version history keeps it safe.

## Key Concepts
- **Combinatorial explosion** — test cases multiplying with each extra argument; the reason for the ≤2 argument rule.
- **Level of abstraction** — how far a statement sits from the domain; mixing levels in one function is a split signal.
- **Flag argument** — a boolean parameter selecting a branch; a direct admission the function does two things.
- **Side effect** — anything a function does other than take a value in and return a value out.
- **Pure function** — takes values, returns values, touches nothing else.
- **Global pollution** — adding to `Array.prototype` or another built-in, risking library collisions.
- **Consistent API** — every type in a position exposes the same method, removing the need to type-check.
- **Dead code** — unreferenced code kept "just in case"; delete it, `git` has it.

## Mental Models
- **Use "can I describe it without 'and'?" as the one-thing test.** `emailClients` that looks up, filters, *and* emails fails it.
- **Think of an argument count as a test-case multiplier.** Four booleans is sixteen paths nobody will write tests for.
- **Think of a boolean parameter as two functions wearing a trench coat.** Split them and both get a real name.
- **Use `switch (this.type)` as a "write the subclasses" signal.** The branch *is* the missing polymorphism.
- **Think of duplication as a restaurant inventory list.** One list, one place to update; multiple lists and every dish served means updating all of them.
- **Prefer a bad duplicate to a bad abstraction.** The guide says it outright: "Bad abstractions can be worse than duplicate code, so be careful!"

## Anti-patterns
- **Four positional arguments** (`createMenu("Foo", "Bar", "Baz", true)`): unreadable at the call site, combinatorially untestable.
- **`if (temp) {...} else {...}` behind a flag param**: two behaviors under one name.
- **Mutating a global** (`let name; function splitIntoFirstAndLastName() { name = name.split(" "); }`): a second consumer of `name` now breaks when the type changes under it.
- **Mutating an argument** (`cart.push({ item, date })`): the guide's retry-purchase bug — a retried network request ships an item the user accidentally added mid-flight.
- **Patching built-ins** (`Array.prototype.diff = ...`): collides with any library doing the same, and the failure appears in *your user's* production.
- **Accumulator loop for a sum**: `for (let i = 0; ...) totalOutput += ...` where `reduce` says it in one expression.
- **Naked compound conditions**: `if (fsm.state === "fetching" && isEmpty(listNode))` — the reader reverse-engineers the intent.
- **Double negatives**: `if (!isDOMNodeNotPresent(node))`.
- **`instanceof` chains**: `if (vehicle instanceof Bicycle) ... else if (vehicle instanceof Car)`.
- **Hand-rolled `typeof` guards on primitives**: verbose, incomplete, and a worse deal than adopting TypeScript.
- **Micro-optimizing loop bounds**: `for (let i = 0, len = list.length; i < len; i++)` — solved by the engine years ago.
- **Keeping `oldRequestModule` around**: nothing calls it; delete it.

## Code Examples
The root rule — do one thing:

```javascript
// Bad
function emailClients(clients) {
  clients.forEach(client => {
    const clientRecord = database.lookup(client);
    if (clientRecord.isActive()) {
      email(client);
    }
  });
}

// Good
function emailActiveClients(clients) {
  clients.filter(isActiveClient).forEach(email);
}

function isActiveClient(client) {
  const clientRecord = database.lookup(client);
  return clientRecord.isActive();
}
```
- **What it demonstrates**: extracting the predicate makes the intent (`filter` then `email`) readable in one line, makes `isActiveClient` independently testable, and renames the function to match what it now does.

Argument consolidation via signature destructuring:

```javascript
// Bad
function createMenu(title, body, buttonText, cancellable) {}
createMenu("Foo", "Bar", "Baz", true);

// Good
function createMenu({ title, body, buttonText, cancellable }) {}
createMenu({
  title: "Foo",
  body: "Bar",
  buttonText: "Baz",
  cancellable: true
});
```
- **What it demonstrates**: the call site becomes self-documenting; `true` is no longer a mystery in position four.

Don't mutate arguments:

```javascript
// Bad
const addItemToCart = (cart, item) => {
  cart.push({ item, date: Date.now() });
};

// Good
const addItemToCart = (cart, item) => {
  return [...cart, { item, date: Date.now() }];
};
```
- **What it demonstrates**: the spread returns a new array, so an in-flight `purchase(cart)` retry keeps the cart it was given.

Polymorphism instead of a type switch:

```javascript
// Bad
class Airplane {
  getCruisingAltitude() {
    switch (this.type) {
      case "777": return this.getMaxAltitude() - this.getPassengerCount();
      case "Air Force One": return this.getMaxAltitude();
      case "Cessna": return this.getMaxAltitude() - this.getFuelExpenditure();
    }
  }
}

// Good
class Airplane {}
class Boeing777 extends Airplane {
  getCruisingAltitude() { return this.getMaxAltitude() - this.getPassengerCount(); }
}
class AirForceOne extends Airplane {
  getCruisingAltitude() { return this.getMaxAltitude(); }
}
class Cessna extends Airplane {
  getCruisingAltitude() { return this.getMaxAltitude() - this.getFuelExpenditure(); }
}
```
- **What it demonstrates**: adding a fourth aircraft now adds a class instead of editing a shared `switch` — the Open/Closed Principle (Ch 6) falling out of the one-thing rule.

## Reference Tables

Argument count guidance:

| Count | Verdict |
|---|---|
| 0–1 | Ideal |
| 2 | Ideal |
| 3 | Avoid if possible |
| 4+ | Consolidate into an object — the function is probably doing too much |

What signature destructuring buys you:

| Benefit | Detail |
|---|---|
| Visible contract | Properties used are clear from the signature alone |
| Named parameters | Simulates them in a language that lacks them |
| Partial side-effect protection | Clones destructured **primitives**; **objects/arrays are NOT cloned** |
| Lint support | Linters can flag unused properties |

Conditional-removal ladder:

| Smell | Fix | Rule |
|---|---|---|
| Compound `if` | Extract a named predicate | Encapsulate conditionals |
| `!isNotX(...)` | Invert to positive predicate | Avoid negative conditionals |
| `switch (this.type)` | Subclass per case | Avoid conditionals |
| `instanceof` chain | Consistent API (`.move()`) | Avoid type-checking (1) |
| `typeof` guards on primitives | Adopt TypeScript | Avoid type-checking (2) |

## Worked Example
**Avoid Side Effects (part 2)** — the shopping-cart bug, walked end to end, because it is the chapter's most concrete failure scenario.

The code:

```javascript
const addItemToCart = (cart, item) => {
  cart.push({ item, date: Date.now() });
};
```

The sequence that breaks it:

1. User clicks **Purchase**. `purchase(cart)` fires a network request carrying the `cart` array.
2. The connection is bad, so `purchase` has to **retry**.
3. Before the retry goes out, the user accidentally clicks **Add to Cart** on an item they don't want.
4. `addItemToCart` mutates the *same array object* `purchase` is holding.
5. The retry sends the mutated cart. **The user is charged for the accidental item.**

Nothing in `purchase` is wrong. The defect is that `addItemToCart` reached into shared state through a reference.

The fix:

```javascript
const addItemToCart = (cart, item) => {
  return [...cart, { item, date: Date.now() }];
};
```

Now step 4 produces a *new* array. The array `purchase` captured is frozen in time, and the retry sends exactly what the user confirmed.

**The two caveats the guide attaches**, so you apply this with judgment rather than reflex:

1. Sometimes you genuinely want to modify the input — but "when you adopt this programming practice you will find that those cases are pretty rare."
2. Cloning big objects is expensive — in practice not a problem, because libraries like Immutable.js make structural sharing fast and memory-cheap compared to manual cloning.

## Key Takeaways
1. **Do one thing.** It is the most important rule here; every other rule in the chapter is a detector for violating it.
2. Keep arguments at **two or fewer**; consolidate the rest into a destructured object.
3. A **boolean flag parameter** always means two functions — split them.
4. Never mutate arguments; return new objects/arrays. Centralize the side effects you genuinely need into **one** service each.
5. Never patch built-in prototypes; `extends` the global instead.
6. Replace conditionals in order: encapsulate → positivize → polymorphize → consistent API → TypeScript.
7. Remove duplication — but only behind a *good* abstraction, since a bad one is worse than the duplication.
8. Delete dead code and skip micro-optimizations; git remembers, and the engine optimizes.

## Connects To
- **Ch 2 (Variables)**: destructuring and naming discipline carry straight into signatures and extracted predicates.
- **Ch 6 (SOLID)**: the guide explicitly routes "Remove duplicate code" through SOLID for getting the abstraction right; "Avoid conditionals" is OCP, and type-checking removal is LSP/DIP in practice.
- **Ch 5 (Classes)**: "prefer small functions over classes until you find yourself needing larger and more complex objects."
- **Ch 7 (Testing)**: the argument-count rule exists because of testability; single-concept tests are the payoff.
- **Ch 9 (Error Handling)**: centralized side effects give you one place to report errors from.
- **clean-code-typescript**: "avoid type-checking (part 2)" is an explicit hand-off to the TypeScript sibling skill.
