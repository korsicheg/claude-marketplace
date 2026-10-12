# Chapter 9: Don't Repeat Yourself (DRY)

## Core Idea
"Do your absolute best to avoid duplicate code. Duplicate code is bad because it means that there's more than one place to alter something if you need to change some logic." But the guide attaches the caveat that keeps DRY honest: "**Getting the abstraction right is critical… Bad abstractions can be worse than duplicate code, so be careful!**"

## Frameworks Introduced
- **DRY — one place to change**: the restaurant inventory. "If you have multiple lists that you keep this on, then all have to be updated when you serve a dish with tomatoes in them. If you only have one list, there's only one place to update!"
  - When to use: whenever two pieces of code would have to change together for the same reason.
- **Near-miss duplication**: "Often you have duplicate code because you have two or more slightly different things, that share a lot in common, but their differences force you to have two or more separate functions that do much of the same things."
  - How: "Removing duplicate code means creating an abstraction that can handle this set of different things with just one function/module/class."
- **The bad-abstraction caveat**: "Getting the abstraction right is critical, that's why you should follow the SOLID principles… Bad abstractions can be worse than duplicate code, so be careful! Having said this, if you can make a good abstraction, do it!"
  - When to use: before every merge — ask whether the two copies really vary together.
- **A three-rung ladder** — the guide's example climbs Bad → Good → **Very good**:
  - Bad: `showDeveloperList()` and `showManagerList()`, identical bodies over different arrays.
  - Good: one `showList(array $employees)`.
  - Very good: "It is better to use a compact version of the code" — the three temporaries inlined into one `render([...])` call.

## Key Concepts
- **Duplication** — the same knowledge in more than one place, so one change requires several edits.
- **Single point of update** — what a good abstraction buys; the "one list" in the restaurant.
- **Near-miss duplication** — copies that differ slightly, which is what makes them tempting to keep separate.
- **Bad abstraction** — a merge of things that don't actually vary together; "can be worse than duplicate code."
- **Generalization** — replacing sibling concepts (`$developers`, `$managers`) with the one the code actually needs (`$employees`).

## Mental Models
- **Deduplicate knowledge, not text.** Two blocks that look alike but change for different reasons are not duplicates.
- **If the merged version needs a flag, the merge is wrong.** A `bool $isManager` parameter inside `showList()` would reintroduce the two code paths (and break Ch 4's flag rule).
- **Ask what the consumer reads.** `showList()` only calls `calculateExpectedSalary()`, `getExperience()` and `getGithubLink()`; it never cares whether the object is a developer or a manager, so the distinction can go.
- **SOLID first, then DRY.** The guide makes the order explicit: a sound abstraction comes from following SOLID; duplication is removed *into* it.

## Anti-patterns
- **Parallel functions per role** (`showDeveloperList` / `showManagerList`): every change to the rendered fields is made twice.
- **Forced unification**: merging code that only coincidentally matches; the first divergent requirement adds a flag, then a branch.
- **Keeping both the old and new version** (`oldRequestModule()` / `newRequestModule()`): "Dead code is just as bad as duplicate code" (Ch 5).

## Code Examples
```php
// Bad
function showDeveloperList(array $developers): void
{
    foreach ($developers as $developer) {
        $expectedSalary = $developer->calculateExpectedSalary();
        $experience = $developer->getExperience();
        $githubLink = $developer->getGithubLink();
        $data = [$expectedSalary, $experience, $githubLink];

        render($data);
    }
}

function showManagerList(array $managers): void
{
    foreach ($managers as $manager) {
        $expectedSalary = $manager->calculateExpectedSalary();
        $experience = $manager->getExperience();
        $githubLink = $manager->getGithubLink();
        $data = [$expectedSalary, $experience, $githubLink];

        render($data);
    }
}
```

```php
// Very good
function showList(array $employees): void
{
    foreach ($employees as $employee) {
        render([$employee->calculateExpectedSalary(), $employee->getExperience(), $employee->getGithubLink()]);
    }
}
```
- **What it demonstrates**: the merge works because nothing in the body depends on the role; the "Very good" rung then removes the three single-use temporaries.

## Reference Tables

**Deduplicate, or leave it?**

| Question | Answer → action |
|---|---|
| Must both copies always change together, for the same reason? | yes → deduplicate |
| Would the merged version need a flag or a role check? | yes → leave them apart; the variation is real |
| Does the code read anything that distinguishes the copies? | no → generalize the type (`$employees`) |
| Is one copy dead? | yes → delete it (Ch 5) |

## Worked Example
The list example, read for *why* the merge is safe:

1. **Spot the duplication** — two functions, same three method calls, same `render()`.
2. **Check what varies** — only the parameter and loop-variable names. No method is called on a developer that isn't also called on a manager.
3. **Generalize** — one `showList(array $employees)`; the caller passes either array. Keep the domain distinction where it matters, at the call site (`showList($developers)`).
4. **Compact** — the guide's "Very good" step inlines `$expectedSalary`, `$experience`, `$githubLink` and `$data` into a single `render([...])` call.

A judgment call the guide leaves open: step 4 trades the explanatory variables Ch 2 recommends for brevity. With three self-describing method calls the inline version reads fine; with opaque expressions, keep the names. And note what makes `showList()` safe to call with either array: both kinds of object must offer the same three methods — in this guide's terms, an `Employee` **interface** (Ch 8), which `array` as a parameter type cannot express. A typed collection or a docblock (`@param Employee[] $employees`) states that contract.

## Key Takeaways
1. **One place to change each piece of logic** — the single inventory list.
2. **Near-miss copies are the usual case**; collapse distinctions the code never reads.
3. **Bad abstractions can be worse than duplicate code** — if the merge needs a flag, don't merge.
4. **Follow SOLID to find the right abstraction**, then remove the duplication into it.
5. **Inline single-use temporaries** only when the remaining expression still reads clearly.

## Connects To
- **Ch 8 (SOLID)**: the guide ties DRY to SOLID explicitly. (Its text says SOLID is "laid out in the Classes section" — a leftover from the JavaScript original, where SOLID sits under Classes; in the PHP guide it is its own section.)
- **Ch 4**: a flag parameter is the sign that a merge went too far.
- **Ch 5**: dead code is the other half of the guide's "just as bad as duplicate code" pairing.
- **Ch 2**: synonym drift (`getUserInfo`/`getUserData`) is how duplicate implementations start.
- **clean-code-java ch17 (G5, Duplication)**: the book's own statement of DRY, in the smells catalogue.
