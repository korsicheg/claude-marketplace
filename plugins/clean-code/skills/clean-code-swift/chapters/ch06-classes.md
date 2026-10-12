# Chapter 6: Classes

## Core Idea
Two class-design rules: **chain mutators by returning `self`** — "use method chaining and see how your code becomes cleaner" — and **prefer composition over inheritance** unless the relationship is genuinely "is-a". In Swift, an optional stored property models "has-a, maybe", and `@discardableResult` keeps chains free of unused-result warnings.

## Frameworks Introduced
- **Method chaining**: "This pattern is very useful in Swift, and you'll find it in many libraries. It allows your code to be expressive and less verbose… In your class functions, just return `self` at the end of each function, and you can chain more class methods on it."
  - When to use: configuring an object through several setters in a row.
  - How: each mutator returns `self`; keep the stored properties `private` so the chain is the only way in. The guide's "Summary of Errors in the Bad Example" lists what a chain must not do: allow invalid states, expose properties for unrestricted modification, or "hide potential issues" by chaining without error handling.
- **Prefer composition over inheritance**: "As famously stated in the *Design Patterns* book by the Gang of Four, you should prefer composition over inheritance where you can." The test: "if your mind instinctively goes for inheritance, try to think if composition could better model your problem."
  - **When inheritance makes more sense** — the guide's three tests:
    1. "Your inheritance represents an 'is-a' relationship and not a 'has-a' relationship (Human→Animal vs. User->UserDetails)."
    2. "You can reuse code from the base classes (Humans can move like all animals)."
    3. "You want to make global changes to derived classes by changing only the base class. (Changing the caloric cost for all animals when they move)."
  - How: if any test fails, hold the other type as a property instead of subclassing it.

## Key Concepts
- **Method chaining / fluent interface** — mutators that return `self`, so calls read as one sentence: `car.setColor("pink").save()`.
- **`@discardableResult`** — attribute that silences the unused-result warning when a chainable method ends a chain; the guide's Bad `Car` uses it, its Good `Car` doesn't.
- **"Is-a" vs "has-a"** — the test between inheritance and composition (`EmployeeTaxData` is not a kind of `Employee`; an `Employee` *has* tax data).
- **Composition** — building a type from other types held as properties.
- **Optional stored property** — `var taxData: EmployeeTaxData?`; the composed part may not exist yet.
- **Reference semantics** — returning `self` from a class mutator chains on the same instance.

## Mental Models
- **Say the relationship out loud.** "Tax data *is an* employee" is false, so `EmployeeTaxData: Employee` is wrong whatever code it saves.
- **Inheritance must pass all three tests; composition needs none.** Default to composition; reach for a subclass only when "is-a", shared code and base-wide change all hold.
- **A chain is only as safe as its setters.** Fluency doesn't validate anything; the guide's Bad chain ends in `Brand: , Speed: -10`.

## Code Examples
Composition — `Employee` *has* optional tax data:

```swift
class EmployeeTaxData {
  var ssn: String
  var salary: Double

  init(ssn: String, salary: Double) {
    self.ssn = ssn
    self.salary = salary
  }
}

class Employee {
  var name: String
  var email: String
  var taxData: EmployeeTaxData?

  init(name: String, email: String) {
    self.name = name
    self.email = email
  }

  func setTaxData(ssn: String, salary: Double) {
    self.taxData = EmployeeTaxData(ssn: ssn, salary: salary)
  }
}
```

- **What it demonstrates**: the "has-a" relationship as a property; the optional says an employee can exist before tax data does.

Method chaining, the guide's Good version:

```swift
class Car {
  private var make: String
  private var model: String
  private var color: String

  init(make: String, model: String, color: String) {
    self.make = make
    self.model = model
    self.color = color
  }

  func setMake(_ make: String) -> Car {
    self.make = make
    return self
  }

  func setColor(_ color: String) -> Car {
    self.color = color
    return self
  }

  func save() -> Car {
    print("\(self.make) \(self.model) \(self.color)")
    return self
  }
}

let car = Car(make: "Ford", model: "F-150", color: "red")
car.setColor("pink").save()
```

