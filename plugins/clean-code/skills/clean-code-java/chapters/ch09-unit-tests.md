# Chapter 9: Unit Tests

## Core Idea
**Test code is just as important as production code — it is not a second-class citizen.**
Tests are what keep production code flexible, maintainable and reusable, because *tests
enable change*. Let the tests rot and the production code rots with them.

## Frameworks Introduced

- **The Three Laws of TDD**:
  1. **You may not write production code until you have written a failing unit test.**
  2. **You may not write more of a unit test than is sufficient to fail — and not
     compiling is failing.**
  3. **You may not write more production code than is sufficient to pass the currently
     failing test.**
  - These lock you into a cycle **roughly thirty seconds long**, with the tests running
    a few seconds ahead of the production code.
  - Consequence: dozens of tests a day, thousands a year, covering virtually all
    production code — a test suite that can rival the production code in size, which is
    itself a management problem worth taking seriously.

- **BUILD-OPERATE-CHECK** — every test splits into three visible parts: build the test
  data, operate on it, check the result yielded what you expected.

- **Domain-Specific Testing Language** — don't drive the system through the same APIs
  programmers use; build a set of functions and utilities *on top of* those APIs that
  make tests convenient to write and easy to read.
  - **This API is not designed up front.** It evolves from continued refactoring of test
    code that got too tainted by obfuscating detail.

- **The Dual Standard** — test code must be simple, succinct and expressive, but **need
  not be as efficient as production code**; it runs in a test environment with different
  needs.
  - The boundary is precise: *"There are things that you might never do in a production
    environment that are perfectly fine in a test environment. Usually they involve
    issues of memory or CPU efficiency. **But they never involve issues of cleanliness.**"*

- **One Assert per Test** — a good *guideline*, not a law. It makes each test reach a
  single conclusion that is quick to understand.
  - Martin's honest position: he tries to build a testing DSL that supports it, **but is
    not afraid to use more than one assert.** Forcing it can require a Template Method
    base class or extra test classes — *"too much mechanism for such a minor issue."*
  - **The best statement of the rule: minimize the number of asserts per test.**

- **Single Concept per Test** — the better rule. Don't write long test functions that
  test one miscellaneous thing after another.
  - **Final formulation: minimize the number of asserts per concept, and test just one
    concept per test function.**

- **F.I.R.S.T.**:

| Letter | Rule | Why |
|---|---|---|
| **Fast** | Tests run quickly | Slow tests don't get run; problems are found late; you stop feeling free to clean up, and the code rots |
| **Independent** | No test sets up conditions for another; any order | Otherwise the first failure cascades, hiding downstream defects and making diagnosis hard |
| **Repeatable** | Runs in production, QA, and on a laptop on the train with no network | Otherwise you always have an excuse for a failure, and can't run tests when the environment is unavailable |
| **Self-Validating** | Boolean output: pass or fail | No reading log files, no manually diffing two text files — otherwise failure becomes subjective |
| **Timely** | Written **just before** the production code that passes them | Write tests after and you may find the production code hard to test, or decide some of it is too hard, because you didn't design it to be testable |

## Worked Example 1: the same three tests, cleaned

**Before** — duplication in every `addPage`/`assertSubString` call [G5], plus a swarm of
irrelevant detail: `PathParser` transformations, responder creation, response casting,
and the "ham-handed" URL construction.

```java
public void testGetPageHieratchyAsXml() throws Exception {
    crawler.addPage(root, PathParser.parse("PageOne"));
    crawler.addPage(root, PathParser.parse("PageOne.ChildOne"));
    crawler.addPage(root, PathParser.parse("PageTwo"));

    request.setResource("root");
    request.addInput("type", "pages");
    Responder responder = new SerializedPageResponder();
    SimpleResponse response =
        (SimpleResponse) responder.makeResponse(new FitNesseContext(root), request);
    String xml = response.getContent();

    assertEquals("text/xml", response.getContentType());
    assertSubString("<name>PageOne</name>", xml);
    assertSubString("<name>PageTwo</name>", xml);
    assertSubString("<name>ChildOne</name>", xml);
}
```

