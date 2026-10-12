# Patterns & Techniques — clean-code-php

Concrete refactorings from the guide, each with its trigger and cost.

## Replace a Magic Number with Named Constants
**When to use**: a literal whose meaning isn't evident — `serialize($data, 448)`, `$user->access & 4`.
**How**: use PHP's predefined constants where they exist (`JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE`); otherwise declare `public const` bit flags (`ACCESS_READ = 1`, `ACCESS_CREATE = 2`, …) and combine with `|`, test with `&`, toggle with `^=`.
**Trade-offs**: none; every use site becomes self-describing and greppable. (Ch 2)

## Name Regex Subpatterns
**When to use**: `preg_match()` results read as `$matches[1]`.
**How**: `(?<city>.+?)` and `(?<zipCode>\d{5})`, then `$matches['city']`. Destructuring (`[, $city, $zipCode] = $matches`) is the middle rung — named, but still positional.
**Trade-offs**: a slightly longer pattern; removes the silent shift when a group is added. (Ch 2)

## Flatten with Guard Clauses
**When to use**: nested `if`s, each with its own trailing `return false;`.
**How**: declare the parameter type; return or throw early for edge cases; express branchy rules as data (`in_array(strtolower($day), $openingDays, true)`); throw instead of returning an error string from a typed function.
**Trade-offs**: more exit points, each trivially readable. (Ch 2)

## Replace an `isset()` Ladder with `??`
**When to use**: `if (isset($a)) … elseif (isset($b)) … else …` to pick a value.
**How**: `$name = $_GET['name'] ?? $_POST['name'] ?? 'nobody';`.
**Trade-offs**: none in PHP 7+. Don't substitute `?:`, which tests truthiness. (Ch 3)

## Make Every Comparison Strict
**When to use**: any `==`/`!=`, and `in_array()`/`array_search()` without the strict flag.
**How**: `===`/`!==`; pass `true` as the third argument.
**Trade-offs**: a `'42'` vs `42` mismatch now surfaces instead of passing — which is the point. (Ch 3)

## Typed Default Argument
**When to use**: a fallback computed in the body (`$name ?: 'Hipster Brew Co.'`) or an untyped default.
**How**: `function createMicrobrewery(string $breweryName = 'Hipster Brew Co.'): void`.
**Trade-offs**: callers can no longer pass `null` to mean "use the default" — make it `?string` explicitly if that's wanted. (Ch 4)

## Introduce Value Objects for Long Parameter Lists
**When to use**: a function or constructor with three or more parameters, especially same-typed ones.
**How**: group what travels together into small classes — eight strings become `Name`, `City`, `Contact`; the signature becomes `__construct(Name $name, City $city, Contact $contact)`.
**Trade-offs**: more classes; each can validate itself, and transposed arguments become type errors. (Ch 4)

## Split a Flag Parameter
**When to use**: a `bool` parameter that selects between code paths.
**How**: `createFile($name, $temp)` → `createFile($name)` + `createTempFile($name)`.
**Trade-offs**: two names; each call site now says what it does. (Ch 4)

## Extract Collaborators and Inject Them
**When to use**: a function mixing levels of abstraction, or calling extracted helper functions directly ("Bad too").
**How**: move each level into a class (`Tokenizer::tokenize()`, `Lexer::lexify()`); the orchestrator takes them in `__construct()` and only sequences them.
**Trade-offs**: more wiring; every part is now replaceable and testable alone. (Ch 4, Ch 8)

## Return a Value Instead of Mutating a Global
**When to use**: a function using `global` to change state.
**How**: `splitIntoFirstAndLastName(string $name): array`; the caller keeps both `$name` and `$newName`.
**Trade-offs**: the caller holds the result; nothing else's variable changes type behind its back. (Ch 4)

