# Chapter 9: Don't Repeat Yourself (DRY)

## Core Idea
Duplicate code means "more than one place to alter something if you need to change some logic." Remove it by finding the right abstraction — but **"bad abstractions can be worse than duplicate code, so be careful!"**

## Frameworks Introduced
- **DRY**: do your absolute best to avoid duplicate code.
  - When to use: whenever the same logic appears twice and both copies must change together.
  - How: "Removing duplicate code means creating an abstraction that can handle this set of different things with just one function/module/class."
  - Why it works: one place to update. "If you only have one list, there's only one place to update!"
- **The restaurant-inventory model**: the guide's mental image for why duplication costs.
  - "Imagine if you run a restaurant and you keep track of your inventory: all your tomatoes, onions, garlic, spices, etc. If you have multiple lists that you keep this on, then all have to be updated when you serve a dish with tomatoes in them."
  - When to use: to explain the cost to someone who sees duplication as merely untidy. The cost isn't the extra lines — it's the *obligation to remember* every copy.
- **The abstraction caveat** — the rule's essential counterweight: "**Getting the abstraction right is critical. Bad abstractions can be worse than duplicate code, so be careful!** Having said this, if you can make a good abstraction, do it!"
  - When to use: before merging two similar-looking blocks.
  - How: ask whether the two copies must *always* change together for the same reason. If they will diverge, the merge creates a class with two reasons to change (Ch 4) and a flag parameter (Ch 3) to tell the cases apart.
  - Decision rule: **duplication of logic** → deduplicate. **Coincidental similarity** → leave it alone.
- **The near-miss diagnosis**: "Often you have duplicate code because you have two or more slightly different things, that share a lot in common, but their differences force you to have two or more separate functions that do much of the same things."
  - When to use: the common real case — the copies aren't identical, which is why they were copied.
  - How: identify what the *consumer* actually needs. In the example the serializer needs only `experience` and `github_link`; the distinction between developer and manager is invisible to it, so it shouldn't exist in its types.

