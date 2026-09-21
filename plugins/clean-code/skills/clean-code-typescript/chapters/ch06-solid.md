# Chapter 6: SOLID

## Core Idea
The five principles, each with a TypeScript-native fix: **SRP** (one reason to change), **OCP**
(extend without modifying — use an abstract base, not `instanceof`), **LSP** (subtypes must be
substitutable — model siblings, not a forced is-a), **ISP** (no client depends on methods it
doesn't use — split fat interfaces), **DIP** (depend on abstractions — inject an `interface`).

## Frameworks Introduced

- **SRP — Single Responsibility Principle.** *"There should never be more than one reason for a
  class to change"* (quoted from *Clean Code*).
  - The stated cost of violating it: the class **won't be conceptually cohesive**, and if too
    much functionality is in one class, modifying a piece of it makes it **difficult to
    understand how that will affect other dependent modules**.
  - How: extract the second responsibility into its own class and hold it as a field.
  - The source's own analogy: jam-packing a class is *"like when you can only take one suitcase
    on your flight."*

- **OCP — Open/Closed Principle.** Bertrand Meyer: *"software entities (classes, modules,
  functions, etc.) should be open for extension, but closed for modification."*
  - Restated plainly by the source: **allow users to add new functionality without changing
    existing code.**
  - When to use: the moment you write `if (x instanceof A) ... else if (x instanceof B)` inside
    a class that will grow.
  - How: declare an `abstract` method on the base, let each subclass implement it, and have the
    consumer call the abstract method. Adding a third adapter now touches **zero** existing code.

- **LSP — Liskov Substitution Principle.** Formally: *"If S is a subtype of T, then objects of
  type T may be replaced with objects of type S without altering any of the desirable properties
  of that program (correctness, task performed, etc.)."*
  - The source's own translation: **a parent class and child class can be used interchangeably
    without getting incorrect results.**
  - How to detect a violation: a subclass overrides a setter/method to maintain its own
    invariant, and a caller written against the parent now gets a wrong answer.
  - The fix pattern: **stop forcing the is-a.** Give both an abstract sibling parent with the
    *behavior* they truly share, and let each hold its own shape.

- **ISP — Interface Segregation Principle.** *"Clients should not be forced to depend upon
  interfaces that they do not use."* The source notes it is **very much related to SRP**.
  - What it really means, per the source: design abstractions so clients using the exposed
    methods **do not get the whole pie**, and are not burdened with **implementing methods they
    don't actually need**.
  - The tell: an implementer that `throw new Error('Fax not supported.')`.
  - How: split the fat interface into role interfaces; classes `implement` the ones they honour.

- **DIP — Dependency Inversion Principle.** Two statements:
  1. **High-level modules should not depend on low-level modules. Both should depend on
     abstractions.**
  2. **Abstractions should not depend upon details. Details should depend on abstractions.**
  - What it buys, per the source: it **reduces coupling between modules** — and *"coupling is a
    very bad development pattern because it makes your code hard to refactor."*
  - DIP keeps high-level modules from knowing the details of low-level modules **and from
    setting them up**; it accomplishes this through **DI** (Dependency Injection). The source is
    careful: **DIP and DI are not identical concepts.** Angular's DI is cited as a familiar
    implementation.
  - DIP is usually achieved with an **IoC container**; the named TypeScript example is
    **InversifyJS**.
  - How: define an `interface` for the capability, have the consumer take it in its constructor,
    and let callers choose the implementation.

## Key Concepts
- **Conceptual cohesion** — whether a class's contents belong to one idea; what SRP protects.
- **Open for extension, closed for modification** — new behavior arrives as new code, not edits.
- **Substitutability** — the property LSP names: swapping in a subtype changes nothing a caller
  depends on.
- **Square–Rectangle problem** — the classic LSP violation: mathematically a square *is* a
  rectangle, but modelling it by inheritance breaks callers.
- **Role interface** — a small interface named for one capability (`Printer`, `Fax`, `Scanner`).
- **Fat interface** — one interface bundling capabilities not every implementer has.
- **Abstraction** — here, a TypeScript `interface` or `abstract class` both modules depend on.
- **Dependency Injection (DI)** — supplying a dependency from outside, usually via constructor.
- **Inversion of Control (IoC) container** — infrastructure that wires implementations to
  abstractions (e.g. InversifyJS).

## Mental Models
- **Read `instanceof` inside a class as "OCP violation here."** In `HttpRequester.fetch`, each
  new adapter forces an edit to a class that has nothing to do with adapters.
