# Chapter 3: Functions

## Core Idea
**"Functions should do one thing" is by far the most important rule in software engineering** —
and almost every other rule in this chapter (few arguments, no flags, one level of abstraction,
no side effects, no conditionals) is a *tell* that a function is doing more than one.

## Frameworks Introduced
- **The argument budget: 2 or fewer ideally, 3 avoided, more consolidated.**
  - When to use: on every signature you write.
  - How: more than two → pass a **destructured options object** with a `type` alias. The stated
    reason is testing: each extra argument multiplies the case matrix combinatorially.
  - Why destructuring specifically, per the source: (1) the signature shows which properties are
    used; (2) it simulates **named parameters**; (3) it **clones the specified primitive values**,
    preventing some side effects — *note: destructured objects and arrays are NOT cloned*;
    (4) TypeScript warns about unused properties, which is impossible without it.
- **Functions should do one thing** — *"If you take nothing else away from this guide other than
  this, you'll be ahead of many developers."*
  - When to use: always; verify with the tells below.
  - How: extract until each function has one reason to be read.
- **One level of abstraction per function.**
  - When to use: when a function mixes orchestration with mechanics (splitting strings *and*
    lexing *and* parsing).
  - How: the body should read as a list of named steps at the same altitude — `tokenize(code)`
    then `parse(tokens)` — with the mechanics one level down.
- **Avoid Side Effects (two parts)**:
  - *Part 1 — global/shared state*: a function that does anything besides take values and
    return values has a side effect. You will need some; **centralize them in one service,
    "one and only one."**
  - *Part 2 — mutable parameters*: objects and arrays are mutable, so a function that edits its
    argument affects every other holder of it. **Clone, edit, return the clone.**
  - Two stated caveats: sometimes you *do* want to mutate the input (rare in practice), and
    cloning big objects costs performance (use a library like `immutable-js`).
- **The polymorphism substitution for conditionals**: a `switch` on a type field is a function
  doing more than one thing; replace it with subclasses overriding one method.
- **Avoid type checking**: in TypeScript, `instanceof` chains are a type-system failure, not a
  control-flow need. Use a union type with a common operation.

## Key Concepts
- **Combinatorial explosion** — the test-case blowup from many parameters; the stated reason for
  the argument budget.
- **Options object** — a single object parameter, named via a `type` alias, destructured in the
  signature.
- **Flag argument** — a boolean parameter that selects a code path; proof the function does two
  things.
- **Pure function** — takes values in, returns values out, touches nothing else.
- **Dead code** — unreachable or uncalled code. *"Just as bad as duplicate code"*; version
  history already remembers it.
- **Encapsulated conditional** — a boolean expression given a name by extracting it into a
  predicate function.
- **Negative conditional** — `isEmailNotUsed(email)`; prefer the positive `!isEmailUsed(email)`.
- **Generator / iterable** — `function*` + `yield`, consumed with `for-of`; lazy, on-demand
  streams.

## Mental Models
- **Treat every one of these as a smell detector for "does more than one thing":** 3+ arguments,
  a boolean parameter, an `if`/`switch` on a type, two altitudes of code in one body, a
  mutation of an argument. They are the same defect wearing different clothes.
- **Think of a flag argument as two functions that got merged.** `createFile(name, temp)` is
  `createFile` and `createTempFile`; the `if` is the seam.
- **Prefer functional pipelines to loops** — `filter`/`map`/`reduce` over `for`. The one-thing
  rule falls out of it: `clients.filter(isActiveClient).forEach(email)` names its two steps.
- **Use a generator when the consumer should decide how much to take.** The stated benefits:
  decoupling the callee from the implementation, lazy on-demand execution, native `for-of`
  support, and room for optimized iterator patterns. An infinite stream becomes expressible.
- **Don't over-optimize.** Modern engines optimize at runtime; caching `list.length` is wasted
  effort on current browsers.
- **Never write to globals.** Extending `Array.prototype` clashes silently with other libraries
  and the API consumer "would be none-the-wiser until they get an exception in production."
  Subclass (`class MyArray<T> extends Array<T>`) instead.

## Code Examples

One thing — the canonical extraction:

```ts
// Bad — filters AND emails in one body.
function emailActiveClients(clients: Client[]) {
  clients.forEach((client) => {
    const clientRecord = database.lookup(client);
    if (clientRecord.isActive()) { email(client); }
  });
}

// Good — two named things, composed.
function emailActiveClients(clients: Client[]) {
  clients.filter(isActiveClient).forEach(email);
}

function isActiveClient(client: Client) {
  const clientRecord = database.lookup(client);
  return clientRecord.isActive();
}
```

Avoid type checking — the TypeScript-specific version of "avoid conditionals":

```ts
// Bad — instanceof chain; adding a Vehicle means editing this function.
function travelToTexas(vehicle: Bicycle | Car) {
  if (vehicle instanceof Bicycle) { vehicle.pedal(currentLocation, new Location('texas')); }
  else if (vehicle instanceof Car) { vehicle.drive(currentLocation, new Location('texas')); }
}

// Good — a union with one shared operation.
type Vehicle = Bicycle | Car;
function travelToTexas(vehicle: Vehicle) {
  vehicle.move(currentLocation, new Location('texas'));
}
```

Side effects, part 2 — clone rather than mutate:

```ts
// Bad — every other holder of `cart` sees this push.
function addItemToCart(cart: CartItem[], item: Item): void {
  cart.push({ item, date: Date.now() });
}

// Good — callers keep the cart they had.
function addItemToCart(cart: CartItem[], item: Item): CartItem[] {
  return [...cart, { item, date: Date.now() }];
}
```