**After** — same behavior, BUILD-OPERATE-CHECK made structurally obvious:

```java
public void testGetPageHierarchyAsXml() throws Exception {
    makePages("PageOne", "PageOne.ChildOne", "PageTwo");

    submitRequest("root", "type:pages");

    assertResponseIsXML();
    assertResponseContains(
        "<name>PageOne</name>", "<name>PageTwo</name>", "<name>ChildOne</name>"
    );
}

public void testSymbolicLinksAreNotInXmlPageHierarchy() throws Exception {
    WikiPage page = makePage("PageOne");
    makePages("PageOne.ChildOne", "PageTwo");
    addLinkTo(page, "PageTwo", "SymPage");

    submitRequest("root", "type:pages");

    assertResponseIsXML();
    assertResponseContains(
        "<name>PageOne</name>", "<name>PageTwo</name>", "<name>ChildOne</name>"
    );
    assertResponseDoesNotContain("SymPage");
}
```

**What it demonstrates:** the test now uses only the data types and functions it truly
needs. *"In the end, this code was not designed to be read"* — that is the defect being
fixed, and Martin notes he helped write the original, *"so I feel free to roundly
criticize it."*

## Worked Example 2: the encoded-state trick (and its honest caveat)

**Before** — your eye must bounce between the state name and the assertion sense:

```java
@Test
public void turnOnLoTempAlarmAtThreashold() throws Exception {
    hw.setTemp(WAY_TOO_COLD);
    controller.tic();
    assertTrue(hw.heaterState());
    assertTrue(hw.blowerState());
    assertFalse(hw.coolerState());
    assertFalse(hw.hiTempAlarm());
    assertTrue(hw.loTempAlarm());
}
```

**After** — upper case means on, lower case means off, order is always
`{heater, blower, cooler, hi-temp-alarm, lo-temp-alarm}`:

```java
@Test public void turnOnCoolerAndBlowerIfTooHot() throws Exception {
    tooHot();      assertEquals("hBChl", hw.getState());
}
@Test public void turnOnHeaterAndBlowerIfTooCold() throws Exception {
    tooCold();     assertEquals("HBchl", hw.getState());
}
@Test public void turnOnHiTempAlarmAtThreshold() throws Exception {
    wayTooHot();   assertEquals("hBCHl", hw.getState());
}
@Test public void turnOnLoTempAlarmAtThreshold() throws Exception {
    wayTooCold();  assertEquals("HBchL", hw.getState());
}
```

And the mock that produces it — deliberately inefficient:

```java
public String getState() {
    String state = "";
    state += heater     ? "H" : "h";
    state += blower     ? "B" : "b";
    state += cooler     ? "C" : "c";
    state += hiTempAlarm ? "H" : "h";
    state += loTempAlarm ? "L" : "l";
    return state;
}
```

**What it demonstrates — two things at once:**
1. Martin flags this as *"close to a violation of the rule about mental mapping"* (Ch2)
   and defends it anyway, because once you know the encoding your eyes glide across it.
   **The rules are heuristics with judgment attached, not absolutes.**
2. `getState` should use a `StringBuffer` for efficiency — in an embedded real-time
   system with constrained memory. **The test environment is not constrained**, so string
   concatenation is fine here. That is the dual standard in one method.

## Worked Example 3: one concept per test

**Before** — three independent things merged into one function, forcing the reader to
work out why each section exists:

```java
/**
 * Miscellaneous tests for the addMonths() method.
 */
public void testAddMonths() {
    SerialDate d1 = SerialDate.createInstance(31, 5, 2004);

    SerialDate d2 = SerialDate.addMonths(1, d1);
    assertEquals(30, d2.getDayOfMonth());
    assertEquals(6, d2.getMonth());
    assertEquals(2004, d2.getYYYY());

    SerialDate d3 = SerialDate.addMonths(2, d1);
    ...
    SerialDate d4 = SerialDate.addMonths(1, SerialDate.addMonths(1, d1));
    ...
}
```

