# Chapter 4: Functions

## Core Idea
**"Functions should do one thing"** — "by far the most important rule in software engineering … If you take nothing else away from this guide other than this, you'll be ahead of many developers." The other rules in this chapter — two arguments or fewer, no boolean flags, names that say what they do, one level of abstraction, no side effects — are detectors for breaking it. The C# adaptation's distinctive moves: a **`record`** as the parameter object, **LINQ** for the extracted filter, and, at the top of the abstraction ladder, **classes injected through a primary constructor**.

## Frameworks Introduced
- **Functions should do one thing** — "When functions do more than one thing, they are harder to compose, test, and reason about. When you can isolate a function to just one action, they can be refactored easily and your code will read much cleaner."
  - How: if you need "and" to describe it, split it. `SendEmailToListOfClients` that looks up, filters *and* emails → `GetActiveClients` (a LINQ `Where`) + the sending loop.
- **Function arguments (2 or fewer ideally)** — "Limiting the amount of function parameters is incredibly important because it makes testing your function easier. Having more than three leads to a combinatorial explosion."
  - The ladder: "Zero arguments is the ideal case. One or two arguments is ok, and three should be avoided. Anything more than that should be consolidated."
  - Why: "Usually, if you have more than two arguments then your function is trying to do too much. In cases where it's not, most of the time a higher-level object will suffice as an argument."
  - How (C#): a positional **`record`** — `public record MenuConfig(string Title, string Body, string ButtonText, bool Cancellable);` — constructed with **named arguments** (`Title: "Foo"`), passed as one parameter.
- **Function names should say what they do** — `message.Handle()` ("What is this? A handle for the message? Are we writing to a file now?") → `message.Send()` ("Clear and obvious").
- **Functions should only be one level of abstraction** — "When you have more than one level of abstraction your function is usually doing too much. Splitting up functions leads to reusability and easier testing." The source marks this entry "Not finished yet", but its three tiers are complete (see Worked Example).
- **Function callers and callees should be close** — "If a function calls another, keep those functions vertically close in the source file. Ideally, keep the caller right above the callee. We tend to read code from top-to-bottom, like a newspaper."
- **Avoid flags in method parameters** — "A flag indicates that the method has more than one responsibility … Split the method into two if a boolean parameter adds multiple responsibilities to the method."
  - How: `CreateFile(string name, bool temp = false)` → `CreateFile(string name)` + `CreateTempFile(string name)`.
- **Avoid side effects** — "A function produces a side effect if it does anything other than take a value in and return another value or values … writing to a file, modifying some global variable, or accidentally wiring all your money to a stranger."
  - How: take a value in, return a value out. Where an effect is genuinely needed, **centralize it**: "Don't have several functions and classes that write to a particular file. Have one service that does it. One and only one."
- **Remove dead code** — "Dead code is just as bad as duplicate code … If it's not being called, get rid of it! It will still be safe in your version history if you still need it."

## Key Concepts
- **Do one thing** — the function performs a single action at a single level of abstraction.
- **Parameter object** — one type bundling related arguments; in C#, idiomatically a positional `record`.
- **Named arguments** — `new MenuConfig(Title: "Foo", …)`; each value labelled at the call site.
- **Flag parameter** — a `bool` that selects between code paths.
- **Level of abstraction** — orchestration (`Tokenize`, then `Lexify`) vs mechanics (the regex loop inside).
- **Side effect** — anything besides taking values in and returning values out.
- **Newspaper order** — callers above callees, so the file reads top-down.
- **Dead code** — code nothing calls; version control is its archive.

## Mental Models
- **Every rule here is a symptom test for "do one thing".** Third argument? Boolean flag? Vague verb like `Handle`? Orchestration mixed with loops? Each says the function does more than one thing.
- **Arguments multiply test cases.** Each one adds a dimension to the case matrix; the budget is really a testing budget.
- **A `bool` parameter is two methods that got merged.** The call site `CreateFile(name, true)` can't say which one it wants; `CreateTempFile(name)` can.
- **Ask "what if I call it twice?"** A method that rewrites a shared variable gives a different answer the second time; a pure one doesn't.
- **The abstraction ladder ends in types.** Extracting methods is the middle rung; the C# source's top rung moves each level into its own class and injects it.

## Anti-patterns
- **Filter-and-act in one loop** — lookup, `IsActive()` check and `Email()` fused in one `foreach`.
- **Four positional parameters**, especially with a trailing `bool`.
- **Vague verbs** — `Handle`, `Process`, `Manage`.
- **Mutating outer state** — the source's bad `SplitAndEnrichFullName()` overwrites a shared `name`: "If we had another function that used this name … it could break it."
- **Several writers for one resource** — "one service that does it. One and only one."
- **Keeping `OldRequestModule` beside `NewRequestModule`** "just in case".
- **Helpers scattered above and below their callers** — the reader scrolls instead of reads.

## Code Examples
Do one thing — extract the filter as a LINQ query:

```csharp
// Bad
public void SendEmailToListOfClients(string[] clients)
{
    foreach (var client in clients)
    {
        var clientRecord = db.Find(client);
        if (clientRecord.IsActive())
        {
            Email(client);
        }
    }
}

// Good
public void SendEmailToListOfClients(string[] clients)
{
    var activeClients = GetActiveClients(clients);
    // Do some logic
}

public List<Client> GetActiveClients(string[] clients)
{
    return db.Find(clients).Where(s => s.Status == "Active").ToList();
}
```
- *Source snippet lightly repaired: `.ToList()` added so the return type matches.* The `"Active"` literal is itself a magic string (Ch 3).

A `record` as the parameter object:

```csharp
// Bad
public void CreateMenu(string title, string body, string buttonText, bool cancellable) { /* ... */ }

// Good
public record MenuConfig(
    string Title,
    string Body,
    string ButtonText,
    bool Cancellable);

var config = new MenuConfig(
    Title: "Foo",
    Body: "Bar",
    ButtonText: "Baz",
    Cancellable: true);

public void CreateMenu(MenuConfig config) { /* ... */ }
```
- **What it demonstrates**: one declaration line gives you an immutable, value-equal bundle; named arguments keep the call site self-describing.

Side effects — return instead of rewrite:

```csharp
// Bad — rewrites a shared variable
var name = "Ryan McDermott";

public void SplitAndEnrichFullName()
{
    var temp = name.Split(" ");
    name = $"His first name is {temp[0]}, and his last name is {temp[1]}"; // side effect
}

// Good — value in, value out
public string SplitAndEnrichFullName(string name)
{
    var temp = name.Split(" ");
    return $"His first name is {temp[0]}, and his last name is {temp[1]}";
}

var name = "Ryan McDermott";
var fullName = SplitAndEnrichFullName(name);
Console.WriteLine(name);     // Ryan McDermott
Console.WriteLine(fullName); // His first name is Ryan, and his last name is McDermott
```

Callers above callees — `PerformanceReview` in newspaper order, with a C# 12 primary constructor:

```csharp
class PerformanceReview(Employee employee)
{
    public PerfReviewData PerfReview()
    {
        GetPeerReviews();
        GetManagerReview();
        GetSelfReview();
    }

    private IEnumerable<PeerReviews> GetPeerReviews()
    {
        var peers = LookupPeers();
        // ...
    }

    private IEnumerable<PeersData> LookupPeers() => db.Lookup(employee, "peers");

    private ManagerData GetManagerReview() => LookupManager();

    private ManagerData LookupManager() => db.Lookup(employee, "manager");

    private EmployeeData GetSelfReview() { /* ... */ }
}
```
- *Condensed; the source writes block bodies and single-quoted strings.* The Bad version declares `LookupPeers`, `LookupManager` and `GetPeerReviews` *before* the public `PerfReview` that uses them.

## Reference Tables

| Detector | Signal | Fix |
|---|---|---|
| Argument count | 3+ parameters | `record` parameter object + named arguments |
| Flag | `bool` selecting a path | Two methods: `CreateFile` / `CreateTempFile` |
| Vague verb | `Handle`, `Process` | Name the action: `Send` |
| Mixed altitude | Orchestration + loops | Extract methods, then classes |
| Shared mutable state | Method returns `void`, changes a field/global | Return the new value |
| Many writers | Several classes write one file | One service, "one and only one" |
| Dead code | `Old…` beside `New…` | Delete; git keeps it |

## Worked Example
**One level of abstraction, in three tiers** — the C# source pushes further than its JavaScript parent, ending in injected classes.

**Bad** — one method tokenizes, lexes and parses:

```csharp
public string ParseBetterJSAlternative(string code)
{
    var regexes = new List<string> { /* ... */ };
    var statements = code.Split(' ');
    var tokens = new List<string>();
    foreach (var regex in regexes)
    {
        foreach (var statement in statements)
        {
            // ...
        }
    }

    var ast = new List<string>();
    foreach (var token in tokens)
    {
        // lex...
    }

    foreach (var node in ast)
    {
        // parse...
    }
}
```

**Bad too** — the steps are extracted into `Tokenize(code)` and `Lexer(tokens)` methods, and `ParseBetterJSAlternative` calls them. The source's verdict: "We have carried out some of the functionality, but the `ParseBetterJSAlternative()` function is still very complex and not testable." The helpers still live in the same class, so the parser can't be tested without the real tokenizer and lexer.

**Good** — "The best solution is move out the dependencies of `ParseBetterJSAlternative()` function":

```csharp
class Tokenizer
{
    public List<string> Tokenize(string code)
    {
        var regexes = new List<string> { /* ... */ };
        var statements = code.Split(' ');
        var tokens = new List<string>();
        foreach (var regex in regexes)
        {
            foreach (var statement in statements)
            {
                tokens.Add(/* ... */);
            }
        }

        return tokens;
    }
}

class Lexer
{
    public List<string> Lexify(List<string> tokens)
    {
        var ast = new List<string>();
        foreach (var token in tokens)
        {
            ast.Add(/* ... */);
        }

        return ast;
    }
}

class BetterJSAlternative(Tokenizer tokenizer, Lexer lexer)
{
    public void Parse(string code)
    {
        var tokens = tokenizer.Tokenize(code);
        var ast = lexer.Lexify(tokens);
        foreach (var node in ast)
        {
            // parse...
        }
    }
}
```
- *Source snippet lightly repaired: PHP's `explode(" ", code)` → `code.Split(' ')`, PHP's `tokens[] = …` → `tokens.Add(…)`, arrays → `List<string>`, return types made consistent.*

**What changed at each tier.** Tier 1 → 2 separates the *steps*; tier 2 → 3 separates the *dependencies*. `Parse` now reads as three intentions at one altitude, and the primary constructor makes the collaborators explicit — the next step, depending on interfaces rather than these concrete classes, is DIP (Ch 9).

## Key Takeaways
1. **Do one thing.** If the description needs "and", split it. This rule outranks the rest.
2. **0 ideal, 1–2 fine, 3 avoid, 4+ consolidate.** In C#, consolidate into a positional `record` and construct it with named arguments.
3. **No `bool` flags**: two named methods.
4. **Name the action** — `Send()`, not `Handle()`.
5. **One level of abstraction**: extract methods, then extract classes and inject them through the constructor.
6. **Callers above callees**, so the file reads top-down.
7. **Value in, value out.** Centralize unavoidable effects in one service.
8. **Delete dead code**; the history keeps it.

## Connects To
- **Ch 3**: the parameter object is the "anonymous object → named type" move from searchable names, applied to signatures.
- **Ch 5**: conditionals and type checks are the other big "does more than one thing" detectors from the source's Functions section.
- **Ch 6**: global state and singletons, the last two rules of the source's Functions section.
- **Ch 9**: `BetterJSAlternative(Tokenizer, Lexer)` is one step from DIP; swap the concrete classes for interfaces.
- **Ch 14**: the newspaper order is the one layout rule no `.editorconfig` can enforce.
- **clean-code-java** ch03: the book's harder thresholds (functions "hardly ever 20 lines", command-query separation, no output arguments).
