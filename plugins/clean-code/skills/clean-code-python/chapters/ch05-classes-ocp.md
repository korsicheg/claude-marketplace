# Chapter 5: Classes — Open/Closed Principle (OCP)

## Core Idea
> "Incorporate new features by extending the system, not by making modifications (to it)." — Uncle Bob

Objects should be **open for extension, closed to modification**. Design classes with explicit hooks that *invite* overriding, so subtypes never have to rewrite inherited behaviour.

## Frameworks Introduced
- **Design a hook, don't override the workflow**: keep the orchestrating method fixed and expose a narrow method for subtypes to replace.
  - When to use: any time a subclass wants to change *part* of what a parent method does.
  - How: find the varying step inside the parent method; extract it into its own method (`render_body()`); promote varying values to class attributes (`content_type`). The parent's `get()` then stays untouched forever.
  - Why it works: a hook "has a single, well defined responsibility that **invites subtypes to override it**." Overriding `get()` instead freezes the parent — "it now relies on the `View` to not change the implementation of the `.get()` method, which now needs to be frozen in time."
  - **Failure mode it prevents**: the guide's precise diagnosis — "We cannot introduce, for example, some additional checks in all our `View`-derived classes because the behaviour is overridden in at least one subtype and we will need to update it." One rogue override taxes every future change to the base.
- **Class attributes as extension points**: `content_type = "text/plain"` on the class, read as `self.content_type`.
  - When to use: when the variation is a *value*, not behaviour.
  - How: declare the default on the base class; subtypes reassign it. Cheaper than a method and needs no `super()` call.
- **Mixins**: "bare-bones classes that are meant to be used exclusively with other related classes", "mixed-in" via multiple inheritance to change the target's behaviour.
  - When to use: to package reusable, single-responsibility behaviour that several classes compose differently — the guide's bridge between inheritance and composition.
  - How, with the guide's two explicit rules:
    - **Mixins should always inherit from `object`**
    - **Mixins always come before the target class** — `class Foo(MixinA, MixinB, TargetClass): ...`
  - Trade-off: composition without a container object, but behaviour now depends on MRO order, and mixins are "Not to be used by itself!" — they are incomplete by design. The guide flags an unresolved typing gap: a `FIXME` about making `typing.Protocol` work with mixins, and a `# type: ignore` on the `super()` call.

## Key Concepts
- **Open for extension** — new behaviour can be added by writing a new subtype.
- **Closed to modification** — adding that behaviour required no edit to existing code, and did not change the base's "internal contracts".
- **Hook method** — a small, single-purpose method existing to be overridden (`render_body()`).
- **Class attribute override** — a subtype reassigning an inherited class-level value (`content_type = "text/html"`).
- **Mixin** — a partial class combined into a target via multiple inheritance; always before the target, always inheriting `object`.
- **MRO (method resolution order)** — the order Python searches bases, which is why mixin position matters and what makes `super().get(request)` reach the target class.
- **Cooperative `super()`** — a mixin calling `super()` to wrap the target's method rather than replace it (`ContentLengthMixin`).
- **`field(default_factory=dict)`** — the dataclass idiom for a safe mutable default, added to `Response` so mixins can inject headers.

## Reference Tables

| Variation is a… | Extension mechanism | Example |
|---|---|---|
| Value | Class attribute | `content_type = "text/html"` |
| Step inside a workflow | Hook method | `render_body()` |
| Reusable cross-cutting behaviour | Mixin | `ContentLengthMixin` |
| Whole workflow | Rethink — you're modifying, not extending | overriding `get()` |

| Mixin rule | Consequence if broken |
|---|---|
| Inherit from `object` | Accidental coupling to a concrete hierarchy |
| Place before the target class | MRO resolves to the target; mixin never runs |
| Never instantiate alone | Missing attributes at runtime — "Not to be used by itself!" |

## Worked Example
A small web framework. `View.get()` handles a GET request and returns `text/plain`; `TemplateView` should return HTML from a template file.

**Bad.** The subtype overrides the whole workflow:

```python
class View:
     """A simple view that returns plain text responses"""

     def get(self, request) -> Response:
          return Response(
               status=200,
               content_type='text/plain',
               body="Welcome to my web site"
          )


class TemplateView(View):
     """A view that returns HTML responses based on a template file."""

     def get(self, request) -> Response:
          with open("index.html") as fd:
               return Response(status=200, content_type='text/html', body=fd.read())
```

