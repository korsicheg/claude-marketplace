# Chapter 6: SOLID

## Core Idea
The five SOLID principles adapted to a language with **no interfaces and no static types** — in JavaScript the abstractions are *implicit contracts* established by duck typing, which makes SRP, OCP, LSP, ISP, and DIP conventions you uphold rather than rules a compiler enforces.

## Frameworks Introduced
- **Single Responsibility Principle (SRP)**: "There should never be more than one reason for a class to change" (*Clean Code*).
  - When to use: when a class accumulates unrelated capabilities.
  - How: split by *reason to change*, not by size. `UserSettings` doing both settings and credential verification → `UserAuth` + `UserSettings` that holds a `UserAuth`.
  - Why it matters: a class packed with functionality is not conceptually cohesive, and modifying one piece makes it hard to understand the effect on dependent modules. Minimize how often you must change a class.
- **Open/Closed Principle (OCP)**: Bertrand Meyer — "software entities (classes, modules, functions, etc.) should be open for extension, but closed for modification."
  - When to use: when adding a new variant means editing an existing `if`/`switch`.
  - How: let each variant implement the shared method; the consumer calls the method and never branches. Adding a third adapter adds a class, touching no existing code.
- **Liskov Substitution Principle (LSP)**: "If S is a subtype of T, then objects of type T may be replaced with objects of type S … without altering any of the desirable properties of that program (correctness, task performed, etc.)."
  - Plain reading the guide offers: a parent and child class must be usable **interchangeably without getting incorrect results**.
  - When to use: before every `extends`; especially when the subclass overrides a setter or invariant.
  - How: if the subclass must break a base-class invariant to be correct, it is not a subtype — give both a common parent instead (Square/Rectangle → both extend `Shape`).
- **Interface Segregation Principle (ISP)**: "Clients should not be forced to depend upon interfaces that they do not use."
  - JS caveat the guide states up front: JavaScript has no interfaces, "so this principle doesn't apply as strictly as others. However, it's important and relevant even with JavaScript's lack of type system." Interfaces are **implicit contracts because of duck typing**.
  - When to use: classes requiring large settings objects.
  - How: make rarely-needed settings optional (nest them under `options`) instead of demanding them — avoid the "**fat interface**".
- **Dependency Inversion Principle (DIP)**: two statements —
  1. High-level modules should not depend on low-level modules. **Both should depend on abstractions.**
  2. Abstractions should not depend upon details. **Details should depend on abstractions.**
  - When to use: whenever a class constructs its own collaborator with `new`.
  - How: inject the collaborator through the constructor. Related to Dependency Injection (DI) as seen in AngularJS — "while they are not identical concepts, DIP keeps high-level modules from knowing the details of its low-level modules and setting them up."
  - Why it matters: reduces coupling; "coupling is a very bad development pattern because it makes your code hard to refactor."

## Key Concepts
- **Reason to change** — the SRP unit of responsibility; two reasons means two classes.
- **Conceptual cohesion** — everything in the class belongs to the same idea.
- **Open for extension, closed for modification** — new behavior arrives as new code, not edits to working code.
- **Subtype substitutability** — a child can stand in for its parent without changing correctness.
- **Implicit contract** — in JS, the set of methods/properties one object expects another to expose; duck typing's stand-in for an interface.
- **Duck typing** — if it has `.request(url)`, it is a requester; no declaration needed.
- **Fat interface** — a required settings object demanding options most clients never use.
- **Dependency Injection (DI)** — constructing collaborators externally and passing them in; the usual mechanism for DIP.
- **Coupling** — a module's dependence on another's concrete details; the thing DIP reduces.

## Mental Models
- **Use "how many reasons could force me to edit this file?" as the SRP test.** Two answers, two classes.
- **Think of `if (adapter.name === ...)` as an OCP violation with a name tag.** The branch you must edit to add a variant is the modification OCP forbids.
- **Use "can I pass the child everywhere the parent goes?" for LSP.** Square/Rectangle fails because `setWidth(4); setHeight(5); getArea()` returns 25 instead of 20.
- **Think of JS interfaces as promises you make in prose.** Nothing checks that a requester has `requestItem` — your tests and reviews are the type system (Ch 3: "Keep your JavaScript clean, write good tests, and have good code reviews").
- **Think of `new` inside a constructor as hard-wiring.** It welds the high-level module to one concrete implementation.

