# Chapter 3: Methods

## Core Idea
**Methods should do one thing** — "by far the most important rule in software engineering." The rest of this chapter (argument count, flags, abstraction levels, side effects) is a set of detectors for breaking it. Ruby's contribution is in the mechanics: **keyword arguments** for signatures, **blocks over `Enumerable`** for the functional style, and an explicit account of how Ruby passes **references by value**.

## Frameworks Introduced
- **Method arguments (2 or fewer ideally)**: "Limiting the amount of method parameters is incredibly important because it makes testing your method easier." More than three "leads to a combinatorial explosion where you have to test tons of different cases with each separate argument."
  - When to use: any signature reaching three parameters; "Anything more than that should be consolidated."
  - How, in the guide's order: "Usually, if you have more than two arguments then your method is trying to do too much." If not, "a higher-level object will suffice", or "you can pass data to the method by instance variables." Ruby lets you "make objects on the fly", and "The prevailing pattern in Ruby is to use a hash of arguments."
  - **The Ruby move — keyword arguments** ("introduced in Ruby 2.1"): `def create_menu(title:, body:)`. Two stated advantages: the signature shows at once which properties are used, and a missing required keyword raises "a useful `ArgumentError` that tells us which required argument we must include."
- **Methods should do one thing**: "If you take nothing else away from this guide other than this, you'll be ahead of many developers."
  - When to use: every method, always.
  - How: if you can only describe it with "and", split it. `email_clients` that looks up *and* filters *and* emails becomes `email_clients` + `active` + `active?`.
- **Method names should say what they do**: poor names "add to the code reviewer's cognitive load at best, and mislead the code reviewer at worst."
  - How: `add_to_date(date, 1)` → `add_month_to_date(date, 1)`. Capture the precise intent — what is being added.
- **Methods should only be one level of abstraction**: "When you have more than one level of abstraction your method is usually doing too much."
  - How: extract each level; "methods should descend by the level of abstraction: one very abstract method should call methods that are less abstract and so on." `interpret` becomes `tokenize` → `lex` → `parse`.
- **Don't use flags as method parameters**: "Flags tell your user that this method does more than one thing."
  - How: `create_file(name, temp)` → `create_file(name)` + `create_temp_file(name)`, the second calling the first.
- **Avoid Side Effects (part 1)**: a method has side effects "if it does anything more than take values and/or return values" — writing a file, "modifying some global variable, or accidentally wiring all your money to a stranger."
  - How: return values instead of mutating `$globals`. When an effect is genuinely needed, centralize it: "Have one service that does it. One and only one."
- **Avoid Side Effects (part 2)**: "In Ruby, everything is an object and everything is passed by value, but these values are references to objects."
  - How: return a new collection — `cart + [item]` — rather than `cart.push(item)`. The guide's two caveats: sometimes you really do want to modify the input ("those cases are pretty rare"), and cloning big objects is expensive — persistent-collection gems such as Hamster address that.
- **Favor functional programming over imperative programming**: "Ruby isn't a functional language in the way that Haskell is, but it has a functional flavor to it."
  - How: replace accumulator loops with `Enumerable` methods and blocks — `sum`, `select`, `map`, `each_with_object`.

## Key Concepts
- **Combinatorial explosion** — the test-case count multiplying with each argument; the stated reason for the argument limit.
- **Keyword arguments** — `title:, body:`; named at the call site, and missing required ones raise `ArgumentError` naming the keyword.
- **Hash of arguments** — the pre-2.1 "prevailing pattern"; bundles parameters but declares nothing in the signature.
- **Predicate method** — a method ending in `?` returning a boolean (`active?`); Ruby's naming convention for questions.
- **Level of abstraction** — the altitude of a statement: orchestration (`tokenize(code)`) vs mechanics (`code.split(' ')`).
- **Flag parameter** — a boolean argument that selects a code path.
- **Side effect** — anything beyond taking values in and returning values out.
- **Global variable (`$name`)** — process-wide mutable state; the guide's side-effect example.
- **Reference passed by value** — the method gets a copy of the reference, so mutating the object (`push`) is visible to every holder, while reassigning the parameter is not.
- **Hamster** — a gem of persistent (immutable, structurally shared) collections, cited to make copying cheap.

## Mental Models
- **Ask "who else holds this reference?"** before calling a mutating method (`push`, `<<`, `merge!`, assigning a hash key) on anything you were *given*.
- **Think of the parent method as a table of contents.** `interpret` reads `tokenize`, `lex`, `parse` — three intentions — and the mechanics live one level down.
- **Treat a boolean parameter as two method names that got merged.** Split it and the call sites start reading correctly.
- **Use blocks to say *what*, not *how*.** `sum { |output| output[:lines_of_code] }` states the result; a running total states the procedure.

## Anti-patterns
- **Long positional signatures** (`create_menu(title, body, button_text, cancellable)`): a combinatorial test surface and unreadable call sites.
- **Filtering and acting in one loop** (`email(client) if client_record.active?` inside `each`): two responsibilities, neither testable alone.
- **Vague verbs** (`add_to_date`): the reader can't tell *what* is added.
- **Mixing altitudes** (regexes, splitting, tokenizing and AST walking in one `interpret`).
- **Boolean flags** (`create_file(name, true)`).
- **Mutating a `$global`**: the guide's comment says it plainly — "If we had another method that used this name, now it'd be an array and it could break it."
- **Mutating an argument** (`cart.push(...)`): every other holder of `cart` sees the change.
- **Several methods and classes writing the same file**: centralize in one service.
- **Accumulator loops** (`total_output += ...` inside `each`).

