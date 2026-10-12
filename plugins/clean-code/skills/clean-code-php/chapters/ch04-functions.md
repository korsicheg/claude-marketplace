# Chapter 4: Functions

*Source: the first half of the guide's Functions section — eight rules on signatures, naming, abstraction and hidden state.*

## Core Idea
A function should do one thing, and its **signature should say so**: typed parameters with defaults, two arguments or fewer, a verb that names the action, no boolean flags. Anything the function reaches for that isn't in its signature — a `global`, a global helper function, a Singleton — is a hidden dependency, and the PHP fix is the same each time: **make it an object and pass the instance in**.

## Frameworks Introduced
- **Use default arguments instead of short circuiting or conditionals** — a three-rung ladder:
  - Not good: `function createMicrobrewery($breweryName = 'Hipster Brew Co.')` — "not good because `$breweryName` can be `NULL`": an untyped parameter accepts anything, including an explicit `null`.
  - Not bad: `$name = null` plus `$breweryName = $name ?: 'Hipster Brew Co.';` — the body now controls the value, at the cost of a second variable and a fallback buried in the body.
  - Good: `function createMicrobrewery(string $breweryName = 'Hipster Brew Co.'): void` — "You can use type hinting and be sure that the `$breweryName` will not be `NULL`."
  - Why it works: the type *and* the default both live in the signature, where callers and tools can see them.
- **Function arguments (2 or fewer ideally)**: "Zero arguments is the ideal case. One or two arguments is ok, and three should be avoided. Anything more than that should be consolidated."
  - Why: "Having more than three leads to a combinatorial explosion where you have to test tons of different cases with each separate argument."
  - How: "Usually, if you have more than two arguments then your function is trying to do too much. In cases where it's not, most of the time a higher-level object will suffice as an argument." The guide applies it to a **constructor**: eight strings become three value objects.
- **Function names should say what they do**: `$message->handle()` → `$message->send()`. "What is this? A handle for the message? Are we writing to a file now?"
- **Functions should only be one level of abstraction**: "When you have more than one level of abstraction your function is usually doing too much. Splitting up functions leads to reusability and easier testing."
  - How: three rungs — one function doing tokenizing, lexing and parsing (Bad); helper *functions* extracted but the parser still calls them directly (Bad too: "still very complex and not testable"); helper **classes** injected through the constructor (Good). See the Worked Example.
- **Don't use flags as function parameters**: "Flags tell your user that this function does more than one thing. Functions should do one thing. Split out your functions if they are following different code paths based on a boolean."
  - How: `createFile(string $name, bool $temp = false)` → `createFile(string $name)` + `createTempFile(string $name)`.
- **Avoid side effects**: a side effect is anything "other than take a value in and return another value or values" — "writing to a file, modifying some global variable, or accidentally wiring all your money to a stranger."
  - How: when a side effect is necessary, **centralize it**: "Don't have several functions and classes that write to a particular file. Have one service that does it. One and only one."
  - Watch for: "sharing state between objects without any structure, using mutable data types that can be written to by anything, and not centralizing where your side effects occur."
- **Don't write to global functions**: a global function such as `config()` "could clash with another library that tried to do the same thing", and the user of your API "would be none-the-wiser until they get an exception in production."
  - How: wrap it in a class (`Configuration`) constructed with its data, and pass the instance where it's needed.
- **Don't use a Singleton pattern**: "Singleton is an anti-pattern." Four reasons, paraphrased in the guide from Brian Button:
  1. Used as a **global instance**, they **hide the dependencies** of your application instead of exposing them through interfaces — "Making something global to avoid passing it around is a code smell."
  2. They violate SRP "by virtue of the fact that **they control their own creation and lifecycle**."
  3. They cause **tight coupling**, which makes faking them out under test difficult.
  4. They carry state for the lifetime of the application, so **tests may need to be ordered** — "a big no for unit tests," which must be independent.
  - The guide also points to Misko Hevery's "Root Cause of Singletons".
  - As written, the guide's "Bad" `getInstance()` calls `new self()` without the constructor's required `$dsn`, which would throw an `ArgumentCountError` — the construction site is hidden even from its own author. The "Good" version makes the constructor public and the DSN explicit: `$connection = new DBConnection($dsn);`.

## Key Concepts
- **Default argument** — a fallback value declared in the signature; combined with a type declaration it rules out `null`.
- **Parameter object / value object** — a small class (`Name`, `City`, `Contact`) that bundles arguments that travel together.
- **Level of abstraction** — the altitude of a statement: orchestration ("tokenize, then lex, then parse") vs mechanics (the loops that do it).
- **Flag argument** — a boolean that selects a code path; evidence of two functions in one.
- **Side effect** — any observable change beyond returning a value: I/O, globals, mutation of shared state.
- **`global` keyword** — PHP's explicit import of a global variable into function scope; the guide's side-effect example.
- **Singleton** — a class holding its only instance in a `private static` property behind a `getInstance()` method and a private constructor.
- **Constructor injection** — passing collaborators (`Tokenizer`, `Lexer`) into `__construct()` instead of reaching for them.

## Mental Models
- **The signature is the contract.** Types, defaults and argument count should tell the whole story; anything else the function touches is a hidden clause.
- **"Hidden dependency" is one smell with three faces** — `global $x`, a global helper function, `Foo::getInstance()`. Each is fixed by constructing an object once and passing it in.
- **Test-pain is the detector.** Many arguments → combinatorial test cases; a Singleton → ordered tests; a non-injectable helper → "not testable." If a function is hard to test, one of these rules is broken.