## Replace a Global Function or Singleton with an Injected Instance
**When to use**: a global `config()` helper, or `DBConnection::getInstance()`.
**How**: a plain class with a public constructor (`Configuration`, `DBConnection`), instantiated once (`new DBConnection($dsn)`) and passed to whoever needs it.
**Trade-offs**: dependencies become visible in signatures — the guide's point; tests no longer need ordering. (Ch 4)

## Encapsulate a Conditional as a Positive Predicate
**When to use**: callers inspect another object's state (`$article->state === 'published'`) or negate a negative (`! isDOMNodeNotPresent()`).
**How**: `$article->isPublished()`; `isDOMNodePresent()`.
**Trade-offs**: none; the representation can change without touching callers. (Ch 5)

## Replace a Type Switch with an Interface
**When to use**: `switch ($this->type)` or an `instanceof` chain.
**How**: declare the operation on an interface (`Airplane::getCruisingAltitude(): int`, `Vehicle::travelTo()`); one class per case; type-hint the interface.
**Trade-offs**: one class per variant; adding a variant adds a file and edits nothing. (Ch 5, Ch 8)

## Replace a Manual Type Check with a Type Declaration
**When to use**: `is_numeric()` / `is_string()` guards on parameters.
**How**: `combine(int $val1, int $val2): int`, and `declare(strict_types=1)` in calling files if numeric strings must be rejected too.
**Trade-offs**: coercive mode still converts `'5'` to `5`; only strict mode makes the declaration as strict as it looks. (Ch 5)

## Delete Dead Code
**When to use**: an unused function beside its replacement.
**How**: delete it; "It will still be safe in your version history."
**Trade-offs**: none. (Ch 5)

## Hide State Behind Operations
**When to use**: callers do arithmetic on a public property (`$bankAccount->balance -= 100`).
**How**: `private $balance` plus `withdraw()` (enforcing the invariant), `deposit()`, `getBalance()`.
**Trade-offs**: more methods; one home for every rule about the state. (Ch 6)

## Narrow Visibility to `private`
**When to use**: any `public` or `protected` member not needed by outside or child classes.
**How**: make it `private`; add a getter only if a caller needs the value.
**Trade-offs**: subclasses lose direct access — intended; the guide treats `protected` as public. (Ch 6)

## Replace Inheritance with Composition
**When to use**: a "has-a" modelled as `extends` (`EmployeeTaxData extends Employee`).
**How**: make the part its own class and hold it as a field (`Employee::setTaxData(EmployeeTaxData $taxData)`).
**Trade-offs**: delegation boilerplate; no inherited coupling. (Ch 7)

## De-chain a Fluent Interface
**When to use**: entity or service setters that `return $this`.
**How**: return `void`; call each setter as its own statement. Keep chaining for builders (query builders, mock builders).
**Trade-offs**: more lines; decorators and mocks work, diffs stay small. (Ch 7)

## Seal a Class Behind an Interface
**When to use**: any concrete class others consume.
**How**: extract an interface holding the public methods; declare the class `final … implements` it; type-hint the interface.
**Trade-offs**: an interface per class; the class can change freely without breaking anyone. (Ch 7)

## Split a Fat Interface by Capability
**When to use**: an implementer forced to write an empty method.
**How**: one interface per capability (`Workable`, `Feedable`), recombined where needed (`interface Employee extends Feedable, Workable`); implement only what applies.
**Trade-offs**: more interface names; no stub methods. (Ch 8)

## Flatten a Broken Subtype into Sibling Implementations
**When to use**: a subclass whose overrides change behaviour callers relied on (`Square extends Rectangle`).
**How**: a shared interface (`Shape::getArea()`), independent implementations, dimensions set in the constructor rather than by setters.
**Trade-offs**: loses the shared base code; restores substitutability. (Ch 8)

## Generalize Near-Miss Duplicates
**When to use**: two functions identical except for names (`showDeveloperList`, `showManagerList`).
**How**: one function over the general concept (`showList(array $employees)`); optionally inline single-use temporaries.
**Trade-offs**: **check first** that the copies change together; if the merge needs a flag, keep them apart. (Ch 9)
