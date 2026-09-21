# Chapter 4: Objects and Data Structures

## Core Idea
TypeScript gives you real tools to **encapsulate** (accessors, `private`/`protected`) and to
**forbid mutation at the type level** (`readonly`, `Readonly<T>`, `ReadonlyArray<T>`,
`as const`) — use them instead of relying on convention, and pick `type` vs `interface` by
which capability you actually need.

## Frameworks Introduced
- **Accessors over bare properties** — five stated reasons to reach for `get`/`set`:
  1. You can do more than get a property without changing every accessor in the codebase.
  2. Adding **validation** on `set` becomes simple.
  3. It **encapsulates the internal representation**.
  4. Logging and error handling on get/set become easy to add.
  5. You can **lazy load** properties — e.g. fetch from a server on first access.
  - When to use: on objects that **encapsulate behavior** (not on plain data bags).
  - How: keep a `private` backing field with a distinct name (`accountBalance`) and expose
    `get balance()` / `set balance(value)`.
- **Default to the narrowest access modifier.** TypeScript has `public` *(the default)*,
  `protected`, and `private`.
  - How: the parameter-property shorthand does declaration, assignment and narrowing in one go:
    `constructor(private readonly radius: number) {}`.
- **The immutability ladder** — four levels, increasing strength:
  | Level | Tool | Forbids |
  |---|---|---|
  | Property | `readonly host: string` | reassigning that property |
  | Whole type | `Readonly<T>` (mapped type) | reassigning any property |
  | Array | `ReadonlyArray<number>` / `readonly string[]` | `push()`, `fill()`; allows `concat()`, `slice()` |
  | Literal | `as const` | any mutation of the object/array/returned literal |
  - When to use: start at `readonly` on every field you don't intend to change; escalate when a
    whole shape or a returned literal must be frozen.
- **`type` vs `interface` — the capability rule**: *use `type` when you might need a **union or
  intersection**; use `interface` when you want **`extends` or `implements`***.
  - The source is explicit that **there is no strict rule** — "use the one that works for you."
  - How: `type Config = EmailConfig | DbConfig` (union → `type`);
    `interface Shape` with `class Circle implements Shape` (implemented → `interface`).

## Key Concepts
- **Getter/setter (accessor)** — `get x()` / `set x(v)` members that look like properties at the
  call site but run code.
- **Parameter property** — an access modifier on a constructor parameter, which declares and
  assigns the field in one line.
- **Mapped type** — a type that transforms each property of another; `Readonly<T>` is the
  built-in one that marks all properties `readonly`.
- **`ReadonlyArray<T>`** — an array type without mutating methods; the non-mutating ones
  (`concat`, `slice`) remain. Since TS 3.4 also written `readonly string[]`.
- **Const assertion (`as const`)** — freezes a literal's type and makes it deeply readonly,
  including values **returned** from a function.
- **Union type** — `A | B`; only `type` can express it.
- **Intersection type** — `A & B`; only `type` can express it.
- **Compile-time vs runtime immutability** — every tool here is erased at runtime; it stops
  *your code* from mutating, not a determined caller.

## Mental Models
- **Think of `readonly` as the type-level enforcement of ch03's "avoid side effects."** Ch03
  asked you to clone instead of mutate by convention; this chapter makes the compiler check it.
- **Use accessors when the object has behavior; skip them when it's a data structure.** The
  `BankAccount` example earns its setter because it has a rule to enforce (no negative
  balance). A plain `type Config` has no behavior, so accessors would be ceremony.
- **The validation argument is the strongest one.** *"If one day the specifications change, and
  we need extra validation rule, we would have to alter only the `setter` implementation,
  leaving all dependent code unchanged."* That is the whole case for encapsulation in one
  sentence.
- **Reach for `as const` on returned literals specifically.** A function returning `{ value }`
  hands the caller a *writable* object — `result.value = 200` silently succeeds. `return { value }
  as const` closes that hole, and it's the case people forget.
- **Pick `type` vs `interface` by capability, then stop arguing.** The source refuses to pick a
  winner; treat it as a team convention decision, not a correctness one.

## Code Examples

Accessors that earn their keep — validation in one place:

```ts
// Bad — the rule lives at the call site, so every caller must remember it.
type BankAccount = { balance: number; }
const account: BankAccount = { balance: 0 };
if (value < 0) { throw new Error('Cannot set negative balance.'); }
account.balance = value;

// Good — BankAccount encapsulates the validation logic.
class BankAccount {
  private accountBalance: number = 0;

  get balance(): number { return this.accountBalance; }

  set balance(value: number) {
    if (value < 0) { throw new Error('Cannot set negative balance.'); }
    this.accountBalance = value;
  }
}

const account = new BankAccount();
account.balance = 100;   // call site unchanged, rule now unskippable
```

Private members via parameter properties:

