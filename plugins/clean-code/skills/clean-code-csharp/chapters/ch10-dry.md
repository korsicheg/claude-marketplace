# Chapter 10: Don't Repeat Yourself (DRY)

## Core Idea
"Do your absolute best to avoid duplicate code. Duplicate code is bad because it means that there's more than one place to alter something if you need to change some logic." But the abstraction that removes duplication has to be the right one: **"Bad abstractions can be worse than duplicate code, so be careful!"** The source files DRY under SOLID and ties the two together — getting the abstraction right is what SOLID is for.

## Frameworks Introduced
- **DRY** — one authoritative place for each piece of logic.
  - When to use: two or more functions, classes or modules doing "much of the same things" because of small differences between the things they handle.
  - How: "Removing duplicate code means creating an abstraction that can handle this set of different things with just one function/module/class."
- **The restaurant inventory** — the source's analogy: "Imagine if you run a restaurant and you keep track of your inventory: all your tomatoes, onions, garlic, spices, etc. If you have multiple lists that you keep this on, then all have to be updated when you serve a dish with tomatoes in them. If you only have one list, there's only one place to update!"
- **The bad-abstraction caveat** — "Getting the abstraction right is critical, that's why you should follow the SOLID principles laid out in the Classes section. Bad abstractions can be worse than duplicate code, so be careful! Having said this, if you can make a good abstraction, do it!"
- **Compact once correct** — the source's third tier, "Very good: It is better to use a compact version of the code", inlines the temporaries into a single C# 12 collection expression passed straight to `Render`.

## Key Concepts
- **Duplicate code** — logic that must be changed in more than one place when the rule it encodes changes.
- **Near-miss duplication** — "two or more slightly different things, that share a lot in common, but their differences force you to have two or more separate functions."
- **Abstraction (DRY sense)** — one function, class or module that handles every variant.
- **Bad abstraction** — a merge of things that don't really vary together; costs more than the copies it replaced.
- **Single point of update** — what a good abstraction buys: one list of tomatoes.

## Mental Models
- **Count the places a rule change would touch.** One place: DRY. Two places that must always change together: duplication. Two places that change for different reasons: not duplication, leave them.
- **Abstract over what the consumer needs.** `ShowList` only calls `CalculateExpectedSalary()`, `GetExperience()` and `GetGithubLink()`. Whatever offers those three can be shown; the developer/manager distinction is invisible to this code.
- **A flag in the merged version is the duplication arguing back.** If the abstraction needs `if (isManager)`, the variation was real — that's the "bad abstraction" the caveat warns about (Ch 4's flag rule says the same).

## Anti-patterns
- **Parallel methods per type** — `ShowDeveloperList` and `ShowManagerList` differing only in the element type.
- **Multiple inventories** — the same fact kept in several lists that must be updated together.
- **Forcing a merge** — an abstraction built before the shared shape is clear, which the caveat ranks below the duplication itself.

## Code Examples
The source's three tiers, lightly repaired so they compile in shape:

```csharp
// Bad — one method per kind of employee
public void ShowDeveloperList(IEnumerable<Developer> developers)
{
    foreach (var developer in developers)
    {
        var expectedSalary = developer.CalculateExpectedSalary();
        var experience = developer.GetExperience();
        var githubLink = developer.GetGithubLink();
        var data = new object[] { expectedSalary, experience, githubLink };

        Render(data);
    }
}

public void ShowManagerList(IEnumerable<Manager> managers)
{
    foreach (var manager in managers)
    {
        var expectedSalary = manager.CalculateExpectedSalary();
        var experience = manager.GetExperience();
        var githubLink = manager.GetGithubLink();
        var data = new object[] { expectedSalary, experience, githubLink };

        Render(data);
    }
}

// Good — one method over the shared abstraction
public void ShowList(IEnumerable<Employee> employees)
{
    foreach (var employee in employees)
    {
        var expectedSalary = employee.CalculateExpectedSalary();
        var experience = employee.GetExperience();
        var githubLink = employee.GetGithubLink();
        object[] data = [expectedSalary, experience, githubLink];

        Render(data);
    }
}

// Very good — compact
public void ShowList(IEnumerable<Employee> employees)
{
    foreach (var employee in employees)
    {
        Render([
            employee.CalculateExpectedSalary(),
            employee.GetExperience(),
            employee.GetGithubLink()
        ]);
    }
}
```
- *Repairs: the source's Bad has `foreach (var developers in developer)` (reversed), a single `Developers`/`Manager` parameter instead of a collection, `Render`/`render` in mixed case, and declared `List<…>` return types it never returns; its Good calls `employees.CalculateExpectedSalary()` on the collection instead of `employee`. Return types are `void` here because nothing is returned.*
- **What it demonstrates**: the merge works because `Developer` and `Manager` already expose the same three operations — so the shared base (or interface) `Employee` needs nothing new. The source leaves that type implicit; in C# it must exist, as a base class or an interface both implement.

## Worked Example
**Deciding whether to merge — `ShowDeveloperList` and `ShowManagerList`.**

1. **Do both always change for the same reason?** Yes — if the list should show a fourth column, both methods change identically. That is duplication.
2. **Does the merged version need a flag or a type test?** No. Both bodies call the same three methods. (If managers showed a team size instead of a GitHub link, the merge would need `if (employee is Manager)` — the warning sign that the abstraction is wrong. Stop there.)
3. **What abstraction does the consumer need?** Exactly the three operations it calls. Give `Developer` and `Manager` a common `Employee` base or interface carrying them.
4. **Merge, then compact.** `ShowList(IEnumerable<Employee>)` replaces both methods; once it's one method, the temporaries add nothing, and the collection expression passes the values straight to `Render`.

The order matters: the source's "Very good" compaction is only safe *after* the abstraction is right — compacting two duplicated methods just produces two compact duplicates.

## Key Takeaways
1. **One rule, one place** — keep one inventory list.
2. Remove near-miss duplication with **an abstraction that handles every variant** in "one function/module/class".
3. **"Bad abstractions can be worse than duplicate code."** If the merge needs a flag or a type test, don't merge.
4. Use **SOLID** (Ch 9) to get the abstraction right — usually an interface or base class carrying exactly what the consumer calls.
5. **Compact last**: inline temporaries once the duplication is gone.

## Connects To
- **Ch 4**: dead code "is just as bad as duplicate code"; flags signal a merge gone wrong.
- **Ch 5**: a type test inside a merged method is the bad-abstraction tell.
- **Ch 9**: the source places DRY under SOLID and points to it for getting abstractions right.
- **clean-code-java** ch17 (G5): duplication as "one of the most important rules in this book", with its three forms and cures.
- **clean-code-python** ch09: the same example, extended with the near-miss generalization `Developer` + `Manager` → `Employee`.
