# Chapter 7: SOLID — Single Responsibility, Open/Closed, Liskov Substitution

## Core Idea
The three SOLID principles the guide works through **class hierarchies**: give each class **one reason to change** (SRP), add behaviour by **adding a type rather than editing a dispatcher** (OCP), and make subtypes **substitutable without incorrect results** (LSP). Each Swift example removes a conditional or an override that lied about its contract.

## Frameworks Introduced
- **Single Responsibility Principle (SRP)**: "As stated in *Clean Code*, 'There should never be more than one reason for a class to change.'"
  - The suitcase image: "It's tempting to pack a class with many functionalities, like when you can only bring one suitcase on your flight."
  - Why: a class with many functions "will not be conceptually cohesive", and when you change a portion of it, "it can be difficult to understand how it will affect other modules that depend on it."
  - How: move the second responsibility to its own class and hold it as a property — `UserSettings` keeps settings; `UserAuth` owns the check of the user's identity.
- **Open/Closed Principle (OCP)**: "As stated by Bertrand Meyer, 'Software entities (classes, modules, functions, etc.) should be open for extension but closed for modification.'" — "you should allow users to add new functionalities without changing existing code."
  - How: give every adapter the same method (`request(url:)`) and have `HttpRequester` call it, instead of switching on `adapter.name`. A new adapter is a new type; `HttpRequester` never changes.
- **Liskov Substitution Principle (LSP)**: formally, "If S is a subtype of T, then objects of type T may be replaced with objects of type S… without altering any of the desirable properties of a program." Plainly: "if you have a parent class and a child class, then the base class and the child class can be used interchangeably without getting incorrect results."
  - The classic case: Square/Rectangle. "Mathematically, a square is a rectangle, but if you model it using an 'is-a' relationship through inheritance, you quickly run into problems."
  - How: don't make `Square` override `Rectangle`'s setters; make both siblings under `Shape`, each constructed with its own dimensions.

## Key Concepts
- **Reason to change** — an external force that would require editing the class; SRP's unit.
- **Conceptual cohesion** — everything in a class serves one purpose.
- **Open for extension** — new behaviour arrives as a new type.
- **Closed for modification** — existing, tested code isn't edited to add it.
- **Adapter** — a type wrapping one way of making a request behind a common method (`SwiftAdapter`, `ObjcAdapter`).
- **String dispatch** — choosing behaviour by comparing a name string (`adapter.name == "SwiftAdapter"`).
- **Substitutability** — a subtype can stand in for its base type without incorrect results.
- **Square/Rectangle problem** — a subclass that keeps the base's setters but changes what they mean.

## Mental Models
- **SRP: name the reasons to change.** Settings layout changes and identity-check changes come from different people for different reasons; that's two classes.
- **OCP: a `switch` or `if` chain on a type name is a list you'll keep editing.** Every new case means opening the dispatcher. Polymorphic dispatch moves the list into the type system.
- **OCP: string dispatch fails late.** In the guide's Bad example the adapter is named `"ObjcAdapter"` but the check compares against `"httpObjcAdapter"` — so that branch can never match, and the call falls through to `fatalError("Adapter not supported")` at runtime. A method call on the adapter can't be misspelled past the compiler.
- **LSP: test the subtype through the base type's caller.** Write the function against `Rectangle`, pass a `Square`, and check the result. If the answer is wrong, the hierarchy is.
- **LSP: remove the setter, remove the problem.** The Good version sets dimensions once in `init`; with no setters, no override can break the area invariant.

## Code Examples
SRP — the identity check moves out of settings:

```swift
class UserAuth {
  var user: User

  init(user: User) {
    self.user = user
  }

  func verifyCredentials() -> Bool {
    // ...
  }
}

class UserSettings {
  var user: User
  var auth: UserAuth

  init(user: User) {
    self.user = user
    self.auth = UserAuth(user: user)
  }

  func changeSettings(settings: Settings) {
    if self.auth.verifyCredentials() {
      // ...
    }
  }
}
```

OCP — one method per adapter, no dispatcher:

```swift
class SwiftAdapter: Adapter {
  override init() {
    super.init()
    self.name = "SwiftAdapter"
  }

  func request(url: String) -> Promise<Response> {
    // make the request and return the promise
  }
}

class HttpRequester {
  var adapter: Adapter

  init(adapter: Adapter) {
    self.adapter = adapter
  }

  func fetch(url: String) -> Promise<Response> {
    return self.adapter.request(url: url).then { response in
      // transform the response and return
    }
  }
}
```

(`ObjcAdapter` mirrors `SwiftAdapter`.)

## Reference Tables