```ts
// Bad — public field + redundant constructor body.
class Circle {
  radius: number;
  constructor(radius: number) { this.radius = radius; }
  perimeter() { return 2 * Math.PI * this.radius; }
}

// Good — declared, assigned, and locked down in one line.
class Circle {
  constructor(private readonly radius: number) {}
  perimeter() { return 2 * Math.PI * this.radius; }
  surface() { return Math.PI * this.radius * this.radius; }
}
```

`type` vs `interface` by capability:

```ts
// type — because Config is a UNION
type EmailConfig = { /* ... */ }
type DbConfig    = { /* ... */ }
type Config      = EmailConfig | DbConfig;

// interface — because Shape is IMPLEMENTED
interface Shape { /* ... */ }
class Circle implements Shape { /* ... */ }
class Square implements Shape { /* ... */ }
```

## Reference Tables

| Need | Use |
|---|---|
| Union (`A \| B`) or intersection (`A & B`) | `type` |
| `extends` / `implements` by a class | `interface` |
| Freeze one property | `readonly prop: T` |
| Freeze every property of a shape | `Readonly<T>` |
| Array that can't `push`/`fill` | `ReadonlyArray<T>` or `readonly T[]` |
| Freeze a literal, incl. a returned one | `as const` |
| Validate / log / lazy-load on access | `get` / `set` |
| Hide from outside the class | `private` |
| Hide from outside the hierarchy | `protected` |

## Worked Example
**The immutability ladder, climbed on one value** — showing exactly what each rung buys, because
the rungs are easy to confuse.

**Rung 0 — nothing.** Everything mutates:

```ts
interface Config { host: string; port: string; db: string; }
const config: Config = { host: 'localhost', port: '5432', db: 'app' };
config.host = 'evil.example';   // fine. Nobody notices.
```

**Rung 1 — `readonly` per property.** Reassignment is now a compile error:

```ts
interface Config {
  readonly host: string;
  readonly port: string;
  readonly db: string;
}
config.host = 'evil.example';   // error
```

**Rung 2 — `ReadonlyArray<T>`.** Note the *pair* of errors, which is the point of the source's
example — the plain-array version only stops one of the two:

```ts
// Bad — reassignment errors, but the push SUCCEEDS.
const array: number[] = [1, 3, 5];
array = [];        // error
array.push(100);   // array will be updated  ← the real bug

// Good — both are errors.
const array: ReadonlyArray<number> = [1, 3, 5];
array = [];        // error
array.push(100);   // error
```

Since TS 3.4 the argument form is shorter: `function hoge(args: readonly string[])`.

**Rung 3 — `as const`, which is the rung that catches the leak.** `readonly` on a *declaration*
does nothing for a value a function *hands back*:

```ts
// Bad — a writable object is returned.
function readonlyData(value: number) { return { value }; }
const result = readonlyData(100);
result.value = 200;   // value is changed — silently

// Good
function readonlyData(value: number) { return { value } as const; }
const result = readonlyData(100);
result.value = 200;   // error
```

And the same for declared literals: `const config = { hello: 'world' } as const` makes
`config.hello = 'world'` an error; `const array = [1, 3, 5] as const` makes `array[0] = 10` one.

**Why it works**: each rung moves the guarantee outward — from "I won't reassign this binding"
to "this property is fixed" to "this collection can't grow" to "this value is frozen wherever it
travels." **Failure mode**: all four are erased at compile time. They protect your code from
itself; they are not a runtime freeze, and `JSON.parse` or an `any` cast walks straight through
them.

## Key Takeaways
1. Use **accessors on objects with behavior** — the payoff is that a new validation rule changes
   one setter and no callers.
2. Default to **`private readonly` parameter properties**; `public` is the default and is
   usually the wrong one.
3. Put **`readonly` on every field you don't intend to change**, and escalate to `Readonly<T>`
   for whole shapes.
4. `number[]` lets `push()` through even when the binding is `const` — use **`ReadonlyArray<T>`**
   when the contents must not change.
5. **`as const` is the one that protects returned literals**; plain `readonly` does not.
6. **`type` for unions/intersections, `interface` for `extends`/`implements`** — and the source
   says there's no strict rule beyond that.
7. All of it is **compile-time only**. No runtime guarantee.

## Connects To
- **Ch 3 (Functions)**: "Avoid Side Effects (part 2)" asked for clone-don't-mutate by
  convention; `readonly`/`as const` is the compiler enforcing it.
- **Ch 5 (Classes)**: `private readonly` constructor parameters are how the high-cohesion
  examples there inject their dependencies.
- **Ch 6 (SOLID)**: `interface` + `implements` is the mechanism behind ISP and DIP; the small
  `Printer`/`Fax`/`Scanner` split is this chapter's tooling put to principled use.
- **Ch 9 (Error Handling)**: the `Failable<R, E>` result type is a union — a direct application
  of the `type`-for-unions rule.
- **`clean-code-java` ch06 (Objects and Data Structures)**: the axis-of-change rule this chapter
  omits — **objects hide data and expose behavior; data structures do the opposite**; choose
  objects when new *types* arrive, procedures when new *operations* do; **never build a hybrid**,
  and don't auto-generate getters and setters. Also the **Law of Demeter** and train wrecks.
