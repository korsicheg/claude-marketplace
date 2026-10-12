# Chapter 9: SOLID

## Core Idea
"**SOLID** is the mnemonic acronym introduced by Michael Feathers for the first five principles named by Robert Martin." In C# every one of them turns on the **interface**: extract a collaborator (SRP), add behaviour as a new implementation (OCP), keep subtypes honest (LSP), split fat interfaces into role interfaces (ISP), and have high-level classes take interfaces through their constructors (DIP) — the pattern .NET's built-in dependency injection already uses.

## Frameworks Introduced
- **SRP — Single Responsibility Principle.** "As stated in Clean Code, 'There should never be more than one reason for a class to change'."
  - The cost: "It's tempting to jam-pack a class with a lot of functionality, like when you can only take one suitcase on your flight … your class won't be conceptually cohesive and it will give it many reasons to change."
  - Why it matters: "if too much functionality is in one class and you modify a piece of it, it can be difficult to understand how that will affect other dependent modules."
  - How: `UserSettings` that also verifies credentials → extract `UserAuth(User user)` with `VerifyCredentials()`; `UserSettings` holds a `UserAuth` and asks it.
- **OCP — Open/Closed Principle.** Bertrand Meyer: "software entities (classes, modules, functions, etc.) should be open for extension, but closed for modification." Plainly: "allow users to add new functionalities without changing existing code."
  - Tell: a class that reads an adapter's *name* and branches on it.
  - How: an `IAdapter` interface with `bool Request(string url)`; `AjaxAdapter` and `NodeAdapter` implement it; `HttpRequester.Fetch` just calls `Adapter.Request(url)`. A new adapter is a new class.
