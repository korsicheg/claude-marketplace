# Chapter 10: Classes
*with Jeff Langr*

## Core Idea
**The first rule of classes is that they should be small. The second rule is that they
should be smaller than that.** But class size is measured in **responsibilities**, not
lines. We want systems composed of many small classes, not a few large ones.

## Frameworks Introduced

- **The Single Responsibility Principle (SRP)** — *a class or module should have one, and
  only one, reason to change.* This gives you both a definition of "responsibility" and
  a guideline for class size.
  - Why it's abused: *"Getting software to work and making software clean are two very
    different activities."* Most of us focus on working code — which is wholly
    appropriate — but then **fail to switch to the second concern** and move on to the
    next problem instead of breaking up the overstuffed class.

- **The Naming Test for size** — *"naming is probably the first way of helping determine
  class size."* If you cannot derive a concise name for a class, it is likely too large.
  The more ambiguous the name, the more responsibilities it probably has.
  - Weasel words that hint at unfortunate aggregation: **`Processor`, `Manager`, `Super`.**

- **The 25-Word Test** — you should be able to describe the class in about 25 words
  **without using "if," "and," "or," or "but."**
  - Worked: *"The SuperDashboard provides access to the component that last held the
    focus, **and** it also allows us to track the version and build numbers."* — the
    first "and" is the tell.

- **Cohesion** — classes should have a small number of instance variables, and each
  method should manipulate one or more of them. **The more variables a method
  manipulates, the more cohesive it is to its class**; a class where every variable is
  used by every method is maximally cohesive.
  - Maximal cohesion is neither advisable nor possible — but high cohesion means the
    methods and variables are co-dependent and hang together as a logical whole.
  - **The operational rule: when classes lose cohesion, split them.**

- **The Open-Closed Principle (OCP)** — *classes should be open for extension but closed
  for modification.* Incorporate new features by **extending** the system, not by
  modifying existing code.

- **The Dependency Inversion Principle (DIP)** — *classes should depend upon
  abstractions, not on concrete details.*

## Class organization (the standard layout)

