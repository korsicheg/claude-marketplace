# Chapter 2: Meaningful Names
*by Tim Ottinger*

## Core Idea
A name must answer why the thing exists, what it does, and how it is used — **if a name
needs a comment to explain it, the name has failed.** Choosing good names costs time and
saves more than it costs.

## Frameworks Introduced

- **Use Intention-Revealing Names**: the name states purpose, measurement, and unit.
  - When to use: every declaration, always.
  - How: ask the four questions the code leaves implicit (what is in this collection?
    what does this index mean? what does this magic value mean? how is the result used?)
    and push each answer into a name.
  - Failure mode it fixes: **implicity** — context that exists in the author's head but
    not in the code.

- **The Scope-Length Rule**: *the length of a name should correspond to the size of its
  scope.*
  - How: single-letter names are acceptable **only** as local variables inside short
    methods (`i`, `j`, `k` as loop counters — never `l`). Anything visible across a
    wider scope needs a searchable, descriptive name. For class/member names the rule
    inverts from the public-API rule in Ch4: **long scope → long name**.

- **Pick One Word per Concept**: one word per abstract concept, used consistently.
  - How: choose `get` *or* `fetch` *or* `retrieve` — not all three across classes. Don't
    mix `controller`, `manager`, and `driver` in one codebase for the same role.
  - Why it works: IDE completion shows you names, not your comments. Names must stand
    alone and sort together.

- **Don't Pun**: never use one word for two different semantics.
  - How: if `add` everywhere means "combine two values into a new value," then a method
    that puts one item into a collection must be `insert` or `append`, not `add` —
    even though `add` would feel "consistent."

- **Add Meaningful Context (by enclosure, not by prefix)**:
  - How, in order of preference: (1) put the names in a well-named **class**; (2) put
    them in a well-named **function** or namespace; (3) **only as a last resort**, prefix
    them (`addrState`).

## Key Concepts

- **Implicity** — the degree to which context is *not* explicit in the code itself.
- **Disinformation** — a name whose entrenched meaning differs from your intent
  (`accountList` for something that is not a `List`; `hp`, `aix`, `sco`).
- **Noise words** — `Info`, `Data`, `Object`, `Variable`, `Table`, `a`, `an`, `the`:
  they distinguish names without distinguishing meaning.
- **Number-series naming** — `a1, a2, …aN`: not disinformative, *non*informative.
- **Hungarian Notation / member prefixes (`m_`)** — type-and-scope encodings; obsolete
  crutches from weakly typed, name-length-limited languages.
- **Mental mapping** — forcing the reader to translate your name into the concept they
  already know (`r` for "lowercased url minus host and scheme").
- **Solution domain names** — CS terms, algorithm names, pattern names (`AccountVisitor`,
  `JobQueue`). Use them; your readers are programmers.
- **Problem domain names** — use when there is no "programmer-eese"; the maintainer can
  then ask a domain expert.

## Mental Models

- **Clarity is king.** The difference between a smart programmer and a *professional*
  programmer is that the professional uses their cleverness to make code others can read,
  not to demonstrate mental juggling.
- **Write for the paperback reader, not the academic.** Your code should be a quick skim,
  not an intense study. The author is responsible for being clear — not the reader for
  digging out the meaning.
- **If you can't pronounce it, you can't discuss it** — and programming is a social
  activity. `genymdhms` forces a team to invent silly spoken words for real concepts.
- **Grep-ability is a design property.** You can `grep MAX_CLASSES_PER_STUDENT`; you
  cannot usefully grep `7` or `e`. Any searchable name beats a literal constant.
- **Don't fear renaming.** Modern tooling makes it cheap; colleagues are usually grateful.
  Expect mild surprise, the same as with any other improvement, and do it anyway.

## Anti-patterns

- **Names requiring a clarifying comment** — `int d; // elapsed time in days`.
- **`l` and `O` as variable names** — visually identical to `1` and `0`. (The reported
  "fix" of mandating a different font is the anti-pattern squared: a new work product
  passed down as oral tradition, when renaming solves it with finality.)
- **Names differing in small ways** — `XYZControllerForEfficientHandlingOfStrings`
  vs `XYZControllerForEfficientStorageOfStrings`.
- **Misspelling to satisfy the compiler** — `klass` because `class` was taken; correcting
  the typo then breaks the build.
- **Indistinguishable overloads of meaning** — `getActiveAccount()`,
  `getActiveAccounts()`, `getActiveAccountInfo()`: no reader can pick correctly.
