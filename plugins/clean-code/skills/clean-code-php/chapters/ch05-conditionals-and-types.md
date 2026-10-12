# Chapter 5: Conditionals, Type-Checking and Dead Code

*Source: the second half of the guide's Functions section — six rules.*

## Core Idea
Every `if` is a place where a function might be doing two things. Name conditions (**encapsulate**), state them positively, and where a condition switches on *what kind of thing* you have, **replace it with polymorphism through an interface**. Don't hand-check types PHP can declare. And delete what nothing calls — "It will still be safe in your version history."

## Frameworks Introduced
- **Encapsulate conditionals**: `if ($article->state === 'published')` → `if ($article->isPublished())`.
  - When to use: any condition that inspects another object's state or combines several clauses.
  - How: move the test into a well-named predicate method on the object that owns the data.
- **Avoid negative conditionals**: `if (! isDOMNodeNotPresent($node))` → `if (isDOMNodePresent($node))`.
  - How: name predicates positively; let the caller add one `!` if needed, never two negations.
- **Avoid conditionals**: "This seems like an impossible task… how am I supposed to do anything without an `if` statement? The answer is that you can use polymorphism to achieve the same task in many cases." Why: "When you have classes and functions that have `if` statements, you are telling your user that your function does more than one thing. Remember, just do one thing."
  - How: a `switch ($this->type)` over `'777'`, `'Air Force One'`, `'Cessna'` becomes an `interface Airplane` with `getCruisingAltitude(): int`, implemented by `Boeing777`, `AirForceOne` and `Cessna`. The PHP version reaches for an **interface**, not a base class.
- **Avoid type-checking (part 1)** — consistent APIs: "PHP is untyped, which means your functions can take any type of argument… The first thing to consider is consistent APIs."
  - How: `travelToTexas($vehicle)` branching on `instanceof Bicycle` / `instanceof Car` → `travelToTexas(Vehicle $vehicle)` calling `$vehicle->travelTo(new Location('texas'))`. Give every implementation the same method; declare the abstraction as the parameter type.
- **Avoid type-checking (part 2)** — type declarations: "If you are working with basic primitive values like strings, integers, and arrays, and you use PHP 7+ and you can't use polymorphism but you still feel the need to type-check, you should consider type declaration or strict mode."
  - Why: "The problem with manually type-checking is that doing it will require so much extra verbiage that the faux 'type-safety' you get doesn't make up for the lost readability."
  - How: `combine($val1, $val2)` with an `is_numeric()` guard → `combine(int $val1, int $val2): int`. "Keep your PHP clean, write good tests, and have good code reviews."
- **Remove dead code**: "Dead code is just as bad as duplicate code. There's no reason to keep it in your codebase. If it's not being called, get rid of it!"
  - How: `oldRequestModule()` next to `newRequestModule()` → one `requestModule()`.

## Key Concepts
- **Predicate method** — a boolean method named for the question it answers (`isPublished()`, `isDOMNodePresent()`).
- **Polymorphism** — choosing behaviour by the object's type at runtime instead of by a `switch`.
- **Interface** — a PHP contract (`interface Airplane`) that unrelated classes implement; the guide's preferred vehicle for polymorphism.
- **Type declaration** — a parameter/return type (`int $val1`, `: int`) that PHP enforces at the call boundary.
- **Strict mode** — `declare(strict_types=1)`; turns off scalar coercion for calls made from that file. Named by the guide but never shown.
- **Coercive (weak) mode** — PHP's default, in which `combine('5', '7')` silently converts both strings to `int`.
- **Dead code** — code with no caller; version control is its archive.

## Mental Models
- **A `switch` on a type field is a missing interface.** Each `case` is a class waiting to be written.
- **`instanceof` chains mean the API is inconsistent.** If `Bicycle` has `pedalTo()` and `Car` has `driveTo()`, unify them as `travelTo()` and the branch disappears.
- **Let the engine check types; let tests check behaviour.** Hand-written `is_numeric()` guards are slower to read than `int` and catch less.
- **A predicate's name should read as English at the `if`.** `if ($article->isPublished())` is the specification.

