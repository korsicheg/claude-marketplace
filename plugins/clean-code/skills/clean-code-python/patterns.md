# Patterns & Techniques — clean-code-python

Concrete refactorings from the guide, each with its trigger and cost.

## Annotate the Type, Drop the Type-Prefix
**When to use**: a name encodes its own type (`ymdstr`, `str_name`, `list_items`).
**How**: delete the type from the name; add a hint — `current_date: str`.
**Trade-offs**: none in Python 3.7+; the annotation is checkable, the prefix isn't. (Ch 2)

## Hoist a Literal to a Module Constant
**When to use**: any literal whose meaning isn't evident at the call site.
**How**: `time.sleep(86400)` → `SECONDS_IN_A_DAY = 60 * 60 * 24` at module level. **Keep the arithmetic** — the derivation documents the value.
**Trade-offs**: none. Also makes the value greppable. (Ch 2)

## Name Regex Sub-Patterns
**When to use**: regex results read by index.
**How**: `(?P<city>.+?)` then `matches['city']`. Middle tier (`city, zip_code = matches.groups()`) is better than indices but still positionally coupled.
**Trade-offs**: slightly longer pattern; removes a whole class of silent shift bugs when a group is added. (Ch 2)

## Promote a Function Cluster to a Class
**When to use**: several functions share an entity noun (`get_user_info`, `get_user_data`, `get_user_record`).
**How**: one class exposing an instance attribute, a `@property`, and a method.
**Trade-offs**: more structure; the shared noun becomes a checked type instead of a convention. (Ch 2)

## Default Argument Instead of Short-Circuiting
**When to use**: `name = "X" if name is None else name` at the top of a function.
**How**: `def create_micro_brewery(name: str = "Hipster Brew Co.")`.
**Trade-offs**: none; also documents the expected type. Beware mutable defaults — use `field(default_factory=...)` in dataclasses. (Ch 2)

## Extract the Filter (then make it a Generator)
**When to use**: a loop that both selects and acts (`if client.active: email(client)`).
**How**: three tiers — (1) fuse; (2) extract `get_active_clients()` returning a list; (3) make it `active_clients()` returning a generator, relaxing the parameter from `List` to `Iterator`.
**Trade-offs**: tier 3 is lazy and allocation-free, but the result is single-pass and has no `len()`. (Ch 3)

## Bundle Parameters into a Typed Object
**When to use**: a signature reaching three parameters.
**How**: pick by need — `NamedTuple` (immutable, unpackable), `@dataclass` (mutable, `astuple()`), `TypedDict` (3.8+, dict access, **all keys required**). Never a bare `dict`.
**Trade-offs**: one more type to name; unlocks moving computation onto the object, which is the real prize. (Ch 3)

## Split a Flag Parameter into Two Functions
**When to use**: any boolean parameter selecting a code path.
**How**: `create_file(name, temp)` → `create_file(name)` + `create_temp_file(name)`.
**Trade-offs**: two names to maintain; each does one thing and reads correctly at the call site. (Ch 3)

## Extract Abstraction Levels
**When to use**: a function mixing orchestration with mechanics.
**How**: extract each level — `parse_better_js_alternative()` becomes `tokenize()` + `parse()` + a walk; the parent reads as a list of intentions.
**Trade-offs**: more functions, each reusable and independently testable. (Ch 3)

## Purify a Side-Effecting Function
**When to use**: a `() -> None` function that changes program state, especially via `global`.
**How**: take a value, return a value — `split_into_first_and_last_name(name: AnyStr) -> List[AnyStr]`.
**Trade-offs**: caller now holds the result. Annotate module state so `mypy` catches the type damage. (Ch 3)

## Own State in a Class with a Property
**When to use**: state genuinely must persist, and a derived view of it is needed.
**How**: `@dataclass class Person` with `@property name_as_first_and_last` — computed on demand, original never overwritten. "The reason why we create instances of classes is to manage state!"
**Trade-offs**: recomputed per access; safe under repeat calls. (Ch 3)

