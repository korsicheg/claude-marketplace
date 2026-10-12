# Chapter 6: SOLID

## Core Idea
The five SOLID principles, expressed with Dart's class tools: **`abstract class` as the interface**, **`extends` when a subtype reuses behaviour, `implements` when it only promises a contract**, **`@override`** on every override, and **constructor injection through a `required` named parameter typed as the abstraction**. The Dart-specific tell to remember: a class that implements an interface with `throw UnimplementedError()` is probably breaking Interface Segregation.

## Frameworks Introduced
- **Single Responsibility Principle (SRP)**: "There should never be more than one reason for a class to change" (the guide attributes it to *Clean Code*).
  - The suitcase image: "It's tempting to jam-pack a class with a lot of functionality, like when you can only take one suitcase on your flight."
  - Why: if too much is in one class, "it can be difficult to understand how that will affect other dependent modules in your codebase."
  - How: `UserSettings` that both changes settings and verifies credentials splits into `UserAuth` (`verifyCredentials()`) and `UserSettings`, which holds a `UserAuth` and calls `auth.verifyCredentials()`.
- **Open/Closed Principle (OCP)**: "software entities (classes, modules, functions, etc.) should be open for extension, but closed for modification" (Bertrand Meyer). In the guide's words, "you should allow users to add new functionalities without changing existing code."
  - How: replace a function that tests types (`if (shape is Circle) … else if (shape is Square)`) with an abstract method on the supertype — `abstract class Shape { double getArea(); }` — that each subtype overrides. A new shape is a new class; `getArea` callers never change.
- **Liskov Substitution Principle (LSP)**: "If S is a subtype of T, then objects of type T may be replaced with objects of type S … without altering any of the desirable properties of that program." The guide's plainer version: "if you have a parent class and a child class, then the base class and child class can be used interchangeably without getting incorrect results."
  - How: the classic Square–Rectangle case. "Mathematically, a square is a rectangle, but if you model it using the 'is-a' relationship via inheritance, you quickly get into trouble." Make them siblings under an abstract `Shape`.
- **Interface Segregation Principle (ISP)**: "Clients should not be forced to depend upon interfaces that they do not use." "You should always create more specific interfaces instead of creating just a generic interface."
  - **The Dart tell**: "if your class, that implements an interface, uses the famous `throw UnimplementedError()`, it is probably not respecting the principle." Because `implements` obliges a class to provide every member of the interface, a fat interface forces a stub.
  - How: split `Book { getNumberOfPages(); download(); }` into `Book` and `DownloadableBook`; `EBook implements Book, DownloadableBook`, `PhysicalBook implements Book`.
- **Dependency Inversion Principle (DIP)**: "1. High-level modules should not depend on low-level modules. Both should depend on abstractions. 2. Abstractions should not depend upon details. Details should depend on abstractions."
  - DI vs DIP: "While they are not identical concepts, DIP keeps high-level modules from knowing the details of its low-level modules and setting them up. It can accomplish this through DI."
  - Why: it reduces coupling, and "Coupling is a very bad development pattern because it makes your code hard to refactor."
  - How: `InventoryTracker` stops constructing `InventoryRequester()` in a field initializer and receives an `InventoryRequester` (now an `abstract class`) through `required this.requester`; `InventoryRequesterV1` and `V2` `implements` it.

## Key Concepts
- **`abstract class`** — a class that can't be instantiated and may declare methods without bodies (`double getArea();`); the guide's way to write an interface.
- **`extends`** — inherit implementation and type; used in the guide for OCP's shapes and LSP's rectangles.
- **`implements`** — take on a class's interface without its implementation; every member must then be provided. Used for ISP's books and DIP's requesters.
- **`@override`** — annotation marking a member that overrides or implements a supertype member; the Good examples put it on every one.
- **`UnimplementedError`** — the error a stub throws; the guide's ISP smell.
- **Type test (`is`)** — `shape is Circle`; a chain of them in a function is the OCP Bad shape.
- **Constructor injection** — supplying a collaborator through the constructor (`required this.requester`) instead of building it inside the class.
- **Initializer list** — `: auth = UserAuth(user: user)` in the SRP example; builds a field from constructor parameters before the body runs.
- **Coupling** — how much one module knows about another's details; what DIP reduces.