- **LSP — Liskov Substitution Principle.** Formally: "If S is a subtype of T, then objects of type T may be replaced with objects of type S … without altering any of the desirable properties of that program (correctness, task performed, etc.)."
  - The source's translation: "if you have a parent class and a child class, then the base class and child class can be used interchangeably without getting incorrect results."
  - Tell: the classic **Square–Rectangle** — "Mathematically, a square is a rectangle, but if you model it using the 'is-a' relationship via inheritance, you quickly get into trouble." `SetWidth(4); SetHeight(5); GetArea()` returns **25 for a Square; should be 20**.
  - How: make `Rectangle` and `Square` **siblings** under an `abstract class ShapeBase` with `abstract double GetArea()`. (See the Worked Example for a flaw in the source's version.)
- **ISP — Interface Segregation Principle.** "Clients should not be forced to depend upon interfaces that they do not use."
  - Tell: an implementer stuck with a method it can't honour — "robot can't eat, but it must implement this method."
  - How: split `IEmployee { Work(); Eat(); }` into **role interfaces** `IWorkable` and `IFeedable`; compose them where both apply (`interface IEmployee : IFeedable, IWorkable`); `Robot` implements only `IWorkable`. "Not every worker is an employee, but every employee is an worker."
- **DIP — Dependency Inversion Principle.** Two statements:
  1. "High-level modules should not depend on low-level modules. Both should depend on abstractions."
  2. "Abstractions should not depend upon details. Details should depend on abstractions."
  - .NET context: "if you've worked with .NET/.NET Core framework, you've seen an implementation of this principle in the form of Dependency Injection (DI). While they are not identical concepts, DIP keeps high-level modules from knowing the details of its low-level modules and setting them up."
  - Why: "it reduces the coupling between modules. Coupling is a very bad development pattern because it makes your code hard to refactor."
  - How: `Manager(Robot robot, Human human)` → `Manager(IEnumerable<IEmployee> employees)` with a primary constructor, iterating and calling `Work()`.

## Key Concepts
- **Reason to change** — a source of change requests; SRP's unit of responsibility.
- **Conceptual cohesion** — whether everything in a class belongs to one idea.
- **Open for extension / closed for modification** — new behaviour arrives as new types, not edits.
- **Substitutability** — a subtype usable wherever its base is expected, with correct results.
- **Square–Rectangle problem** — the textbook LSP violation.
- **Fat interface** — one interface bundling capabilities not every implementer has.
- **Role interface** — a small interface for one capability (`IWorkable`, `IFeedable`).
- **Interface inheritance** — `interface IEmployee : IFeedable, IWorkable`; composing role interfaces.
- **Dependency Injection (DI)** — supplying collaborators from outside, usually via the constructor; DIP's usual mechanism, not DIP itself.
- **`IEnumerable<T>` injection** — taking every implementation of an interface as a collection.

## Mental Models
- **SRP asks "who would ask for this change?"** Settings change when product changes; credential checks change when security changes. Two askers, two classes.
- **Branching on a name or type inside a class is OCP's alarm.** `if (adapterName == "ajaxAdapter")` means every new adapter edits `HttpRequester`.
- **LSP is about callers, not taxonomies.** Not "is a square a rectangle?", but "is code written against `Rectangle` still right when handed a `Square`?"
- **An empty or apologetic method is ISP's smoking gun** — `Robot.Eat()` exists only because the interface demanded it.
- **DIP inverts who chooses.** `Manager(Robot robot, Human human)` chose its workers; `Manager(IEnumerable<IEmployee> employees)` is told them. In Microsoft.Extensions.DependencyInjection, a constructor parameter of type `IEnumerable<IEmployee>` receives every registered `IEmployee` (context for reading the example; the source doesn't spell it out).

## Anti-patterns
- **One class, two askers** — `UserSettings` changing settings *and* verifying credentials.
- **String dispatch on an adapter's name** — and the Bad example proves the danger: `NodeAdapter` sets its name to `"nodeAdapter"` but `Fetch` compares against `"httpNodeAdapter"`, so the node path can never run. (Observation; the source doesn't comment on it.)
- **Overriding to preserve your own invariant** — `Square.SetWidth` also setting height.
- **Forced stubs** — `Robot.Eat()`.
- **Depending on concrete classes** — `Manager` holding a `Robot` and a `Human` even though both already share `EmployeeBase`.

## Code Examples
**SRP** — extract the second responsibility:

```csharp
// Bad
class UserSettings
{
    private User User;

    public UserSettings(User user)
    {
        User = user;
    }

    public void ChangeSettings(Settings settings)
    {
        if (VerifyCredentials())
        {
            // ...
        }
    }

    private bool VerifyCredentials()
    {
        // ...
    }
}

// Good
class UserAuth(User user)
{
    public bool VerifyCredentials()
    {
        // ...
    }
}

class UserSettings(User user)
{
    private readonly UserAuth _auth = new(user);

    public void ChangeSettings(Settings settings)
    {
        if (_auth.VerifyCredentials())
        {
            // ...
        }
    }
}
```
- Note that the Good version still **constructs** its collaborator (`new(user)`). That satisfies SRP; DIP (below) would take `UserAuth` — or an interface for it — through the constructor instead.

**OCP** — one interface, no dispatch:

```csharp
interface IAdapter
{
    bool Request(string url);
}

class AjaxAdapter : IAdapter
{
    public bool Request(string url) { /* request and return promise */ }
}

class NodeAdapter : IAdapter
{
    public bool Request(string url) { /* request and return promise */ }
}

class HttpRequester
{
    private readonly IAdapter Adapter;

    public HttpRequester(IAdapter adapter)
    {
        Adapter = adapter;
    }

    public bool Fetch(string url)
    {
        return Adapter.Request(url);
    }
}
```
- The "return promise" comments are carried over from the JavaScript original; in C# these would return `Task<bool>` (Ch 12).

**ISP** — role interfaces composed by interface inheritance:

```csharp
public interface IWorkable
{
    void Work();
}

public interface IFeedable
{
    void Eat();
}

public interface IEmployee : IFeedable, IWorkable
{
}

public class Human : IEmployee
{
    public void Work() { /* ....working */ }
    public void Eat() { /* .... eating in lunch break */ }
}

// robot can only work
public class Robot : IWorkable
{
    public void Work() { /* ....working */ }
}
```
- The source's prose for ISP (about "classes that require large settings objects") is inherited from the JavaScript version and doesn't match this example; the example is the C# content.

**DIP** — inject the abstraction:

```csharp
public interface IEmployee
{
    void Work();
}

public class Human : IEmployee
{
    public void Work() { /* ....working */ }
}

public class Robot : IEmployee
{
    public void Work() { /* .... working much more */ }
}

public class Manager(IEnumerable<IEmployee> employees)
{
    public void Manage()
    {
        foreach (var employee in employees)
        {
            employee.Work();
        }
    }
}
```

## Worked Example
**LSP — Square and Rectangle, and a flaw in the source's fix.**

**Bad** — `Square` inherits from `Rectangle` and overrides both setters to keep its sides equal:

```csharp
class Rectangle
{
    protected double Width = 0;
    protected double Height = 0;

    public Drawable Render(double area) { /* ... */ }

    public virtual void SetWidth(double width) { Width = width; }
    public virtual void SetHeight(double height) { Height = height; }

    public double GetArea() { return Width * Height; }
}

class Square : Rectangle
{
    public override void SetWidth(double width) { Width = Height = width; }
    public override void SetHeight(double height) { Width = Height = height; }
}

void RenderLargeRectangles(IEnumerable<Rectangle> rectangles)
{
    foreach (var rectangle in rectangles)
    {
        rectangle.SetWidth(4);
        rectangle.SetHeight(5);
        var area = rectangle.GetArea(); // BAD: Will return 25 for Square. Should be 20.
        rectangle.Render(area);
    }
}
```
- *Lightly repaired: `virtual`/`override` added (the source declares `Square`'s setters as new `double`-returning methods, which would hide rather than override), and the parameter made a collection.*

A caller written against `Rectangle` sets width 4, height 5 and expects 20. Hand it a `Square` and it gets 25 — the subtype changed a "desirable property of the program."

**The source's Good** splits the hierarchy: `abstract class ShapeBase` with `abstract double GetArea()` and a shared `Render`; `Rectangle : ShapeBase` keeps `SetWidth`/`SetHeight`; `Square : ShapeBase` has `SetLength`. The two are now **siblings**, so neither can break the other's contract. That is the fix.

**But its consumer still branches on type:**

```csharp
foreach (var rectangle in rectangles)
{
    if (rectangle is Square)
    {
        rectangle.SetLength(5);
    }
    else if (rectangle is Rectangle)
    {
        rectangle.SetWidth(4);
        rectangle.SetHeight(5);
    }

    var area = rectangle.GetArea();
    rectangle.Render(area);
}
```

This contradicts the source's own "Avoid type-checking" rule (Ch 5) and OCP above: a `Circle` would edit this loop. The JavaScript and TypeScript originals finish the job by giving each shape its dimensions **at construction** and leaving the consumer only what every shape shares:

```csharp
abstract class ShapeBase
{
    public abstract double GetArea();
    public Drawable Render(double area) { /* ... */ }
}

class Rectangle(double width, double height) : ShapeBase
{
    public override double GetArea() => width * height;
}

class Square(double length) : ShapeBase
{
    public override double GetArea() => Math.Pow(length, 2);
}

void RenderLargeShapes(IEnumerable<ShapeBase> shapes)
{
    foreach (var shape in shapes)
    {
        shape.Render(shape.GetArea());
    }
}

ShapeBase[] shapes = [new Rectangle(4, 5), new Rectangle(4, 5), new Square(5)];
RenderLargeShapes(shapes);
```

**The transferable rule**: when a subclass must override a method to protect its own invariant, it isn't a subtype — make it a sibling. And once it is, the consumer should need no type test at all; if it still does, the shared abstraction is missing an operation.

## Reference Tables

| Principle | Tell in C# | Fix in C# | Source example |
|---|---|---|---|
| SRP | Class needs "and" to describe; private helper for a second concern | Extract a class; hold or inject it | `UserSettings` → `UserAuth` |
| OCP | `if (name == "…")` / `switch` on a type in a consumer | Interface + one class per variant | `IAdapter` |
| LSP | Override that keeps its own invariant; wrong result via base reference | Sibling classes under an abstract base | `ShapeBase` |
| ISP | Method that does nothing or throws "not supported" | Role interfaces; compose by interface inheritance | `IWorkable`, `IFeedable` |
| DIP | Constructor takes concrete classes, or `new`s them | Constructor takes interfaces (or `IEnumerable<I…>`) | `Manager(IEnumerable<IEmployee>)` |

## Key Takeaways
1. **SRP**: split by *reason to change* — `UserAuth` out of `UserSettings`.
2. **OCP**: a new variant should be a new class; dispatch on names or types is the violation.
3. **LSP**: if a subclass must break a base invariant to be correct, make it a **sibling**; and a consumer that still needs `is Square` is missing an abstraction.
4. **ISP**: small **role interfaces**, composed with interface inheritance; no forced stubs.
5. **DIP**: take **interfaces through the constructor**; .NET's DI container does the wiring. DIP ≠ DI, but DI is how .NET usually delivers it.

## Connects To
- **Ch 4**: `BetterJSAlternative(Tokenizer, Lexer)` is DIP's constructor injection with concrete types — one interface away.
- **Ch 5**: "Avoid conditionals" and "Avoid type-checking" are OCP and LSP at function scale.
- **Ch 6**: the Singleton breaks SRP (it manages its own lifecycle) and DIP (callers fetch it).
- **Ch 8**: composition over inheritance is the design habit LSP rewards.
- **Ch 10**: DRY — "Getting the abstraction right is critical, that's why you should follow the SOLID principles."
- **clean-code-python** ch04–ch08: the same five principles in a duck-typed language, one chapter each.
- **clean-code-java** ch10–ch11: SRP and DIP from the book itself, with cohesion and systems-level construction.
