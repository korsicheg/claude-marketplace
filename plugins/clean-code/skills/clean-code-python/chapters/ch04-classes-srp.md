# Chapter 4: Classes — Single Responsibility Principle (SRP)

## Core Idea
> "A class should have only one reason to change." — Robert C. Martin

Split classes by **reason to change**, not by size. The guide's gloss is the operative part: *"'Reasons to change' are, in essence, the responsibilities managed by a class or function."*

## Frameworks Introduced
- **One reason to change**: enumerate the distinct forces that would make you edit the class. More than one means split.
  - When to use: before adding a method to an existing class, and whenever a class name contains "and" or "Manager"/"Handler".
  - How: (1) list the class's responsibilities in plain language; (2) ask which *external* change would force an edit to each; (3) extract every responsibility that answers differently into a function or collaborator; (4) pass the result in via `__init__`.
  - Why it works: "Any change to one or the other carries the risk of impacting the other." Decoupling removes the risk, not just the untidiness.
  - **Bonus test**: a correctly extracted responsibility is immediately reusable elsewhere. If the extraction produces nothing reusable, you may have split by size rather than by reason.
- **Contract-based decoupling**: after extraction, the two parts are independent "as long as the contract between them does not change, i.e. the function provides a string and the class `__init__` method accepts a string."
  - When to use: to decide *how narrow* the seam should be.
  - How: make the seam a primitive or a small stable type. A narrow contract is what makes the two sides changeable in isolation.

## Key Concepts
- **Reason to change** — an external force (a library upgrade, a format change, a new requirement) that would compel an edit; the unit of responsibility.
- **Responsibility** — one such force, managed by exactly one class or function.
- **Contract** — the type-level agreement at the seam between extracted parts (here: "produces a `str`" / "accepts a `str`").
- **Constructor injection** — supplying a collaborator or value through `__init__` instead of computing it internally.
- **Reusability dividend** — the extracted unit becoming callable from elsewhere; evidence the split was along a real seam.
- **`importlib.metadata`** — the stdlib package-version lookup whose use is the extracted responsibility in the example.

## Reference Tables

| Question | SRP verdict |
|---|---|
| Can you name two unrelated forces that would edit this class? | Split |
| Does the class name contain "and", or a vague noun (`Manager`, `Handler`)? | Inspect — likely split |
| After splitting, is the extracted part reusable? | Confirms a real seam |
| Is the seam a primitive or small stable type? | Good contract |
| Did you split purely because the class got long? | Not SRP — re-examine |

## Worked Example
The guide builds an HTML element that renders a comment carrying the program's version number.

**Bad.** One class, two jobs:

```python
from importlib import metadata


class VersionCommentElement:
     """An element that renders an HTML comment with the program's version number
     """

     def get_version(self) -> str:
          """Get the package version"""
          return metadata.version("pip")

     def render(self) -> None:
          print(f'<!-- Version: {self.get_version()} -->')


VersionCommentElement().render()
```

The guide names the two responsibilities explicitly:

- Retrieve the version number of the Python package
- Render itself as an HTML element

These answer to different forces. The first changes if the packaging metadata API changes, or if the version should come from somewhere else entirely, or if the target package stops being `pip`. The second changes if the HTML output changes. Fused in one class, *"any change to one or the other carries the risk of impacting the other."* Note the hardcoded `"pip"` — the retrieval half isn't even parameterized, because nothing forced it to be.

**Good.** The retrieval responsibility leaves the class, and the value arrives through the constructor:

```python
from importlib import metadata


def get_version(pkg_name: str) -> str:
     """Retrieve the version of a given package"""
     return metadata.version(pkg_name)


class VersionCommentElement:
     """An element that renders an HTML comment with the program's version number
     """

     def __init__(self, version: str):
          self.version = version

     def render(self) -> None:
          print(f'<!-- Version: {self.version} -->')


VersionCommentElement(get_version("pip")).render()
```

**What changed, and why it counts.** The class now "only needs to take care of rendering itself." The two halves are independent so long as the contract holds — `get_version` returns a `str`, `__init__` accepts a `str`. Three dividends follow, and the third is the one people miss:

1. The renderer is testable with a literal string; no packaging metadata needed in the test.
2. `get_version()` gained a `pkg_name` parameter, because as a standalone function the generalization was obvious.
3. *"As an added bonus, the `get_version()` is now reusable elsewhere."* The reuse is the evidence that the split followed a real seam rather than an arbitrary line.

## Anti-patterns
- **A class that both acquires and presents data**: the canonical two-responsibility shape, and exactly this example.
- **Splitting by line count**: SRP is about reasons to change. A 200-line class with one reason to change is fine; a 20-line class with two is not.
- **Computing a dependency inside the class**: `metadata.version("pip")` in a method hardwires the source and the target; inject the result instead.
- **Extracting into a unit nothing else can use**: usually a sign of a split along the wrong axis.
- **A wide seam** (passing whole framework objects between the halves): re-couples what you just separated; keep the contract narrow.

## Key Takeaways
1. **One reason to change per class.** Count the external forces, not the lines.
2. **Name the responsibilities out loud** — the bad example is obvious only once "retrieve" and "render" are written down as a list.
3. **Inject, don't compute.** Take the value through `__init__`; let a separate function produce it.
4. **Keep the seam narrow** — a `str` in, a `str` out. The contract is what buys independent change.
5. **Reusability is the proof.** `get_version()` became useful elsewhere; if your extraction isn't, re-examine the split.
6. **A function is a legitimate collaborator.** The extraction here is a plain module-level function, not another class — don't reach for a class when a function suffices.

## Connects To
- **Ch 3**: "do one thing" is the same rule at function scope; the SRP fix extracts `get_version()` exactly as Ch 3 extracts `get_active_clients()`.
- **Ch 5 (OCP)**: SRP decides *what* a class owns; OCP decides how subtypes extend it. The OCP example's `render_body()` is a single-responsibility hook.
- **Ch 7 (ISP)**: ISP is SRP applied to interfaces — `Persistable` fails because it bundles loading and saving.
- **Ch 8 (DIP)**: constructor injection here is the same move DIP generalizes to abstractions.
- **Ch 2**: the "Even better" class-packaging tier is where SRP starts, at the naming layer.
