# Chapter 5: Classes

## Core Idea
Reach for classes only when objects get large and complex — then use **ES2015/ES6 class syntax**, return `this` for chaining, and prefer **composition over inheritance** unless the relationship is genuinely "is-a".

## Frameworks Introduced
- **Prefer ES2015/ES6 classes over ES5 plain functions**: the ES5 prototype idiom is unreadable for inheritance, construction, and method definition.
  - When to use: when you have decided you need a class at all.
  - How: `class X {}` / `extends` / `super()` instead of constructor functions, `Object.create`, and manual `constructor` reassignment.
  - Important caveat the guide attaches: "prefer small functions over classes until you find yourself needing larger and more complex objects" — and "if you need inheritance (**and be aware that you might not**)".
- **Use method chaining**: return `this` at the end of every mutating class method.
  - When to use: builder-style and configuration-style APIs — the pattern used by jQuery and Lodash.
  - How: end each setter with `return this;`, letting callers write `new Car("Ford", "F-150", "red").setColor("pink").save()`.
  - Why it works: expressive and less verbose — the object flows through the calls instead of being re-named on every line.
- **Prefer composition over inheritance**: from *Design Patterns* (Gang of Four).
  - When to use: as the default. "If your mind instinctively goes for inheritance, try to think if composition could model your problem better."
  - How: hold the collaborator as a field (`this.taxData = new EmployeeTaxData(...)`) rather than extending it.
  - **The three tests for when inheritance IS right** — the chapter's most reusable decision rule:
    1. The relationship is genuinely **"is-a"**, not "has-a" (Human→Animal, *not* User→UserDetails).
    2. You can **reuse code from the base class** (humans move like all animals).
    3. You want **global changes to derived classes** by changing the base (change caloric expenditure for all animals when they move).

## Key Concepts
- **is-a vs has-a** — the relationship test that decides inheritance vs composition. `EmployeeTaxData` is not a kind of `Employee`; an `Employee` *has* tax data.
- **Method chaining** — returning `this` so calls compose into one expression.
- **Fluent interface** — the API style method chaining produces (jQuery, Lodash).
- **Prototype boilerplate** — the ES5 `Object.create` + `prototype.constructor` + `instanceof` guard ritual that ES6 classes replace.
- **`super()`** — base-class constructor call, replacing `Animal.call(this, age)`.
- **Composition** — modeling a relationship by holding an instance rather than extending a type.

## Mental Models
- **Think of a class as a late-stage optimization.** Start with small functions (Ch 3) and factory objects (Ch 4); promote to a class only when the object is genuinely large and complex.
- **Use "is-a or has-a?" as the inheritance gate.** Say the sentence out loud. "An EmployeeTaxData is an Employee" is false, so `extends` is wrong.
- **Think of `return this` as the price of a fluent API.** It is one line per method and it must be on *every* method, including `save()`.
- **Inheritance is a coupling decision, not a reuse shortcut.** The three tests exist because reuse alone is not sufficient reason.

## Anti-patterns
- **ES5 constructor-function hierarchies**: the `if (!(this instanceof Animal)) throw` guard, `Animal.call(this, age)`, `Mammal.prototype = Object.create(Animal.prototype)`, `Mammal.prototype.constructor = Mammal` — three lines of ceremony per level, and easy to get subtly wrong.
- **Reaching for a class when a function would do**: the guide's explicit ordering is small functions first.
- **Inheriting a "has-a" relationship** (`class EmployeeTaxData extends Employee`): the guide's own bad example — "Employees *have* tax data. EmployeeTaxData is not a type of Employee."
- **Setters that return `undefined`**: forces `car.setColor("pink"); car.save();` across separate statements and blocks chaining entirely.
- **Chaining partially**: one method missing `return this` breaks the chain at an arbitrary point with a confusing `undefined` error.

## Code Examples
ES6 classes vs the ES5 ritual (the good side; the bad side runs three times longer):

```javascript
class Animal {
  constructor(age) {
    this.age = age;
  }
  move() { /* ... */ }
}

class Mammal extends Animal {
  constructor(age, furColor) {
    super(age);
    this.furColor = furColor;
  }
  liveBirth() { /* ... */ }
}

class Human extends Mammal {
  constructor(age, furColor, languageSpoken) {
    super(age, furColor);
    this.languageSpoken = languageSpoken;
  }
  speak() { /* ... */ }
}
```
- **What it demonstrates**: `extends` + `super()` express the same three-level hierarchy that ES5 needed `Object.create`, manual `constructor` reassignment, and `instanceof` guards for.

Composition over inheritance:

```javascript
// Bad — Employees "have" tax data. EmployeeTaxData is not a type of Employee
class EmployeeTaxData extends Employee {
  constructor(ssn, salary) {
    super();
    this.ssn = ssn;
    this.salary = salary;
  }
}

// Good
class EmployeeTaxData {
  constructor(ssn, salary) {
    this.ssn = ssn;
    this.salary = salary;
  }
}

class Employee {
  constructor(name, email) {
    this.name = name;
    this.email = email;
  }

  setTaxData(ssn, salary) {
    this.taxData = new EmployeeTaxData(ssn, salary);
  }
}
```
- **What it demonstrates**: the bad version gives every `EmployeeTaxData` a `name` and `email` it has no business having, and calls `super()` with no arguments to get there.

## Reference Tables

Inheritance decision table — use `extends` only when all three hold:

| Test | Question | Example (pass) | Example (fail) |
|---|---|---|---|
| 1. Relationship | Is it "is-a", not "has-a"? | Human → Animal | User → UserDetails |
| 2. Code reuse | Can the subclass reuse base-class code? | Humans move like all animals | — |
| 3. Global change | Do you want base changes to propagate to all derived classes? | Change caloric expenditure of all animals | — |

ES5 → ES6 translation:

| ES5 | ES6 |
|---|---|
| `const Animal = function(age) {...}` | `class Animal { constructor(age) {...} }` |
| `if (!(this instanceof Animal)) throw ...` | unnecessary — classes throw without `new` |
| `Animal.prototype.move = function move() {}` | `move() {}` inside the class body |
| `Mammal.call(this, age)` | `super(age)` |
| `Mammal.prototype = Object.create(Animal.prototype)` | `class Mammal extends Animal` |
| `Mammal.prototype.constructor = Mammal` | automatic |

## Worked Example
**Method chaining**, walked end to end — the smallest change in the chapter with the largest effect on the call site.

Before, every setter returns `undefined`:

```javascript
class Car {
  constructor(make, model, color) {
    this.make = make;
    this.model = model;
    this.color = color;
  }

  setMake(make) { this.make = make; }
  setModel(model) { this.model = model; }
  setColor(color) { this.color = color; }
  save() { console.log(this.make, this.model, this.color); }
}

const car = new Car("Ford", "F-150", "red");
car.setColor("pink");
car.save();
```

Three statements, and `car` is repeated on each. After — one added line per method:

```javascript
class Car {
  constructor(make, model, color) {
    this.make = make;
    this.model = model;
    this.color = color;
  }

  setMake(make) {
    this.make = make;
    // NOTE: Returning this for chaining
    return this;
  }

  setModel(model) {
    this.model = model;
    // NOTE: Returning this for chaining
    return this;
  }

  setColor(color) {
    this.color = color;
    // NOTE: Returning this for chaining
    return this;
  }

  save() {
    console.log(this.make, this.model, this.color);
    // NOTE: Returning this for chaining
    return this;
  }
}

const car = new Car("Ford", "F-150", "red").setColor("pink").save();
```

**Two details that are easy to miss:**
- `save()` returns `this` too. The guide chains it deliberately — a terminal method that returns `undefined` silently caps the chain and makes `.save().anythingElse()` a runtime error.
- The whole expression now evaluates to the car, so `const car = ...` still binds the object, not the return of `save()`.

**When not to do this:** chaining reads well for configuration and building. It reads badly when methods return *different* things — a method that genuinely needs to return a computed value should return it, not `this`.

## Key Takeaways
1. Prefer small functions to classes; promote to a class only for larger, more complex objects.
2. When you do need a class, use **ES6 class syntax** — never the ES5 prototype ritual.
3. You may not need inheritance at all. Check it against the three tests before typing `extends`.
4. **Composition is the default**; inheritance requires a true "is-a" relationship plus reuse plus a desire for base-class changes to propagate.
5. `return this` from every mutating method to enable chaining — including terminal methods like `save()`.
6. `EmployeeTaxData extends Employee` is the canonical mistake: "has-a" modeled as "is-a".

## Connects To
- **Ch 6 (SOLID)**: LSP is the formal statement of what goes wrong when inheritance is used for a non-"is-a" relationship (Square/Rectangle); DIP shows composition wired through constructor injection.
- **Ch 4 (Objects and Data Structures)**: the closure/factory approach is where you stay until an object justifies a class.
- **Ch 3 (Functions)**: "Avoid conditionals" produces subclasses — the payoff needs ES6 class syntax to stay readable.
- **Gang of Four, *Design Patterns***: the cited source for "prefer composition over inheritance".
