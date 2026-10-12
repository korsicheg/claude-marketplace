# Chapter 4: Methods, continued — Duplication, Conditionals, Type-Checking and Dead Code

## Core Idea
The second half of the guide's Methods section. Remove duplication — carefully; name your conditions as **predicate methods**; replace `case` on a type with **polymorphism**; replace `is_a?` checks with **duck typing**; and delete what nobody calls. The through-line: "When you have classes and methods that have `if` statements, you are telling your user that your method does more than one thing."

## Frameworks Introduced
- **Remove duplicate code**: "Duplicate code is bad because it means that there's more than one place to alter something if you need to change some logic."
  - The restaurant model: keep one inventory list, not several — "If you only have one list, there's only one place to update!"
  - The cause: "two or more slightly different things, that share a lot in common", so you build "an abstraction that can handle this set of different things with just one method/module/class."
  - **The caveat**: "Getting the abstraction right is critical, that's why you should follow the SOLID principles … Bad abstractions can be worse than duplicate code, so be careful! Having said this, if you can make a good abstraction, do it!"
- **Encapsulate conditionals**: give a compound condition a name.
  - How: `params[:message].present? && params[:recipient].present?` → `def send_message?(params)`, then `if send_message?(params)`.
- **Avoid negative conditionals**: `if !genres.blank?` → `unless genres.blank?`, or better, the positive predicate `if genres.present?`.
- **Avoid conditionals**: "how am I supposed to do anything without an `if` statement?" — "you can use polymorphism to achieve the same task in many cases."
  - How: a `case @type` inside `Airplane#cruising_altitude` becomes one subclass per case (`Boeing777`, `AirForceOne`, `Cessna`), each with its own `cruising_altitude`.
  - Why: "a method should only do one thing … Remember, just do one thing."
- **Avoid type-checking (part 1)**: "Ruby is dynamically typed, which means your methods can take any type of argument. Sometimes you are bitten by this freedom." The first remedy: **consistent APIs**.
  - How: an `is_a?(Bicycle)` / `is_a?(Car)` chain calling `pedal` or `drive` becomes one message, `vehicle.move(...)`, that both types answer.
- **Avoid type-checking (part 2)**: for basic values (strings, integers) where polymorphism isn't available, consider **contracts.ruby** — "The problem with manually type-checking Ruby is that doing it well requires so much extra verbiage that the faux 'type-safety' you get doesn't make up for the lost readability. Keep your Ruby clean, write good tests, and have good code reviews."
- **Remove dead code**: "Dead code is just as bad as duplicate code." "If it's not being called, get rid of it! It will still be safe in your version history if you still need it."

## Key Concepts
- **Duplicate code** — logic that exists in more than one place, so a change must be made in more than one place.
- **Bad abstraction** — a merge of things that don't vary together; "can be worse than duplicate code".
- **Predicate method** — a `?`-suffixed method naming a condition (`send_message?`).
- **`unless`** — Ruby's negated `if`; the guide's first fix for `if !x`.
- **`present?` / `blank?`** — ActiveSupport (Rails) predicates for "has content" / "is empty or nil"; the guide uses them without comment.
- **Polymorphism** — dispatching on the receiver's class instead of on a `case` inside one class.
- **Duck typing** — accepting any object that answers the message you send, regardless of class.
- **Consistent API** — one message name (`move`) across types, so callers needn't ask which type they hold.
- **contracts.ruby** — a gem adding declarative runtime contracts to methods; the guide's suggestion for primitive-value checks.
- **Faux type-safety** — the guide's term for hand-written `is_a?` guards: verbose, partial, and not worth the lost readability.
- **Dead code** — code nothing calls; version control keeps it if you need it back.

## Mental Models
- **The conditional-removal ladder** — climb only as far as the case requires:
  1. compound condition → **named predicate method** (`send_message?`);
  2. negative condition → **`unless`** or a **positive predicate** (`present?`);
  3. `case` on the object's own type → **a subclass per case**;
  4. `is_a?` on an argument → **one message every type answers** (`move`);
  5. type guards on primitives → **contracts.ruby**, or nothing at all — tests and review.
- **Think of a type check as a missing method.** If you must ask *what* an object is, some object should have been asked *to do* something instead.
- **Deduplicate the logic, not the appearance.** If merging two methods needs a role branch, ask whether the variation is real before merging.

## Anti-patterns
- **Copy-paste methods that differ in one field** (`show_developer_list` / `show_manager_list`).
- **A bad abstraction merged for tidiness**: the guide's explicit warning.
- **Inline compound conditions** repeated across call sites.
- **Double negatives**: `if !genres.blank?`.
- **`case @type` inside a class**: every new type edits the method.
- **`is_a?` chains** dispatching to differently named methods (`pedal` vs `drive`).
- **Hand-rolled primitive type guards** (`val1.is_a?(Numeric) && val2.is_a?(Numeric)`): "faux type-safety".
- **Keeping the old implementation "just in case"** (`old_request_module`): version history already does that.