## Code Examples
Keyword arguments — the signature becomes the documentation:

```ruby
# Bad
def create_menu(title, body)
  # ...
end

create_menu('Foo', 'Bar')

# Good
def create_menu(title:, body:)
  # ...
end

create_menu(title: 'Foo', body: 'Bar')
```
- **What it demonstrates**: call sites name every value, argument order stops mattering, and omitting `body:` raises `ArgumentError` naming `body` rather than failing somewhere downstream.

Do one thing — the filter becomes a predicate method and a selector:

```ruby
# Good
def email_clients(clients)
  clients.each { |client| email(client) }
end

def active(objects)
  objects.select { |object| active?(object) }
end

def active?(object)
  record = database.lookup(object)
  record.active?
end

email_clients(active(clients))
```
- **What it demonstrates**: `email_clients` no longer knows what "active" means; `active?` is reusable and testable alone; the call site composes them.

Functional over imperative — the guide's version:

```ruby
# Bad
total_output = 0

programmer_output.each do |output|
  total_output += output[:lines_of_code]
end

# Good
INITIAL_VALUE = 0

total_output = programmer_output.sum(INITIAL_VALUE) { |output| output[:lines_of_code] }
```
- **What it demonstrates**: `Enumerable#sum` with a block replaces the mutable accumulator. (The `INITIAL_VALUE` constant is a ported habit — `sum` already starts at `0` — and an instance of the README's own "may not be idiomatic" warning.)

## Reference Tables

The argument ladder, as the guide lays it out:

| Option | Example | Notes |
|---|---|---|
| Positional, 3+ | `create_menu(title, body, button_text, cancellable)` | Avoid; consolidate |
| Split the method | — | "Usually … your method is trying to do too much" |
| Higher-level object | `create_menu(menu)` | "most of the time a higher-level object will suffice" |
| Instance variables | `@title`, `@body` read inside the method | Offered without an example; couples the method to object state |
| Hash of arguments | `create_menu(options)` | "The prevailing pattern in Ruby" — keys undeclared |
| **Keyword arguments** | `create_menu(title:, body:)` | Ruby 2.1+; self-documenting; `ArgumentError` on a missing keyword |

| Detector | Signal | Fix |
|---|---|---|
| Argument count | ≥3 params | Keyword arguments or a higher-level object |
| Flag | boolean selects a path | Two named methods |
| Vague verb | `add_to_date` | Name the action: `add_month_to_date` |
| Mixed altitude | orchestration + mechanics | Extract each level |
| `$global` | mutation of shared state | Return a value |
| `push` on a parameter | caller's object changes | Return a new collection |
| Accumulator loop | `+=` inside `each` | `sum`, `map`, `select`, `each_with_object` |

## Worked Example
**Side effects, part 2 — the shopping-cart retry bug.**

The scenario, in the guide's words: the user clicks "Purchase", which calls a `purchase` method that sends the `cart` array to the server. A bad connection makes `purchase` retry. Meanwhile, the user accidentally clicks "Add to Cart" on an item they don't want. Because `purchase` "has a reference to a shopping cart array that the `add_item_to_cart` method modified", the retry sends the unwanted item.

The mutating version:

```ruby
def add_item_to_cart(cart, item)
  cart.push(item: item, time: Time.now)
end
```

`push` changes the very array `purchase` is holding. Ruby passed `add_item_to_cart` a *copy of the reference*, not a copy of the array — so there is still only one cart.

The non-mutating version:

```ruby
def add_item_to_cart(cart, item)
  cart + [{ item: item, time: Time.now }]
end
```

`Array#+` builds a new array. The retrying `purchase` keeps its snapshot; the caller decides whether to adopt the new cart. The guide's caveats complete the picture: genuine in-place updates are "pretty rare", and when copying gets expensive, persistent collections (Hamster) keep it cheap.

**The transferable rule**: a method that receives a collection and calls `push`, `<<`, `concat`, `merge!` or `[]=` on it is writing to its caller's state. Return a new value unless mutation is the method's stated purpose — and then say so in its name.

## Key Takeaways
1. **Methods do one thing.** If the description needs "and", split it.
2. **Two arguments or fewer.** At three, reach for **keyword arguments** (or a higher-level object); they document the signature and fail loudly when a keyword is missing.
3. **Name the action precisely** — `add_month_to_date`.
4. **One level of abstraction per method**, descending from abstract to concrete.
5. **No flag parameters** — two branches, two method names.
6. **Pure by default; one service per unavoidable effect.** Never mutate `$globals`.
7. **Don't mutate what you were given** — Ruby passes references by value; return `cart + [item]`.
8. **Prefer `Enumerable` with blocks** over accumulator loops.

## Connects To
- **Ch 2**: default arguments and keyword arguments are the same idea — let the signature carry the contract.
- **Ch 4**: the rest of the Methods section — duplication, conditionals, type-checking, dead code.
- **Ch 5**: accessor methods are where deliberate state lives once side effects are centralized.
- **Ch 7 (SRP)**: "one reason to change" is the class-level form of "do one thing".
- **Ch 8**: the argument limit's stated payoff is easier testing.
- **clean-code-python**: the parameter-object ladder (`NamedTuple`, `@dataclass`, `TypedDict`) is Python's answer to the same rule Ruby answers with keyword arguments.