Generators — an infinite stream the consumer bounds:

```ts
function* fibonacci(): IterableIterator<number> {
  let [a, b] = [0, 1];
  while (true) { yield a; [a, b] = [b, a + b]; }
}

function print(n: number) {
  let i = 0;
  for (const fib of fibonacci()) { if (i++ === n) break; console.log(fib); }
}
```
- **What it demonstrates**: the generator never builds the array, and `n` moves from the
  producer to the consumer.

## Reference Tables

Three ways to set defaults on an options object (all endorsed):

| Technique | Code | Note |
|---|---|---|
| `Object.assign` | `Object.assign({ title: 'Foo' }, config)` | **Sets** properties |
| Spread | `{ title: 'Foo', ...config }` | **Defines** new properties; subtly different from `assign` |
| Destructuring defaults | `function createMenu({ title = 'Foo' }: MenuConfig)` | Default visible in the signature |

Pair any of them with **`--strictNullChecks`** so an explicit `undefined`/`null` can't be passed in.

Smell → what it means → fix:

| Smell | Means | Fix |
|---|---|---|
| 3+ arguments | doing too much | options object, or split |
| boolean parameter | two functions merged | split (`createTempFile` / `createFile`) |
| `switch` on a type field | one function, many things | subclass + override |
| `instanceof` chain | type system underused | union type + shared method |
| mutates an argument | hidden coupling | clone, edit, return |
| two altitudes in one body | mixed abstraction | extract the mechanics |
| unnamed boolean expression | intent implicit | encapsulate as a predicate |

## Worked Example
**"Remove duplicate code" — including the exception, which is the part people miss.**

Two list renderers that differ in exactly one line:

```ts
function showDeveloperList(developers: Developer[]) {
  developers.forEach((developer) => {
    const expectedSalary = developer.calculateExpectedSalary();
    const experience = developer.getExperience();
    const githubLink = developer.getGithubLink();          // <- the only difference
    render({ expectedSalary, experience, githubLink });
  });
}

function showManagerList(managers: Manager[]) {
  managers.forEach((manager) => {
    const expectedSalary = manager.calculateExpectedSalary();
    const experience = manager.getExperience();
    const portfolio = manager.getMBAProjects();            // <- the only difference
    render({ expectedSalary, experience, portfolio });
  });
}
```

The source's own analogy: a restaurant keeping **multiple inventory lists** — serve one dish
with tomatoes and every list needs updating. One list, one place to update.

**The fix — push the difference behind a shared method, then unify:**

```ts
class Developer {
  getExtraDetails() { return { githubLink: this.githubLink }; }
}

class Manager {
  getExtraDetails() { return { portfolio: this.portfolio }; }
}

type Employee = Developer | Manager;    // or a common parent class

function showEmployeeList(employees: Employee[]) {
  employees.forEach((employee) => {
    render({
      expectedSalary: employee.calculateExpectedSalary(),
      experience: employee.getExperience(),
      extra: employee.getExtraDetails(),
    });
  });
}
```

**Why it works**: the varying part is now a polymorphic call, so the loop has one reason to
change (how employees render) instead of two.

**The stated failure mode — and it is explicit:** *"Bad abstractions can be worse than duplicate
code, so be careful!"* Getting the abstraction right is why the source sends you to
**[SOLID](#solid)** (ch06) before deduplicating. And the harder case:

> When two implementations **from two different modules** look similar but **live in different
> domains**, duplication might be acceptable and preferred over extracting the common code. The
> extracted common code introduces an **indirect dependency** between the two modules.

So the decision rule is not "is this duplicated" but **"do these two copies share a reason to
change?"** Same domain, one reason → extract. Different domains, coincidental resemblance →
leave both copies and accept the duplication; you are buying independence, not laziness.

## Key Takeaways
1. **Do one thing.** Everything else in this chapter is a detector for violations of it.
2. **≤2 arguments**; beyond that, a destructured options object with a `type` alias — the reason
   is combinatorial test explosion.
3. **No flag arguments** — split the function.
4. **One level of abstraction per body**; orchestration and mechanics never mix.
5. **Clone, don't mutate** arguments; centralize unavoidable side effects in one service.
6. **Deduplicate within a domain, tolerate duplication across domains** — bad abstractions are
   worse than duplication, and cross-module extraction creates indirect dependencies.
7. In TypeScript, replace `instanceof` chains with **union types**, and type-field `switch`es
   with **polymorphism**.
8. **Delete dead code** — git remembers it. **Don't over-optimize** — the engine already does.
9. Never extend built-in prototypes; **subclass** instead.
10. Use **generators** when the consumer should decide how much of a stream to take.

## Connects To
- **Ch 2 (Variables)**: destructuring-as-naming and default arguments are the same levers,
  applied to parameters.
- **Ch 4 (Objects and Data Structures)**: `readonly`/`Readonly<T>`/`as const` are the type-level
  enforcement of the immutability this chapter asks for by convention.
- **Ch 5 (Classes)**: the extraction habit here is what makes small, cohesive classes possible.
- **Ch 6 (SOLID)**: the source explicitly routes "getting the abstraction right" to SOLID; OCP
  is the principled version of "avoid conditionals", DIP of "avoid type checking".
- **Ch 8 (Concurrency)**: `async`/`await` is the same readability argument applied to callbacks.
- **`clean-code-java` ch03 (Functions)**: the harder thresholds this chapter leaves out —
  **hardly ever 20 lines, 2–4 the target, indent depth ≤ 2**, the TO-paragraph test, **Command
  Query Separation**, `try` as the first word of its function, and *"duplication may be the
  root of all evil in software."*
