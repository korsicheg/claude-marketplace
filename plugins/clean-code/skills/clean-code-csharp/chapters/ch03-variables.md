# Chapter 3: Variables

## Core Idea
Ten rules that make a variable carry its own meaning: return early instead of nesting, name things so they can be searched for, put magic strings and numbers behind a `const` or an `enum`, name regex groups, and put defaults in the signature. Twice the source invokes the same tie-breaker: **"Explicit is better than implicit."**

## Frameworks Introduced
- **Avoid nesting too deeply and return early** — "Too many if else statements can make the code hard to follow."
  - When to use: an `if` whose `else` holds the rest of the method; ladders of `else if` returning `true`/`false`.
  - How: invert the precondition into a **guard clause** that returns at once, then write the happy path flat. Replace value ladders with data: `string[] openingDays = ["friday", "saturday", "sunday"]; return openingDays.Any(d => d == day.ToLower());`.
- **Avoid mental mapping** — "Don't force the reader of your code to translate what the variable means."
  - How: `l`/`li` with an index loop → `locations` / `foreach (var location in locations)`. "Wait, what is `li` for again?" is the tell.
- **Avoid magic strings** — they "end up being duplicated within the system, and since they cannot automatically be updated using refactoring tools, they become a common source of bugs when changes are made to some strings but not others."
  - How: `if (userRole == "Admin")` → a named `const string` compared instead. "Using this we only have to change in centralize place and others will adapt it."
- **Don't add unneeded context** — "If your class/object name tells you something, don't repeat that in your variable name."
  - How: `Car.CarMake`, `Car.CarModel`, `Car.CarColor` → `Car.Make`, `Car.Model`, `Car.Color`.
- **Use meaningful and pronounceable variable names** — `ymdstr` → `currentDate`.
- **Use the same vocabulary for the same type of variable** — `GetUserInfo()`, `GetUserData()`, `GetUserRecord()`, `GetUserProfile()` → `GetUser()`.
- **Use searchable names** (two parts) — "We will read more code than we will ever write. It's important that the code we do write is readable and searchable."
  - Part 1: an anonymous `new { Name = "John", Age = 42 }` held in `data` → a named `Person` type. The type name is searchable; `data` and `typeof(object)` are not.
  - Part 2: `if (data.PersonAccess == 4)` ("What the heck is 4 for?") → an `enum PersonAccess` whose members name each value.
- **Use explanatory variables** — "Decrease dependence on regex by naming subpatterns."
  - How: `.NET` named groups `(?<city>…)` and `(?<zipCode>…)`, read back as `match.Groups["city"]`.
- **Use default arguments instead of short circuiting or conditionals**
  - How: `CreateMicrobrewery(string name = null)` + `!string.IsNullOrEmpty(name) ? name : "Hipster Brew Co."` → `CreateMicrobrewery(string breweryName = "Hipster Brew Co.")`. The default lives where every caller reads it.

## Key Concepts
- **Guard clause** — an early `return` (or `throw`) that handles a precondition so the rest of the method needn't nest.
- **Mental mapping** — translating a short name (`li`) back into the concept it stands for.
- **Magic string / magic number** — a literal with behavioural meaning, not explained or centralized.
- **Unneeded context** — repeating the enclosing type's name in its own members.
- **Searchable name** — a name (or type) grep and *Find All References* can locate.
- **Anonymous type** — `new { Name = …, Age = … }`; compiler-named, so neither searchable nor reusable.
- **Named capture group** — `(?<name>…)` in .NET regex, read via `Groups["name"]`.
- **Default argument** — `string breweryName = "…"`; must be a compile-time constant in C#.

## Mental Models
- **Shape the method like a funnel**: rejections at the top, one flat happy path at the bottom. Every `else` after a `return` is indentation you didn't need.
- **A literal that matters twice is a bug waiting for the second edit.** Promote it the first time it carries meaning; the refactoring tools can then follow it.
- **Read the member at its use site.** `car.CarMake` reads "car car make"; context the type already supplies is noise.
- **If you have to grep for a number, you have already lost.** Give it a name — a `const`, an `enum` member, or a type.

## Anti-patterns
- **`else` after `return`** and nested precondition checks.
- **Index loops for plain iteration** with throwaway names (`for (var i …) { var li = l[i]; … }`).
- **String comparisons against literals scattered through the code** (`"Admin"`, `"published"`, `"ajaxAdapter"`).
- **Synonym drift** — four `GetUser*` methods for one concept.
- **Positional regex access** — `matches[0].Value`, `matches[1].Value`.
- **Defaulting inside the body** with `?:` or `??` when the signature could say it.

## Code Examples
Return early, and replace a value ladder with data:

