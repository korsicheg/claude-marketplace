# Chapter 3: Functions

## Core Idea
**Functions should do one thing** — "by far the most important rule in software engineering." Every other rule in this chapter (argument count, flags, abstraction levels, side effects) is a *detector* for violating it.

## Frameworks Introduced
- **Do one thing** — the root rule. "If you take nothing else away from this guide other than this, you'll be ahead of many developers."
  - When to use: every function, always.
  - How: if you can only describe it using "and", split it. `email_clients` that *filters and emails* becomes `get_active_clients` + `email_clients`.
  - Why it works: single-action functions "can be refactored easily"; multi-action functions are "harder to compose, test, and reason about."
  - **Python's third tier**: once filtering is its own function, make it a **generator** — laziness comes free and the pipeline stops materializing intermediate lists.
- **Two arguments or fewer** — "A large amount of parameters is usually the sign that a function is doing too much (has more than one responsibility)."
  - When to use: any signature reaching three parameters; mandatory at four.
  - How: bundle related parameters into a **dedicated data structure**. The guide's reasoning is not merely cosmetic: "we may be able to move some computations, done with those parameters inside the function, into methods belonging to the new object, therefore reducing the complexity of the function." The new object is also reusable elsewhere.
- **Function names should say what they do** — `message.handle()` → `message.send()`.
  - When to use: any verb vague enough to cover several actions (`handle`, `process`, `manage`, `do`).
  - How: name the single action. If no single verb fits, the function violates "do one thing".
- **One level of abstraction per function** — "When you have more than one level of abstraction, your function is usually doing too much."
  - When to use: when a function mixes orchestration with mechanics (tokenizing *and* parsing *and* walking).
  - How: extract each level into its own named function; the parent reads as a sequence of intentions. "Splitting up functions leads to reusability and easier testing."
- **No flags as function parameters** — "Flags tell your user that this function does more than one thing."
  - When to use: any boolean parameter that selects a code path.
  - How: split into two named functions — `create_file` / `create_temp_file`. The flag's two branches become two names.
- **Avoid and centralize side effects** — "A function produces a side effect if it does anything other than take a value in and return another value or values."
  - When to use: file writes, global mutation, shared mutable state, network calls.
  - How: prefer pure input→output. When an effect is genuinely needed, "have one (and only one) service that does it" — centralize and *indicate* where effects occur. To manage state deliberately, use a class: "The reason why we create instances of classes is to manage state!"

## Key Concepts
- **Side effect** — anything a function does other than take values in and return values out: writing a file, mutating a global, "or accidentally wiring all your money to a stranger."
- **`global` keyword** — the explicit marker of module-level mutation; the guide notes it "is changing the meaning of the following line" and introduces the side effect.
- **Flag parameter** — a boolean argument selecting between code paths; a signature-level confession of multiple responsibilities.
- **Level of abstraction** — the altitude of a statement: orchestration (`tokenize(code)`) vs mechanics (`code.split('\n')`).
- **Generator** — a lazy iterator (`(c for c in clients if c.active)`), the guide's "Even better" answer to filtering.
- **`Iterator` / `Generator[Y, S, R]`** — the `typing` annotations that make a lazy pipeline's contract explicit.
- **Parameter object** — a `dataclass` / `NamedTuple` / `TypedDict` bundling related arguments into one reusable entity.
- **`astuple`** — `dataclasses.astuple(config)`, unpacks a dataclass positionally.
- **Idempotence (implied)** — the bad side-effect example works once and breaks on the second call: "what will happen if we call the function again?"

## Code Examples
The do-one-thing rule at its **"Even better"** tier — the guide asks "Do you see an opportunity for using generators now?" and this is the answer:

```python
from typing import Generator, Iterator


class Client:
    active: bool


def email(client: Client):
    pass


def active_clients(clients: Iterator[Client]) -> Generator[Client, None, None]:
    """Only active clients"""
    return (client for client in clients if client.active)


def email_client(clients: Iterator[Client]) -> None:
    """Send an email to a given list of clients.
    """
    for client in active_clients(clients):
        email(client)
```

- **What it demonstrates**: splitting for *correctness* (one thing each) unlocks a *performance* improvement for free. Once filtering is isolated, it becomes a generator, the `List` parameter relaxes to `Iterator`, and nothing is materialized.

The side-effects rule's **"Also good"** tier, which reframes the problem as state ownership rather than purity:

```python
from dataclasses import dataclass


@dataclass
class Person:
    name: str

    @property
    def name_as_first_and_last(self) -> list:
        return self.name.split()


# The reason why we create instances of classes is to manage state!
person = Person("Ryan McDermott")
print(person.name)                       # => "Ryan McDermott"
print(person.name_as_first_and_last)     # => ["Ryan", "McDermott"]
```

- **What it demonstrates**: the derived value becomes a `@property` computed on demand, so the original `name` is never overwritten and repeat access is safe.

## Reference Tables

The argument-bundling ladder — all six tiers the guide names, in its own order:

