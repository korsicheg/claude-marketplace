# Chapter 2: Naming

## Core Idea
"A good name allows the code to be used by many developers. The name should reflect what it does and give context." In C# that means: say what a thing is *for*, never what *type* it is, and follow one capitalization convention per kind of symbol — PascalCase for types, methods, properties and constants; camelCase for locals and parameters.

## Frameworks Introduced
- **Avoid using bad names** — `int d;` → `int daySinceModification;`.
  - When to use: any single-letter or abbreviated name outside a tiny scope.
  - How: make the name answer "what does this hold, and why does it exist?"
- **Avoid misleading names** — "Name the variable to reflect what it is used for."
  - When to use: names that describe *where data came from* instead of *what it is*.
  - How: `var dataFromDb = db.GetFromService().ToList();` → `var listOfEmployee = _employeeService.GetEmployees().ToList();`. The source of the data is an implementation detail; the content is the meaning.
- **Avoid Hungarian notation** — "Hungarian Notation restates the type which is already present in the declaration. This is pointless since modern IDEs will identify the type."
  - When to use: `iCounter`, `strFullName`, `dModifiedDate`, and **parameters too**: `pDay`, `pAmount`.
  - How: drop the prefix. `int counter; string fullName; DateTime modifiedDate;` and `IsShopOpen(string day, int amount)`.
- **Use consistent capitalization** — "These rules are subjective, so your team can choose whatever they want. The point is, no matter what you all choose, just be consistent."
  - How (the source's Good example): constants `DaysInWeek`, `DaysInMonth`; methods `EraseDatabase`, `RestoreDatabase`; types `Animal`, `Alpaca`; locals `songs`, `artists`.
- **Use pronounceable names** — "It will take time to investigate the meaning of the variables and functions when they are not pronounceable."
  - How: `sWorkDate` → `StartWorkingDate`; `modTime` → `ModificationTime`. Note these are **properties**, so they also move to PascalCase.
- **Use camelCase notation** for "variable and method parameters."
  - How: `employeephone` → `employeePhone`; `CalculateSalary(int workingdays, int workinghours)` → `CalculateSalary(int workingDays, int workingHours)`.
- **Use domain names** — "People who read your code are also programmers. Naming things right will help everyone be on the same page."
  - When to use: when a well-known pattern or computer-science term already names what the code does.
  - How: borrow the programmer's vocabulary (the source's example uses Singleton vocabulary: `GetInstance()`), so nobody needs the concept explained.

## Key Concepts
- **Hungarian notation** — encoding the type in the name (`str`, `i`, `d`, and `p` for parameters). The declaration and the IDE already say it.
- **PascalCase** — `DaysInWeek`; .NET's convention for types, methods, properties and `const` fields.
- **camelCase** — `workingDays`; the convention for locals and parameters.
- **Misleading name** — a name that describes provenance (`dataFromDb`) or a type it no longer has.
- **Pronounceable name** — one you can say in a code review without spelling it out.
- **Domain name** — a name from the solution domain (pattern names, algorithm names) that programmers already share.

## Mental Models
- **The declaration already knows the type; the name should know the purpose.** `string strFullName` says "string" twice and "full name" once.
- **Capitalization is a type tag the compiler doesn't check.** In C#, case tells the reader the *kind* of symbol: `DaysInWeek` (a constant or member), `daysInWeek` (a local). Mixing conventions makes the reader re-learn which is which on every line. Ch 14's `.editorconfig` makes the convention checkable.
- **Test a name by saying it aloud in review.** If you have to spell it (`s-work-date`), rename it.

## Anti-patterns
- **Type prefixes** on locals, fields *or* parameters (`pDay`). The source calls them "pointless".
- **Provenance names** — `dataFromDb`, `resultFromService`. The data's meaning outlives its source.
- **Mixed conventions in one codebase** — `DAYS_IN_WEEK` beside `daysInMonth`, `EraseDatabase` beside `Restore_database`, `class animal` beside `class Alpaca`.
- **Unpronounceable abbreviations** with a comment explaining them ("what the heck is this").

## Code Examples
Hungarian notation, including the parameter case the source calls out separately:

```csharp
// Bad
int iCounter;
string strFullName;
DateTime dModifiedDate;

public bool IsShopOpen(string pDay, int pAmount) { /* some logic */ }

// Good
int counter;
string fullName;
DateTime modifiedDate;

public bool IsShopOpen(string day, int amount) { /* some logic */ }
```
- **What it demonstrates**: the type is in the declaration; the name carries only the meaning.

Pronounceable names on properties:

```csharp
// Bad
public class Employee
{
    public DateTime sWorkDate { get; set; } // what the heck is this
    public DateTime modTime { get; set; }   // same here
}

// Good
public class Employee
{
    public DateTime StartWorkingDate { get; set; }
    public DateTime ModificationTime { get; set; }
}
```
- *Source snippet lightly repaired: `Datetime` → `DateTime`.*

## Reference Tables

The capitalization the source's examples and `.editorconfig` (Ch 14) settle on:

| Symbol | Convention | Source example |
|---|---|---|
| Class, record, interface | PascalCase | `Animal`, `Alpaca`, `MenuConfig`, `IAdapter` |
| Method | PascalCase | `RestoreDatabase()`, `CalculateSalary()` |
| Property | PascalCase | `StartWorkingDate`, `Make` |
| `const` field | PascalCase | `DaysInWeek` |
| Local variable, parameter | camelCase | `artists`, `workingDays` |
| Private / internal field | `_camelCase` | `_employeeService`, `_balance` |
| Static field | `s_camelCase` | (`.editorconfig` rule only) |

## Worked Example
The source's **Use domain names** example is the weakest in this chapter and worth reading carefully. It shows a class built on Singleton vocabulary (condensed; the source writes block bodies and comments every line):

```csharp
public class SingleObject
{
    private static SingleObject _instance = new SingleObject();
    private SingleObject() {}
    public static SingleObject GetInstance() => _instance;
    public string ShowMessage() => "Hello World!";
}

var singletonObject = SingleObject.GetInstance();
singletonObject.ShowMessage();
```

What the rule means: `GetInstance()` is a name every programmer recognizes, so the reader knows the lifecycle without reading the body. That is the "same page" the source promises.

What to ignore: the example itself is a Singleton, and the same source tells you in Ch 6, **"Don't use a Singleton pattern"**. Its entry point is even Java (`public static void main(String[] args)`). Take the naming lesson — use the shared vocabulary of patterns and algorithms (`Visitor`, `Factory`, `Queue`, `Hash`) when your code *is* that thing — and not the design.

## Key Takeaways
1. Name the **purpose**, not the type or the provenance: `daySinceModification`, `listOfEmployee`, not `d`, `dataFromDb`.
2. **No Hungarian notation**, on fields, locals or parameters.
3. **One capitalization convention per symbol kind**, applied everywhere; .NET's is PascalCase for types/members/constants, camelCase for locals/parameters.
4. If you can't **pronounce** it, rename it.
5. Use **domain vocabulary** programmers already share — but naming a thing after a pattern doesn't make the pattern a good idea.

## Connects To
- **Ch 3**: the variable rules continue this chapter (searchable, explanatory, same vocabulary).
- **Ch 6**: the Singleton the domain-name example uses is the anti-pattern argued there.
- **Ch 14**: `.editorconfig` turns the capitalization table into analyzer suggestions.
- **clean-code-java** ch02 (Meaningful Names): the full list — intention-revealing, avoid disinformation, solution vs problem domain names.
