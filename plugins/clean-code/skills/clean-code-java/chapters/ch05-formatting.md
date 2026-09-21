# Chapter 5: Formatting

## Core Idea
**Code formatting is communication, and communication is the professional developer's
first order of business** — ahead of "getting it working." Today's functionality will
likely change next release; your formatting discipline sets precedents that outlive the
code itself. *Your style and discipline survives, even though your code does not.*

## Frameworks Introduced

- **The Newspaper Metaphor** — read a source file top to bottom like a newspaper article.
  - How: the **name** is the headline — simple, explanatory, sufficient on its own to
    tell you whether you are in the right module. The **top** of the file holds the
    high-level concepts and algorithms. **Detail increases as you move down**, ending in
    the lowest-level functions.
  - Corollary: a newspaper is many small articles, not one long agglomeration of facts.
    If it were the latter, nobody would read it.

- **Vertical Openness Between Concepts** — each group of lines is a complete thought;
  separate thoughts with **blank lines**.
  - Why it works: your eye is drawn to the first line *after* a blank line. Unfocus your
    eyes on a well-spaced listing and the groupings pop out; on an unspaced one you see
    a muddle.

- **Vertical Density Implies Association** — tightly related lines belong vertically
  adjacent, so the reader takes them in "in an eye-full" without moving their head.
  - The common destroyer of density is useless javadoc between fields.

- **Vertical Distance ∝ Conceptual Affinity** [G10] — the stronger the relationship
  between two pieces of code, the less vertical distance between them.
  - Affinity comes from direct dependence (one function calls another, or uses a
    variable) **and** from similarity — `assertTrue`/`assertFalse` overloads want to be
    together because they share a naming scheme and perform variations of one task, even
    apart from calling each other.
  - Corollary: don't split closely related concepts into different files without a very
    good reason. *This is one of the reasons protected variables should be avoided.*

- **Vertical Ordering / dependencies point downward** — a called function goes **below**
  its caller. This is the opposite of what Pascal/C/C++ once forced, and it lets you skim
  the first few functions for the gist without immersing in detail.

- **Team Rules** (a deliberate pun) — every programmer has favorite rules, *but if he
  works in a team, then the team rules.*
  - How: agree on one style, **encode it in the IDE's formatter**, and comply. Martin's
    own FitNesse team did this in about 10 minutes in 2002 — braces, indent size, naming
    — and stuck with it. They were **not** the rules he personally preferred.
  - Why: a good software system is a set of documents that read nicely. The reader must
    be able to trust that a formatting gesture means the same thing in every file.

## Reference Table: the concrete numbers

| Dimension | Martin's guidance | Evidence cited |
|---|---|---|
| **File length** | ~200 lines typical, **500-line upper limit** — desirable, not a hard rule | FitNesse is ~50,000 lines with an average file of ~65 lines, max ~400. JUnit, FitNesse, Time and Money: none over 500. Tomcat and Ant: files in the thousands, nearly half over 200 |
| **Line width** | Short. 80 (the Hollerith limit) is arbitrary; 100–120 is fine; **"beyond that is probably just careless."** Martin personally sets **120** | Across 7 projects, every width from 20–60 chars is ~1% of lines each (≈40% total); ~30% more are under 10 chars; sharp drop-off above 80 |
| **Indent depth** | Proportional to scope nesting; never collapse a scope to one line | — |
| **Local variables** | At the top of the function (functions are short, so this *is* close to usage) | — |
| **Loop control variables** | Declared **inside** the loop statement | — |
| **Instance variables** | **Top of the class**, in one well-known place | The JUnit `TestSuite` counter-example hides two fields halfway down the file — "it would be hard to hide them in a better place" |

## Horizontal formatting rules

- **Surround assignment operators with spaces** — an assignment has two distinct major
  elements, left and right; the spaces make the separation obvious.
- **No space between a function name and its opening paren** — they are closely related;
  separating them makes them look disjoined.
- **Space after commas in argument lists** — accentuates that the arguments are separate.
- **Use spacing to show operator precedence**: high-precedence factors get no space, lower-
  precedence terms get space:

```java
private static double determinant(double a, double b, double c) {
    return b*b - 4*a*c;
}
public static double root1(double a, double b, double c) {
    double determinant = determinant(a, b, c);
    return (-b + Math.sqrt(determinant)) / (2*a);
}
```
  - **Caveat Martin states himself**: most reformatting tools are blind to precedence and
    will flatten this spacing. Don't fight the formatter over it.