| Principle | Bad shape in the guide | Good shape |
|---|---|---|
| SRP | `UserSettings` changes settings *and* verifies the user | `UserAuth` + `UserSettings` holding it |
| OCP | `HttpRequester.fetch` branches on `adapter.name` strings | each adapter implements `request(url:)` |
| LSP | `Square: Rectangle` overrides `setWidth`/`setHeight` | `Rectangle` and `Square` both subclass `Shape`, dimensions set in `init` |

## Worked Example
Square/Rectangle, end to end.

**Bad** — `Square` inherits `Rectangle`'s setters and keeps its sides equal:

```swift
class Rectangle {
  var width: Double
  var height: Double

  init() {
    self.width = 0
    self.height = 0
  }

  func render(area: Double) {
    // ...
  }

  func setWidth(width: Double) {
    self.width = width
  }

  func setHeight(height: Double) {
    self.height = height
  }

  func getArea() -> Double {
    return self.width * self.height
  }
}

class Square: Rectangle {
  override func setWidth(width: Double) {
    self.width = width
    self.height = width
  }

  override func setHeight(height: Double) {
    self.width = height
    self.height = height
  }
}

func renderLargeRectangles(rectangles: [Rectangle]) {
  rectangles.forEach { rectangle in
    rectangle.setWidth(width: 4)
    rectangle.setHeight(height: 5)
    let area = rectangle.getArea() // BAD: Returns 25 for the Square. Should be 20.
    rectangle.render(area: area)
  }
}

let rectangles: [Rectangle] = [Rectangle(), Rectangle(), Square()]
renderLargeRectangles(rectangles: rectangles)
```

`renderLargeRectangles` is correct for every `Rectangle`. Handed a `Square`, its second setter silently undoes the first, and the area comes out 25. The compiler accepts every line: the overrides match the base signatures exactly. Substitutability is a property of **behaviour**, not of signatures.

**Good** — siblings, not parent and child:

```swift
class Shape {
  func setColor(color: String) {
    // ...
  }

  func render(area: Double) {
    // ...
  }
}

class Rectangle: Shape {
  var width: Double
  var height: Double

  init(width: Double, height: Double) {
    self.width = width
    self.height = height
  }

  func getArea() -> Double {
    return self.width * self.height
  }
}

class Square: Shape {
  var length: Double

  init(length: Double) {
    self.length = length
  }

  func getArea() -> Double {
    return self.length * self.length
  }
}

func renderLargeShapes(shapes: [Shape]) {
  shapes.forEach { shape in
    let area = shape.getArea()
    shape.render(area: area)
  }
}
```

Two moves fix it. `Square` no longer claims to be a `Rectangle`, so no caller can expect independent sides. And dimensions are set once, in `init`, so there are no setters to override. **As written, this doesn't compile**: `Shape` declares no `getArea()`, so `shape.getArea()` has nothing to call. The example needs `getArea()` declared on `Shape` — as an overridable method or, more naturally in Swift, as a protocol requirement — which the guide leaves implicit.

## Source Caveats
- **OCP**: `Adapter` is never shown, and the Good version only compiles if `Adapter` declares `request(url:)` for the subclasses to `override`. `Promise<Response>` and `.then` are not Swift standard library types; they come from the JavaScript original (a third-party promise library would supply them). Ch 9's `async`/`await` is the native shape.
- **SRP**: `UserSettings` still builds its own `UserAuth` in `init`; Ch 8's DIP rule would inject it instead.
- **LSP**: see the Worked Example; the Good `Shape` lacks the `getArea()` it calls.

## Anti-patterns
- **One class, two reasons to change** (`UserSettings` with identity checks inside): edits to one concern risk the other.
- **Dispatch on a name string**: every new case edits the dispatcher, and a misspelling reaches `fatalError` at runtime.
- **Overriding a setter to enforce a subtype's invariant**: the Square/Rectangle trap — compiles, then gives wrong answers.
- **"Is-a" taken from mathematics rather than behaviour**: a square is a rectangle on paper, not under `setWidth`.

## Key Takeaways
1. **One reason to change per class**; extract the second responsibility and hold it as a property.
2. **Add types, don't edit dispatchers** — one method per adapter, called polymorphically.
3. **A `switch` on a type name is an OCP smell**, and a runtime-only one.
4. **Subtypes must give correct results through the base type's callers.** Check behaviour, not just signatures.
5. **Prefer immutable construction** (`init(width:height:)`) to overridable setters.
6. **Declare what callers call**: a base type or protocol must expose every method used through it.

## Connects To
- **Ch 3**: SRP is "do one thing" for classes.
- **Ch 4**: OCP is "avoid conditionals" for dispatchers; the `Airplane` example is the same refactor.
- **Ch 6**: Square/Rectangle is what the "is-a" test in composition-over-inheritance guards against.
- **Ch 8**: ISP and DIP move from base classes to protocols, the abstraction that would make the OCP and LSP examples compile.
- **`clean-code-java`** (ch10, Classes): SRP, OCP and DIP in the book's own terms.