## Mental Models
- **Think of `extends` as "behaves like, and reuses"; `implements` as "promises the same shape".** OCP and LSP are about substitutable behaviour, so the guide uses `extends`; ISP and DIP are about contracts, so it uses `implements`.
- **Treat `throw UnimplementedError()` in a non-abstract class as a review finding.** It's the type checker being satisfied by a lie: the class claims a capability it doesn't have.
- **If a subclass must override a setter to keep itself valid, it isn't a subtype.** `Square` overriding both setters to keep width and height equal is the tell; make the two shapes siblings.
- **Construct collaborators at the edge, pass them in.** `final requester = InventoryRequester();` inside a class is a decision made in the wrong place; the top-level `InventoryTracker(…, requester: InventoryRequesterV2())` is where it belongs.
- **Read SRP and DIP together.** The guide's SRP Good still builds its `UserAuth` in the initializer list; by DIP's standard you'd pass the `UserAuth` in (typed as an abstraction) so `UserSettings` can be tested with a fake.

## Anti-patterns
- **Grab-bag classes** — settings changes and credential checks in one `UserSettings`.
- **Type-testing chains** (`if (shape is Circle) … else if (shape is Square)`): every new shape edits this function.
- **Subclasses that strengthen the parent's rules** — `Square extends Rectangle`, overriding `setWidth`/`setHeight` to set both; it returns 25 where a `Rectangle` caller expects 20.
- **Fat interfaces forcing stubs** — `PhysicalBook.download()` throwing `UnimplementedError()`.
- **Concrete dependencies created internally** — `final requester = InventoryRequester();`, flagged in the guide's own comment: "InventoryTracker depends on low-level module."

## Code Examples
ISP, with the Dart tell:

```dart
// Bad
abstract class Book {
  int getNumberOfPages();
  void download();
}

class PhysicalBook implements Book {
  @override
  int getNumberOfPages() {
    // ...
  }

  @override
  void download() {
    throw UnimplementedError(); // Physical book doesn't download.
  }
}

// Good
abstract class Book {
  int getNumberOfPages();
}

abstract class DownloadableBook {
  void download();
}

class EBook implements Book, DownloadableBook {
  @override
  int getNumberOfPages() {
    // ...
  }

  @override
  void download() {
    // ...
  }
}

class PhysicalBook implements Book {
  @override
  int getNumberOfPages() {
    // ...
  }
}
```
- **What it demonstrates**: once download is its own interface, `PhysicalBook` stops claiming it, and a function that needs downloading can ask for a `DownloadableBook` and never receive a book that throws.

DIP, injection through a named parameter:

```dart
abstract class InventoryRequester {
  void requestItem(item);
}

class InventoryRequesterV2 implements InventoryRequester {
  @override
  void requestItem(item) {
    // ...
  }
}

class InventoryTracker {
  List<String> items;
  InventoryRequester requester;

  InventoryTracker({
    required this.items,
    required this.requester,
  });

  void requestItems() {
    for (var item in items) {
      requester.requestItem(item);
    }
  }
}

// By constructing our dependencies externally and injecting them, we can easily
// substitute our request module for a fancy new one.
final inventoryTracker = InventoryTracker(
  items: ['apples', 'bananas'],
  requester: InventoryRequesterV2(),
);
```
- **What it demonstrates**: `InventoryTracker` names only the abstraction; switching V1 for V2 is a one-word change at the construction site.

## Reference Tables

| Principle | Dart Bad shape | Dart Good shape |
|---|---|---|
| SRP | one class, two reasons to change | `UserAuth` + `UserSettings` holding it |
| OCP | `is` chain in a free function | abstract method + `@override` per subtype |
| LSP | `Square extends Rectangle` overriding setters | `Rectangle` and `Square` both `extends Shape` |
| ISP | `implements` a fat abstract class + `throw UnimplementedError()` | one abstract class per capability; `implements A, B` |
| DIP | `final dep = Concrete();` field initializer | `required this.dep` typed as an `abstract class` |