## Anti-patterns
- **Leaking state strings** (`$article->state === 'published'`) into callers: every caller now knows the representation.
- **Double negatives** (`! isNotPresent()`): the reader has to flip twice.
- **Type-code switches** (`switch ($this->type)`): every new type edits the method — and the guide's bad version has no `default`, so an unknown type falls off the end of an `: int` method, a `TypeError` at runtime.
- **`instanceof` dispatch** in a function that takes an untyped `$vehicle`.
- **`is_numeric()` / `is_string()` guards** on parameters PHP could declare.
- **Commented-out or superseded functions** kept "just in case".

## Code Examples
```php
interface Airplane
{
    // ...

    public function getCruisingAltitude(): int;
}

class Boeing777 implements Airplane
{
    // ...

    public function getCruisingAltitude(): int
    {
        return $this->getMaxAltitude() - $this->getPassengerCount();
    }
}

class AirForceOne implements Airplane
{
    // ...

    public function getCruisingAltitude(): int
    {
        return $this->getMaxAltitude();
    }
}

class Cessna implements Airplane
{
    // ...

    public function getCruisingAltitude(): int
    {
        return $this->getMaxAltitude() - $this->getFuelExpenditure();
    }
}
```
- **What it demonstrates**: each `case` of the old `switch` became a class; adding a fourth airplane adds a file and edits nothing.

## Reference Tables

**The conditional-removal ladder**

| You see | Rule | Replace with |
|---|---|---|
| `$obj->state === 'published'` | Encapsulate conditionals | `$obj->isPublished()` |
| `! isNotX()` | Avoid negative conditionals | `isX()` |
| `switch ($this->type)` | Avoid conditionals | interface + one class per case |
| `instanceof A … elseif instanceof B` | Avoid type-checking (part 1) | one method name on a declared interface type |
| `is_numeric($x)` guard on a scalar | Avoid type-checking (part 2) | `int $x` (and strict mode) |
| `oldX()` beside `newX()` | Remove dead code | delete `oldX()` |

**What a scalar type declaration does, by mode** (the guide says "type declaration or strict mode"; this is why both are needed)

| Call | Default (coercive) mode | `declare(strict_types=1)` in the calling file |
|---|---|---|
| `combine(5, 7)` | `12` | `12` |
| `combine('5', '7')` | `12` — strings silently converted | `TypeError` |
| `combine('five', 7)` | `TypeError` | `TypeError` |

## Worked Example
**Avoid type-checking, both parts, on one call site.**

Part 1 starts with a function that dispatches on class:

```php
function travelToTexas($vehicle): void
{
    if ($vehicle instanceof Bicycle) {
        $vehicle->pedalTo(new Location('texas'));
    } elseif ($vehicle instanceof Car) {
        $vehicle->driveTo(new Location('texas'));
    }
}
```

The fix is not a smarter check but a **consistent API**: give both classes `travelTo(Location $location)`, have them implement a `Vehicle` abstraction, and declare it:

```php
function travelToTexas(Vehicle $vehicle): void
{
    $vehicle->travelTo(new Location('texas'));
}
```

Part 2 handles what polymorphism can't — primitives. The `is_numeric()` guard in `combine()` becomes `int $val1, int $val2`. But note what the type alone guarantees: **in the default coercive mode, `combine('5', '7')` still succeeds** because PHP converts the numeric strings. The guide's phrase "type declaration *or strict mode*" is doing real work here — only with `declare(strict_types=1)` at the top of the calling file does a string argument raise a `TypeError`. The guide never shows that line (its own linter config skips the `DeclareStrictTypesFixer`), so apply it yourself if you want the "Good" version to be as strict as it looks.

## Key Takeaways
1. **Wrap conditions in named predicate methods** on the object that owns the data.
2. **Name predicates positively.**
3. **Replace type-code `switch`es with an interface and one class per case.**
4. **Replace `instanceof` chains with one consistent method** and an interface-typed parameter.
5. **Declare scalar types instead of hand-checking them** — and add `declare(strict_types=1)` if you need coercion off.
6. **Delete dead code**; version control remembers it.

## Connects To
- **Ch 4**: "a function should only do one thing" — the rule this chapter's conditionals rules are detectors for, and which the PHP guide cites but never states as its own entry.
- **Ch 3**: type declarations and `===` both defend against type juggling.
- **Ch 7**: `final class Car implements Vehicle` is the class-side half of "declare the interface".
- **Ch 8 (OCP, LSP)**: the airplane hierarchy is open for extension, and every implementation must be substitutable for `Airplane`.
- **Ch 9 (DRY)**: "Dead code is just as bad as duplicate code."
