# Patterns & Techniques — clean-code-dart

Concrete refactorings from the guide, each with its trigger, the Dart move, and its cost.

## Name the Magic Value with `const`
**When to use**: a bare literal whose meaning isn't obvious at the call site (`Duration(minutes: 32)`).
**How**: `const setupTimeInMinutes = 32;` — `const` if known at compile time, `final` if assigned once at run time, lowerCamelCase, type inferred. Put the unit in the name.
**Trade-offs**: none; the value becomes greppable and self-describing. (Ch 2)

## Explanatory `final` for Positional Access
**When to use**: list indices or other positional values passed straight into a call (`saveCityZipCode(address[1], address[2])`).
**How**: `final city = address[1]; final zipCode = address[2];` then call with the names.
**Trade-offs**: two extra lines; the call now reads as what it means. (Ch 2)

## Default Parameter Value Instead of `??`
**When to use**: a nullable optional parameter whose only purpose is a constant fallback (`{String? name}` + `name ?? '…'`).
**How**: `{String breweryName = 'Hipster Brew Co.'}`; the parameter becomes non-nullable.
**Trade-offs**: defaults must be compile-time constants. For a computed fallback (`DateTime.now()`), keep `T?` + `??`. (Ch 2)

## Named `required` Parameters for Long Signatures
**When to use**: a function taking three or more positional parameters.
**How**: wrap them in `{}` and mark each `required`; callers write `getMenu(title: 'Foo', body: 'Bar', …)`.
**Trade-offs**: longer call sites, no order mistakes; doesn't reduce the number of cases to test. If the parameters travel together, bundle them into a class instead. (Ch 3)

## Extract a Predicate, Filter with a Tear-off
**When to use**: a loop that both selects and acts (`if (clientRecord.isActive()) email(client)`).
**How**: `bool isActiveClient(Client client)`; then `clients.where(isActiveClient).forEach(email);` and rename the function for what it now does (`emailActiveClients`).
**Trade-offs**: one more function; each piece is testable alone. (Ch 3)

## Extract Abstraction Levels into Typed Helpers
**When to use**: one function tokenizes, builds a tree and walks it.
**How**: `List<String> tokenize(String code)`, `List<Node> lexer(List<String> tokens)`; the parent calls them in order. Type the collection literals (`<String>[]`).
**Trade-offs**: more functions; each level is reusable and testable. (Ch 3)

## Merge Near-Duplicates over a Supertype
**When to use**: two functions differing only in the concrete type they take (`buildDeveloperCard`, `buildManagerCard`).
**How**: one function over the supertype (`buildEmployeeCard(Employee employee)`) for everything shared. Push what varies into the types (an overridden member), not into an `is` chain.
**Trade-offs**: "Bad abstractions can be worse than duplicate code" — if the merge needs type tests or a flag, it isn't finished. (Ch 3, Ch 6)

## Split a Flag Parameter
**When to use**: a `bool` parameter that selects between code paths.
**How**: `createFile(name, temp)` → `createFile(name)` + `createTempFile(name)`.
**Trade-offs**: two names; each does one thing and reads correctly where it's called. (Ch 3)

## Return a Value Instead of Mutating a Global
**When to use**: a function that rewrites a module-level variable (`dynamic name` reassigned to a list).
**How**: take the value as a parameter, return the result with a declared type: `List<String> splitIntoFirstAndLastName(name)`.
**Trade-offs**: the caller holds the result. Removing `dynamic` lets the type checker catch the next attempt. (Ch 3)

## Return a New Collection Instead of Mutating an Argument
**When to use**: a function that calls `.add`/`.remove` on a list it was given.
**How**: `return [...cart, item];` and let the caller decide which list to keep.
**Trade-offs**: an allocation per call; cloning big objects "can be very expensive". The guide names no Dart immutability library. (Ch 3)

## Centralize a Side Effect in One Service
**When to use**: several functions or classes write to the same file or resource.
**How**: "Have one service that does it. One and only one."
**Trade-offs**: one more indirection; one place to change, audit and fake. (Ch 3)

## `fold` Instead of an Accumulator Loop
**When to use**: `var total = 0; for (var i = 0; …) total += …;`.
**How**: `list.fold<int>(0, (previousValue, x) => previousValue + x.linesOfCode)`.
**Trade-offs**: none for simple sums; `reduce` won't work when the result type differs from the element type. (Ch 3)

## Encapsulate a Condition / Make It Positive
**When to use**: a compound condition inline, or a negatively named predicate used with `!`.
**How**: `bool isValidDartProgrammer(Programmer p)`; rename `isFileNotValid` → `isFileValid`.
**Trade-offs**: none. (Ch 3)