| Keyword | Inherits code? | Must provide every member? | Guide uses it for |
|---|---|---|---|
| `extends` | yes | only abstract ones | OCP, LSP |
| `implements` | no | yes | ISP, DIP |

## Worked Example
**LSP — Square and Rectangle**, end to end.

**Bad.** `Square` extends `Rectangle` and overrides both setters so the square stays square:

```dart
class Rectangle {
  double width;
  double height;

  Rectangle({
    this.width = 0,
    this.height = 0,
  });

  // setWidth e setHeight used just for example
  void setWidth(double value) => width = value;

  void setHeight(double value) => height = value;

  double getArea() {
    return width * height;
  }
}

class Square extends Rectangle {
  Square({
    super.width = 0,
    super.height = 0,
  });

  @override
  void setWidth(double value) {
    width = value;
    height = value;
  }

  @override
  void setHeight(double value) {
    width = value;
    height = value;
  }
}

final rectangles = [Rectangle(), Rectangle(), Square()];

for (final rectangle in rectangles) {
  rectangle.setWidth(4);
  rectangle.setHeight(5);

  final area = rectangle.getArea();
  print(area); // BAD: Returns 25 for Square. Should be 20.
}
```

The loop is written against `Rectangle` and assumes what every rectangle guarantees: setting the height leaves the width alone. `Square` compiles, type-checks and is accepted by the list, then breaks that assumption. The type system can't see the problem; only the behaviour can.

**Good.** Make them siblings with a shared abstract parent, and give each its own natural constructor:

```dart
abstract class Shape {
  double getArea();
}

class Rectangle extends Shape {
  double width;
  double height;

  Rectangle({
    required this.width,
    required this.height,
  });

  @override
  double getArea() {
    return width * height;
  }
}

class Square extends Shape {
  double length;

  Square({
    required this.length,
  });

  @override
  double getArea() {
    return length * length;
  }
}

final rectangles = [
  Rectangle(width: 4, height: 5),
  Rectangle(width: 4, height: 5),
  Square(length: 4),
];

for (final rectangle in rectangles) {
  final area = rectangle.getArea();
  print(area); // Show the correct values: 20, 20, 16.
}
```

**What changed**: the setters are gone, and with them the operation that `Square` couldn't honour. `Square` has a single `length`, so there is no width/height pair to keep in step. The list is now a `List<Shape>`, and the only thing the loop asks of each element — its area — every element can answer correctly.

## Key Takeaways
1. **SRP**: one reason to change per class; split by reason, then have one class hold the other.
2. **OCP**: an `is` chain over subtypes is a modification waiting to happen; move the varying behaviour into an abstract method.
3. **LSP**: substitutable means *same observable behaviour*, not just the same type. If a subclass must override setters to protect itself, make it a sibling.
4. **ISP**: `throw UnimplementedError()` in an implementer means the interface is too big. One abstract class per capability; `implements A, B` composes them.
5. **DIP**: depend on an `abstract class`, receive the implementation through a `required` named parameter, and construct concrete classes at the top level.
6. **`@override` on every override** — every Good example in the chapter has it.

## Connects To
- **Ch 3**: "Avoid conditionals" is OCP at function scale, and the duplicate-code example's `is` chain is OCP's Bad shape.
- **Ch 5**: composition (a field holding a collaborator) is how SRP and DIP keep classes small; the three-item inheritance gate explains why `Square extends Rectangle` fails.
- **Ch 7**: injected abstractions are what make a class testable with a fake.
- ***Clean Code*** ch. 10 (Classes): SRP's home in the book; the guide credits OCP's wording to Bertrand Meyer, and LSP is Barbara Liskov's.
- **`clean-code-javascript` Ch 6**: same five principles; the Dart port replaces its OCP and ISP examples (`HttpRequester` adapters, settings objects) with shapes and books, and adds `abstract class` / `implements` / `@override` where JavaScript had implicit duck-typed contracts.
