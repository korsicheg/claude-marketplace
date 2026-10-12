# Chapter 7: Classes

## Core Idea
Three rules about how classes relate to each other: **compose instead of inheriting** unless the relationship is truly "is-a"; **don't return `$this` for chaining** outside builders; and **declare classes `final` and put an interface in front of them**. Two of the three are PHP-only, and one reverses its JavaScript parent outright.

## Frameworks Introduced
- **Prefer composition over inheritance**: from the Gang of Four's *Design Patterns* — "if your mind instinctively goes for inheritance, try to think if composition could model your problem better. In some cases it can."
  - When inheritance makes more sense — the guide's three tests:
    1. "Your inheritance represents an 'is-a' relationship and not a 'has-a' relationship (Human->Animal vs. User->UserDetails)."
    2. "You can reuse code from the base classes (Humans can move like all animals)."
    3. "You want to make global changes to derived classes by changing a base class."
  - How: `EmployeeTaxData extends Employee` is wrong — "Employees 'have' tax data. EmployeeTaxData is not a type of Employee" — so `Employee` holds an `EmployeeTaxData`, supplied through `setTaxData(EmployeeTaxData $taxData)`.
- **Avoid fluent interfaces**: a fluent interface "aims to improve the readability of the source code by using Method chaining." The guide grants that "there can be some contexts, frequently builder objects, where this pattern reduces the verbosity of the code (for example the PHPUnit Mock Builder or the Doctrine Query Builder)", but "more often it comes at some costs":
  1. "Breaks Encapsulation."
  2. "Breaks Decorators."
  3. "Is harder to mock in a test suite."
  4. "Makes diffs of commits harder to read."
  - How: setters return `void`; call them as separate statements. The guide cites Marco Pivetta's (Ocramius) "Fluent Interfaces are Evil".
  - Note: this **reverses** clean-code-javascript, whose rule is "Use method chaining".
- **Prefer final classes**: "The `final` keyword should be used whenever possible":
  1. "It prevents an uncontrolled inheritance chain."
  2. "It encourages composition."
  3. "It encourages the Single Responsibility Principle."
  4. "It encourages developers to use your public methods instead of extending the class to get access to protected ones."
  5. "It allows you to change your code without breaking applications that use your class."
  - The condition: "**The only condition is that your class should implement an interface and no other public methods are defined.**" Again citing Ocramius ("When to declare classes final").

## Key Concepts
- **Composition** — an object holding another object as a field ("has-a") and delegating to it.
- **Inheritance** — `extends`; a subclass is-a base class and inherits its public and protected members.
- **"is-a" vs "has-a"** — the guide's test for choosing between them (Human→Animal vs User→UserDetails).
- **Fluent interface** — an API whose mutators `return $this` so calls chain: `(new Car())->setColor('pink')->setMake('Ford')`.
- **Builder** — an object whose whole purpose is staged configuration; the guide's accepted home for fluent APIs.
- **Decorator** — a wrapper implementing the same interface that adds behaviour; a returned `$this` escapes it.
- **`final` class** — a class that cannot be extended.
- **Interface-first class** — a `final` class whose public methods are exactly those of the interface it implements.

## Mental Models
- **`extends` is the tightest coupling PHP offers.** Every protected member becomes API. Reach for a field first.
- **`final` + interface = closed to inheritance, open to substitution.** Callers depend on `Vehicle`; anyone needing different behaviour writes another `Vehicle` or a decorator, not a subclass of `Car`.
- **`return $this` leaks identity.** Wrap a fluent object in a decorator and the first chained call returns the inner object, silently dropping the wrapper.
- **Fluency is a builder feature, not a domain feature.** Query builders and mock builders earn it; entities and services don't.

## Anti-patterns
- **Inheriting to reuse fields** (`EmployeeTaxData extends Employee`): tax data is not a kind of employee, and the subclass constructor must replicate the parent's.
- **Chaining setters on domain objects**: harder to mock, breaks decorators, and every added call rewrites a multi-line expression in the diff.
- **`final` without an interface**: the guide's own "Bad" example — callers are now bound to a concrete class they can neither extend nor substitute.
- **Public methods on a `final` class beyond its interface**: the condition for `final` is that the interface is the whole public surface.
- **Using `extends` to get at `protected` members**: the habit `final` exists to stop.