(`setModel(_:)` follows the same pattern.)

## Reference Tables

The three inheritance tests, applied to the guide's examples:

| Test | Human → Animal | EmployeeTaxData → Employee |
|---|---|---|
| "Is-a", not "has-a" | ✓ a human is an animal | ✗ an employee *has* tax data |
| Reuses base-class code | ✓ humans move like all animals | ✗ tax data uses nothing of `Employee` |
| Base-wide changes are wanted | ✓ change the caloric cost of moving for all | ✗ |
| Verdict | inheritance is defensible | compose |

## Worked Example
Composition over inheritance, from the wrong hierarchy to the right shape.

**Bad** — inheritance used to attach data:

```swift
class Employee {
  var name: String
  var email: String

  init(name: String, email: String) {
    self.name = name
    self.email = email
  }
}

// Bad because Employees "have" tax data. EmployeeTaxData is not a type of Employee
class EmployeeTaxData: Employee {
  var ssn: String
  var salary: Double

  init(name: String, email: String, ssn: String, salary: Double) {
    self.ssn = ssn
    self.salary = salary
    super.init(name: name, email: email)
  }
}
```

Run the three tests. *Is-a*: tax data is not an employee — fails. *Code reuse*: nothing in `EmployeeTaxData` uses `Employee`'s behaviour; it only borrows the fields — fails. *Base-wide change*: a change to `Employee` should not ripple into tax records — fails. The symptom shows in the initializer: building tax data requires a name and an email.

**Good** — the code under Code Examples. `EmployeeTaxData` stands alone with only `ssn` and `salary`; `Employee` holds it as `taxData: EmployeeTaxData?` and creates it through `setTaxData(ssn:salary:)`. Each type now has one reason to change (Ch 7), and an employee no longer has to be built with tax data it may not have yet.

## Source Caveats
- **Method chaining**: the Good `Car` differs from the Bad one mainly in making its properties `private` and dropping `@discardableResult`; neither version validates input, so the Bad version's "Lack of Validation" error is not actually fixed. The commentary credits the Good version with "Using `Result` allows each step in the chain to handle errors gracefully", but no `Result` appears in the code.
- Without `@discardableResult`, `car.setColor("pink").save()` triggers an unused-result warning, because `save()` returns a `Car` nobody reads.
- The rule is stated for classes. On a `struct`, a method returning `self` returns a copy, so a chain of value-type "setters" builds a new value rather than configuring the original — a distinction the source doesn't draw.

## Anti-patterns
- **Inheriting to borrow fields** (`EmployeeTaxData: Employee`): fails the "is-a" test and forces nonsense initializers.
- **Fluent setters with no validation**: the chain reads well and stores `""` and `-10`.
- **Public stored properties alongside chainable setters**: two ways to mutate, one of them uncontrolled.
- **Instinctive inheritance**: "if your mind instinctively goes for inheritance, try to think if composition could better model your problem."

## Key Takeaways
1. **Chainable mutators return `self`**; mark the last link `@discardableResult` if its result is often unused.
2. **Keep chained state `private`** so the chain is the only door — and validate in it.
3. **Default to composition.** Inherit only when "is-a", code reuse and base-wide change all hold.
4. **Model optional parts as optional properties** (`taxData: EmployeeTaxData?`).

## Connects To
- **Ch 5**: getters and setters, the validation the chained setters here still lack.
- **Ch 7 (SRP, LSP)**: splitting tax data from the employee is SRP; Square/Rectangle is what happens when "is-a" is taken at face value.
- **Ch 8 (ISP)**: `GoodStylableView` holds a `StyleConfigurable` as a property — composition through a protocol.
- **`clean-code-java`** (ch10, Classes): class size and cohesion, which this guide's two class rules don't address.
