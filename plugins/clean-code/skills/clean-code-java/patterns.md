# Clean Code — Techniques & Patterns

## Extract Method Until You Can't
**When to use**: any function longer than a few lines, or with any section comment.
**How**: extract until you cannot pull out a function whose name is more than a restatement of its body. Blocks inside `if`/`while` become one line — a call. Keep indent depth ≤ 2.
**Trade-offs**: more functions and more total lines; you buy readability and named intent. (Ch3, Ch17 G30)

## The TO-Paragraph Test
**When to use**: to check whether a function does "one thing."
**How**: write "TO \<function name\>, we \<step\>, then \<step\>." If the paragraph doesn't read naturally, the statements aren't one level below the name.
**Trade-offs**: none; it's a reading exercise. (Ch3)

## Replace Switch with Polymorphism (ONE SWITCH rule)
**When to use**: a `switch`/`if-else` chain on a type, especially if the same shape appears elsewhere.
**How**: move the switch into an Abstract Factory that creates derivatives; dispatch behavior through the base interface.
**Trade-offs**: adding a *function* now touches every class. Correct when new **types** are more likely than new **functions**. At most one switch per selection type. (Ch3, Ch6, Ch17 G23)

## Argument Reduction
**When to use**: any function with 2+ arguments.
**How**, in order: make the method a member of one argument (`outputStream.writeField(name)`); make the argument a field; extract a class taking it in the constructor; wrap co-travelling arguments in an argument object (`makeCircle(Point, double)`).
**Trade-offs**: more small classes; testing gets dramatically easier. (Ch3)

## Split on the Flag
**When to use**: any boolean or selector parameter.
**How**: `render(true)` / `render(false)` → `renderForSuite()` / `renderForSingleTest()`.
**Trade-offs**: more entry points, but each does one thing and reads at the call site. (Ch3, Ch17 F3/G15)

## Extract Try/Catch
**When to use**: any function containing a `try`.
**How**: the error-handling function contains only the try/catch; the body becomes its own function. `try` must be the first word in the function and nothing follows `catch`/`finally`.
**Trade-offs**: one extra function per handled scope. (Ch3, Ch7)

## Write the Try-Catch-Finally First
**When to use**: writing code that can throw.
**How**: start with a test that *expects* the exception → stub → implement enough to throw → narrow the caught type to what's actually thrown → then build the real logic inside the try, pretending nothing goes wrong.
**Trade-offs**: none; it fixes the transaction scope before the logic hides it. (Ch7)

## Wrap the Third-Party API
**When to use**: any external library, and any API returning null or throwing many exception types.
**How**: a thin class that translates their exceptions to one of yours and exposes only what you need. Never return or accept the boundary type in your public API.
**Trade-offs**: one indirection layer; you gain swappability, mockability, and freedom from their design choices. (Ch7, Ch8)

## Special Case Object (Null Object)
**When to use**: a "missing" case that has a defined business answer; anywhere you'd return null.
**How**: return an object that answers the default (`PerDiemMealExpenses.getTotal()`), or `Collections.emptyList()` for collections.
**Trade-offs**: one small class; deletes a catch block or a null check from every caller. (Ch7)

## Learning Tests
**When to use**: adopting an unfamiliar library.
**How**: call the API exactly as you intend to use it, in tests, until it behaves; keep them and re-run on every upgrade.
**Trade-offs**: free — you had to learn it anyway — and they detect breaking changes at upgrade time. (Ch8)

## Write the Interface You Wish You Had
**When to use**: the collaborator doesn't exist, isn't finished, or is out of your control.
**How**: define your own interface in domain terms, build against it with a fake, add an Adapter when the real API lands.
**Trade-offs**: an Adapter to maintain; you get an unblocked team and a test seam. (Ch8)

## Domain-Specific Testing Language
**When to use**: tests cluttered with setup detail.
**How**: refactor tests into `makePages(...)`, `submitRequest(...)`, `assertResponseIsXML()`. **Not designed up front** — it evolves from cleaning tests.
**Trade-offs**: test-support code to maintain, held to cleanliness (not efficiency) standards. (Ch9)