1. **Public static constants**
2. **Private static variables**
3. **Private instance variables** (*"there is seldom a good reason to have a public
   variable"*)
4. **Public functions**, each followed immediately by **the private utilities it calls**

That last point follows the Stepdown Rule and makes the class read like a newspaper
article (Ch5).

**On encapsulation — the pragmatic exception:** keep variables and utilities private,
*"but we're not fanatic about it."* If a test in the same package needs access, make it
protected or package scope. **"For us, tests rule."** But always look for a way to
maintain privacy first — *loosening encapsulation is always a last resort.*

## Worked Example 1: `SuperDashboard` — why five methods can be too many

The "God class" version exposes ~70 public methods. Obvious. But consider the trimmed
version:

```java
public class SuperDashboard extends JFrame implements MetaDataUser {
    public Component getLastFocusedComponent()
    public void setLastFocused(Component lastFocused)
    public int getMajorVersionNumber()
    public int getMinorVersionNumber()
    public int getBuildNumber()
}
```

**Five methods isn't too much, is it? In this case it is** — two reasons to change:
1. It tracks **version information**, updated every time the software ships.
2. It manages **Java Swing components** (it derives from `JFrame`).

Note the asymmetry Martin points out: you'd bump the version when Swing code changes,
but the converse isn't true — version changes for reasons unrelated to Swing. Extract:

```java
public class Version {
    public int getMajorVersionNumber()
    public int getMinorVersionNumber()
    public int getBuildNumber()
}
```

**What it demonstrates:** identifying reasons to change *"often helps us recognize and
create better abstractions."* And `Version` has **high reuse potential in other
applications** — a benefit you never get from the God class.

## Worked Example 2: `PrintPrimes` → three classes

Knuth's `PrintPrimes` (as emitted by his WEB tool) is one deeply indented function with
`M`, `RR`, `CC`, `WW`, `ORDMAX`, `P[]`, `PAGENUMBER`, `PAGEOFFSET`, `ROWOFFSET`, `C`,
`J`, `K`, `JPRIME`, `ORD`, `SQUARE`, `N`, `MULT[]` — a plethora of odd variables in a
tightly coupled structure.

The refactoring splits it along **three responsibilities**:

| Class | Responsibility | Changes when… |
|---|---|---|
| `PrimePrinter` | handle the execution environment (holds `main`) | the method of invocation changes — e.g. converting to a SOAP service |
| `RowColumnPagePrinter` | format a list of numbers into pages of rows and columns | the output formatting needs changing |
| `PrimeGenerator` | generate a list of prime numbers | the prime-computation algorithm changes |

```java
public class PrimePrinter {
    public static void main(String[] args) {
        final int NUMBER_OF_PRIMES = 1000;
        int[] primes = PrimeGenerator.generate(NUMBER_OF_PRIMES);

        final int ROWS_PER_PAGE = 50;
        final int COLUMNS_PER_PAGE = 4;
        RowColumnPagePrinter tablePrinter =
            new RowColumnPagePrinter(ROWS_PER_PAGE, COLUMNS_PER_PAGE,
                "The First " + NUMBER_OF_PRIMES + " Prime Numbers");
        tablePrinter.print(primes);
    }
}
```

**Three things worth noting, because they are counterintuitive:**

1. **The program got longer** — from one page to nearly three. Three stated reasons:
   longer descriptive variable names; function and class declarations used *as a way to
   add commentary*; whitespace and formatting for readability. **Longer is the right
   trade.**
2. **`PrimeGenerator` is never instantiated.** *"The class is just a useful scope in
   which its variables can be declared and kept hidden."* A class can exist purely to
   scope state.
3. **This was not a rewrite.** Same algorithm, same mechanics. The method was: write a
   test suite verifying the precise behavior of the original, then make *"a myriad of
   tiny little changes… one at a time,"* running the program after each to confirm
   behavior was unchanged.

## Worked Example 3: the `Sql` class — SRP and OCP together

**Before** — one class that must be opened for every change:

```java
public class Sql {
    public Sql(String table, Column[] columns)
    public String create()
    public String insert(Object[] fields)
    public String selectAll()
    public String findByKey(String keyColumn, String keyValue)
    public String select(Column column, String pattern)
    public String select(Criteria criteria)
    public String preparedInsert()
    private String columnList(Column[] columns)
    private String valuesList(Object[] fields, final Column[] columns)
    private String selectWithCriteria(String criteria)
    private String placeholderList(Column[] columns)
}
```

Two reasons to change: adding a **new statement type**, and altering the details of **an
existing statement type** (e.g. subselects in `select`). That's an SRP violation.

**How to spot it from the outline alone:** private methods like `selectWithCriteria`
apply only to a subset of the class. *"Private method behavior that applies only to a
small subset of a class can be a useful heuristic for spotting potential areas for
improvement."*

**After** — each public method becomes its own derivative; private helpers move where
they're needed; shared behavior isolates into `Where` and `ColumnList`:

```java
abstract public class Sql {
    public Sql(String table, Column[] columns)
    abstract public String generate();
}
public class CreateSql extends Sql              { @Override public String generate() }
public class SelectSql extends Sql              { @Override public String generate() }
public class InsertSql extends Sql {
    @Override public String generate()
    private String valuesList(Object[] fields, final Column[] columns)
}
public class SelectWithCriteriaSql extends Sql  { @Override public String generate() }
public class SelectWithMatchSql extends Sql     { @Override public String generate() }
public class FindByKeySql extends Sql           { @Override public String generate() }
public class PreparedInsertSql extends Sql {
    @Override public String generate()
    private String placeholderList(Column[] columns)
}
public class Where      { public Where(String criteria) public String generate() }
public class ColumnList { public ColumnList(Column[] columns) public String generate() }
```

Now `update` support means **adding `UpdateSql`** — no existing class changes, nothing
else can break. That is OCP.

**The crucial timing caveat, easy to miss:** *"the primary spur for taking action should
be system change itself. If the `Sql` class is deemed logically complete… we should leave
`Sql` alone. But as soon as we find ourselves opening up a class, we should consider
fixing our design."* **Don't pre-split speculatively — split when change arrives.**

## Worked Example 4: DIP and the testability payoff

`Portfolio` depending directly on `TokyoStockExchange` is untestable — *"it's hard to
write a test when we get a different answer every five minutes!"*

```java
public interface StockExchange {
    Money currentPrice(String symbol);
}

public class Portfolio {
    private StockExchange exchange;
    public Portfolio(StockExchange exchange) {
        this.exchange = exchange;
    }
    // ...
}
```

```java
public class PortfolioTest {
    private FixedStockExchangeStub exchange;
    private Portfolio portfolio;

    @Before
    protected void setUp() throws Exception {
        exchange = new FixedStockExchangeStub();
        exchange.fix("MSFT", 100);
        portfolio = new Portfolio(exchange);
    }

    @Test
    public void GivenFiveMSFTTotalShouldBe500() throws Exception {
        portfolio.add(5, "MSFT");
        Assert.assertEquals(500, portfolio.value());
    }
}
```

**What it demonstrates:** *"If a system is decoupled enough to be tested in this way, it
will also be more flexible and promote more reuse."* Testability is not a separate goal
from good design — it is a **detector** for it.

## Anti-patterns

- **God classes** — `SuperDashboard` with ~70 public methods.
- **`Manager`, `Processor`, `Super`, `Data`, `Info` in class names** — weasel words
  masking aggregated responsibilities.
- **Class descriptions needing "and"/"or"/"but"** — more than one responsibility.
- **Low cohesion from too many instance variables** — when keeping functions small and
  parameter lists short produces fields used by only a subset of methods, *"it almost
  always means that there is at least one other class trying to get out."*
- **Depending on concrete details** — makes the client fragile and hard to test.
- **Public instance variables** — seldom a good reason.

## The cohesion/extraction loop (the mechanism behind "many small classes")

This is the chapter's most useful causal chain, and it runs in a loop:

1. You want to extract part of a long function, but it uses four local variables.
2. Rather than pass four arguments, **promote them to instance variables** — now the
   extraction is free and the function splits easily.
3. But the class **loses cohesion**: it accumulates fields that exist only so a few
   functions can share them.
4. *"If there are a few functions that want to share certain variables, doesn't that make
   them a class in their own right? Of course it does."* → **Split the class.**
5. Repeat.

**So breaking large functions into small ones naturally produces small classes**, better
organization, and a more transparent structure.

## Mental Models

- **The toolbox question**: *"Do you want your tools organized into toolboxes with many
  small drawers each containing well-defined and well-labeled components? Or do you want
  a few drawers that you just toss everything into?"*
- **Answering the "too many pieces" fear**: a system of many small classes has **no more
  moving parts** than one with a few large classes — there is just as much to learn
  either way. The difference is that the small-class system lets you *"understand only
  the directly affected complexity at any given time,"* while large multipurpose classes
  make you wade through things you don't need to know right now.
- **Responsibilities, not lines, are the unit of class size.**
- **Testability is a design smell detector.** If it's hard to test, it's too coupled.

## Key Takeaways

1. **Measure classes in responsibilities**; apply SRP — one reason to change.
2. **Use the naming test and the 25-word test** to detect oversized classes cheaply.
3. **High cohesion, few instance variables**; split when cohesion drops.
4. **Extract small functions → promote variables → split the class.** That loop is how
   good structure emerges.
5. **Apply OCP when change actually arrives** — extend by subclassing rather than
   reopening.
6. **Apply DIP** — depend on interfaces, inject them, and your tests come for free.
7. **Refactor in tiny verified steps under a test suite.** Never rewrite.
8. **Longer code with better names and more classes is usually the better code.**

## Connects To
- **Ch3 (Functions)**: the extraction loop starts there; class organization follows the
  Stepdown Rule.
- **Ch5 (Formatting)**: the newspaper layout, and the over-long field list as a
  split signal.
- **Ch9 (Unit Tests)**: "tests rule" on encapsulation; DIP makes the `Portfolio` test
  possible.
- **Ch11 (Systems)**: dependency injection at system scale.
- **Ch12 (Emergence)**: "minimal classes and methods" and the cohesion rules restated.
- **Ch17 (Smells)**: G-series heuristics on class design.
- **SOLID** (*PPP*); **Wirfs-Brock, *Object Design*** (responsibilities);
  **Knuth, *Literate Programming***.
