# Chapter 5: Classes

## Core Idea
Two rules, both about how objects fit together. **Chain at the call site with cascades (`..`)**, so classes don't have to be designed for chaining, and **prefer composition over inheritance**: hold a collaborator in a field (nullable when it's optional) instead of extending a class you merely *have*.

*(A short chapter; the class-design principles proper are in Ch 6, SOLID.)*

## Frameworks Introduced
- **Use method chaining (cascade notation)**: "It allows your code to be expressive, and less verbose. For that reason, I say, use method chaining and take a look at how clean your code will be."
  - How: instead of repeating the receiver (`car.color = 'pink'; car.save();`), write `Car(…)..color = 'pink'..save();`.
  - **What's Dart-specific**: in the guide's example the `Car` class is *identical* in Bad and Good. Only the call site changes. A cascade applies each operation to the same receiver and evaluates to that receiver, so methods don't need to `return this` — the JavaScript parent's version of this rule required exactly that in every method, including `save()`.
  - When to use: a sequence of operations on one object, typically configuring something you just built.
- **Prefer composition over inheritance**: "As stated famously in *Design Patterns* by the Gang of Four, you should prefer composition over inheritance where you can." The point is not that inheritance is wrong but that "if your mind instinctively goes for inheritance, try to think if composition could model your problem better."
  - **When inheritance makes more sense** — the guide's three-item list:
    1. The relationship is **"is-a"**, not **"has-a"** (Human→Animal vs. User→UserDetails).
    2. You can **reuse code** from the base class ("Humans can move like all animals").
    3. You want **global changes** to derived classes by changing the base ("Change the caloric expenditure of all animals when they move").
  - How (Dart): give the owner a field of the collaborator's type. The guide's `Employee` holds `EmployeeTaxData? taxData` and fills it through `setTaxData(ssn, salary)`.

## Key Concepts
- **Cascade notation (`..`)** — performs a sequence of operations on one object; the whole expression's value is that object, whatever the operations return.
- **Method chaining** — the JavaScript technique of returning `this` from every method; cascades make it unnecessary in Dart.
- **"is-a" vs "has-a"** — the test for `extends` vs a field.
- **Composition** — building an object from other objects held in fields.
- **Nullable field** — `EmployeeTaxData? taxData`; under null safety the type says "an employee may not have tax data yet", and every reader has to handle that case.
- **Super parameters** — `required super.name` in a subclass constructor, forwarding to the superclass constructor (Dart 2.17+); in the Bad example, the visible cost of an inheritance edge.

## Mental Models
- **Think of a cascade as a call-site feature, not a class design.** Any object can be cascaded, so the class stays simple and the chaining decision belongs to whoever is writing the sequence.
- **Use cascades to configure what you own.** A cascade full of setters on an object someone handed you is the argument mutation that Ch 3's side-effects rule warns about, written more compactly.
- **Use the three-item list as a gate, not a menu.** The guide offers it as the cases where inheritance "makes more sense"; if the relationship fails the is-a test, the other two don't rescue it.
- **Let `?` record optional composition.** A nullable field documents "may be absent" in the type, which is more honest than a subclass that always exists.

## Anti-patterns
- **Repeating the receiver** for a run of operations on one object.
- **Adding `return this` to Dart methods to enable chaining**: the cascade already does it, for every class.
- **Inheriting what you merely have** — the guide's Bad `EmployeeTaxData extends Employee`, commented "Bad because Employees 'have' tax data. EmployeeTaxData is not a type of Employee". It also forces tax data to carry `name` and `email` it has no use for.

## Code Examples
Cascade notation — note that `Car` is the same class in both versions:

```dart
class Car {
  String make;
  String model;
  String color;

  Car({
    required this.make,
    required this.model,
    required this.color,
  });

  save() => print('$make, $model, $color');
}

// Bad
final car = Car(make: 'Ford', model: 'F-150', color: 'red');
car.color = 'pink';
car.save();

// Good
final car = Car(make: 'Ford', model: 'F-150', color: 'red')
  ..color = 'pink'
  ..save();
```
- **What it demonstrates**: `car` is bound to the `Car`, not to `save()`'s result; the cascade made chaining possible without touching the class.

## Reference Tables

| Need | Dart tool | Guide's verdict |
|---|---|---|
| Several operations on one object | cascade `..` | Good |
| Chainable API by design | `return this` | not needed in Dart |
| Genuine "is-a" with reusable base code | `extends` + `super` parameters | allowed (three-item list) |
| "has-a" | field of the collaborator's type | Good |
| Optional "has-a" | nullable field (`Type?`) + a method to set it | the guide's Good shape |
| Behaviour shared across unrelated classes | (mixins, `with`) | not covered by the guide |

## Worked Example
**Employee and tax data**: the guide's composition example, read for what the types say.

**Bad** — tax data inherits from employee:

```dart
class Employee {
  String name;
  String email;

  Employee({
    required this.name,
    required this.email,
  });
}

// Bad because Employees "have" tax data. EmployeeTaxData is not a type of Employee
class EmployeeTaxData extends Employee {
  String ssn;
  double salary;

  EmployeeTaxData({
    required this.ssn,
    required this.salary,
    required super.name,
    required super.email,
  });
}
```

Run the three-item gate. *Is-a?* No — tax data is not an employee. *Reuse?* Nothing from `Employee` is used by tax logic. *Global changes?* A change to `Employee` (say, a new required field) would now break every `EmployeeTaxData` construction for no reason. The super parameters are the symptom: tax data has to be built with a name and email.

**Good** — the employee has tax data:

```dart
class EmployeeTaxData {
  String ssn;
  double salary;

  EmployeeTaxData({
    required this.ssn,
    required this.salary,
  });
}

class Employee {
  String name;
  String email;
  EmployeeTaxData? taxData;

  Employee({
    required this.name,
    required this.email,
  });

  void setTaxData(String ssn, double salary) {
    taxData = EmployeeTaxData(ssn: ssn, salary: salary);
  }
}
```

Each class now has one reason to change (Ch 6, SRP). The `?` on `taxData` is the type system recording what the inheritance version couldn't express: an employee can exist before their tax data does. Code that reads `employee.taxData` has to decide what happens when it's `null` — which is a real business question the Bad version hid.

## Key Takeaways
1. **Cascade at the call site** (`..`) instead of repeating the receiver; Dart classes don't need `return this`.
2. **Cascade what you own.** Don't use cascades to mutate objects passed in to you.
3. **Prefer composition**; reach for `extends` only for a genuine is-a with reusable base code and wanted propagation.
4. **Model optional parts as nullable fields** and let null safety make callers handle absence.
5. The guide does **not** cover mixins, Dart's third way to share behaviour; it weighs only `extends` against a field.

## Connects To
- **Ch 3**: cascades plus setters are a compact way to mutate; the side-effects rule still applies.
- **Ch 4**: the classes here use public fields with `required this.x`, Ch 4's default.
- **Ch 6**: SRP is the reason the tax-data split is right; LSP is the reason `Square extends Rectangle` is wrong.
- ***Design Patterns*** (Gamma, Helm, Johnson, Vlissides): the source of "favor composition over inheritance".
- **`clean-code-javascript` Ch 5**: the parent chapter, which also had "Prefer ES2015/ES6 classes" — dropped in the port — and used `return this` for chaining.
