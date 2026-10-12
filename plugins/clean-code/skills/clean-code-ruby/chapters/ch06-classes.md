# Chapter 6: Classes

## Core Idea
Two rules. **Avoid fluent interfaces** — the one place the Ruby port **reverses** its JavaScript parent, which says "use method chaining". And **prefer composition over inheritance**, with three tests for when inheritance is right.

## Frameworks Introduced
- **Avoid fluent interfaces**: a fluent interface "aims to improve the readability of the source code by using method chaining." The guide grants "some contexts, frequently builder objects, where this pattern reduces the verbosity of the code (e.g., ActiveRecord queries)", but "more often it comes at some costs":
  1. Breaks encapsulation
  2. Breaks decorators
  3. Is harder to mock in a test suite
  4. Makes diffs of commits harder to read
  - Source of the argument: Marco Pivetta's blog post *Fluent Interfaces are Evil*, which the guide links.
  - When to use: whenever you're tempted to end a setter with `self`.
  - How: plain writers (`attr_accessor :make, :model, :color`) and separate statements — `car.color = 'pink'`, then `car.save`.
  - Allowed exception: builder-style query objects such as ActiveRecord relations, where chaining is the API's whole point.
- **Prefer composition over inheritance**: "As stated famously in *Design Patterns* by the Gang of Four … if your mind instinctively goes for inheritance, try to think if composition could model your problem better."
  - **When inheritance makes more sense** — the guide's three tests:
    1. "Your inheritance represents an 'is-a' relationship and not a 'has-a' relationship (Human->Animal vs. User->UserDetails)."
    2. "You can reuse code from the base classes (Humans can move like all animals)."
    3. "You want to make global changes to derived classes by changing a base class."
  - How: hold the collaborator in an instance variable — `@tax_data = EmployeeTaxData.new(ssn, salary)` — instead of `class EmployeeTaxData < Employee`.

## Key Concepts
- **Fluent interface** — an API designed around method chaining, each call returning `self`.
- **Method chaining** — `Car.new(...).set_color('pink').save`; the mechanism a fluent interface relies on.
- **Builder** — an object that accumulates configuration before producing a result; the guide's sanctioned home for chaining.
- **Decorator** — a wrapper adding behaviour around an object; chaining breaks it because `self` returns the *inner* object, escaping the wrapper.
- **Mock** — a test double; chained calls need every intermediate return value stubbed.
- **Composition** — modelling "has-a" by holding an instance (`@tax_data`).
- **Inheritance (`<`)** — modelling "is-a" by subclassing.
- **is-a vs has-a** — the test that decides between them.

## Mental Models
- **Ask what each call returns.** A writer returning `self` makes the object's own identity part of every method's contract — which is exactly what a decorator, a mock, or a later refactoring can't preserve.
- **Read the diff, not the expression.** A one-line chain becomes a one-line diff for any change to any link; separate statements diff separately.
- **Say the relationship aloud.** "An `EmployeeTaxData` *is an* `Employee`" is false; "an `Employee` *has* tax data" is true. The sentence picks the mechanism.

## Anti-patterns
- **`self` at the end of every setter** so callers can chain.
- **`set_*` methods** (`set_make`, `set_model`) where a writer (`make=`) is the Ruby idiom.
- **Inheriting to share data**: `class EmployeeTaxData < Employee` — tax data is not a kind of employee.
- **Inheritance by instinct**: the guide's whole point is to pause and consider composition first.

## Code Examples
Composition over inheritance:

```ruby
# Bad — Employees "have" tax data. EmployeeTaxData is not a type of Employee
class EmployeeTaxData < Employee
  def initialize(ssn, salary)
    @ssn = ssn
    @salary = salary
  end

  # ...
end

# Good
class EmployeeTaxData
  def initialize(ssn, salary)
    @ssn = ssn
    @salary = salary
  end

  # ...
end

class Employee
  def initialize(name, email)
    @name = name
    @email = email
  end

  def set_tax_data(ssn, salary)
    @tax_data = EmployeeTaxData.new(ssn, salary)
  end
  # ...
end
```
- **What it demonstrates**: `EmployeeTaxData` stands alone and `Employee` holds one. (The bad subclass's `initialize` also never calls `super`, so its `@name` and `@email` are never set — inheritance that didn't even inherit the state.)