- **LSP is about callers, not taxonomies.** The question is never "is a square a rectangle?" but
  **"will code written against `Rectangle` still be right if handed a `Square`?"** In the bad
  example it isn't: `.setWidth(4).setHeight(5).getArea()` returns **25 for Square, should be 20**.
- **`throw new Error('Not supported')` is ISP's smoking gun.** An implementer apologizing for a
  method it was forced to have means the interface was too fat.
- **DIP inverts *who owns the choice*.** `private readonly formatter = new XmlFormatter()` means
  `ReportReader` picked; `constructor(private readonly formatter: Formatter)` means the caller
  picks — and suddenly the same reader handles JSON with no edit.
- **ISP and SRP are the same instinct at two altitudes** — one splits interfaces, the other
  splits classes.
- **Notice the LSP fix changes the hierarchy, not the method.** You don't patch `Square`; you
  introduce `abstract class Shape` and make `Rectangle` and `Square` siblings.

## Code Examples

**OCP** — abstract method replaces the `instanceof` chain:

```ts
// Bad — every new adapter edits HttpRequester.
class HttpRequester {
  constructor(private readonly adapter: Adapter) {}
  async fetch<T>(url: string): Promise<T> {
    if (this.adapter instanceof AjaxAdapter) { const response = await makeAjaxCall<T>(url); }
    else if (this.adapter instanceof NodeAdapter) { const response = await makeHttpCall<T>(url); }
  }
}

// Good — the base declares the contract; HttpRequester never changes again.
abstract class Adapter {
  abstract request<T>(url: string): Promise<T>;   // source writes `abstract async` — see note
  // code shared to subclasses ...
}

class AjaxAdapter extends Adapter {
  async request<T>(url: string): Promise<T> { /* request and return promise */ }
}

class NodeAdapter extends Adapter {
  async request<T>(url: string): Promise<T> { /* request and return promise */ }
}

class HttpRequester {
  constructor(private readonly adapter: Adapter) {}
  async fetch<T>(url: string): Promise<T> {
    const response = await this.adapter.request<T>(url);
    // transform response and return
  }
}
```

> **Corrected from the source**: it writes `abstract async request<T>(...)`, which does not
> compile — *"'async' modifier cannot be used with 'abstract' modifier"* (TS1243). An abstract
> method has no body, so `async` is meaningless on it; the `Promise<T>` return type is what
> obliges implementers to be async. Implementations still use `async request<T>(...)`.

**ISP** — split the fat interface:

```ts
// Bad — EconomicPrinter must apologize for two methods.
interface SmartPrinter { print(); fax(); scan(); }

class EconomicPrinter implements SmartPrinter {
  print() { /* ... */ }
  fax() { throw new Error('Fax not supported.'); }
  scan() { throw new Error('Scan not supported.'); }
}

// Good — role interfaces; implement only what you honour.
interface Printer { print(); }
interface Fax { fax(); }
interface Scanner { scan(); }

class AllInOnePrinter implements Printer, Fax, Scanner {
  print() {} fax() {} scan() {}
}

class EconomicPrinter implements Printer {
  print() { /* ... */ }
}
```

**SRP** — extract the second reason to change:

```ts
// Bad — UserSettings both changes settings AND verifies credentials.
class UserSettings {
  constructor(private readonly user: User) {}
  changeSettings(settings: UserSettings) { if (this.verifyCredentials()) { /* ... */ } }
  verifyCredentials() { /* ... */ }
}

// Good
class UserAuth {
  constructor(private readonly user: User) {}
  verifyCredentials() { /* ... */ }
}

class UserSettings {
  private readonly auth: UserAuth;
  constructor(private readonly user: User) { this.auth = new UserAuth(user); }
  changeSettings(settings: UserSettings) { if (this.auth.verifyCredentials()) { /* ... */ } }
}
```

## Reference Tables

| Principle | One-line rule | TS tell that it's violated | TS fix |
|---|---|---|---|
| **SRP** | One reason to change | Class name needs "and" | Extract a class, hold as field |
| **OCP** | Extend, don't modify | `instanceof` chain in a consumer | `abstract` method + subclasses |
| **LSP** | Subtypes substitute cleanly | Override maintains a private invariant; callers get wrong results | Abstract sibling parent; make them peers |
| **ISP** | No unused dependencies | `throw new Error('… not supported')` | Split into role interfaces |
| **DIP** | Depend on abstractions | `new ConcreteThing()` inside a field initializer | `interface` + constructor injection |

## Worked Example
**DIP, walked end to end** — the one that pays back immediately and visibly.