Split into three tests, stated as given/when/then:

- *Given the last day of a 31-day month (May):* adding one month, where that month ends
  on the 30th (June), yields the 30th, not the 31st.
- *Given the same:* adding two months, where the final month has 31 days, yields the 31st.
- *Given the last day of a 30-day month (June):* adding one month into a 31-day month
  yields the 30th, not the 31st.

**The payoff is the real lesson:** stating them this way exposes a general rule hiding in
the miscellany — *when you increment the month, the date can be no greater than the last
day of that month.* Which implies incrementing February 28th should give March 28th —
**a test that is missing and would be useful to write.** Clean tests find missing tests.

## The cautionary tale: why dirty tests are worse than none

A team decided test code needn't meet production standards. "Quick and dirty" — badly
named variables, long test functions, no design. The sequence that followed:

1. Tests must change as production code evolves; **dirty tests are hard to change.**
2. Cramming new tests into the tangle starts to cost more than writing the production code.
3. Old tests fail on every modification, and the mess makes them hard to get green again.
4. The suite is viewed as an ever-increasing liability; maintenance cost rises each release.
5. Developers blame the tests for growing estimates. **The suite is discarded entirely.**
6. Without tests, they can't verify changes or catch cross-module breakage → defect rate rises.
7. Fearing change, they **stop cleaning the production code** → it rots.
8. End state: no tests, tangled bug-riddled code, frustrated customers, and the belief
   that testing had failed them.

*"In a way they were right. Their testing effort had failed them. But it was their
decision to allow the tests to be messy that was the seed of that failure."*

## Anti-patterns

- **Throwaway manual tests** — Martin's own 1990s `Timer` "test": tap a melody on the
  keyboard, watch it replay five seconds later, demo it, delete it.
- **Dirty tests** — *equivalent to, if not worse than, having no tests.*
- **Tests loaded with irrelevant detail** — `PathParser` calls, casts, and response
  plumbing that obscure the intent.
- **Duplicate code in tests** [G5] — just as bad as in production code.
- **Tests that depend on each other** or on a particular environment.
- **Writing tests after the production code** — you end up with code that is hard or
  impossible to test because you never designed it to be.

## Mental Models

- **Tests enable the -ilities.** *"If you have tests, you do not fear making changes to
  the code."* Higher coverage → less fear → you can improve even a poor architecture
  without dread. Without tests, no amount of architectural elegance makes you brave.
- **What makes a clean test? "Readability, readability, and readability"** — and it
  matters *more* in tests than in production code. Clarity, simplicity, density of
  expression: say a lot with few expressions.
- **Refactor tests toward a language, not toward abstraction for its own sake.** The
  testing DSL is discovered by cleaning, exactly as production designs are.
- **Dirty tests are a slow-motion decision to stop refactoring.**

## Key Takeaways

1. **Follow the three laws of TDD** — test first, minimally, in ~30-second cycles.
2. **Hold tests to production standards of cleanliness** — efficiency is the only
   dimension where the standard differs.
3. **Structure every test as Build-Operate-Check.**
4. **Grow a domain-specific testing language** by refactoring tests, not by designing
   it up front.
5. **One concept per test; minimize asserts per concept.**
6. **Apply F.I.R.S.T.** — Fast, Independent, Repeatable, Self-Validating, Timely.
7. **Tests and code are checked in together** and must be convenient for anyone to run.
8. **If you let the tests rot, your code will rot too.**

## Connects To
- **Ch3 (Functions)**: the green suite is what makes aggressive extraction safe —
  "write it dirty, then refactor under tests."
- **Ch7 (Error Handling)**: the try-catch-first workflow is driven by a failing test.
- **Ch8 (Boundaries)**: learning tests and boundary tests.
- **Ch12 (Emergence)**: "Runs all the tests" is the first rule of simple design.
- **Ch15 (JUnit Internals)** and **Ch16 (SerialDate)**: the `addMonths` example above is
  from the SerialDate code refactored in Ch16.
- **GoF Template Method**; **RSpec** (given-when-then); **Beck, *TDD***.