## Code Examples
Remove duplicate code — the guide's merge:

```ruby
def show_employee_list(employees)
  employees.each do |employee|
    data = build_data(employee)
    render(data)
  end
end

def build_data(employee)
  general_data = {
    expected_salary: employee.expected_salary,
    experience: employee.experience
  }

  general_data.merge(position_specific_data(employee))
end

def position_specific_data(employee)
  case employee.type
  when 'manager'
    { portfolio: employee.mba_projects }
  when 'developer'
    { github_link: employee.github_link }
  end
end
```
- **What it demonstrates**: the shared fields live in one place and only the difference branches. Note the residual `case employee.type`: by this chapter's own "Avoid conditionals" rule it is the next refactoring target — a `position_specific_data` method on each employee class. The guide stops one rung short.

Avoid type-checking — part 1 and part 2:

```ruby
# Bad
def travel_to_texas(vehicle)
  if vehicle.is_a?(Bicycle)
    vehicle.pedal(@current_location, Location.new('texas'))
  elsif vehicle.is_a?(Car)
    vehicle.drive(@current_location, Location.new('texas'))
  end
end

# Good
def travel_to_texas(vehicle)
  vehicle.move(@current_location, Location.new('texas'))
end

# Bad
def combine(val1, val2)
  if (val1.is_a?(Numeric) && val2.is_a?(Numeric)) ||
     (val1.is_a?(String) && val2.is_a?(String))
    return val1 + val2
  end

  raise 'Must be of type String or Numeric'
end

# Good
def combine(val1, val2)
  val1 + val2
end
```
- **What it demonstrates**: in part 1, a shared message (`move`) makes the check unnecessary; in part 2, the guide accepts the dynamic behaviour (`+` already raises on incompatible operands) and moves the safety net to tests and review.

## Reference Tables

| Smell | Ruby fix | Rule |
|---|---|---|
| `a.present? && b.present?` inline | `def send_message?(params)` | Encapsulate conditionals |
| `if !genres.blank?` | `unless genres.blank?` / `if genres.present?` | Avoid negative conditionals |
| `case @type` in one class | subclass per case | Avoid conditionals |
| `is_a?` chain on an argument | one shared message | Avoid type-checking (1) |
| `is_a?(Numeric)` guards on primitives | contracts.ruby, or tests + review | Avoid type-checking (2) |
| `old_request_module` beside `new_request_module` | delete it | Remove dead code |

## Worked Example
**Avoid conditionals — the `Airplane` refactoring.**

The bad version keeps every variant inside one method:

```ruby
class Airplane
  # ...
  def cruising_altitude
    case @type
    when '777'
      max_altitude - passenger_count
    when 'Air Force One'
      max_altitude
    when 'Cessna'
      max_altitude - fuel_expenditure
    end
  end
end
```

Every new aircraft type edits this method, and the method answers three questions at once. The guide's fix moves each branch onto the type it describes:

```ruby
class Airplane
  # ...
end

class Boeing777 < Airplane
  # ...
  def cruising_altitude
    max_altitude - passenger_count
  end
end

class AirForceOne < Airplane
  # ...
  def cruising_altitude
    max_altitude
  end
end

class Cessna < Airplane
  # ...
  def cruising_altitude
    max_altitude - fuel_expenditure
  end
end
```

The `@type` string disappears; the class *is* the type. Callers send `cruising_altitude` and never branch. Adding a fourth aircraft is a new class, not an edit — which is exactly the Open/Closed Principle of Ch 7, arrived at from the conditional side. Note that the guide reaches for inheritance here; Ch 6's composition rule still applies when the variants share no real "is-a" relationship.

**The transferable rule**: a `case` whose `when` arms are type names is a list of classes waiting to be written.

## Key Takeaways
1. **Remove duplication** — one place to change each piece of logic — but **bad abstractions can be worse than duplicate code**.
2. **Name compound conditions** as `?` predicate methods.
3. **State conditions positively**: `unless x.blank?` or `if x.present?`, never `if !x.blank?`.
4. **Replace `case` on a type with a subclass per case.**
5. **Replace `is_a?` chains with one message** every type answers.
6. **Don't hand-roll primitive type checks**; use contracts.ruby if you must, otherwise trust tests and review.
7. **Delete dead code** — version control remembers it.

## Connects To
- **Ch 3**: "Avoid conditionals" is justified by "do one thing"; flag parameters are the argument-level form of the same problem.
- **Ch 6**: the `Airplane` hierarchy uses inheritance; the composition rule decides when not to.
- **Ch 7 (OCP, LSP)**: the adapter refactoring is this chapter's `is_a?` fix applied to a class; subclasses must stay substitutable.
- **Ch 8**: with no type checker, tests are the safety net the guide sends you to.
- **Ch 11**: commented-out code is dead code in disguise.
- **clean-code-javascript**: its type-checking rule points to TypeScript; the Ruby port points to contracts.ruby instead.