| Tier | Mechanism | Trade-off |
|---|---|---|
| **Bad** | `create_menu(title, body, button_text, cancellable)` | 4 positional args; combinatorial test surface |
| **Java-esque** | `Menu(config: dict)` | Untyped `dict`; keys unchecked, no IDE support |
| **Also good** | Plain class with annotated class attributes | Typed and mutable; needs per-field assignment |
| **Fancy** | `NamedTuple` | Immutable, unpackable, typed; defaults allowed |
| **Even fancier** | `@dataclass` + `astuple()` | Typed, mutable, `__repr__`/`__eq__` free |
| **Even fancier (3.8+)** | `TypedDict` | Dict ergonomics with type checking; **all keys required** |

| Detector | Signal | Fix |
|---|---|---|
| Argument count | ≥3 params | Bundle into a parameter object |
| Flag param | `bool` selecting a path | Split into two named functions |
| Vague verb | `handle`, `process` | Name the one action |
| Mixed altitude | Orchestration + mechanics | Extract each level |
| `global` statement | Module mutation | Return a value, or own state in a class |

## Worked Example
The side-effects rule, walked end to end — the guide's sharpest example because the bug is invisible on the first call.

**Bad.** A module-level string is mutated in place by a function that takes nothing and returns nothing:

```python
# type: ignore

fullname = "Ryan McDermott"


def split_into_first_and_last_name() -> None:
    # The use of the global keyword here is changing the meaning of the
    # following line. This function is now mutating the module-level
    # state and introducing a side-effect!
    global fullname
    fullname = fullname.split()


split_into_first_and_last_name()
print(fullname)  # ["Ryan", "McDermott"]
```

Two things have gone wrong, and the guide names both. First, the type changed underneath the name — `fullname` was declared `str` and is now `list`, so **mypy reports** `Incompatible types in assignment: (expression has type "List[str]", variable has type "str")`. That is why the block needs `# type: ignore` to survive the project's own CI. Second, and worse: *"OK. It worked the first time, but what will happen if we call the function again?"* — the second call reaches `.split()` on a list and raises `AttributeError`. The function is not idempotent, and nothing in its signature (`() -> None`) warns you.

**Good.** Take a value, return a value. The signature now states the whole contract, and calling it twice is harmless:

```python
from typing import List, AnyStr


def split_into_first_and_last_name(name: AnyStr) -> List[AnyStr]:
    return name.split()


fullname = "Ryan McDermott"
name, surname = split_into_first_and_last_name(fullname)
```

**The transferable lesson**: a side effect that mutates a name's *type* is caught by `mypy` for free — so annotate module-level state and let the checker find this class of bug. A `() -> None` signature that still changes program behavior is the shape to distrust.

## Anti-patterns
- **Filtering and acting in one loop** (`if client.active: email(client)`): two responsibilities fused; neither is testable alone.
- **Passing a bare `dict` as a config object** (the "Java-esque" tier): buys bundling but forfeits type checking — the guide ranks it *above* four positional args yet below every typed alternative.
- **Boolean flag parameters**: `create_file(name, temp=True)` — the caller reads `True` with no idea what it selects.
- **Mutating module state via `global`**: breaks idempotence and usually breaks the declared type as well.
- **Several functions writing to the same file**: "Don't have several functions and classes that write to a particular file — rather, have one (and only one) service that does it."
- **Vague verbs** (`handle`, `process`): usually a name for a function that does several things.
- **Unstructured shared state**: "sharing state between objects without any structure, using mutable data types that can be written to by anything."

## Key Takeaways
1. **Functions do one thing.** If the description needs "and", split it. This outranks every other rule here.
2. **≤2 arguments.** At three, bundle into a typed parameter object — and migrate computation into that object's methods.
3. Choose the parameter object by need: **`NamedTuple`** for immutable, **`@dataclass`** for mutable, **`TypedDict`** (3.8+) for dict ergonomics. Never a bare `dict`.
4. **Name the action.** `send()`, not `handle()`.
5. **One level of abstraction per function** — the parent should read as a list of intentions.
6. **No flag parameters.** Two branches, two function names.
7. **Pure by default; centralize unavoidable effects in one service.** Own deliberate state in a class — that's what instances are for.
8. **Ask "what if I call it twice?"** Non-idempotence is the tell for a hidden side effect, and `mypy` often catches the type damage.

## Connects To
- **Ch 2**: naming rules are the cheapest detector here; `handle` → `send` is the same discipline as `seq` → `locations`.
- **Ch 4 (SRP)**: "one reason to change" is the class-level statement of "do one thing"; the SRP example extracts `get_version()` exactly as this chapter extracts `get_active_clients()`.
- **Ch 8 (DIP)**: the `Echo` class with only `.write()` is this chapter's purity discipline applied to a dependency.
- **Ch 9 (DRY)**: extracted single-purpose functions are the units DRY then deduplicates.
- **Functional programming**: `map`/`filter`/comprehensions/generators are the language-level expression of "no side effects".