```csharp
// Bad
public bool IsShopOpen(string day)
{
    if (!string.IsNullOrEmpty(day))
    {
        day = day.ToLower();
        if (day == "friday") { return true; }
        else if (day == "saturday") { return true; }
        else if (day == "sunday") { return true; }
        else { return false; }
    }
    else
    {
        return false;
    }
}

// Good
public bool IsShopOpen(string day)
{
    if (string.IsNullOrEmpty(day))
    {
        return false;
    }

    string[] openingDays = ["friday", "saturday", "sunday"];
    return openingDays.Any(d => d == day.ToLower());
}
```
- **What it demonstrates**: a guard clause plus a LINQ `Any` over a C# 12 collection expression turns a 20-line ladder into two statements.

Named regex groups:

```csharp
const string Address = "One Infinite Loop, Cupertino 95014";
var cityZipCodeWithGroupRegex = @"^[^,\\]+[,\\\s]+(?<city>.+?)\s*(?<zipCode>\d{5})?$";
var matchesWithGroup = Regex.Match(Address, cityZipCodeWithGroupRegex);
var cityGroup = matchesWithGroup.Groups["city"];
var zipCodeGroup = matchesWithGroup.Groups["zipCode"];
if (cityGroup.Success && zipCodeGroup.Success)
{
    SaveCityZipCode(cityGroup.Value, zipCodeGroup.Value);
}
```
- *Source snippet lightly repaired: the source wraps the pattern in JavaScript's `/…/` delimiters, which .NET would treat as literal slashes, and loses a backslash in each character class in transit; both restored to the JavaScript original's pattern. `== true` dropped.* The **Bad** version calls `Regex.Matches` and reads `matches[0]`/`matches[1]` — in .NET those are two separate *matches*, not two groups, so the positional version is wrong as well as unreadable.

## Reference Tables

| Smell | Fix | Source example |
|---|---|---|
| Nested `if`/`else` returning bools | Guard clause + data + LINQ | `IsShopOpen` |
| `l`, `li`, `i` | Plural collection, singular element, `foreach` | `locations` / `location` |
| `== "Admin"` | Named `const string` | `ADMIN_ROLE` (see casing note) |
| `== 4` | `enum` member | `PersonAccess.ACCESS_UPDATE` |
| `new { … }` in `data` | Named type | `Person` |
| `matches[1].Value` | `(?<zipCode>…)` + `Groups["zipCode"]` | city/zip regex |
| `x ?? "default"` in body | Default argument | `CreateMicrobrewery` |

**Casing note.** The source's own examples write `const string ADMIN_ROLE` and enum members `ACCESS_READ`, `ACCESS_CREATE`. Both contradict its capitalization rule (Ch 2) and its `.editorconfig` (Ch 14), which make constants PascalCase. Follow the rules, not the examples: `AdminRole`, `PersonAccess.Update`.

## Worked Example
The source's second early-return example, a recursive Fibonacci, shows the technique and also a trap worth knowing.

**Bad** — three levels of nesting, with the error case at the bottom:

```csharp
public long Fibonacci(int n)
{
    if (n < 50)
    {
        if (n != 0)
        {
            if (n != 1)
            {
                return Fibonacci(n - 1) + Fibonacci(n - 2);
            }
            else
            {
                return 1;
            }
        }
        else
        {
            return 0;
        }
    }
    else
    {
        throw new System.Exception("Not supported");
    }
}
```

**Good** — every special case is a guard, and the recursion is the last, unindented line:

```csharp
public long Fibonacci(int n)
{
    if (n == 0)
    {
        return 0;
    }

    if (n == 1)
    {
        return 1;
    }

    if (n > 50)
    {
        throw new System.Exception("Not supported");
    }

    return Fibonacci(n - 1) + Fibonacci(n - 2);
}
```

**The trap.** Compare the boundaries: the Bad version throws for `n >= 50`; the Good version throws only for `n > 50`, so `Fibonacci(50)` now recurses instead of throwing. Flattening conditions means inverting them, and inverting `<` gives `>=`, not `>`. The structure lesson stands — but when you flatten guards, **pin the boundary values with a test first** (Ch 11).

## Key Takeaways
1. **Return early.** Guards at the top, one flat happy path. Replace `if`/`else if` value ladders with a collection and LINQ.
2. **No mental mapping**: plural collection, singular `foreach` variable.
3. **No magic strings or numbers**: `const` for strings, `enum` for coded values — PascalCase, whatever the examples say.
4. **Drop repeated context**: `Car.Make`, not `Car.CarMake`.
5. **One word per concept**: `GetUser()`, not four synonyms.
6. **Name things so Find All References works**: named types over anonymous ones, named regex groups over indices.
7. **Defaults go in the signature.**
8. When inverting conditions into guards, **check the boundary** — `<` becomes `>=`.

## Connects To
- **Ch 2**: naming rules this chapter extends; the casing conflict above is resolved there.
- **Ch 4**: the `MenuConfig` record is the same move as "anonymous object → named type", applied to parameters.
- **Ch 5**: "Encapsulate conditionals" is the next step after returning early — name the condition itself.
- **Ch 9**: OCP's bad example compares against string literals (`"ajaxAdapter"`) and, tellingly, gets one of them wrong.
- **Ch 11**: the Fibonacci boundary shift is exactly what a test on boundary values catches.
