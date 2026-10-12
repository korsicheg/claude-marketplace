# Chapter 3: Functions

## Core Idea
**Functions should do one thing** — "by far the most important rule in software engineering. … If you take nothing else away from this guide other than this, you'll be ahead of many developers." The chapter's other twelve rules (argument count, names, abstraction levels, duplication, flags, side effects, conditionals, dead code) are detectors for violations of it, each satisfied with a Dart mechanism: named `required` parameters, `where` with tear-offs, spread literals, `fold<int>`, and subclass overrides.

## Frameworks Introduced
- **Function arguments (2 or fewer ideally)**: "One or two arguments is the ideal case, and three should be avoided if possible. Anything more than that should be consolidated."
  - Why: fewer parameters make the function easier to test; more than three "leads to a combinatorial explosion where you have to test tons of different cases with each separate argument."
  - **The Dart move — named parameters.** `getMenu(String title, String body, String buttonText, bool cancellable)` becomes `getMenu({required String title, required String body, required String buttonText, required bool cancellable})`, called as `getMenu(title: 'Foo', body: 'Bar', …)`. The guide gives two advantages: (1) "When someone looks at the function signature, it's immediately clear what properties are being used"; (2) "Linters can warn you about unused properties, if they are `required`" — in practice, the analyzer reports a call that omits a `required` argument as an error.
  - Judgment: named parameters fix *call-site readability* and argument order; they don't shrink the test matrix that the rule's rationale is about. Where four parameters travel together, the guide's other fix applies — "most of the time a higher-level object will suffice as an argument."
- **Functions should do one thing**: split `emailClients` (look up, filter, email in one loop) into `emailActiveClients` + `isActiveClient`.
  - How (Dart): the parent becomes a pipeline of **tear-offs** — `clients.where(isActiveClient).forEach(email);` — so it reads as the sentence it implements.
  - Test: if you can only describe it using "and", split it.
- **Function names should say what they do**: `addToDate(date, 1)` → `addMonthsToDate(1, date)`. "It's hard to tell from the function name what is added."
- **Functions should only be one level of abstraction**: "When you have more than one level of abstraction your function is usually doing too much."
  - How: `parseBetterAlternative` stops tokenizing and building the AST itself and calls `tokenize(code)` → `List<String>`, then `lexer(tokens)` → `List<Node>`. Along the way `tokens` gets a **typed collection literal** (`<String>[]`) where the Bad version had an untyped `[]`, and each helper declares its return type.
- **Remove duplicate code**: "Duplicate code is bad because it means that there's more than one place to alter something if you need to change some logic."
  - The restaurant model: one inventory list, one place to update.
  - The caveat: "Getting the abstraction right is critical … Bad abstractions can be worse than duplicate code, so be careful! Having said this, if you can make a good abstraction, do it!"
  - The guide's example is the only Flutter code in it: `buildDeveloperCard` and `buildManagerCard` collapse into `buildEmployeeCard` (see Worked Example).
- **Don't use flags as function parameters**: "Flags tell your user that this function does more than one thing." `createFile(name, temp)` → `createFile(name)` + `createTempFile(name)`.
- **Avoid Side Effects (part 1)**: "A function produces a side effect if it does anything other than take a value in and return another value or values." When an effect is necessary, centralize it: "Don't have several functions and classes that write to a particular file. Have one service that does it. One and only one."
- **Avoid Side Effects (part 2)**: don't mutate collections and objects passed in. `cart.add(item)` → `return [...cart, item];`.
  - The guide's scenario: a retrying `purchase` request and an accidental "Add to Cart" click — the mutated `cart` sends an item the user never meant to buy.
  - Two caveats: genuinely wanting to modify the input is "pretty rare", and cloning big objects can be expensive.
- **Favor functional programming over imperative programming**: Dart "has a functional flavor to it." Replace the index loop with `programmerOutput.fold<int>(0, (previousValue, programmer) => previousValue + programmer.linesOfCode)`.
  - Why `fold`, not `reduce`: in Dart, `reduce` must return the element type (`Programmer`); summing to an `int` needs `fold` with its explicit type argument `<int>`.
- **Encapsulate conditionals**: `programmer.language == 'dart' && programmer.projectsList.isNotEmpty` → `isValidDartProgrammer(programmer)`.
- **Avoid negative conditionals**: `if (!isFileNotValid(file))` → `if (isFileValid(file))`.
- **Avoid conditionals**: "how am I supposed to do anything without an `if` statement?" — polymorphism. `Airplane.getCruisingAltitude()` switching on a `type` string becomes one override each in `Boeing777`, `AirForceOne`, `Cessna`. "When you have classes and functions that have `if` statements, you are telling your user that your function does more than one thing."
- **Remove dead code**: "If it's not being called, get rid of it! It will still be safe in your version history if you still need it."