**Before.** `ReportReader` reaches out and constructs its own formatter:

```ts
class XmlFormatter {
  parse<T>(content: string): T { /* Converts an XML string to an object T */ }
}

class ReportReader {
  // BAD: We have created a dependency on a specific request implementation.
  // We should just have ReportReader depend on a parse method: `parse`
  private readonly formatter = new XmlFormatter();

  async read(path: string): Promise<ReportData> {
    const text = await readFile(path, 'UTF8');
    return this.formatter.parse<ReportData>(text);
  }
}

const reader = new ReportReader();
const report = await reader.read('report.xml');
```

`ReportReader` is the **high-level** module (it knows *reading a report* is: load bytes, parse
them). `XmlFormatter` is the **low-level detail**. The high-level module depends on the detail
*and* decides which detail to use. Consequences: JSON support requires editing `ReportReader`;
a unit test cannot substitute a fake parser; `ReportReader` cannot be reused anywhere XML is
not the format.

**After.** Introduce the abstraction, and let the caller choose:

```ts
interface Formatter {
  parse<T>(content: string): T;
}

class XmlFormatter implements Formatter {
  parse<T>(content: string): T { /* Converts an XML string to an object T */ }
}

class JsonFormatter implements Formatter {
  parse<T>(content: string): T { /* Converts a JSON string to an object T */ }
}

class ReportReader {
  constructor(private readonly formatter: Formatter) {}

  async read(path: string): Promise<ReportData> {
    const text = await readFile(path, 'UTF8');
    return this.formatter.parse<ReportData>(text);
  }
}

const reader = new ReportReader(new XmlFormatter());
const report = await reader.read('report.xml');

// or if we had to read a json report
const reader = new ReportReader(new JsonFormatter());
const report = await reader.read('report.json');
```

**Both halves of the principle are now satisfied**: the high-level `ReportReader` and the
low-level `XmlFormatter` both depend on `Formatter` (statement 1), and `Formatter` — the
abstraction — is defined by what the *reader* needs, not by what XML parsing happens to offer
(statement 2). That second half is the one people skip: an interface extracted mechanically
from the concrete class is still an abstraction depending on a detail.

**Why it works**: `JsonFormatter` was added without touching `ReportReader` — which is OCP
falling out of DIP for free. At scale, an **IoC container** (InversifyJS) does the wiring so
call sites don't hand-assemble graphs.

**Failure mode**: DIP is not "add an interface for everything." Each abstraction is a layer of
indirection to read through. Invert where the detail is genuinely likely to vary — formats,
transports, storage, clocks — not where there will only ever be one implementation.

## Key Takeaways
1. **SRP**: one reason to change. Extract the second responsibility; hold it as a field.
2. **OCP**: an `instanceof` chain in a consumer is the violation; an `abstract` method is the fix.
   New subclasses should require **zero** edits to existing code.
3. **LSP**: ask *"is code written against the parent still correct?"* — Square/Rectangle returns
   **25 instead of 20**. Fix the hierarchy (abstract sibling parent), not the override.
4. **ISP**: `throw new Error('… not supported')` means the interface is too fat. Split into role
   interfaces and `implements` several.
5. **DIP**: depend on an `interface`, inject via constructor, let the caller choose. Both the
   high-level module *and* the detail depend on the abstraction — and the abstraction is shaped
   by the consumer's need.
6. **DIP ≠ DI.** DI is the usual mechanism; an IoC container (InversifyJS) is the usual tooling.
7. The source routes **"getting the abstraction right"** (ch03's duplication rule) through these
   five principles — they are the prerequisite for safe deduplication.

## Connects To
- **Ch 3 (Functions)**: "Avoid conditionals" and "Avoid type checking" are OCP and DIP stated as
  local tactics; ch03 explicitly sends you here for the principled version.
- **Ch 5 (Classes)**: SRP appears there as a *sizing* rule (responsibility, not lines); ISP is
  the interface-level echo of its cohesion argument.
- **Ch 4 (Objects and Data Structures)**: `interface` + `implements` is the tool ISP and DIP run
  on; `private readonly` parameter properties are how injection is written.
- **Ch 7 (Testing)**: DIP is what makes units testable in isolation — inject a fake `Formatter`.
- **`clean-code-java` ch10–ch11**: DIP and OCP in the original, plus **boundaries** (ch08) for
  wrapping third-party APIs and **systems** (ch11) for dependency injection at architecture
  scale. Note ch11 there is dated (EJB/Spring-XML specifics).