## Key Concepts
- **DRY (Don't Repeat Yourself)** — one authoritative place for each piece of logic.
- **Bad abstraction** — a merge of things that don't actually vary together; worse than the duplication it replaced.
- **Coincidental duplication** — code that looks alike today for unrelated reasons and will diverge.
- **Near-miss duplication** — two nearly-identical units whose small differences motivated the copy.
- **Generalization** — replacing sibling types with one supertype the consumer can serve (`Developer` + `Manager` → `Employee`).
- **Single point of update** — the property a good abstraction buys.

## Reference Tables

| Situation | Action | Reason |
|---|---|---|
| Same logic, must change together | Deduplicate | One place to update |
| Similar shape, different reasons to change | Leave duplicated | A merge would need a flag (Ch 3) |
| Near-miss: differs only in type name | Generalize the type | The difference is invisible to the consumer |
| Unsure whether they'll diverge | Wait | "Bad abstractions can be worse" |
| Merge requires a boolean parameter | Abandon the merge | The flag confesses two responsibilities |

## Worked Example
The guide models a company with developers and managers, each carrying `experience` and a `github_link`, and serializes each group to a list of dicts.

**Bad.** Two identical classes and two identical functions:

```python
@dataclass
class Developer:
    def __init__(self, experience: float, github_link: str) -> None:
        self._experience = experience
        self._github_link = github_link

    @property
    def experience(self) -> float:
        return self._experience

    @property
    def github_link(self) -> str:
        return self._github_link


@dataclass
class Manager:
    # ... character-for-character identical to Developer ...


def get_developer_list(developers: List[Developer]) -> List[Dict]:
    developers_list = []
    for developer in developers:
        developers_list.append({
            'experience': developer.experience,
            'github_link': developer.github_link
        })
    return developers_list


def get_manager_list(managers: List[Manager]) -> List[Dict]:
    # ... identical but for the names ...
```

`Developer` and `Manager` differ only in their names, and the two functions differ only in their variable names. Add a `years_at_company` field and there are four edits, with nothing to catch a missed one. This is the restaurant with two inventory lists.

**Good.** One type, one function:

```python
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Employee:
    def __init__(self, experience: float, github_link: str) -> None:
        self._experience = experience
        self._github_link = github_link

    @property
    def experience(self) -> float:
        return self._experience

    @property
    def github_link(self) -> str:
        return self._github_link


def get_employee_list(employees: List[Employee]) -> List[Dict]:
    employees_list = []
    for employee in employees:
        employees_list.append({
            'experience': employee.experience,
            'github_link': employee.github_link
        })
    return employees_list


## create list objects of developers
company_developers = [
    Employee(experience=2.5, github_link='https://github.com/1'),
    Employee(experience=1.5, github_link='https://github.com/2')
]
company_developers_list = get_employee_list(employees=company_developers)

## create list objects of managers
company_managers = [
    Employee(experience=4.5, github_link='https://github.com/3'),
    Employee(experience=5.7, github_link='https://github.com/4')
]
company_managers_list = get_employee_list(employees=company_managers)
```

**Why this abstraction is a good one** — the test the caveat demands. The distinction between a developer and a manager is real in the business, but **invisible to this code**: nothing here reads a role, branches on one, or formats one differently. The two types encoded a distinction the program never used, so collapsing them removes no information. Note the call sites keep their meaningful names — `company_developers`, `company_managers` — so the domain distinction survives where it belongs, in the data, not in duplicated types.

**And when it would be a bad one.** If managers gained a `reports` field, or the serializer needed to emit a `role` key, `Employee` would start growing role-conditional branches — a flag parameter in disguise (Ch 3) and a second reason to change (Ch 4). At that point the right shape is a shared base or protocol with role-specific subtypes, not one merged class. This is exactly the judgment the guide is warning about: the same merge is correct today and wrong after one requirement.

## Anti-patterns
- **Parallel near-identical classes** (`Developer` / `Manager`): duplication created by naming a distinction the code doesn't use.
- **Parallel near-identical functions** (`get_developer_list` / `get_manager_list`): differ only in variable names.
- **Merging on appearance**: deduplicating code that merely looks alike; "bad abstractions can be worse than duplicate code."
- **An abstraction needing a flag to distinguish its cases**: proof the merge was wrong (Ch 3).
- **Deduplicating too early**: with one example of a pattern you cannot see the axis of variation; wait for the second or third.
- **Keeping duplication out of caution indefinitely**: the guide is explicit — "if you can make a good abstraction, do it!"

## Key Takeaways
1. **Duplication's cost is the obligation to remember every copy**, not the extra lines. One list, one place to update.
2. **Deduplicate logic, not appearance.** Ask whether the copies must always change together for the same reason.
3. **Bad abstractions can be worse than duplication** — the most important sentence in the chapter.
4. **Near-miss duplication is the normal case.** Ask what the consumer actually needs; distinctions it never reads shouldn't exist in its types.
5. **If the merge requires a flag, abandon the merge.** The flag is the duplication telling you it was real variation.
6. **Keep domain distinctions in the data** (`company_developers`) when the code doesn't act on them.
7. **When unsure, wait.** You cannot see the axis of variation from one example — but don't let caution become permanent.

## Connects To
- **Ch 3 (flags, do one thing)**: a flag parameter appearing during a merge is the sign the abstraction is wrong.
- **Ch 4 (SRP)**: a bad abstraction is a unit with two reasons to change; SRP is the test for whether a merge was sound.
- **Ch 5 (OCP)**: mixins remove duplication across classes without forcing them into one type.
- **Ch 7 (ISP)**: segregated capability ABCs let types share contracts without sharing a fat implementation.
- **Ch 2 (vocabulary)**: synonym drift is how this duplication is born — the same entity under two names becomes two types.
- **Rule of Three** (external): a common companion heuristic — wait for the third occurrence before abstracting.