## Replace a Type Switch with Subclass Overrides
**When to use**: a method that `switch`es on a type field (`case '777':`) or a function with an `is` chain.
**How**: declare the method on an abstract supertype (`abstract class Shape { double getArea(); }`); each subtype overrides it with `@override`.
**Trade-offs**: more classes; adding a variant no longer edits existing code. (Ch 3, Ch 6)

## Field Instead of Pass-through Accessors
**When to use**: a private field with a getter and setter that only pass the value through.
**How**: make it a public field with an initializing formal (`BankAccount({this.balance = 0})`). Add a getter/setter later, when there's logic; callers don't change.
**Trade-offs**: none in Dart; field and getter look the same to callers. (Ch 4)

## Make Internal State Private
**When to use**: a field outside code shouldn't read or write.
**How**: `String _name;` set from a public named parameter: `Employee({required String name}) : _name = name;`.
**Trade-offs**: privacy is per library (file); classes in the same file still see it. (Ch 4)

## Cascade Instead of Repeating the Receiver
**When to use**: several operations in a row on one object.
**How**: `Car(…)..color = 'pink'..save();`. No `return this` needed in the class.
**Trade-offs**: compact mutation; use it on objects you own, not ones passed in. (Ch 5)

## Compose with a (Nullable) Field Instead of Extending
**When to use**: `B extends A` where B is something A *has* (`EmployeeTaxData extends Employee`).
**How**: B stands alone; A holds `B? b` and a method to set it (`setTaxData`).
**Trade-offs**: callers must handle `null`; that is the honest model of "may not exist yet". (Ch 5)

## Split a Class by Reason to Change
**When to use**: a class with two jobs (`UserSettings` that also verifies credentials).
**How**: extract `UserAuth`; `UserSettings` holds one and delegates.
**Trade-offs**: two classes to wire; inject the extracted one to satisfy DIP too. (Ch 6)

## Siblings Under an Abstract Parent (LSP)
**When to use**: a subclass overrides a parent's setters to keep its own invariant (`Square extends Rectangle`).
**How**: `abstract class Shape { double getArea(); }`; `Rectangle(width:, height:)` and `Square(length:)` both extend it.
**Trade-offs**: lose the "a square is a rectangle" reuse; gain correct results through the shared type. (Ch 6)

## Segregate a Fat Interface
**When to use**: an implementer contains `throw UnimplementedError()`.
**How**: one abstract class per capability (`Book`, `DownloadableBook`); `implements A, B` for classes that have both.
**Trade-offs**: more types; consumers can ask for exactly the capability they use. (Ch 6)

## Inject an Abstract Dependency
**When to use**: a class builds its collaborator (`final requester = InventoryRequester();`).
**How**: make the collaborator an `abstract class`, add `required this.requester` typed as it, construct the concrete class at the top level.
**Trade-offs**: callers do the wiring; implementations swap with a one-word change and tests can pass a fake. (Ch 6)

## One `test` per Concept, `group` per Unit
**When to use**: a test that checks several behaviours, especially by reassigning a variable.
**How**: `group('String', …)` with `test('.split() …')` and `test('.trim() …')`, each with its own `const` input.
**Trade-offs**: more test cases; each failure names its behaviour. (Ch 7)

## Wrap a `.then` Chain in an `async` Function
**When to use**: `await` applied to a `.then(…)` chain, or `.then` callbacks anywhere `await` is available.
**How**: `Future<String> getAlbumTitle() async { final response = await …; return title; }`.
**Trade-offs**: none; errors then flow through ordinary `try`/`catch`. (Ch 8)

## Typed Catch with a Plan
**When to use**: `catch (error) { print(error); }` or `.onError((e, s) { print(e); })`.
**How**: `on Exception catch (e, s)` (or `.onError((e, s) …)`), then log with `error:`/`stackTrace:`, notify the user, or report to a service.
**Trade-offs**: if there's no plan, remove the `try`/`catch` and let the error propagate. (Ch 9)

## Order Members Caller-First
**When to use**: a class whose methods appear in arbitrary order.
**How**: depth-first walk of the call graph: entry point, then each method it calls followed by that method's helpers.
**Trade-offs**: reordering churn once; the file then reads top-down. (Ch 10)

## Delete Comment Noise
**When to use**: narrating comments, commented-out code, journal headers, banner markers.
**How**: delete them; keep only comments that explain business-logic complexity.
**Trade-offs**: none — version control has the history. (Ch 11)