## Centralize a Side Effect in One Service
**When to use**: several functions or classes write to the same file/resource.
**How**: "have one (and only one) service that does it", and indicate where effects occur.
**Trade-offs**: one more indirection; one place to audit, mock, and change. (Ch 3)

## Extract a Responsibility and Inject the Result
**When to use**: a class both acquires and presents data.
**How**: move acquisition to a function; accept its output via `__init__` — `VersionCommentElement(get_version("pip"))`. Keep the seam a primitive.
**Trade-offs**: caller wires two pieces; each is independently testable and the extracted function is reusable. (Ch 4)

## Replace an Override with a Hook Method
**When to use**: a subclass overrides the orchestrating method.
**How**: extract the varying step into a single-responsibility method (`render_body()`); promote varying values to class attributes (`content_type`). The workflow method never changes again.
**Trade-offs**: base class needs foresight about its extension points; without it every base change is a multi-class edit. (Ch 5)

## Compose Behaviour with Mixins
**When to use**: reusable cross-cutting behaviour several unrelated classes need.
**How**: one mixin per concern; **inherit `object`**; **place before the target** (`class Foo(MixinA, MixinB, Target)`); use cooperative `super()` to wrap. Never instantiate alone.
**Trade-offs**: behaviour depends on MRO order, and typing mixins is unresolved — the guide carries a `FIXME` about `typing.Protocol`. Django's class-based views are the reference implementation. (Ch 5)

## Move Extra Information from Signature to State
**When to use**: an override wants data the base method doesn't receive.
**How**: make it a class attribute (`template_file = "index.html"`), not a parameter. Signature stays identical.
**Trade-offs**: none — this single move satisfies LSP and OCP at once. (Ch 5, Ch 6)

## Gate Substitutability with mypy
**When to use**: any inheritance hierarchy with overrides.
**How**: run `mypy` in CI. Signature breaks surface as `Signature of "get" incompatible with supertype "View"`. Never silence with `# type: ignore`.
**Trade-offs**: catches signature breaks only; invariants and history properties still need review. (Ch 6)

## Segregate a Fat ABC into Capability ABCs
**When to use**: `Can't instantiate abstract class X with abstract method y` — an implementer is forced to supply what it doesn't need.
**How**: shared state in a carrier (`DataCarrier`); one ABC per capability (`Loadable`, `Saveable`); implementers inherit only what they use; consumers annotate the narrowest sufficient ABC.
**Trade-offs**: more type names; adding a capability later becomes additive rather than breaking. (Ch 7)

## Accept an ABC Instead of a Concrete Class
**When to use**: a function shouldn't care which class it gets, only that it has certain members.
**How**: define a minimal ABC (`Greeter.greet`) and annotate the parameter against it.
**Trade-offs**: implementers must inherit it; use `typing.Protocol` for structural typing instead. (Ch 7)

## Implement Only the Method the Dependency Requires
**When to use**: you're manipulating a library's internals (buffers, cursors) to extract a result.
**How**: find the minimal contract — `csv.writer` "just needs an object with a `.write()` method" — and supply a two-line class. `Echo.write()` *returns* the value instead of storing it, converting buffering into streaming.
**Trade-offs**: an undeclared duck-typed seam can drift on a library upgrade; add a `Protocol` if it's load-bearing. Deletes a page of code and runs faster. (Ch 8)

## Generalize Near-Miss Duplicates
**When to use**: two types or functions differing only in names, where the distinction is invisible to the code.
**How**: collapse to one (`Developer` + `Manager` → `Employee`); keep the domain distinction in the call-site variable names (`company_developers`).
**Trade-offs**: **check first** whether they'll diverge. If the merge would need a flag or a role branch, abandon it — "bad abstractions can be worse than duplicate code." (Ch 9)
