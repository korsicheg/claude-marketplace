# Chapter 3: Functions

## Core Idea
**Functions should do one thing** — "one of the most important principles in software engineering… If you remember nothing else from this guide, this principle will put you ahead of many developers." The other rules here — at most two arguments, no flags, one level of abstraction, a name that says what it does, no duplication — are detectors for violating it. Swift's contribution: a `struct` as the parameter object, a non-optional parameter with a default value instead of `?` plus `??`, and an `enum` to hold per-case variation.

## Frameworks Introduced
- **Function arguments (max 2 params)**: "It is best to limit function arguments to a maximum of two, and avoid three whenever possible. If more parameters are needed, consider consolidating them into an object."
  - Why: "When a function has more than three arguments, complexity increases significantly, requiring detailed tests for each parameter," and "Functions with too many arguments often indicate multiple responsibilities."
  - How: a `struct` with `let` properties — `MenuViewData` — passed as one argument. Swift writes its memberwise initializer for free, which is the guide's "Swift's efficiency in creating objects."
- **Use default arguments instead of short-circuiting or conditionals**: `func createMicrobrewery(name: String?)` with `name ?? "Hipster Brew Co."` → `func createMicrobrewery(breweryName: String = "Hipster Brew Co.")`.
  - When to use: a parameter is optional only so the body can substitute a fallback.
  - How: make the parameter non-optional and put the fallback in the signature. Named gains: *Clean Default Argument*, *Clear Intent* — "a sensible default is always available without complicating the implementation."
- **Functions should do one thing**: "Functions that perform multiple tasks become difficult to compose, test, and reason about."
  - How: if the description needs "and", split. `emailClients` (look up *and* filter *and* email) → `emailActiveClients` + `isActiveClient`.
- **Function names should say what they do**: `addToDate(date:month:)` → `addMonthToDate(month:date:)`.
  - When to use: when a caller can't tell from the call site what happens ("It's hard to tell by the function name what is being added").
  - How: put the action and its object in the name. Named risk: *Potential for Misuse*.
- **Functions should have one level of abstraction**: "When functions operate on more than one level of abstraction, they tend to become overloaded with responsibilities."
  - How: separate orchestration (parse the input) from mechanics (write to the database) into their own functions.
- **Remove duplicated code**: "Duplicated code is bad because it means there's more than one place to change something."
  - How: find what the near-duplicates share and create "an abstraction that can handle those differences with only one function/method." The guide's Swift tool for the differences is an `enum` with a computed property.
- **Avoid using flags as function parameters**: "Flags indicate that the function does more than one thing."
  - How: `createFile(name:temporary:)` → `createTemporaryFile(name:)` + `createPermanentFile(name:)`.

## Key Concepts
- **Parameter object** — a `struct` bundling related arguments (`MenuViewData`); the guide's answer to three or more parameters.
- **Memberwise initializer** — the initializer Swift synthesizes for a struct's stored properties; it makes a parameter object one declaration long.
- **Argument label** — the external name in a Swift signature (`createMenu(viewData:)`); every example in the guide uses labels, though no rule discusses them.
- **Default argument** — a fallback value in the signature, used when the caller omits the argument.
- **Nil-coalescing (`??`)** — `a ?? b` unwraps `a` or falls back to `b`; the guide's Bad default-argument example.
- **Level of abstraction** — the altitude of a statement: "parse the input" vs "call `database.save`".
- **Flag parameter** — a `Bool` that selects between code paths.
- **Restaurant analogy** — two client lists (chef's, delivery's) mean a cancellation must be made twice; one list means "only one place to update."

## Mental Models
- **Every argument multiplies the test matrix.** The guide's reason for the two-argument limit is testing, not aesthetics.
- **An optional parameter with a fallback is a default argument in disguise.** If the body's first line is `?? someDefault`, the optional is lying about what the function accepts.
- **A flag is two functions sharing a signature.** The call `createFile(name: "x", temporary: true)` names the mode only because Swift has argument labels; the two-function version names it in the function itself.
- **Put the variation in an enum, not in a second copy.** `Role.developer` / `.manager` carry their own `description`; the function that prints a person no longer cares which role it got.

## Code Examples
The parameter-object struct:

```swift
struct MenuViewData {
  let title: String
  let body: String
  let buttonText: String
  let cancellable: Bool
}

func createMenu(viewData: MenuViewData) {
  // ...
}

// Usage:
let viewData = MenuViewData(
  title: "Foo",
  body: "Bar",
  buttonText: "Baz",
  cancellable: true
)

createMenu(viewData: viewData)
```

- **What it demonstrates**: four parameters become one; the struct's `let`s make the bundle immutable, and its memberwise initializer costs nothing to write.

Duplication removed with an enum:

```swift
enum Role {
    case developer
    case manager

    var description: String {
        switch self {
        case .developer: return "Coding..."
        case .manager: return "Meeting..."
        }
    }
}

func showPerson(name: String, role: Role) {
    print("\(role): \(name)")
    print(role.description)
}
```

