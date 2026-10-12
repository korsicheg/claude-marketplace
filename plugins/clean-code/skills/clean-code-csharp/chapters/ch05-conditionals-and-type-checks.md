# Chapter 5: Conditionals and Type Checks

## Core Idea
A branch is a confession that a method does more than one thing. Name conditions positively, wrap them in intention-revealing members, and where a `switch` or `if` chooses behaviour **by type**, let the type choose instead: an interface with one implementation per case. In a statically typed language, "avoid type-checking" also means **don't step outside the type system** — no `GetType() == typeof(…)`, no `object`, no `dynamic` where a real type would do.

## Frameworks Introduced
- **Avoid negative conditionals** — `if (!IsDOMNodeNotPresent(node))` → `if (IsDOMNodePresent(node))`.
  - How: name the predicate for the positive case; let `!` do the negating at the call site, once.
- **Avoid conditionals** — "Upon first hearing this, most people say, 'how am I supposed to do anything without an `if` statement?' The answer is that you can use polymorphism to achieve the same task in many cases."
  - Why: "When you have classes and functions that have `if` statements, you are telling your user that your function does more than one thing. Remember, just do one thing."
  - How: a `switch` on a type field (`_type` of `"777"`, `"Air Force One"`, `"Cessna"`) → an `IAirplane` interface with one class per case, each implementing `GetCruisingAltitude()`.
- **Avoid type-checking (part 1)** — branching on the runtime type of an `object` parameter.
  - How, first choice: give the types a common abstraction and call it — `TravelToTexas(Traveler vehicle) { vehicle.TravelTo(new Location("texas")); }`.
  - How, second choice ("or"): C# **type patterns** — `if (vehicle is Bicycle bicycle) { bicycle.PeddleTo(…); }` — instead of `vehicle.GetType() == typeof(Bicycle)` plus an `as` cast.
- **Avoid type-checking (part 2)** — `Combine(dynamic val1, dynamic val2)` with `int.TryParse` guards and a `throw` → `Combine(int val1, int val2)`.
  - How: put the type in the **signature** and let the compiler reject bad calls; runtime validation of something the type system can express is dead weight.
- **Encapsulate conditionals** — `if (article.state == "published")` → `if (article.IsPublished())`.
  - How: move the comparison into a member of the type that owns the state; the call site reads as a sentence and the literal lives in one place.