- **`IShapeFactory`** — if you must encode one side, encode the *implementation*
  (`ShapeFactoryImp`), not the interface. Users should not need to know it's an interface.
- **Cute / slang names** — `HolyHandGrenade` for `DeleteItems`, `whack()` for `kill()`,
  `eatMyShorts()` for `abort()`. Clarity over entertainment.
- **Verb-named classes / noun-named methods** — and `Manager`, `Processor`, `Data`,
  `Info` in class names.
- **Gratuitous context** — prefixing every class in "Gas Station Deluxe" with `GSD`,
  which defeats IDE completion. `GSDAccountAddress` is 10 redundant characters of 17.

## Reference Table: naming rules by construct

| Construct | Rule | Good | Bad |
|---|---|---|---|
| Class / object | noun or noun phrase | `Customer`, `WikiPage`, `AddressParser` | `Manager`, `ProcessData`, `CustomerObject` |
| Method | verb or verb phrase | `postPayment`, `deletePage`, `save` | `data()`, `holyHandGrenade()` |
| Accessor / mutator / predicate | `get` / `set` / `is` prefix (JavaBean) | `getName()`, `setName()`, `isPosted()` | `name()`, `posted()` |
| Overloaded constructor | static factory named for the arguments; make the constructor `private` to enforce it | `Complex.FromRealNumber(23.0)` | `new Complex(23.0)` |
| Loop counter in a tiny scope | single letter is fine | `i`, `j`, `k` | `l` |
| Anything with wider scope | searchable, length ∝ scope | `WORK_DAYS_PER_WEEK` | `5`, `e`, `a1` |

## Worked Example: the four-question rename

The book's central demonstration — same operators, same constants, same nesting depth,
radically different readability.

**Before** — nothing is wrong except that all the context is missing:

```java
public List<int[]> getThem() {
    List<int[]> list1 = new ArrayList<int[]>();
    for (int[] x : theList)
        if (x[0] == 4)
            list1.add(x);
    return list1;
}
```

The reader cannot answer: *What is in `theList`? What does subscript `0` mean? What does
`4` mean? How do I use the result?*

**Step 1 — name the concepts.** It's a minesweeper board; subscript 0 is a status value;
status 4 means "flagged":

```java
public List<int[]> getFlaggedCells() {
    List<int[]> flaggedCells = new ArrayList<int[]>();
    for (int[] cell : gameBoard)
        if (cell[STATUS_VALUE] == FLAGGED)
            flaggedCells.add(cell);
    return flaggedCells;
}
```

**Step 2 — let a type absorb the magic numbers.** Replace the `int[]` with a `Cell`
class exposing an intention-revealing predicate:

```java
public List<Cell> getFlaggedCells() {
    List<Cell> flaggedCells = new ArrayList<Cell>();
    for (Cell cell : gameBoard)
        if (cell.isFlagged())
            flaggedCells.add(cell);
    return flaggedCells;
}
```

**What it demonstrates:** complexity never changed — only implicity did. Naming is not
decoration; it is where the design becomes visible.

**Second worked example — context by enclosure.** `printGuessStatistics` holds `number`,
`verb`, and `pluralModifier` whose shared meaning must be inferred from the whole
algorithm. Promoting them to fields of a new `GuessStatisticsMessage` class gives them
definitive context, and *that* is what makes it possible to split the algorithm into
`thereAreNoLetters()`, `thereIsOneLetter()`, `thereAreManyLetters(count)`. Note the
direction of causation: **better context enabled smaller functions**, not the reverse.

## Key Takeaways

1. **If a name needs a comment, rename it** — that is the single test for this chapter.
2. **Length ∝ scope.** Single letters only in tiny local scopes; searchable names
   everywhere else.
3. **Replace magic numbers with named constants**, always — searchability alone justifies it.
4. **One word per concept, and never pun.** A consistent lexicon is a gift to every
   future reader.
5. **Prefer a class over a prefix** when adding context.
6. **Drop encodings**: no Hungarian notation, no `m_`, no `I` on interfaces.
7. **Classes are nouns, methods are verbs**, accessors follow `get`/`set`/`is`.
8. **Add no more context than necessary** — shorter is better when still clear.

## Connects To
- **Ch3 (Functions)**: intention-revealing names are what allow functions to shrink;
  extracting a function is largely an act of naming.
- **Ch4 (Comments)**: most comments are failures of naming — this chapter is the cure.
- **Ch17 (Smells)**: the N-series heuristics (N1–N7) restate these rules as review checks.
- **Ch10 (Classes)**: a class name you cannot make precise signals the class does too much.