`TemplateView` has "modified the internal behaviour of its parent class in order to enable the more advanced functionality." Nothing in `View.get()` is reused — status, content type and body are all re-specified. The base is now frozen: add a permission check to `View.get()` and `TemplateView` silently skips it.

**Good.** Split `get()` into a fixed workflow plus two extension points — one value, one hook:

```python
class View:
     """A simple view that returns plain text responses"""

     content_type = "text/plain"

     def render_body(self) -> str:
          """Render the message body of the response"""
          return "Welcome to my web site"

     def get(self, request) -> Response:
          """Handle a GET request and return a message in the response"""
          return Response(
               status=200,
               content_type=self.content_type,
               body=self.render_body()
          )


class TemplateView(View):
     """A view that returns HTML responses based on a template file."""

     content_type = "text/html"
     template_file = "index.html"

     def render_body(self) -> str:
          """Render the message body as HTML"""
          with open(self.template_file) as fd:
               return fd.read()
```

The guide is careful about what just happened: *"Note that we did need to override the `render_body()` in order to change the source of the body, but this method has a single, well defined responsibility that invites subtypes to override it."* Overriding is not the sin — overriding a method that wasn't designed for it is. Now a permission check added to `get()` applies to every subtype automatically.

**Also good — mixins.** When the behaviour should be reusable across unrelated views, package each concern separately. `ContentLengthMixin` shows cooperative `super()`, wrapping rather than replacing:

```python
class TemplateRenderMixin:
     """A mixin class for views that render HTML documents using a template file

     Not to be used by itself!
     """
     template_file: str = ""

     def render_body(self) -> str:
          if not self.template_file:
               raise ValueError("The path to a template file must be given.")
          with open(self.template_file) as fd:
               return fd.read()


class ContentLengthMixin:
     """A mixin class for views that injects a Content-Length header in the
     response

     Not to be used by itself!
     """

     def get(self, request) -> Response:
          """Introspect and amend the response to inject the new header"""
          response = super().get(request)  # type: ignore
          response.headers['Content-Length'] = len(response.body)
          return response


class TemplateView(TemplateRenderMixin, ContentLengthMixin, View):
     """A view that returns HTML responses based on a template file."""

     content_type = "text/html"
     template_file = "index.html"
```

Mixins "make object composition easier by packaging together related functionality into a highly reusable class with a single responsibility, allowing clean decoupling." **Django makes heavy use of mixins to compose its class-based views** — the guide cites it as the reference implementation.

## Anti-patterns
- **Overriding the orchestrating method** (`get()`): freezes the parent and makes every future base change a multi-class edit.
- **No extension points at all**: forces subtypes into exactly the above.
- **Adding a variant by editing an existing conditional**: the modification OCP forbids; move the behaviour onto the variant.
- **Instantiating a mixin directly**: they are incomplete — "Not to be used by itself!"
- **Placing a mixin after the target class**: MRO finds the target's method first and the mixin never runs.
- **A mixin inheriting from something other than `object`**: drags a hierarchy into every class that composes it.
- **A hook with more than one responsibility**: subtypes must re-implement parts they didn't want to change, reproducing the original problem one level down.

## Key Takeaways
1. **Extend, never modify.** Adding a variant must not require editing existing code.
2. **Design hooks deliberately.** Overriding is fine when the method exists to be overridden; extract the varying step into a single-responsibility method.
3. **Values vary via class attributes** (`content_type`), behaviour via hook methods (`render_body`).
4. **Never override the workflow method.** That's the tell that the base has no real extension points.
5. **One rogue override taxes the whole hierarchy** — you can no longer change the base safely.
6. **Mixins compose reusable behaviour**: inherit `object`, place before the target, never instantiate alone.
7. **Use cooperative `super()`** in mixins to wrap a result rather than replace the method.
8. **Django's class-based views are the worked reference** for mixin composition at scale.

## Connects To
- **Ch 4 (SRP)**: a good hook is a single-responsibility method — SRP is what makes OCP achievable.
- **Ch 6 (LSP)**: the very next section reuses this `View`/`TemplateView` pair to show the *other* way a subtype breaks its parent — by changing a method signature.
- **Ch 7 (ISP)**: mixins and segregated ABCs are two routes to the same goal — small, composable units.
- **Ch 9 (DRY)**: mixins remove duplication across classes without a shared concrete base.
- **Template Method pattern**: `get()` + `render_body()` is exactly it — fixed algorithm, overridable step.
- **Django CBVs / `typing.Protocol`**: the framework precedent, and the guide's open `FIXME` on typing mixins.
