# Chapter 6: Classes — Liskov Substitution Principle (LSP)

## Core Idea
> "Functions that use pointers or references to base classes must be able to use objects of derived classes without knowing it." — Uncle Bob

**A function accepting a supertype must also accept all its subtypes with no modification.** In Python the most common breach is a subclass changing a method's *signature* — and `mypy` catches it mechanically.

## Frameworks Introduced
- **Substitutability test**: pass a subtype instance wherever the supertype is annotated. If the call site must change, LSP is broken.
  - When to use: on every override, and before widening a parameter's annotation to a base class.
  - How: write the consumer function against the base type (`def render(view: View, request)`), then call it with each subtype. A `TypeError` means the subtype isn't one.
- **Preserve the public-facing protocol**: the guide poses the hard question directly — *"But how do we know what constitutes it for a given class?"*
  - Answer: **run a type checker.** "Type hinters like *mypy* will raise an error when it detects mistakes like this." The protocol is whatever `mypy` compares between supertype and subtype: parameter list, parameter types, return type.
  - When to use: as a CI gate, not a review convention. This is the chapter's practical payload.
- **Behavioural subtyping (Liskov & Wing, 1994)**: the principle is named after **Barbara Liskov**, who with **Jeannette Wing** wrote the seminal paper *"A behavioral notion of subtyping"*.
  - Core tenet, quoted: "a subtype (must) preserve the behaviour of the supertype methods **and also all invariant and history properties** of its supertype".
  - When to use: when signatures match but semantics don't — the part `mypy` cannot check.
  - How: enumerate the supertype's invariants (what's always true) and history properties (what sequences of states are legal), then confirm the subtype honours each.

## Key Concepts
- **Substitutability** — a subtype is usable wherever the supertype is expected, with no call-site change.
- **Public-facing protocol** — the signatures a consumer may rely on; what `mypy` compares across the inheritance edge.
- **Invariant** — a property always true of an object (from Liskov & Wing).
- **History property** — a constraint on how an object's state may legally change over time.
- **Signature incompatibility** — the concrete Python breach: an override adding, removing, or retyping a parameter.
- **Behavioural subtyping** — the formal name for LSP-as-semantics, not merely LSP-as-types.
- **`# type: ignore`** — the pragma the guide must add to its own bad example, because `mypy` refuses it otherwise.

## Code Examples
The breach, reduced to its essential line. `TemplateView` demands an extra required argument that `View` never had:

```python
class View:
     content_type = "text/plain"

     def get(self, request) -> Response:
          ...


class TemplateView(View):
     content_type = "text/html"

     def get(self, request, template_file: str) -> Response:  # type: ignore
          """Render the message body as HTML"""
          with open(template_file) as fd:
               return Response(status=200, content_type=self.content_type, body=fd.read())


def render(view: View, request) -> Response:
     """Render a View"""
     return view.get(request)
```

- **What it demonstrates**: `render()` is written against `View` and is correct for it. Called with a `TemplateView`, it **raises `TypeError`** — the missing `template_file`. The subclass declares `TemplateView(View)` but is not substitutable for one.

The exact `mypy` output the guide reproduces — this is what the gate looks like in practice:

```
error: Signature of "get" incompatible with supertype "View"
<string>:36: note:      Superclass:
<string>:36: note:          def get(self, request: Any) -> Response
<string>:36: note:      Subclass:
<string>:36: note:          def get(self, request: Any, template_file: str) -> Response
```

## Reference Tables

| Override change | LSP verdict | Caught by mypy |
|---|---|---|
| Add a **required** parameter | ✗ Breaks | Yes |
| Add an **optional** parameter (with default) | ✓ Safe | — |
| Remove a parameter | ✗ Breaks | Yes |
| Narrow a parameter type | ✗ Breaks (contravariance) | Yes |
| Widen a parameter type | ✓ Safe | — |
| Narrow the return type | ✓ Safe (covariance) | — |
| Widen the return type | ✗ Breaks | Yes |
| Same signature, violated invariant | ✗ Breaks | **No** — review needed |
| Same signature, raises new exception | ✗ Breaks (history property) | **No** — review needed |

## Worked Example
Compare this chapter's `TemplateView` with the *identical class name* in Ch 5 (OCP). Same base, same goal — serve HTML from a template — and two different failures, which is why the guide reuses the example.

**Ch 5's bad version** overrode `get()` with a *matching* signature. `mypy` is silent; `render(view, request)` works for both classes. The damage is to *maintainability*: the base can never change again.

**This chapter's bad version** overrides `get()` with an *extra required parameter*. `mypy` fails the build; `render()` raises `TypeError` at runtime. The damage is to *correctness* — the subtype is simply not a `View`.

**The fix is Ch 5's fix.** Keep `get()`'s signature fixed and move the variation into state — `template_file` becomes a class attribute, not a parameter:

```python
class TemplateView(View):
     content_type = "text/html"
     template_file = "index.html"        # state, not a parameter

     def render_body(self) -> str:
          with open(self.template_file) as fd:
               return fd.read()
```

**The transferable rule**: when an override wants more information than the base method receives, that information belongs in the subtype's **state**, not in its **signature**. Widening the signature is how LSP gets broken; widening the state is how OCP gets satisfied. The two principles point at the same refactoring from opposite directions.

## Anti-patterns
- **Adding a required parameter to an override**: the canonical Python LSP break, and the one `mypy` names outright.
- **Silencing the checker with `# type: ignore`**: the guide uses it only to keep a deliberately broken example in CI. In real code it converts a build failure into a runtime `TypeError`.
- **`raise NotImplementedError` in an override**: signature-compatible, substitutability destroyed — no checker will catch it. (Ch 7 shows the ISP fix for the pressure that causes this.)
- **Strengthening a precondition**: a subtype rejecting inputs the base accepted; violates the invariant clause even with identical types.
- **Raising a new exception type**: a history-property violation, invisible to `mypy`.
- **Inheriting for code reuse alone**: if the subtype isn't substitutable, use composition or a mixin (Ch 5) instead.

## Key Takeaways
1. **A function taking a supertype must accept every subtype unchanged.** Test by calling the consumer with each subtype.
2. **Signature changes are the Python breach** — and `mypy` reports them as `Signature of "get" incompatible with supertype "View"`.
3. **Put mypy in CI.** This is the chapter's real mechanism; LSP compliance becomes a build gate rather than a review opinion.
4. **Never silence the error with `# type: ignore`** — you're trading a build failure for a production `TypeError`.
5. **Extra information belongs in state, not in the signature.** That single move satisfies both LSP and OCP.
6. **Type compatibility is necessary, not sufficient.** Liskov & Wing require invariants and history properties too — those need human review.
7. **If it isn't substitutable, it isn't a subtype.** Reach for composition or mixins.

## Connects To
- **Ch 5 (OCP)**: the same `View`/`TemplateView` pair, failing differently — and OCP's fix is LSP's fix.
- **Ch 7 (ISP)**: fat interfaces pressure implementers into `NotImplementedError` stubs, an LSP break a checker can't see.
- **Ch 8 (DIP)**: depending on a narrow abstraction (`.write()`) shrinks the protocol a subtype must preserve.
- **Ch 1**: the clearest instance of this adaptation's thesis — prefer rules a checker can enforce.
- **Liskov & Wing (1994)**, *"A behavioral notion of subtyping"*: the source of the invariant/history-property formulation.
- **`typing.Protocol` / structural typing**: Python's alternative to nominal inheritance when substitutability is all you need.
