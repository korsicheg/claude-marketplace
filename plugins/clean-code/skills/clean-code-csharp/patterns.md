# Patterns & Techniques — clean-code-csharp

Concrete refactorings from the guide, each with its trigger and cost.

## Drop the Type Prefix
**When to use**: a name encodes its type — `iCounter`, `strFullName`, `dModifiedDate`, or a parameter `pDay`.
**How**: delete the prefix; the declaration already states the type.
**Trade-offs**: none; renames are one IDE action. (Ch 2)

## Guard Clause, then a Flat Happy Path
**When to use**: nested `if`/`else`, an `else` after a `return`, or a ladder of `else if` returning `true`/`false`.
**How**: invert each precondition into an early `return`/`throw`; replace value ladders with data and LINQ — `string[] openingDays = [...]; return openingDays.Any(d => d == day.ToLower());`.
**Trade-offs**: inverting conditions can shift a boundary (`<` → `>=`, not `>` — the source's own Fibonacci slips here); pin boundaries with a test first. (Ch 3)

## Promote a Literal to a `const` or an `enum`
**When to use**: a string or number whose meaning isn't obvious and may recur — `"Admin"`, `4`.
**How**: `const string AdminRole = "Admin";`; coded values become `enum` members. PascalCase, per the `.editorconfig`.
**Trade-offs**: one more symbol; every use is now findable and refactorable. (Ch 3)

## Anonymous Object → Named Type
**When to use**: `var data = new { … }` that travels, is serialized, or is compared.
**How**: declare the type (`Person`) and use it; serializers get `typeof(Person)`, readers get a searchable name.
**Trade-offs**: a declaration to maintain; a `record` keeps it to one line. (Ch 3)

## Name the Regex Groups
**When to use**: regex results read by position.
**How**: `(?<city>…)` and `(?<zipCode>…)`, read with `match.Groups["city"]`.
**Trade-offs**: longer pattern; inserting a group no longer shifts every index. (Ch 3)

## Default Argument Instead of Body Defaulting
**When to use**: `name ?? "X"` or `!string.IsNullOrEmpty(name) ? name : "X"` at the top of a method.
**How**: `CreateMicrobrewery(string breweryName = "Hipster Brew Co.")`.
**Trade-offs**: defaults must be compile-time constants; a caller can still pass `null` explicitly. (Ch 3)

## Record Parameter Object
**When to use**: three or more related parameters.
**How**: `public record MenuConfig(string Title, string Body, string ButtonText, bool Cancellable);`, built with named arguments and passed as one parameter.
**Trade-offs**: one more type; you gain value equality, immutability and a self-describing call site. (Ch 4)

## Split a Flag into Two Methods
**When to use**: a `bool` parameter that selects a path.
**How**: `CreateFile(name, temp)` → `CreateFile(name)` + `CreateTempFile(name)`.
**Trade-offs**: two names; each does one thing and reads correctly at the call site. (Ch 4)

## Extract the Filter as a LINQ Query
**When to use**: a loop that looks up, filters and acts in one body.
**How**: `GetActiveClients(clients)` returning `db.Find(clients).Where(c => c.Status == "Active").ToList()`; the caller acts on the result.
**Trade-offs**: an extra method; each half is testable alone. (Ch 4)

## Climb the Abstraction Ladder to Injected Classes
**When to use**: one method tokenizes, lexes and parses.
**How**: (1) extract methods; (2) move each level into its own class (`Tokenizer`, `Lexer`); (3) inject them — `class BetterJSAlternative(Tokenizer tokenizer, Lexer lexer)`.
**Trade-offs**: more types; the orchestrator becomes testable with substitutes once the dependencies are interfaces. (Ch 4, Ch 9)

## Return Instead of Rewrite
**When to use**: a `void` method that rewrites shared or outer state.
**How**: take the value as a parameter and return the result — `string SplitAndEnrichFullName(string name)`. Centralize unavoidable effects in one service.
**Trade-offs**: the caller holds the result; repeat calls become safe. (Ch 4)

## Newspaper Order
**When to use**: helpers declared above, below and between their callers.
**How**: public entry point first, each helper directly below its first caller.
**Trade-offs**: none; no tool enforces it, so it takes review attention. (Ch 4)

## Replace a Type-Code `switch` with an Interface
**When to use**: `switch (_type)` or `if (name == "…")` selecting behaviour.
**How**: an interface (`IAirplane`, `IAdapter`) with one implementation per case; callers call the method.
**Trade-offs**: more classes; a new case is a new class, and no working method is edited. (Ch 5, Ch 9)

## Type Pattern at the Boundary
**When to use**: you must branch on types you don't own and can't give a shared abstraction.
**How**: `if (vehicle is Bicycle bicycle) bicycle.PeddleTo(…);` instead of `GetType() == typeof(Bicycle)` plus `as`.
**Trade-offs**: still grows with each new type — keep it at boundaries, prefer an abstraction elsewhere. (Ch 5)

## Put the Type in the Signature
**When to use**: `object` or `dynamic` parameters guarded by `TryParse` or type checks.
**How**: `Combine(int val1, int val2)`; let the compiler reject bad calls.
**Trade-offs**: none in statically typed code; it deletes code. (Ch 5)

## Encapsulate a Conditional
**When to use**: `article.state == "published"` at call sites.
**How**: `article.IsPublished()` on the owning type.
**Trade-offs**: one member; the literal and the rule now live in one place. (Ch 5)

## Singleton → Constructor + Options Pattern
**When to use**: `X.GetInstance()` or a global configuration method.
**How**: a public constructor taking `IOptions<TOptions>` (or the data); resolve the instance from the IoC container; classes that need it declare it in their constructors.
**Trade-offs**: wiring at the composition root; dependencies become visible and fakeable, and tests stop depending on order. (Ch 6)

## Field → Property + Intention-Revealing Methods
**When to use**: `public double Balance = 1000;` that callers mutate directly.
**How**: private `_balance`, get-only `Balance`, and `WithdrawBalance`/`DepositBalance` enforcing the rules.
**Trade-offs**: a few more lines; validation, logging and lazy loading can now be added without touching callers. (Ch 7)

## Primary Constructor + Get-Only Property
**When to use**: a settable property assigned once in a constructor.
**How**: `class Employee(string name) { public string Name { get; } = name; }`.
**Trade-offs**: C# 12+; don't use the captured parameter directly in methods, where it behaves as a hidden mutable field. (Ch 7)

## Fluent Extension Methods
**When to use**: a type you don't own whose mutators return `void`.
**How**: a `static` class of `this T` extensions that perform the call and `return` the receiver.
**Trade-offs**: the source's versions mutate in place — make that clear in the names, or return new values instead. (Ch 8)

## Has-a via Record + Nullable Property
**When to use**: a subclass created only to reuse members (`EmployeeTaxData : Employee`).
**How**: `record EmployeeTaxData(string Ssn, double Salary);` held as `EmployeeTaxData? TaxData { get; private set; }` and set by `SetTax`.
**Trade-offs**: callers handle `null`; no accidental propagation from the base class. (Ch 8)

## Siblings Under an Abstract Base (LSP)
**When to use**: a subclass overrides to protect its own invariant (`Square : Rectangle`).
**How**: `abstract class ShapeBase { abstract double GetArea(); }` with `Rectangle` and `Square` as siblings; give dimensions at construction so consumers call only `GetArea()`/`Render()`.
**Trade-offs**: no shared mutators; a consumer that still type-tests means the base is missing an operation. (Ch 9)

## Role Interfaces
**When to use**: an implementer forced to stub a method (`Robot.Eat()`).
**How**: split into `IWorkable`, `IFeedable`; compose with `interface IEmployee : IFeedable, IWorkable`; implement only what applies.
**Trade-offs**: more interface names; consumers depend on exactly what they use. (Ch 9)

## Inject a Collection of Implementations
**When to use**: a class holds several concrete workers (`Manager(Robot, Human)`).
**How**: `class Manager(IEnumerable<IEmployee> employees)`; the DI container supplies every registered implementation.
**Trade-offs**: order and membership are decided at registration; adding a worker type edits no consumer. (Ch 9)

## Merge Near-Miss Duplicates over a Shared Abstraction
**When to use**: `ShowDeveloperList` and `ShowManagerList` with identical bodies.
**How**: one `ShowList(IEnumerable<Employee>)` over a base or interface exposing the shared calls; then compact with a collection expression.
**Trade-offs**: if the merge needs a flag or a type test, stop — "bad abstractions can be worse than duplicate code". (Ch 10)

## One Concept per Test, in AAA
**When to use**: a test method that reassigns its subject and asserts several scenarios.
**How**: one `[Fact]` per behaviour, named for it (`HandleLeapYear`), with `// Arrange`, `// Act`, `// Assert`.
**Trade-offs**: more methods; a failure names one cause, and later cases still run. (Ch 11)

## Blocking → Awaitable Twin
**When to use**: `.Result`, `.Wait()`, `WaitAll`, `WaitAny`, `Thread.Sleep` in async code.
**How**: `await`, `await Task.WhenAll`, `await Task.WhenAny`, `await Task.Delay`; make the caller `async Task` too.
**Trade-offs**: async spreads up the call chain — by design ("async all the way"). (Ch 12)

## Typed Catch Blocks, Rethrow with `throw;`
**When to use**: `if (ex is …)` inside one `catch (Exception)`, `throw ex;`, or an empty `catch`.
**How**: one `catch` per type, most specific first; `throw;` after logging; `throw new CustomException("context", ex)` to add information.
**Trade-offs**: none; the stack trace and the cause survive. (Ch 13)

## Commit an `.editorconfig`
**When to use**: mixed tabs and spaces, or naming conventions enforced only by review.
**How**: a root `.editorconfig` with formatting, `dotnet_style_*`/`csharp_style_*` preferences and `dotnet_naming_rule` blocks.
**Trade-offs**: `suggestion` severity only nudges; raise severities to enforce. (Ch 14)

## WHAT Comment → Name; Keep the WHY
**When to use**: comments narrating what lines do.
**How**: extract a variable or method named after the comment (`ConvertTo32BitInt`); keep comments that record decisions (why djb2). Delete banners, `#region`, commented-out code and journals.
**Trade-offs**: none; names can't drift from the code the way comments do. (Ch 15)