## Key Concepts
- **Negative conditional** — a predicate named for the absence of something (`IsNotPresent`), forcing double negation.
- **Polymorphism** — one call (`GetCruisingAltitude()`) dispatched to the right implementation by the object's type.
- **Interface** — the C# contract each case implements (`IAirplane`); `I`-prefixed throughout the source.
- **Type pattern** — `x is Car car`: tests and binds in one step (C# 7.0+).
- **`GetType() == typeof(T)`** — exact-type comparison; ignores subclasses and needs a separate cast.
- **`dynamic`** — opts a value out of compile-time checking; errors move to run time.
- **Encapsulated conditional** — a named predicate (`IsPublished()`) hiding the comparison it makes.

## Mental Models
- **Every `case` on a type code is a class that wasn't written yet.** Adding a fourth airplane to the `switch` edits a method that already works; adding a fourth `IAirplane` class edits nothing (this is OCP, Ch 9).
- **Prefer, in order**: a common abstraction → a type pattern → never `GetType() ==`. The source endorses the first two; the third is its Bad.
- **Let the signature do the checking.** If `Combine` can only add numbers, `int` says so and the compiler enforces it. `dynamic` plus `TryParse` re-implements, badly, what the compiler gives you free.
- **A condition with a name is documentation that can't drift.** `IsPublished()` changes when the rule changes; a comment beside `== "published"` doesn't.

## Anti-patterns
- **Double negatives** — `!IsDOMNodeNotPresent`.
- **`switch` on a type code** inside a class that will gain cases.
- **`GetType() == typeof(…)` followed by `as`** — two operations, and subclasses silently fail the test.
- **`object` / `dynamic` parameters** where a concrete type or interface would do.
- **Raw state comparisons at call sites** — `article.state == "published"` repeated wherever it matters.

## Code Examples
Replace a type-code `switch` with polymorphism:

```csharp
// Bad
class Airplane
{
    // ...
    public double GetCruisingAltitude()
    {
        switch (_type)
        {
            case "777":
                return GetMaxAltitude() - GetPassengerCount();
            case "Air Force One":
                return GetMaxAltitude();
            case "Cessna":
                return GetMaxAltitude() - GetFuelExpenditure();
        }
    }
}

// Good
interface IAirplane
{
    // ...
    double GetCruisingAltitude();
}

class Boeing777 : IAirplane
{
    // ...
    public double GetCruisingAltitude() => GetMaxAltitude() - GetPassengerCount();
}

class AirForceOne : IAirplane
{
    // ...
    public double GetCruisingAltitude() => GetMaxAltitude();
}

class Cessna : IAirplane
{
    // ...
    public double GetCruisingAltitude() => GetMaxAltitude() - GetFuelExpenditure();
}
```
- *Source snippet lightly repaired: single-quoted `case '777':` labels → strings; bodies condensed.*

Type checking, then a real type:

```csharp
// Bad
public int Combine(dynamic val1, dynamic val2)
{
    int value;
    if (!int.TryParse(val1, out value) || !int.TryParse(val2, out value))
    {
        throw new Exception("Must be of type Number");
    }

    return val1 + val2;
}

// Good
public int Combine(int val1, int val2)
{
    return val1 + val2;
}
```
- **What it demonstrates**: in C# the cure for runtime type-checking is usually to delete it and state the type.

## Reference Tables

| You see | Prefer | Acceptable fallback | Never |
|---|---|---|---|
| Behaviour varies by kind | Interface + one class per kind | — | `switch` on a type code |
| Method receives several unrelated types | Common abstraction (`Traveler.TravelTo`) | `is Bicycle bicycle` type pattern | `GetType() == typeof(…)` + `as` |
| Parameter can be "anything" | Concrete type in the signature | — | `dynamic` + `TryParse` |
| Raw state comparison | `article.IsPublished()` | — | `== "published"` everywhere |
| `!IsNotX()` | `IsX()` | — | Double negation |

## Worked Example
**Avoid type-checking, part 1**, walked through all three forms the source shows.

**Bad** — exact type comparison, then a cast:

```csharp
public Path TravelToTexas(object vehicle)
{
    if (vehicle.GetType() == typeof(Bicycle))
    {
        (vehicle as Bicycle).PeddleTo(new Location("texas"));
    }
    else if (vehicle.GetType() == typeof(Car))
    {
        (vehicle as Car).DriveTo(new Location("texas"));
    }
}
```

Three problems: the parameter is `object`, so the compiler can't help; `GetType() ==` rejects a `SportsCar : Car`; and each new vehicle edits this method.

**Good (first choice)** — a shared abstraction:

```csharp
public Path TravelToTexas(Traveler vehicle)
{
    vehicle.TravelTo(new Location("texas"));
}
```

`Bicycle` and `Car` each implement `TravelTo` (pedalling, driving). The caller can't pass a non-traveler, and a new vehicle is a new class.

**Good (the source's "or")** — pattern matching, when you can't change the types (they're in a library you don't own, say):

```csharp
// pattern matching
public Path TravelToTexas(object vehicle)
{
    if (vehicle is Bicycle bicycle)
    {
        bicycle.PeddleTo(new Location("texas"));
    }
    else if (vehicle is Car car)
    {
        car.DriveTo(new Location("texas"));
    }
}
```

This fixes two of the three problems — the test and cast are one step, and subclasses match — but the method still grows with every vehicle. **Use it at boundaries you don't control; use the abstraction everywhere else.**

## Key Takeaways
1. Name predicates **positively**; negate at the call site.
2. A `switch` on a type code is **polymorphism waiting to happen** — an interface and one class per case.
3. For mixed types: **abstraction first, `is T t` pattern second, `GetType() ==` never.**
4. In C#, the cure for runtime type checks is usually a **better signature** — not `object`, not `dynamic`.
5. **Encapsulate** state comparisons in a named member of the owning type.

## Connects To
- **Ch 4**: "do one thing" is the reason the source gives for avoiding conditionals.
- **Ch 3**: returning early and named constants are the lighter-weight fixes for conditionals you keep.
- **Ch 9**: the `IAirplane` move is OCP; the source's LSP "Good" example, by contrast, still type-checks `is Square` — see the note there.
- **clean-code-typescript**: the same rule rendered with union types instead of interfaces.
- **clean-code-java** ch17 (G23): "Prefer polymorphism to if/else or switch/case" in the smells catalogue.
