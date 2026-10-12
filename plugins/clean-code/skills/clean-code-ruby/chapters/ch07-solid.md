# Chapter 7: SOLID

## Core Idea
The five SOLID principles, worked in Ruby. The decisive fact is stated twice in the source: "Ruby doesn't have interfaces", so abstractions are **implicit contracts** — "the methods and properties that an object/class exposes to another object/class." SRP and OCP read as in any language; LSP is the Square/Rectangle trap through Ruby writer methods; ISP and DIP become questions about **which messages a client actually sends**.

## Frameworks Introduced
- **Single Responsibility Principle (SRP)**: "There should never be more than one reason for a class to change."
  - The image: jam-packing a class "like when you can only take one suitcase on your flight." The cost: "if too much functionality is in one class and you modify a piece of it, it can be difficult to understand how that will affect other dependent modules."
  - How: split by reason to change. `UserSettings` that also checks authentication becomes `UserAuth` (`valid_credentials?`) plus `UserSettings` (`change_settings`).
- **Open/Closed Principle (OCP)**: Bertrand Meyer's "software entities (classes, modules, functions, etc.) should be open for extension, but closed for modification" — "allow users to add new functionalities without changing existing code."
  - Tell: "adding another adapter would require changing `HttpRequester` class."
  - How: give every adapter the same message (`request(url)`) and have the consumer send it — `@adapter.request(url)` — instead of a `case @adapter.name`.