## Code Examples
```php
// Bad: the guide's "Bad" is already final — but implements nothing
final class Car
{
    private $color;

    public function __construct($color)
    {
        $this->color = $color;
    }

    /**
     * @return string The color of the vehicle
     */
    public function getColor()
    {
        return $this->color;
    }
}

// Good: an interface carries the contract; the final class implements it
interface Vehicle
{
    /**
     * @return string The color of the vehicle
     */
    public function getColor();
}

final class Car implements Vehicle
{
    private $color;

    public function __construct($color)
    {
        $this->color = $color;
    }

    public function getColor()
    {
        return $this->color;
    }
}
```
- **What it demonstrates**: the rule is not "add `final`" but "**add `final` *and* the interface**". The difference between Bad and Good is only the `Vehicle` interface — the thing that keeps a final class substitutable.

## Reference Tables

**Inherit or compose?**

| Question | Yes → | No → |
|---|---|---|
| Is the child genuinely a kind of the parent ("is-a")? | consider `extends` | compose |
| Does it reuse the base's *behaviour*, not just its fields? | consider `extends` | compose |
| Should changing the base change every child on purpose? | consider `extends` | compose |
| Any answer "no"? | — | **compose** (hold it as a field) |

**Fluent interface: where the guide accepts it**

| Context | Verdict |
|---|---|
| Builders — PHPUnit Mock Builder, Doctrine Query Builder | acceptable: chaining reduces verbosity |
| Entities, services, value objects | avoid: setters return `void` |

**Prefer `final` — the checklist**

| Check | Required |
|---|---|
| Class implements an interface | yes |
| Every public method comes from that interface | yes ("no other public methods are defined") |
| Callers type-hint the interface, not the class | implied — otherwise `final` blocks substitution |

## Worked Example
**Fluent `Car`, de-chained.**

Bad — every setter returns `$this`:

```php
class Car
{
    private $make = 'Honda';
    private $model = 'Accord';
    private $color = 'white';

    public function setMake(string $make): self
    {
        $this->make = $make;

        // NOTE: Returning this for chaining
        return $this;
    }

    // setModel() and setColor() likewise return $this

    public function dump(): void
    {
        var_dump($this->make, $this->model, $this->color);
    }
}

$car = (new Car())
    ->setColor('pink')
    ->setMake('Ford')
    ->setModel('F-150')
    ->dump();
```

Good — setters return `void` and are called as statements:

```php
$car = new Car();
$car->setColor('pink');
$car->setMake('Ford');
$car->setModel('F-150');
$car->dump();
```

Walk the four costs on this example:
1. **Encapsulation** — the return value becomes part of the contract: callers rely on getting the *same* object back, an implementation detail the class can no longer change.
2. **Decorators** — wrap `Car` in a logging decorator: `$logged->setColor('pink')` returns the inner `Car`, so `->setMake()` bypasses the logging.
3. **Mocking** — a test double must be configured to return itself from every setter before a chained call works.
4. **Diffs** — inserting one call into the chain touches the expression; in the Good version it's one added line.

(Incidentally, the Bad version assigns the result of `dump()` — a `void` method — to `$car`, so `$car` ends up `null`: chaining makes it easy to lose track of what an expression returns.)

## Key Takeaways
1. **Compose by default**; inherit only for a true "is-a" that also reuses behaviour.
2. **Setters return `void`.** Keep `return $this` for builders.
3. **Declare classes `final`** — *and* give them an interface whose methods are their entire public API.
4. **Type-hint the interface**, so `final` never stops anyone substituting an implementation.

## Connects To
- **Ch 6**: `final` removes the audience for `protected` entirely, completing "private by default".
- **Ch 8 (SRP, OCP, DIP)**: `final` "encourages the Single Responsibility Principle"; interfaces are how the guide does OCP and DIP.
- **Ch 4**: the `Name`/`City`/`Contact` value objects are composition used to cut argument count.
- **clean-code-javascript ch05**: the parent's "Use method chaining" — the rule this chapter reverses.
- **Marco Pivetta (Ocramius)**: "Fluent Interfaces are Evil" and "When to declare classes final", both cited by the guide.