## Key Concepts
- **Named parameter / `required`** — `{required String title}`; the caller must pass it by name, and omitting it is a compile-time error.
- **Tear-off** — passing a function by name (`where(isActiveClient)`, `forEach(email)`) instead of wrapping it in a closure.
- **Level of abstraction** — the altitude of a statement: orchestration (`tokenize(code)`) vs mechanics (`code.split(' ')`).
- **Side effect** — anything besides values in, value out: a file write, a global mutation, "or accidentally wiring all your money to a stranger."
- **`dynamic`** — opts a variable out of static checking; the side-effect example's Bad version needs it to compile at all.
- **Spread literal** — `[...cart, item]`; builds a new list instead of mutating the argument.
- **`fold<T>`** — `Iterable.fold`, accumulating into a type other than the element type.
- **Predicate function** — a named `bool` function wrapping a condition (`isValidDartProgrammer`, `isFileValid`).
- **Polymorphism** — the subclass override that replaces a `switch` on a type field.

## Mental Models
- **Think of every rule here as a detector for "does more than one thing".** A third argument, a `bool` flag, a mixed-altitude body, a vague verb and a `switch` on `type` are all the same finding.
- **Read the signature as the contract.** `void splitIntoFirstAndLastName()` takes nothing and returns nothing, so anything it does is a side effect. `List<String> splitIntoFirstAndLastName(name)` states its whole effect in its type.
- **Let the type system referee side effects.** The Bad global in the side-effects example is declared `dynamic name = 'Ryan McDermott';` — with `final` or an inferred `String`, `name = name.split(' ')` would not compile. If a refactor needs `dynamic` to let a value change its type, it is a side effect asking to be hidden.
- **Prefer returning a new collection to editing the one you were given.** `[...cart, item]` costs one allocation and removes a whole class of "who changed my list?" bugs.

## Anti-patterns
- **Four positional parameters** (`getMenu(String, String, String, bool)`): a call like `getMenu('Foo', 'Bar', 'Baz', true)` reads as noise.
- **Filtering and acting in one loop** (`if (clientRecord.isActive()) email(client)`).
- **Boolean flags** (`createFile(name, true)`): the caller reads `true` and learns nothing.
- **Mutating a module-level variable** through `dynamic` (`name = name.split(' ')`).
- **Mutating an argument** (`cart.add(item)` inside `addItemToCart`).
- **Index loops with an accumulator** where `fold` states the intent.
- **Double negatives** (`!isFileNotValid(file)`).
- **`switch` on a type string** inside a method (`case '777':`, `case 'Cessna':`).
- **Keeping old versions "just in case"** (`oldRequest` beside `newRequest`).

## Code Examples
Do one thing, as a pipeline of tear-offs:

```dart
// Bad
void emailClients(List<Client> clients) {
  for(final client in clients) {
    final clientRecord = database.lookup(client);
    if (clientRecord.isActive()) {
      email(client);
    }
  }
}

// Good
void emailActiveClients(List<Client> clients) {
  clients
    .where(isActiveClient)
    .forEach(email);
}

bool isActiveClient(Client client) {
  final clientRecord = database.lookup(client);
  return clientRecord.isActive();
}
```
- **What it demonstrates**: the lookup-and-check becomes a named predicate, and the function's new name (`emailActiveClients`) says what the old one hid.

Side effects (part 2), Dart's spread literal:

```dart
// Bad
void addItemToCart(List<int> cart, int item) {
  cart.add(item);
}

// Good
List<int> addItemToCart(List<int> cart, int item) {
  return [...cart, item];
}

final cart = <int>[1, 2];
final newCart = addItemToCart(cart, 3);
print(cart); // [1, 2]
print(newCart); // [1, 2, 3]
```
- **What it demonstrates**: `final` on `cart` only stops *reassignment*; the list itself is still mutable, so the function, not the declaration, has to refuse to mutate it.

## Reference Tables