## Anti-patterns
- **SRP**: `UserSettings` that both changes settings and verifies credentials — two reasons to change in one class.
- **OCP**: `HttpRequester.fetch` branching on `this.adapter.name === "ajaxAdapter"` — every new adapter edits this method.
- **LSP**: `class Square extends Rectangle` overriding `setWidth`/`setHeight` to keep sides equal, which breaks any code that sets them independently.
- **ISP**: `new DOMTraverser({ rootNode, animationModule() {} })` where `setup()` unconditionally calls `this.settings.animationModule.setup()` — "most of the time, we won't need to animate when traversing", yet every client must supply it.
- **DIP**: `InventoryTracker` constructing `new InventoryRequester()` in its own constructor — swapping HTTP for WebSockets now means editing the high-level class.
- **Treating ISP as inapplicable because "JS has no interfaces"**: the guide explicitly rejects this — duck typing makes the contracts implicit, not absent.

## Code Examples
OCP — push the variation into the variants:

```javascript
// Bad — adding an adapter means editing fetch()
class HttpRequester {
  constructor(adapter) { this.adapter = adapter; }
  fetch(url) {
    if (this.adapter.name === "ajaxAdapter") {
      return makeAjaxCall(url).then(response => { /* transform */ });
    } else if (this.adapter.name === "nodeAdapter") {
      return makeHttpCall(url).then(response => { /* transform */ });
    }
  }
}

// Good — each adapter owns request(); fetch() never branches
class AjaxAdapter extends Adapter {
  constructor() { super(); this.name = "ajaxAdapter"; }
  request(url) { /* request and return promise */ }
}

class NodeAdapter extends Adapter {
  constructor() { super(); this.name = "nodeAdapter"; }
  request(url) { /* request and return promise */ }
}

class HttpRequester {
  constructor(adapter) { this.adapter = adapter; }
  fetch(url) {
    return this.adapter.request(url).then(response => { /* transform */ });
  }
}
```
- **What it demonstrates**: the `if/else if` chain disappears into polymorphism — a third adapter is purely additive.

DIP — inject rather than construct:

```javascript
// Bad
class InventoryTracker {
  constructor(items) {
    this.items = items;
    // BAD: We have created a dependency on a specific request implementation.
    this.requester = new InventoryRequester();
  }
  requestItems() {
    this.items.forEach(item => { this.requester.requestItem(item); });
  }
}

// Good
class InventoryTracker {
  constructor(items, requester) {
    this.items = items;
    this.requester = requester;
  }
  requestItems() {
    this.items.forEach(item => { this.requester.requestItem(item); });
  }
}

// By constructing our dependencies externally and injecting them, we can easily
// substitute our request module for a fancy new one that uses WebSockets.
const inventoryTracker = new InventoryTracker(
  ["apples", "bananas"],
  new InventoryRequesterV2()
);
```
- **What it demonstrates**: the implicit contract is "any Request module for an `InventoryTracker` will have a `requestItems`/`requestItem` method" — `V1` (HTTP) and `V2` (WS) are interchangeable because they honor it, and nothing declares it but the code and its tests.

ISP — make the rare option optional:

```javascript
// Good — options are nested and checked, not demanded
class DOMTraverser {
  constructor(settings) {
    this.settings = settings;
    this.options = settings.options;
    this.setup();
  }
  setup() {
    this.rootNode = this.settings.rootNode;
    this.setupOptions();
  }
  setupOptions() {
    if (this.options.animationModule) { /* ... */ }
  }
  traverse() { /* ... */ }
}

const $ = new DOMTraverser({
  rootNode: document.getElementsByTagName("body"),
  options: { animationModule() {} }
});
```
- **What it demonstrates**: the required surface shrinks to `rootNode`; everything else moves behind an `options` bag that is checked before use.

## Reference Tables

SOLID in JavaScript — what changes without types:

| Principle | Statement | JS-specific twist | Mechanism |
|---|---|---|---|
| **SRP** | One reason to change per class | unchanged | Extract collaborator class |
| **OCP** | Open for extension, closed for modification | unchanged | Polymorphic method, no branching |
| **LSP** | Subtypes substitutable for base types | No compiler check — tests catch it | Common parent instead of false "is-a" |
| **ISP** | No forced dependence on unused interface | **No interfaces**; contracts implicit via duck typing | Optional `options` object, avoid fat interface |
| **DIP** | Depend on abstractions, not details | Abstraction = the methods an object exposes | Constructor injection (DI) |