## Reference Tables

| Test (all should hold for inheritance) | `Boeing777 < Airplane` (Ch 4) | `EmployeeTaxData < Employee` |
|---|---|---|
| Genuine "is-a" | ✓ | ✗ (has-a) |
| Reuses base-class code | ✓ (`max_altitude`) | ✗ |
| Base changes should propagate | ✓ | ✗ |
| **Verdict** | inheritance | **composition** |

| Fluent-interface cost | Why it happens |
|---|---|
| Breaks encapsulation | callers depend on every method returning the receiver |
| Breaks decorators | `self` is the wrapped object, so the chain escapes the wrapper |
| Harder to mock | each intermediate return needs stubbing |
| Harder-to-read diffs | one logical statement spans many changes |

## Worked Example
**The same `Car`, two opposite rules.** The JavaScript parent's `Car` returns `this` from every method so callers can write one chained expression. The Ruby port takes the same class and argues the opposite.

The chained version:

```ruby
class Car
  def initialize(make, model, color)
    @make = make
    @model = model
    @color = color
    # NOTE: Returning self for chaining
    self
  end

  def set_make(make)
    @make = make
    # NOTE: Returning self for chaining
    self
  end

  # set_model, set_color, save — each also ends in `self`
end

car = Car.new('Ford','F-150','red')
  .set_color('pink')
  .save
```

Two things are worth seeing. First, the `self` at the end of `initialize` does nothing — `Car.new` returns the new object whatever `initialize` returns. That line is a JavaScript habit carried across, an example of the README's own "may not be idiomatic" disclaimer. Second, every method's return value is now load-bearing: a decorator around `Car` loses control after the first call, and a test double must return itself from each stub.

The guide's version:

```ruby
class Car
  attr_accessor :make, :model, :color

  def initialize(make, model, color)
    @make = make
    @model = model
    @color = color
  end

  def save
    # Save object...
  end
end

car = Car.new('Ford', 'F-150', 'red')
car.color = 'pink'
car.save
```

Writers are generated, `save` returns whatever saving returns, and each statement does one thing. **The transferable rule**: return `self` only from objects whose purpose is to be chained (builders, query relations); everywhere else, a writer returns the value it set and the caller writes another statement.

The same rule — with the same four costs and the same Pivetta citation — appears in the PHP adaptation (piotrplenik/clean-code-php, the source of clean-code-php). Ch 5's caution applies to the fix: `attr_accessor` makes every attribute publicly writable, so prefer `attr_reader` where nothing should set it.

## Key Takeaways
1. **Avoid fluent interfaces** — chaining breaks encapsulation and decorators, complicates mocks, and muddies diffs.
2. **Chaining is fine for builders** such as ActiveRecord queries.
3. **Use writers (`color=`), not `set_color` returning `self`.**
4. **Prefer composition**; inherit only for genuine "is-a" with real code reuse and wanted propagation.
5. **Hold collaborators in instance variables** (`@tax_data`).

## Connects To
- **Ch 4**: the `Airplane` subclasses are the case where all three inheritance tests pass.
- **Ch 5**: `attr_accessor` generates the writers that replace chained setters — with its own smell caveat.
- **Ch 7 (LSP)**: inheritance that fails substitutability is the strongest argument for composition.
- **Ch 8**: "harder to mock" is a testing cost.
- **clean-code-javascript**: its "Use method chaining" rule is the one this port reverses.
- **clean-code-php**: carries the same "Avoid fluent interfaces" rule, word for word in its list of costs.