- **Do NOT horizontally align declarations or assignments in columns.** Martin used to,
  and stopped. It emphasizes the wrong thing — your eye runs down the variable names
  without seeing the types, or down the rvalues without seeing the assignment operator.
  Worse: **if the list is long enough to want alignment, the problem is the length of the
  list, not the lack of alignment.** The over-long aligned field list in
  `FitNesseExpediter` is really telling you the class should be split.

## Anti-patterns

- **Collapsing scopes onto one line** — `public String render() throws Exception {return "";}`.
  Martin: every time he succumbed to this temptation, he went back and undid it.
- **Dummy scopes with an invisible semicolon** — `while (dis.read(buf,0,size) != -1);`.
  Avoid them; when unavoidable, put the semicolon on its own indented line with braces.
- **No indentation at all** — the unindented `FitNesseServer` is semantically identical
  to the indented one and *virtually impenetrable without intense study*.
- **Instance variables buried mid-class** — the reader finds them by accident.
- **Noise comments between fields** — they break the vertical density of related
  declarations and force extra eye and head motion for the same comprehension.
- **A jumble of individual styles in one codebase** — it should not look like it was
  written by a bunch of disagreeing individuals, or by *"a bevy of drunken sailors."*

## Worked Example: vertical openness, the same class twice

**With blank lines** — package, imports, constants, and each method are visually separate
concepts:

```java
package fitnesse.wikitext.widgets;

import java.util.regex.*;

public class BoldWidget extends ParentWidget {
    public static final String REGEXP = "'''.+?'''";
    private static final Pattern pattern = Pattern.compile("'''(.+?)'''",
        Pattern.MULTILINE + Pattern.DOTALL);

    public BoldWidget(ParentWidget parent, String text) throws Exception {
        super(parent);
        Matcher match = pattern.matcher(text);
        match.find();
        addChildWidgets(match.group(1));
    }

    public String render() throws Exception {
        StringBuffer html = new StringBuffer("<b>");
        html.append(childHtml()).append("</b>");
        return html.toString();
    }
}
```

Remove the blank lines and nothing changes semantically — but the groupings stop popping
out and the file reads as a muddle. **That entire effect comes from a bit of vertical
openness.**

**Second worked example — dependent functions flow downward.** In FitNesse's
`WikiPageResponder`, `makeResponse` calls `getPageNameOrDefault`, `loadPage`,
`notFoundResponse`, and `makePageResponse`, and each is defined just below, in call
order. The reader can trust that a definition follows shortly after its use.

As an aside from that same listing: the `"FrontPage"` constant is passed *down* into
`getPageNameOrDefault` rather than buried inside it — **keep constants at the level where
knowing them makes sense** [G35], not hidden in an inappropriately low-level function.

## Mental Models

- **When someone looks under the hood, what should they conclude?** Neatness, consistency
  and attention to detail read as "professionals have been at work." A scrambled mass
  reads as inattention pervading the whole project.
- **Formatting is too important to ignore and too important to treat religiously.**
- **Chasing your tail through a file is a formatting failure**, not a you problem: you
  are spending mental energy locating pieces instead of understanding the system.
- **Long declaration lists are a design smell wearing a formatting costume.**

## Key Takeaways

1. **Files ~200 lines, 500 max; lines ≤ 120.** Small files are easier to understand.
2. **Blank lines between concepts; no blank lines inside a tightly related group.**
3. **Caller above callee**; keep related things vertically close.
4. **Instance variables at the top, locals near use, loop counters in the loop.**
5. **Never collapse a scope to one line; always indent.**
6. **Don't column-align** — and treat the urge to align as a signal to split the class.
7. **Agree on one team style and put it in the IDE formatter.** The team rules, not you.
8. **Structure the file like a newspaper**: headline name, high-level first, detail last.

## Connects To
- **Ch3 (Functions)**: the Stepdown Rule is the vertical-ordering rule seen from the
  abstraction side — both say high level on top, detail below.
- **Ch10 (Classes)**: the 500-line file limit and the over-long field list both point at
  class size and SRP.
- **Ch17 (Smells)**: G10 "Vertical Separation", G35 "Keep Configurable Data at High
  Levels", F-series function heuristics.
- **Automated formatters / linters**: the practical way to make "team rules" stick.