Violation smells → fix:

| Smell | Principle | Fix |
|---|---|---|
| Class has two unrelated method groups | SRP | Split, hold one as a field |
| `if (x.name === "...")` before dispatch | OCP | Move behavior onto the variant |
| Subclass overrides setter to preserve an invariant | LSP | Sibling classes under a shared parent |
| Constructor demands options most callers don't use | ISP | Nest under `options`, guard with `if` |
| `new Collaborator()` inside a constructor | DIP | Take it as a constructor parameter |

## Worked Example
**LSP via Square/Rectangle** — the chapter's sharpest example, because the code is obviously correct until it isn't.

Mathematically a square *is* a rectangle, so `extends` looks right:

```javascript
class Square extends Rectangle {
  setWidth(width) {
    this.width = width;
    this.height = width;   // keep it square
  }
  setHeight(height) {
    this.width = height;
    this.height = height;
  }
}
```

Each override is individually reasonable — a square with unequal sides is not a square. Now a caller that only knows about rectangles:

```javascript
function renderLargeRectangles(rectangles) {
  rectangles.forEach(rectangle => {
    rectangle.setWidth(4);
    rectangle.setHeight(5);
    const area = rectangle.getArea(); // BAD: Returns 25 for Square. Should be 20.
    rectangle.render(area);
  });
}

const rectangles = [new Rectangle(), new Rectangle(), new Square()];
renderLargeRectangles(rectangles);
```

Trace the `Square`: `setWidth(4)` sets both to 4; `setHeight(5)` sets both to 5; `getArea()` returns **25**, not the 20 the function is entitled to expect. The substitution altered correctness — LSP violated. Note that no single line is buggy; the defect lives in the *relationship*.

The fix is to stop claiming the subtype relationship and give both a common parent, with each owning its own area:

```javascript
class Shape {
  setColor(color) { /* ... */ }
  render(area) { /* ... */ }
}

class Rectangle extends Shape {
  constructor(width, height) {
    super();
    this.width = width;
    this.height = height;
  }
  getArea() { return this.width * this.height; }
}

class Square extends Shape {
  constructor(length) {
    super();
    this.length = length;
  }
  getArea() { return this.length * this.length; }
}

function renderLargeShapes(shapes) {
  shapes.forEach(shape => {
    const area = shape.getArea();
    shape.render(area);
  });
}

const shapes = [new Rectangle(4, 5), new Rectangle(4, 5), new Square(5)];
renderLargeShapes(shapes);
```

**What actually changed:** dimensions move into constructors (no mutating setters to violate), each shape computes its own area, and `renderLargeShapes` drops to the one operation every shape genuinely shares. The polymorphic call `shape.getArea()` is also OCP — a `Circle` is now purely additive.

**The transferable rule:** when a subclass has to override a method to *preserve its own invariant*, that is the signal it is not a subtype. Move both to siblings under a shared parent.

## Key Takeaways
1. **SRP**: split by *reason to change*, not by line count — `UserAuth` out of `UserSettings`.
2. **OCP**: adding a variant should add a file, never edit a branch. A `name === ` check before dispatch is the violation.
3. **LSP**: if a subclass must break a base invariant to be correct, it isn't a subtype — use sibling classes under a shared parent.
4. **ISP**: JavaScript has no interfaces, but duck typing makes them implicit — don't force clients into fat settings objects; nest rare options and guard them.
5. **DIP**: never `new` your collaborators inside a constructor; inject them so `V1`→`V2` is a call-site change.
6. Every abstraction here is an **implicit contract** with nothing to enforce it — tests and code review are your type system.

## Connects To
- **Ch 3 (Functions)**: "Remove duplicate code" explicitly defers to SOLID for getting the abstraction right; "Avoid conditionals" and "Avoid type-checking" are OCP and LSP in function form.
- **Ch 5 (Classes)**: the three inheritance tests are the practical front end of LSP; DIP's injection is composition over inheritance applied.
- **Ch 7 (Testing)**: DIP makes collaborators substitutable, which is what makes units testable in isolation.
- **Ch 4 (Objects)**: encapsulated internals are the precondition for depending on contracts rather than shapes.
- **Bertrand Meyer** (OCP) and **Barbara Liskov** (LSP): the cited originators; SRP is quoted from *Clean Code*.
