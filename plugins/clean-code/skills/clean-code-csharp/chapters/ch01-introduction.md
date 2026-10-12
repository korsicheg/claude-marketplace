# Chapter 1: Introduction

## Core Idea
Robert C. Martin's *Clean Code* principles, adapted for .NET and written with C# examples: "a guide to producing readable, reusable, and refactorable software in .NET/.NET Core." It says outright: **"This is not a style guide."** It governs structure and design; the one formatting rule it does give (Ch 14) hands formatting to a tool.

## Frameworks Introduced
- **The 3 Rs (readable, reusable, refactorable)**: the stated quality standard behind every rule.
  - When to use: as the tie-breaker when two designs both compile and pass the tests.
  - How: name which of the three a change improves. If it improves none, it is taste, not cleanliness.
- **Guidelines, not laws**: "Not every principle herein has to be strictly followed, and even fewer will be universally agreed upon. These are guidelines and nothing more."
  - When to use: when a rule collides with a real constraint (a framework's API, performance, a deadline).
  - How: override deliberately and say why. Never override by accident.
- **Adaptation lineage**: "Inspired from clean-code-javascript and clean-code-php lists." Most rules, and many examples, are ports of those two documents.
  - When to use: whenever a snippet looks un-C#-like (`explode`, `tokens[] = …`, `'multi-char'` literals). That is a port artifact, not a C# idiom.
  - How: **copy the shape, not the snippet.** Take the before/after transformation; rewrite the syntax in real C#.

## Key Concepts
- **Readable** — a reader can reconstruct intent without running the code or asking the author.
- **Reusable** — the unit can be called from a second site without modification.
- **Refactorable** — the unit can change without a cascade of edits elsewhere.
- **Not a style guide** — brace placement and spacing are delegated to `.editorconfig` (Ch 14).
- **Collective experience** — the rules are "codified over many years of collective experience by the authors of *Clean Code*", not invented for .NET.
- **Port artifact** — a fragment of JavaScript or PHP left in a C# example: single-quoted strings, `explode`, `data.length`, `charCodeAt`, `tokens[] =`.
- **Modernized examples** — the source's latest commit (Feb 2026) rewrote many examples with C# 12 primary constructors and collection expressions; the prose around them is older.

## Mental Models
- **Think of the rules as detectors, not commandments.** Nearly every downstream rule (no flags, ≤2 arguments, one level of abstraction, no type checks) tests for the root rule in Ch 4: *functions should do one thing.*
- **Let the compiler be the referee.** C# is statically typed, so several JavaScript rules change meaning here: "avoid type-checking" becomes "don't escape the type system" (`object`, `dynamic`, `GetType() ==`), and an interface replaces duck typing as the unit of abstraction.
- **Read every example twice**: once for the transformation it teaches, once for what a C# compiler would reject. The first is the content; the second is noise from the port.

## Anti-patterns
- **Treating it as a style guide**: it says it is not one. Formatting debates belong to `.editorconfig`.
- **Pasting snippets verbatim**: many do not compile (`pubic double Balance`, `public BankAccount(balance = 1000)`, `throw new Exception('…')`). The skill's copies are lightly repaired and say so.
- **Strict, unexamined application**: the source pre-empts it — these are guidelines.
- **Assuming JavaScript advice transfers unchanged**: C# has properties, interfaces, records, pattern matching, LINQ, `async`/`await` on `Task`, and typed `catch`. The C# rules route through those.

## Reference Tables

Which C# features the examples rely on — the source never states a target version, so this is read off the code:

| Feature in the examples | C# / .NET version | Where |
|---|---|---|
| Auto-properties `{ get; set; }`, getter-only `{ get; }` | C# 3 / C# 6 | Ch 2, Ch 3, Ch 7 |
| Type pattern `vehicle is Bicycle bicycle` | C# 7.0 | Ch 5 |
| Nullable reference annotation `EmployeeTaxData?` | C# 8 | Ch 8 |
| Positional `record` (`MenuConfig`, `EmployeeTaxData`) | C# 9 / .NET 5 | Ch 4, Ch 8 |
| `IOptions<T>` Options pattern | Microsoft.Extensions.Options (docs link targets ASP.NET Core 2.1) | Ch 6 |
| Primary constructors on classes (`class Employee(string name)`) | C# 12 / .NET 8 | Ch 4, Ch 7, Ch 8, Ch 9 |
| Collection expressions (`["friday", "saturday"]`, `render([...])`) | C# 12 / .NET 8 | Ch 3, Ch 8, Ch 10 |
| async tables (`ConfigureAwait`, `Task.WhenAll`) | .NET Framework 4.5 era (2012–2013 sources) | Ch 12 |

| Source section | Entries | Chapters here |
|---|---|---|
| Naming | 7 | Ch 2 |
| Variables | 10 | Ch 3 |
| Functions | 15 | Ch 4, Ch 5, Ch 6 |
| Objects and Data Structures | 2 | Ch 7 |
| Classes | 2 | Ch 8 |
| SOLID (incl. DRY) | 7 (1 intro) | Ch 9, Ch 10 |
| Testing | 2 (1 intro) | Ch 11 |
| Concurrency | 1 | Ch 12 |
| Error Handling | 5 (1 intro) | Ch 13 |
| Formatting | 1 | Ch 14 |
| Comments | 4 | Ch 15 |

## Worked Example
Reading a ported snippet. The source's capitalization rule (Ch 2) gives this as its **Good** example:

```csharp
const int DaysInWeek = 7;
const int DaysInMonth = 30;

var songs = new List<string> { 'Back In Black', 'Stairway to Heaven', 'Hey Jude' };
var artists = new List<string> { 'ACDC', 'Led Zeppelin', 'The Beatles' };

bool EraseDatabase() {}
bool RestoreDatabase() {}

class Animal {}
class Alpaca {}
```

**Pass 1 — the transformation.** `DAYS_IN_WEEK`/`daysInMonth` became `DaysInWeek`/`DaysInMonth`; `Artists` became `artists`; `Restore_database` became `RestoreDatabase`; `animal` became `Animal`. The rule: one convention per kind of symbol, applied everywhere — PascalCase for constants, methods and types, camelCase for locals.

**Pass 2 — the noise.** `'Back In Black'` is a JavaScript string; in C# single quotes delimit a `char`, so this is a compile error. `bool EraseDatabase() {}` has no `return`. Neither has anything to do with the rule. A clean C# rendering keeps pass 1 and fixes pass 2:

```csharp
const int DaysInWeek = 7;
var artists = new List<string> { "ACDC", "Led Zeppelin", "The Beatles" };
```

**The transferable lesson**: the source's value is in its before/after pairs and the reasons attached to them. Apply the reasons; write the syntax yourself.

## Key Takeaways
1. Judge code on **readable, reusable, refactorable**; name which R a change improves.
2. These are **guidelines** — override them with a stated reason, never by accident.
3. It is **not a style guide**; formatting goes to `.editorconfig` (Ch 14).
4. The source is a **port** of the JavaScript and PHP lists: trust the transformations, not the syntax.
5. The newest examples assume **C# 12 / .NET 8** (primary constructors, collection expressions); the async guidance is a decade older.
6. In C#, lean on the **type system**: many rules become "say it in the signature" rather than "check it at runtime".

## Connects To
- **Ch 4**: "Functions should do one thing" is the root rule the rest detect violations of.
- **Ch 5**: type-checking rules, rewritten for a statically typed language.
- **Ch 14**: the source's one formatting rule — let `.editorconfig` decide.
- **clean-code-javascript** and **clean-code-php**: the two parent lists this one was ported from.
- **clean-code-java**: the book itself; Java is C#'s closest sibling, so its original examples read almost as C#.
