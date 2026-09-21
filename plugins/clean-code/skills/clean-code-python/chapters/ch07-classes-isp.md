# Chapter 7: Classes — Interface Segregation Principle (ISP)

## Core Idea
> "Keep interfaces small so that users don't end up depending on things they don't need." — Uncle Bob

**Python has no interfaces — it has Abstract Base Classes**, "which are a little different, but can serve the same purpose." Decompose a fat ABC into small, composable ABCs that segregate each feature.

## Frameworks Introduced
- **ABCs as Python's interfaces**: define public methods and properties without implementing them.
  - When to use: when a function should accept "any object with these methods", not one concrete class. The guide's framing: *"I don't care what object you give me, as long as it has certain methods and attributes I expect to make use of."*
  - How: `class Greeter(metaclass=ABCMeta)` with `@abstractmethod` members; annotate the consumer against the ABC (`def welcome_user(user_name: str, actor: Greeter)`).
  - Note the Python mechanics: ABCs are enforced **at instantiation**, not at definition. Stacking order matters — `@staticmethod` above `@abstractmethod`, and `@property` above `@abc.abstractmethod`.
- **Segregate by feature**: split one ABC into several, each carrying one capability.
  - When to use: the moment an implementer is forced to supply a member it doesn't need.
  - How: (1) identify the capabilities the fat ABC bundles; (2) put shared *state* in a base carrier (`DataCarrier`); (3) give each capability its own ABC inheriting that carrier (`Loadable`, `Saveable`); (4) implementers inherit only what they use; (5) consumers annotate against the narrowest ABC that covers their needs.
  - Why it works: it removes the dilemma the guide names — implement a useless stub, or delete the method and add it back later. Both are worse than splitting.
- **Don't write interfaces for features you don't use yet**: "The problem is that we have written an *interface* that has features we don't need right now as we are not using them."
  - When to use: when designing "comprehensive" base classes up front.
  - How: add a capability ABC when the first real implementer needs it. Segregated interfaces make that addition non-breaking, which is what makes the deferral safe.

## Key Concepts
- **Abstract Base Class (ABC)** — `abc.ABCMeta` / `abc.abstractmethod`; Python's stand-in for an interface, enforced at instantiation.
- **`@abstractmethod`** — marks a member subclasses must implement before the class can be instantiated.
- **Fat interface** — an ABC bundling capabilities no single implementer needs in full.
- **Capability ABC** — a small ABC representing exactly one feature (`Loadable`, `Saveable`).
- **Data carrier** — a base holding the shared state contract (`DataCarrier.data`) that capability ABCs build on.
- **Dummy/stub implementation** — a no-op or `NotImplementedError` method written only to satisfy an abstract member; "useless code that we will need to maintain."
- **Duck typing** — the informal counterpart: usable if it has the right methods, no declaration required.

## Code Examples
The baseline — an ABC used the way an interface would be, so the consumer depends on a capability rather than a class:

```python
from abc import ABCMeta, abstractmethod


# Define the Abstract Class for a generic Greeter object
class Greeter(metaclass=ABCMeta):
     """An object that can perform a greeting action."""

     @staticmethod
     @abstractmethod
     def greet(name: str) -> None:
          """Display a greeting for the user with the given name"""


class FriendlyActor(Greeter):
     """An actor that greets the user with a friendly salutation"""

     @staticmethod
     def greet(name: str) -> None:
          """Greet a person by name"""
          print(f"Hello {name}!")


def welcome_user(user_name: str, actor: Greeter):
     """Welcome a user with a given name using the provided actor"""
     actor.greet(user_name)


welcome_user("Barbara", FriendlyActor())
```

- **What it demonstrates**: `welcome_user` names one required capability. Any `Greeter` works — the interface is exactly one method wide, which is ISP satisfied by construction.

## Reference Tables

| Symptom | ISP diagnosis | Fix |
|---|---|---|
| `Can't instantiate abstract class X with abstract method y` | ABC demands an unneeded feature | Split into capability ABCs |
| A method that does nothing / raises `NotImplementedError` | Stub written to satisfy the ABC | Split; drop the inheritance |
| Removing a member now, re-adding it later | Interface designed ahead of need | Add a capability ABC when needed |
| Implementers use disjoint subsets of the ABC | Fat interface | One ABC per subset |

| Concern | Goes in |
|---|---|
| Shared state contract | Base carrier (`DataCarrier`) |
| One capability | Its own ABC (`Loadable`, `Saveable`) |
| Consumer's requirement | Narrowest ABC that covers it |

## Worked Example
The guide's scenario: PDF documents authored in-house and served to website visitors. Tempted by completeness, we "design a comprehensive abstract base class for our document."

**Error.** One ABC bundling three members:

```python
import abc


class Persistable(metaclass=abc.ABCMeta):
     """Serialize a file to data and back"""

     @property
     @abc.abstractmethod
     def data(self) -> bytes:
          """The raw data of the file"""

     @classmethod
     @abc.abstractmethod
     def load(cls, name: str):
          """Load the file from disk"""

     @abc.abstractmethod
     def save(self) -> None:
          """Save the file to disk"""


# We just want to serve the documents, so our concrete PDF document
# implementation just needs to implement the `.load()` method and have
# a public attribute named `data`.

class PDFDocument(Persistable):
     """A PDF document"""

     @property
     def data(self) -> bytes: ...

     @classmethod
     def load(cls, name: str): ...
```

We serve documents; we never save them. So `.save()` goes unimplemented — and Python refuses to cooperate:

```
Can't instantiate abstract class PDFDocument with abstract method save.
```

The guide walks the dilemma and rejects both horns. *"That's annoying. We don't really need to implement `.save()` here. We could implement a dummy method that does nothing or raises `NotImplementedError`, but that's useless code that we will need to maintain."* And deleting it only defers the pain: *"if we remove `.save()` from the abstract class now we will need to add it back when we will later implement a way for users to submit their documents, bringing us back to the same situation as before."*

The diagnosis is the lesson: *"we have written an interface that has features we don't need right now as we are not using them."*

**Good.** Shared state in a carrier; each capability its own ABC:

```python
import abc


class DataCarrier(metaclass=abc.ABCMeta):
     """Carries a data payload"""

     @property
     def data(self):
          ...


class Loadable(DataCarrier):
     """Can load data from storage by name"""

     @classmethod
     @abc.abstractmethod
     def load(cls, name: str):
          ...


class Saveable(DataCarrier):
     """Can save data to storage"""

     @abc.abstractmethod
     def save(self) -> None:
          ...


class PDFDocument(Loadable):
     """A PDF document"""

     @property
     def data(self) -> bytes: ...

     @classmethod
     def load(cls, name: str) -> None: ...


def view(request):
     """A web view that handles a GET request for a document"""
     requested_name = request.qs['name']  # We want to validate this!
     return PDFDocument.load(requested_name).data
```

**Why this resolves the dilemma rather than dodging it.** `PDFDocument` inherits `Loadable` only, instantiates cleanly, and contains no stub. When upload support arrives, a writable type inherits `Saveable` — or both — and **no existing class changes**. That is the deferral made safe: segregated interfaces turn "add a capability later" from a breaking edit into an additive one.

Two details worth copying: `DataCarrier.data` is a plain `@property`, *not* abstract, so it states the shared contract without forcing a re-declaration; and the guide leaves its own open thread in the view — `# We want to validate this!` — a reminder that `request.qs['name']` reaching `load()` is an unvalidated path-traversal surface.

## Anti-patterns
- **The comprehensive base class**: designing `Persistable` for every imaginable future need; the exact mistake this section is built on.
- **Stub implementations**: a no-op or `NotImplementedError` to satisfy an abstract member — "useless code that we will need to maintain", and an LSP break (Ch 6) no checker will catch.
- **Delete-now-re-add-later**: returns you to the same situation; split instead.
- **Annotating against the fattest available ABC**: re-imports the dependency you segregated away. Annotate the narrowest sufficient one.
- **Bundling state and behaviour in one ABC**: separate the carrier from the capabilities.
- **Passing unvalidated user input to a loader**: flagged in the guide's own code.

## Key Takeaways
1. **Python has ABCs, not interfaces** — same purpose, enforced at instantiation.
2. **`Can't instantiate abstract class … with abstract method …` is an ISP violation report.** Treat it as a design signal, not an obstacle.
3. **Never write a stub to satisfy an ABC.** It's unmaintained code and a substitutability lie.
4. **One capability, one ABC** — `Loadable`, `Saveable` — with shared state in a carrier base.
5. **Implementers inherit only what they use**; consumers annotate the narrowest ABC that covers their need.
6. **Don't design interfaces for unbuilt features.** Segregation makes adding one later additive rather than breaking.
7. **Keep the consumer's requirement one method wide where you can** — `Greeter.greet` is the ideal.

## Connects To
- **Ch 4 (SRP)**: ISP is SRP applied to interfaces — `Persistable` has two reasons to change (loading, saving).
- **Ch 6 (LSP)**: fat interfaces cause the `NotImplementedError` stubs that silently break substitutability.
- **Ch 8 (DIP)**: DIP says depend on abstractions; ISP says keep each one small. `Echo`'s single `.write()` is both principles at once.
- **Ch 5 (OCP)**: mixins and capability ABCs are two routes to small composable units; mixins carry behaviour, ABCs carry contracts.
- **`typing.Protocol`**: structural typing — the same segregation without requiring implementers to inherit at all.
- **Go / Java interfaces**: the languages the guide contrasts Python against.