| Detector | Signal | Fix | Dart mechanism |
|---|---|---|---|
| Argument count | ≥3 parameters | name them, or bundle them | `{required …}` named params; a parameter class |
| Fused loop | filter + act together | extract the predicate | `where(isX).forEach(act)` |
| Vague name | `addToDate` | name the action | `addMonthsToDate` |
| Mixed altitude | orchestration + mechanics | extract each level | typed helpers returning `List<…>` |
| Flag | `bool` selects a path | two functions | `createFile` / `createTempFile` |
| Global mutation | `dynamic` global reassigned | take a value, return a value | typed return |
| Argument mutation | `.add` on a parameter | return a new collection | `[...cart, item]` |
| Accumulator loop | `for (var i …) total +=` | fold | `fold<int>(0, …)` |
| Compound condition | `a && b` inline | named predicate | `bool isValidDartProgrammer(…)` |
| Double negative | `!isNotX` | positive predicate | `isFileValid` |
| Type switch | `switch (type)` | subclass per case | override in each subclass |

**What the Dart port dropped from its JavaScript parent's Functions section**: "Set default objects with Object.assign", "Don't write to global functions" (prototype patching), "Avoid type-checking" parts 1 and 2, and "Don't over-optimize". None has a Dart rule in its place.

## Worked Example
**Remove duplicate code** — the guide's Flutter-flavoured example, and a case where the example itself needs the chapter's own advice.

**Bad** — two widget builders that differ only in where the projects link comes from:

```dart
Widget buildDeveloperCard(Developer developer) {
  return CustomCard(
    expectedSalary: developer.calculateExpectedSalary(),
    experience: developer.getExperience(),
    projectsLink: developer.getGithubLink(),
  );
}

Widget buildManagerCard(Manager manager) {
  return CustomCard(
    expectedSalary: manager.calculateExpectedSalary(),
    experience: manager.getExperience(),
    projectsLink: manager.getMBAProjects(),
  );
}
```

**Good, as the guide writes it** — one builder over a shared `Employee` type:

```dart
Widget buildEmployeeCard(Employee employee) {
  String projectsLink;

  if (employee is Manager) {
    projectsLink = manager.getMBAProjects();
  } else if (employee is Developer) {
    projectsLink = developer.getGithubLink();
  }

  return CustomCard(
    expectedSalary: employee.calculateExpectedSalary(),
    experience: employee.getExperience(),
    projectsLink: projectsLink,
  );
}
```

**Reading it carefully.** The deduplication is right: salary and experience come from `Employee`, so they appear once. But the snippet won't compile as printed: `manager` and `developer` are not in scope (the intent is `employee`, which Dart's `is` check promotes to `Manager` or `Developer` inside each branch), and the non-nullable `projectsLink` isn't definitely assigned when neither branch runs. The repository's history shows the `is` chain replaced an earlier `switch` on `runtimeType`.

**And by the guide's own standard it's a halfway house.** An `is` chain is exactly what Ch 6's Open/Closed rule marks as Bad (`if (shape is Circle) … else if (shape is Square)`), and "Avoid conditionals" above says to replace a type-switch with an override. Applying those rules (this step is not in the guide): declare the varying part on the supertype — a `projectsLink` getter or method on `Employee` that `Manager` and `Developer` override — and `buildEmployeeCard` drops to one `return CustomCard(…)` with no branches. Adding a `Designer` then touches no existing builder.

**The transferable lesson**: deduplicate what is truly shared, and push what varies *into the types*, not into a branch at the call site. If the merged function needs a type test to tell its cases apart, the abstraction isn't finished.

## Key Takeaways
1. **Functions do one thing.** If the description needs "and", split it.
2. **Two arguments or fewer.** Past that, use **named `required` parameters** for readability — and a parameter object when they travel together.
3. **Names say what's done**: `addMonthsToDate`, `emailActiveClients`.
4. **One level of abstraction per function**; give each extracted level a typed return.
5. **Deduplicate carefully**: a bad abstraction can be worse than duplication, and a merge that needs `is` tests isn't finished.
6. **No flag parameters**: two branches, two names.
7. **No hidden side effects**: return values instead of mutating globals or arguments; `[...list, item]` instead of `list.add(item)`; one service per real effect.
8. **`where`/`fold` over index loops; named predicates over inline conditions; overrides over `switch` on a type.**
9. **Delete dead code** — version control keeps it.

## Connects To
- **Ch 2**: naming discipline is the cheapest detector here; `getUser`'s single vocabulary is DRY at the naming level.
- **Ch 5**: cascades and composition are the class-level tools; the parameter object the arguments rule asks for is a class.
- **Ch 6**: "Avoid conditionals" and the duplicate-code example both lead to OCP's abstract method; the `is` chain is OCP's own Bad example.
- **Ch 8, Ch 9**: `Future<void> newRequest(url)` in the dead-code example is the guide's first `Future`; async style and Future errors follow.
- **`clean-code-javascript` Ch 3**: the parent chapter, which has five more rules (listed above) the Dart port dropped.