## Anti-patterns
- **Untyped defaults** (`$breweryName = 'Hipster Brew Co.'` with no type): `null` slips through.
- **Eight-string constructors**: callers can transpose `$city` and `$district` and nothing will notice.
- **Generic verbs** (`handle()`, `process()`): the call site can't say what happens.
- **Half-extracted helpers** that the orchestrator still calls statically: the "Bad too" rung — tidier, still untestable in isolation.
- **Boolean mode switches** (`createFile($name, true)`): the call site reads as a riddle.
- **`global $name;` followed by reassignment**: "If we had another function that used this name, now it'd be an array and it could break it."
- **`DBConnection::getInstance()` everywhere**: the connection becomes an invisible, untestable dependency of every caller.

## Code Examples
```php
// Bad: one constructor, eight strings
class Questionnaire
{
    public function __construct(
        string $firstname,
        string $lastname,
        string $patronymic,
        string $region,
        string $district,
        string $city,
        string $phone,
        string $email
    ) {
        // ...
    }
}

// Good: three value objects (each with a constructor and getters)
class Questionnaire
{
    public function __construct(Name $name, City $city, Contact $contact)
    {
        // ...
    }
}
```
- **What it demonstrates**: the "higher-level object" remedy. `Name` takes `firstname`/`lastname`/`patronymic`, `City` takes `region`/`district`/`city`, `Contact` takes `phone`/`email` — each a class with private properties and getters. Each group can now be validated once and reused.

```php
// Bad
$name = 'Ryan McDermott';

function splitIntoFirstAndLastName(): void
{
    global $name;

    $name = explode(' ', $name);
}

// Good
function splitIntoFirstAndLastName(string $name): array
{
    return explode(' ', $name);
}

$name = 'Ryan McDermott';
$newName = splitIntoFirstAndLastName($name);
```
- **What it demonstrates**: the side-effect fix is to take a value and return a value. `$name` stays a string; the split lives in `$newName`.

## Reference Tables

| Hidden dependency | Why it hurts | Replace with |
|---|---|---|
| `global $name;` | silently changes a variable's meaning (and type) for every other reader | parameter in, return value out |
| global `function config(): array` | name clashes with other libraries; can't be swapped | `new Configuration([...])`, passed in |
| `DBConnection::getInstance()` | hides dependencies, owns its lifecycle, couples, orders tests | `new DBConnection($dsn)`, passed in |
| `tokenize($code)` called from inside `parse()` | can't substitute or test the parts separately | `Tokenizer` injected via `__construct()` |

| Argument count | Guide's verdict |
|---|---|
| 0 | "the ideal case" |
| 1–2 | "ok" |
| 3 | "should be avoided" |
| 4+ | "should be consolidated" into a higher-level object |

## Worked Example
**One level of abstraction**, all three rungs on `parseBetterPHPAlternative()`.

**Bad** — tokenizing, lexing and parsing loops in one function body.

**Bad too** — the loops move into `tokenize(string $code): array` and `lexer(array $tokens): array`, and the parser becomes:

```php
function parseBetterPHPAlternative(string $code): void
{
    $tokens = tokenize($code);
    $ast = lexer($tokens);
    foreach ($ast as $node) {
        // parse...
    }
}
```

Readable — but the parser is hard-wired to those two global functions, so it "is still very complex and not testable."

**Good** — "The best solution is move out the dependencies of `parseBetterPHPAlternative()` function":

```php
class BetterPHPAlternative
{
    private $tokenizer;
    private $lexer;

    public function __construct(Tokenizer $tokenizer, Lexer $lexer)
    {
        $this->tokenizer = $tokenizer;
        $this->lexer = $lexer;
    }

    public function parse(string $code): void
    {
        $tokens = $this->tokenizer->tokenize($code);
        $ast = $this->lexer->lexify($tokens);
        foreach ($ast as $node) {
            // parse...
        }
    }
}
```

`Tokenizer::tokenize()` and `Lexer::lexify()` hold the extracted loops. The JavaScript parent stops at extracting functions; the PHP guide takes one more step, to **classes injected through the constructor**, because in PHP that is what makes the parts substitutable in a test. It is the same move the guide later names Dependency Inversion (Ch 8).

## Key Takeaways
1. **Put the type and the default in the signature**: `string $name = 'X'`, not `$name ?: 'X'` in the body.
2. **Two arguments or fewer**; at four or more, consolidate into value objects — constructors included.
3. **Name the action** (`send()`), never the plumbing (`handle()`).
4. **One level of abstraction per function** — and in PHP, extract to injectable classes, not just helper functions.
5. **No boolean flags**; write two functions.
6. **Take a value, return a value.** Centralize unavoidable side effects in one service.
7. **No `global`, no global helper functions, no Singletons** — construct the object once and pass it in.

## Connects To
- **Ch 3**: `?:` (the default-argument "Not bad" rung) vs `??` (used in `Configuration::get()`).
- **Ch 5**: the rest of the Functions section — conditionals, type-checking, dead code.
- **Ch 7**: value objects like `Name` and `Contact` are composition at work; Ch 7's `EmployeeTaxData` is the same idea.
- **Ch 8 (SOLID)**: the Singleton breaks SRP by the guide's own argument; constructor injection is DIP.
- **clean-code-java ch03 (Functions)**: the book's argument ladder, Command Query Separation and output arguments, which this guide omits.