- **Liskov Substitution Principle (LSP)**: "If S is a subtype of T, then objects of type T may be replaced with objects of type S … without altering any of the desirable properties of that program." The guide's plain version: "if you have a parent class and a child class, then the base class can always be replaced by the child class without getting incorrect results."
  - How: when a subclass must override writers to keep its own invariant (a square's sides equal), it isn't a subtype. Make both siblings of a shared parent (`Shape`) that promises only what both can keep (`area`, `render`, `color=`).
- **Interface Segregation Principle (ISP)**: "Clients should not be forced to depend upon interfaces that they do not use." Ruby "doesn't have interfaces so this principle doesn't apply as strictly as others. However, it's important and relevant even with Ruby's lack of type system." "Interfaces are implicit contracts in Ruby because of duck typing."
  - Why: a client depending on a class whose other methods serve other clients "will be affected by the changes that those other clients force upon the class."
  - How: split the class along its clients — `Car` (`open`, `start_engine`) for `Driver`, `CarInternals` (`change_engine`) for `Mechanic`. (The guide credits this example to a 2015 geekhmer blog post.)
- **Dependency Inversion Principle (DIP)**: "1. High-level modules should not depend on low-level modules. Both should depend on abstractions. 2. Abstractions should not depend upon details. Details should depend on abstractions."
  - How: dependency injection — "constructing our dependencies externally and injecting them". `InventoryTracker.new(items, requester)` instead of `@requester = InventoryRequester.new` inside `initialize`.
  - In Ruby the abstraction is the implicit contract: "any Request module for an `InventoryTracker` will have a `request_items` method." (The code itself calls `request_item(item)` on the requester — the contract is that singular method.)

## Key Concepts
- **Reason to change** — an external force that would compel an edit; SRP's unit.
- **Open for extension / closed for modification** — a new variant adds code without editing the consumer.
- **Adapter** — a class wrapping one transport behind a shared message (`request(url)`).
- **Substitutability** — a subclass usable wherever the parent is expected, without wrong results.
- **Implicit contract** — the set of messages one object relies on another answering; Ruby's stand-in for an interface.
- **Duck typing** — satisfying a contract by answering its messages, with no declared relationship.
- **Dependency injection** — passing a collaborator into `initialize` rather than constructing it there.
- **Coupling** — "a very bad development pattern because it makes your code hard to refactor."

## Mental Models
- **Write the contract down as a list of messages.** For DIP it is `request_item`; for OCP it is `request`; for ISP, each client's list is different — and that difference is the split.
- **A writer is a promise.** `Rectangle#width=` promises that width changes and height doesn't. `Square` can't keep that promise, so it can't be a `Rectangle`.
- **`.new` inside `initialize` is a hard-coded dependency.** Whatever you construct there, you can't substitute in a test or swap for V2.

## Anti-patterns
- **A class with two reasons to change** (`UserSettings` that also authenticates).
- **`case` on a collaborator's name** (`case @adapter.name when 'ajaxAdapter'`): every new adapter edits the consumer.
- **Subclass overriding writers to preserve its own invariant** (`Square#width=` also setting height).
- **One class serving unrelated clients** (`Car#change_engine` beside `Car#open`).
- **Constructing collaborators internally** (`@requester = InventoryRequester.new`) — "BAD: We have created a dependency on a specific request implementation."
- **Note on the source's own SRP fix**: its good `UserSettings` still constructs `@auth = UserAuth.new(user)` inside `initialize` — the very pattern the DIP section calls bad. Inject it when you need to substitute it.

## Code Examples
OCP — one message, any number of adapters:

```ruby
class AjaxAdapter
  def request(url)
    # ...
  end
end

class NodeAdapter
  def request(url)
    # ...
  end
end

class HttpRequester
  def initialize(adapter)
    @adapter = adapter
  end

  def fetch(url)
    @adapter.request(url)
  end
end
```
- **What it demonstrates**: `HttpRequester` never asks which adapter it holds; a third adapter is a new class with a `request` method and zero edits here. (The bad version gave each adapter an `attr_reader :name` and switched on it.)

DIP — inject the requester:

```ruby
class InventoryTracker
  def initialize(items, requester)
    @items = items
    @requester = requester
  end

  def request_items
    @items.each do |item|
      @requester.request_item(item)
    end
  end
end

# By constructing our dependencies externally and injecting them, we can easily
# substitute our request module for a fancy new one that uses WebSockets.
inventory_tracker = InventoryTracker.new(['apples', 'bananas'], InventoryRequesterV2.new)
inventory_tracker.request_items
```
- **What it demonstrates**: `InventoryRequesterV1` (HTTP) and `InventoryRequesterV2` (WebSockets) share no parent class — they only both answer `request_item`. That's the whole abstraction.

ISP — split by client:

```ruby
# used by Driver only
class Car
  def open
    # ...
  end

  def start_engine
    # ...
  end
end

# used by Mechanic only
class CarInternals
  def change_engine
    # ...
  end
end
```

## Reference Tables

| Principle | Ruby tell | Ruby fix |
|---|---|---|
| SRP | class name needs "and"; unrelated methods share a class | extract a class per reason (`UserAuth`) |
| OCP | `case collaborator.name` in the consumer | shared message on each variant (`request`) |
| LSP | subclass overrides writers to keep its own invariant | sibling classes under a parent promising only common behaviour (`Shape#area`) |
| ISP | methods grouped by comments "used by X" | one class per client's message set (`Car` / `CarInternals`) |
| DIP | `SomeClass.new` inside `initialize` | inject through `initialize` (`InventoryTracker.new(items, requester)`) |

## Worked Example
**LSP — the Square/Rectangle trap, through Ruby writers.**

Mathematically a square is a rectangle; modelled with inheritance, it isn't:

```ruby
class Rectangle
  def initialize
    @width = 0
    @height = 0
  end

  def color=(color)
    # ...
  end

  def render(area)
    # ...
  end

  def width=(width)
    @width = width
  end

  def height=(height)
    @height = height
  end

  def area
    @width * @height
  end
end

class Square < Rectangle
  def width=(width)
    @width = width
    @height = width
  end

  def height=(height)
    @width = height
    @height = height
  end
end

def render_large_rectangles(rectangles)
  rectangles.each do |rectangle|
    rectangle.width = 4
    rectangle.height = 5
    area = rectangle.area # BAD: Returns 25 for Square. Should be 20.
    rectangle.render(area)
  end
end

rectangles = [Rectangle.new, Rectangle.new, Square.new]
render_large_rectangles(rectangles)
```

`render_large_rectangles` is correct for every `Rectangle`. Handed a `Square`, the second writer silently rewrites the first and the area comes out 25. Nothing raises; the program just computes the wrong answer — precisely the "incorrect results" the definition forbids.

The guide's fix drops the writers and the false "is-a":

```ruby
class Shape
  def color=(color)
    # ...
  end

  def render(area)
    # ...
  end
end

class Rectangle < Shape
  def initialize(width, height)
    @width = width
    @height = height
  end

  def area
    @width * @height
  end
end

class Square < Shape
  def initialize(length)
    @length = length
  end

  def area
    @length * @length
  end
end

def render_large_shapes(shapes)
  shapes.each do |shape|
    area = shape.area
    shape.render(area)
  end
end

shapes = [Rectangle.new(4, 5), Rectangle.new(4, 5), Square.new(5)]
render_large_shapes(shapes)
```

Dimensions are fixed at construction, and `Shape` promises only what both can keep: a color, an `area`, a `render`. The consumer now sends only those messages. **The transferable rule**: if a subclass must override a writer to protect its own invariant, it isn't a subtype — make it a sibling, and move the shared messages up.

## Key Takeaways
1. **SRP**: one reason to change per class; split authentication from settings.
2. **OCP**: give every variant the same message; the consumer never asks which variant it holds.
3. **LSP**: substitutability is about results, not just method names — `Square < Rectangle` returns 25 where 20 was promised.
4. **ISP**: in Ruby, an interface is the set of messages a client sends; split classes along those sets.
5. **DIP**: inject collaborators through `initialize`; the abstraction is an implicit contract (`request_item`).
6. **No interfaces means the contracts are conventions** — tests (Ch 8) are what hold them.

## Connects To
- **Ch 3**: SRP is "do one thing" at class scale.
- **Ch 4**: OCP's adapter fix is the `is_a?`/`case` removal applied to a collaborator.
- **Ch 5**: LSP breaks through public writers — a reason to question every `attr_accessor`.
- **Ch 6**: when LSP fails, composition is the fallback.
- **Ch 8**: dependency injection is what makes collaborators replaceable with test doubles.
- **clean-code-python**: the same principles with ABCs and `mypy` as the referee; Ruby has neither, by design.