- **What it demonstrates**: `showDeveloper(name:)` and `showManager(name:)` collapse into one function; the per-role difference lives in an exhaustive `switch` inside the enum, so adding a role is a compile error until its description exists.

## Reference Tables

| Detector | Signal in Swift | Fix |
|---|---|---|
| Argument count | 3+ parameters | `struct` parameter object |
| Optional + fallback | `name: String?` then `name ?? "…"` | `name: String = "…"` |
| Description needs "and" | look up *and* filter *and* act | split into named functions |
| Vague name | `addToDate` | `addMonthToDate` |
| Mixed altitude | parsing and persistence in one body | one function per level |
| Near-duplicate functions | `showDeveloper` / `showManager` | one function + an `enum` |
| Flag parameter | `temporary: Bool` | `createTemporaryFile` / `createPermanentFile` |

## Worked Example
"Functions should do one thing", end to end.

**Bad** — one loop looks up records, filters on activity, and sends mail:

```swift
func emailClients(clients: [Client]) {
    clients.forEach { client in
        let clientRecord = database.lookup(client)
        if clientRecord.isActive() {
            email(client)
        }
    }
}
```

The guide names three costs: *Multiple Responsibilities* (lookup and emailing), *Decreased Testability* ("the function combines logic that could be isolated into separate tests"), and *Reduced Readability*.

**Good** — the predicate gets its own name, and the pipeline reads as a sentence:

```swift
func emailActiveClients(clients: [Client]) {
    clients
        .filter { isActiveClient(client: $0) }
        .forEach { email(client: $0) }
}

func isActiveClient(client: Client) -> Bool {
    let clientRecord = database.lookup(client)
    return clientRecord.isActive()
}
```

Three things changed. The **name** now states the whole job (`emailActiveClients`). The **predicate** is a function you can test without sending email. And the **loop** became `filter` + `forEach`, which is the functional style Ch 4 recommends — the split for correctness made the Swift idiom fall out. `$0` is fine here because each closure is one call long (Ch 2's mental-mapping rule bites in longer closures).

## Source Caveats
- **One level of abstraction**: the Bad and Good snippets are nearly identical — the only change is `saveData(inputData)` → `saveData(data: inputData)`, adding an argument label, and `parseInput` still calls `saveData` in both. Learn this rule from its prose, not its example.
- **Default arguments**: the note that defaults "are only applied to `nullable` arguments; other 'falsy' values like `""`, `false`, `null`, and `0` will not trigger default values" is carried over from JavaScript. Swift has no falsy values, and a default is used only when the argument is omitted. The Good example's real Swift move is removing the optional.
- **Duplication**: the Good version prints `developer: …` (the case name) where the Bad printed `Developer: …`; a small behaviour change worth noticing when you deduplicate. The source also drops the JavaScript original's warning that "bad abstractions can be worse than duplicate code."
- **Argument count**: no rule discusses argument labels, which make a three-argument Swift call far more readable than its JavaScript equivalent; the two-argument limit is stated without that nuance.

## Anti-patterns
- **Four positional-ish parameters** (`createMenu(title:body:buttonText:cancellable:)`): *Excessive Arguments*, *Increased Complexity*, *Violation of Single Responsibility*.
- **`?` plus `??` for a fallback**: *Redundant Conditional Logic*; the signature hides the default.
- **Lookup-and-filter-and-act loops**: three responsibilities, none testable alone.
- **Names that hide the action** (`addToDate`): readers must "delve into the implementation."
- **Copy-and-tweak functions** (`showDeveloper`/`showManager`): *Potential for Inconsistencies* when one copy gets the fix.
- **Boolean mode parameters**: the function admits it does two things.

## Key Takeaways
1. **Do one thing.** If the description needs "and", split it. This outranks every other rule.
2. **Two arguments, at most.** At three, introduce a `struct` parameter object.
3. **Non-optional parameter + default value**, never `?` + `??`.
4. **Name the action and its object** (`addMonthToDate`).
5. **One level of abstraction per function.**
6. **Deduplicate into one function; push per-case differences into an `enum`.**
7. **No `Bool` flags** — two functions, two names.

## Connects To
- **Ch 2**: naming discipline applied to functions; default arguments remove an optional where Ch 2's `if let` unwraps one.
- **Ch 4**: the rest of the Functions section — side effects, extensions on shared types, functional style, conditionals and type checks.
- **Ch 5**: enums replace string comparisons, the same move as `Role` here.
- **Ch 7 (SRP)**: "one reason to change" is "do one thing" stated for a class.
- **`clean-code-java`** (ch03, Functions): "Small!", the stepdown rule, command-query separation and the argument-arity ladder behind the two-argument limit.
- **`clean-code-javascript`**, **`clean-code-python`**: both keep the "bad abstractions can be worse than duplicate code" caveat this port dropped; apply it before deduplicating.
