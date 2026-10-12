# Chapter 15: Comments

## Core Idea
"Comments are an apology, not a requirement. Good code *mostly* documents itself." Delete comments that say **what** the code does — replace them with a well-named variable or method — and keep the ones that say **why**, the reasoning code can't express. Remove positional markers (including C#'s **`#region`**), commented-out code and journal comments: version control holds history; the file holds the current code.

## Frameworks Introduced
- **Avoid positional markers** — "They usually just add noise. Let the functions and variable names along with the proper indentation and formatting give the visual structure to your code."
  - C#-specific: the source lists **`#region` / `#endregion`** blocks as a Bad example alongside `////////` banner comments.
- **Don't leave commented out code in your codebase** — "Version control exists for a reason. Leave old code in your history."
- **Don't have journal comments** — "Remember, use version control! There's no need for dead code, commented code, and especially journal comments. Use `git log` to get history!"
- **Only comment things that have business logic complexity**
  - The WHAT/WHY test: "If a comment explains WHAT the code is doing, it is probably a useless comment and can be implemented with a well named variable or function … However it would be hard to express by code WHY the developer chose djb2 hash algorithm instead of sha-1 or another hash function. In that case a comment is acceptable."
  - How: three tiers — every line commented (Bad); most comments deleted but "Convert to 32-bit integer" left (Better but still Bad, because a method named `ConvertTo32BitInt` would say it); only the WHY comment kept and the WHAT comment turned into a method (Good).

## Key Concepts
- **Positional marker** — a banner (`////////`) or region that labels a section of a file.
- **`#region` / `#endregion`** — C# preprocessor directives that make a collapsible block in the IDE; here, a positional marker.
- **Commented-out code** — old code kept as comments; version control already keeps it.
- **Journal comment** — a dated changelog at the top of a member or file.
- **WHAT comment** — restates what the code does; replace it with a name.
- **WHY comment** — records a decision code can't express (an algorithm choice, a trade-off); keep it.
- **Self-documenting code** — names and structure that make most comments unnecessary; the source says *mostly*.

## Mental Models
- **A comment is an apology for a name you didn't find.** "Convert to 32-bit integer" *is* the method name `ConvertTo32BitInt`; the comment contained the fix.
- **Ask WHAT or WHY.** WHAT → rename or extract. WHY → keep and write it well.
- **If a file needs regions to be navigable, it's too big.** Regions hide length instead of reducing it; the names of extracted members and classes are better structure (Ch 4, Ch 9).
- **History belongs in history.** Journal entries and commented-out code are a version-control system implemented badly by hand.

## Anti-patterns
- **Banner comments and `#region` blocks** separating sections of a file.
- **Commented-out calls** — `// doOtherStuff();`.
- **Journal headers** — "2018-12-20: Removed monads, didn't understand them (RM)".
- **Line-by-line narration** — `// The hash`, `// Length of string`, `// Loop through every character in data`.

## Code Examples
`#region` as a positional marker (the source's Bad, rendered as C#):

```csharp
#region Scope Model Instantiation

var model = new
{
    Menu = "foo",
    Nav = "bar"
};

#endregion

#region Action setup

void Actions()
{
    // ...
}

#endregion
```
- *Lightly repaired: the source's model literal is JavaScript object syntax.* **Good** is the same code with the regions and banners deleted.

Journal comments:

```csharp
// Bad
/**
 * 2018-12-20: Removed monads, didn't understand them (RM)
 * 2017-10-01: Improved using special monads (JP)
 * 2016-02-03: Removed type-checking (LI)
 * 2015-03-14: Added combine with type-checking (JR)
 */
public int Combine(int a, int b)
{
    return a + b;
}

// Good
public int Combine(int a, int b)
{
    return a + b;
}
```

## Worked Example
**Comment only the WHY — the djb2 hash.**

**Bad** — every line narrated:

```csharp
public int HashIt(string data)
{
    // The hash
    var hash = 0;

    // Length of string
    var length = data.Length;

    // Loop through every character in data
    for (var i = 0; i < length; i++)
    {
        // Get character code.
        var character = data[i];
        // Make the hash
        hash = ((hash << 5) - hash) + character;
        // Convert to 32-bit integer
        hash &= hash;
    }

    return hash;
}
```

**Better but still bad** — the narration is gone except `// Convert to 32-bit integer`. "The comment in the previous code could be replaced with a function named `ConvertTo32bitInt` so this comment is still useless."

**Good** — the WHAT became a method; the WHY stayed:

```csharp
public int Hash(string data)
{
    var hash = 0;
    var length = data.Length;

    for (var i = 0; i < length; i++)
    {
        var character = data[i];
        // use of djb2 hash algorithm as it has a good compromise
        // between speed and low collision with a very simple implementation
        hash = ((hash << 5) - hash) + character;

        hash = ConvertTo32BitInt(hash);
    }
    return hash;
}

private int ConvertTo32BitInt(int value)
{
    return value & value;
}
```
- *Lightly repaired in the Bad tiers: JavaScript's `data.length`, `charCodeAt(i)` and `const char = …` → C#.*

**What survives the port.** The lesson — WHAT comments become names, WHY comments stay — is sound. The arithmetic is a JavaScript leftover: in JavaScript `hash & hash` forces a 32-bit integer, but a C# `int` is already 32 bits and wraps on overflow (in an unchecked context), so `value & value` returns `value` unchanged. In C#, `ConvertTo32BitInt` and its call can simply be deleted — the cleanest possible outcome for a WHAT comment.

## Key Takeaways
1. **Comments are an apology**; good code *mostly* documents itself.
2. **WHAT → rename or extract; WHY → keep.** The djb2 choice is a WHY.
3. **No positional markers** — banners *and* `#region`.
4. **No commented-out code, no journal comments** — `git log` has the history.
5. When a comment names an operation, **that's the method name you were looking for**.

## Connects To
- **Ch 2, Ch 3**: names are what replace WHAT comments.
- **Ch 4**: "Remove dead code" — commented-out code is dead code that also clutters.
- **Ch 14**: formatting and indentation are the source's prescribed substitute for visual markers.
- **clean-code-java** ch04 (Comments) and ch17 (C1 inappropriate information, C5 commented-out code): the full taxonomy, including legitimate kinds this source doesn't list — legal headers, TODOs, warnings of consequences, and public-API documentation.
- **clean-code-typescript** ch11: the same rules, plus `// TODO` as the one endorsed form.