## Dependency Injection for Testability
**When to use**: a class depends on something slow, remote, or nondeterministic.
**How**: extract an interface (`StockExchange`), inject it via constructor, pass a stub in tests.
**Trade-offs**: an interface and a wiring point; you get tests and DIP compliance at once. (Ch10, Ch11)

## Separate Construction from Use
**When to use**: anywhere `new` or lazy init appears in runtime logic.
**How**: move all construction to `main` or a DI container; use an Abstract Factory when the app must control *when* creation happens. Dependency arrows all point away from `main`.
**Trade-offs**: a startup module; you get testability, one global wiring strategy, and no hidden hard dependencies. (Ch11)

## Template Method
**When to use**: two or more methods share an algorithm but differ in one step.
**How**: the base class holds the algorithm and declares the varying step abstract; subclasses fill the hole.
**Trade-offs**: inheritance coupling; use Strategy when composition fits better. (Ch12, Ch17 G5)

## Encapsulate the Conditional / the Boundary
**When to use**: compound boolean expressions, negatives, and repeated `±1` arithmetic.
**How**: `if (shouldBeDeleted(timer))` not `if (timer.hasExpired() && !timer.isRecurrent())`; `int nextLevel = level + 1;` used twice rather than `level + 1` twice.
**Trade-offs**: one named function or variable, always worth it. (Ch17 G28, G29, G33)

## Bucket Brigade (expose temporal coupling)
**When to use**: functions that must be called in a particular order.
**How**: make each produce what the next consumes — `diveForMoog(reticulateSplines(saturateGradient()), reason)`.
**Trade-offs**: more syntactic complexity, which is the point: *"that extra syntactic complexity exposes the true temporal complexity."* (Ch17 G31)

## Physicalize the Logical Dependency
**When to use**: a module assumes a fact about a collaborator (e.g. `PAGE_SIZE = 55`).
**How**: ask the collaborator — add `getMaxPageSize()` and call it.
**Trade-offs**: one extra method; removes a silent assumption that can break. (Ch17 G22)

## Refactor Under Green Tests, in Tiny Steps
**When to use**: any structural improvement.
**How**: build the test suite first (unit + acceptance); add the new abstraction as a harmless skeleton; migrate one use at a time; fix any test break before proceeding; expect to reverse earlier steps.
**Trade-offs**: slower than a rewrite, and the only approach that reliably lands. (Ch14, Ch15, Ch16)

## Coverage-Driven Bug Hunting
**When to use**: inheriting unfamiliar code, or a passing suite you don't trust.
**How**: run a coverage tool; never-executed lines expose impossible conditions; the *pattern* of failing tests exposes boundary errors; a function with repeated past "bug fixes" needs a new algorithm.
**Trade-offs**: none. Note coverage % can legitimately *drop* as a class shrinks. (Ch16, Ch17 T2/T6/T7/T8)

## Isolate Thread Management
**When to use**: any concurrent code.
**How**: one `Scheduler`-style class owns all threading; everything else is thread-ignorant POJOs. Swapping to an `Executor` pool then costs one new class.
**Trade-offs**: an interface; you gain one place to look for concurrency bugs and testable domain logic. (Ch13, App A)

## Jiggle to Force Concurrency Failures
**When to use**: testing threaded code.
**How**: a `ThreadJigglePoint.jiggle()` that is a no-op in production and randomly sleeps/yields/falls through in test; or IBM ConTest.
**Trade-offs**: call sites to place; measured effect was 1-in-10,000,000 failures → 1-in-30. (Ch13, App A)

## Prefer Atomics to `synchronized`
**When to use**: simple shared counters and flags.
**How**: `AtomicInteger.incrementAndGet()` instead of `synchronized { ++value; }`.
**Trade-offs**: CAS is optimistic locking and *"nearly always"* wins; cases where it's slower are *"virtually nonexistent."* (App A)

## Break One Deadlock Condition Deliberately
**When to use**: any system with multiple limited resource pools.
**How**: usually **circular wait** — agree a global resource ordering and always acquire in it.
**Trade-offs**: resources locked longer than necessary, and ordering is infeasible when resource #2's identity comes from resource #1. Other options (breaking mutual exclusion, lock & wait, or preemption) trade starvation or CPU. (App A)
