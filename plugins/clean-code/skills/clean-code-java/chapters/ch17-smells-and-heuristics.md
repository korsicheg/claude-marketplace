# Chapter 17: Smells and Heuristics
*The complete catalogue — 66 numbered heuristics*

## Core Idea
Martin compiled this list by refactoring several programs and, **after each change,
asking himself why he made it and writing the reason down.** It extends Fowler's code
smells. It is meant to be read top to bottom *and* used as a reference — and its closing
warning matters: *"Clean code is not written by following a set of rules. You don't
become a software craftsman by learning a list of heuristics. **Professionalism and
craftsmanship come from values that drive disciplines.**"* The list's purpose is to
**imply a value system.**

---

## Comments (C1–C5)

| # | Smell | Rule |
|---|---|---|
| **C1** | **Inappropriate Information** | Comments must not hold what belongs in source control, the issue tracker, or another record-keeping system. No change histories, authors, last-modified-date, SPR numbers. **Comments are for technical notes about the code and design.** |
| **C2** | **Obsolete Comment** | Old, irrelevant, incorrect. *"Obsolete comments tend to migrate away from the code they once described. They become floating islands of irrelevance and misdirection."* Best not to write one that will go stale; update or delete on sight. |
| **C3** | **Redundant Comment** | `i++; // increment i`. Or a Javadoc saying no more than the signature: `/** @param sellRequest @return @throws ... */`. **Comments should say things the code cannot say for itself.** |
| **C4** | **Poorly Written Comment** | *"A comment worth writing is worth writing well."* Choose words carefully, correct grammar and punctuation, don't ramble, don't state the obvious, be brief. |
| **C5** | **Commented-Out Code** | *"An abomination."* It calls functions that no longer exist, uses renamed variables, follows obsolete conventions. Nobody deletes it because everyone assumes someone else needs it. **Delete it — source control remembers.** |

## Environment (E1–E2)

| # | Smell | Rule |
|---|---|---|
| **E1** | **Build Requires More Than One Step** | One command to check out, one to build: `svn get mySystem; cd mySystem; ant all`. No arcane command sequences, no hunting for stray JARs and XML files. |
| **E2** | **Tests Require More Than One Step** | One button in the IDE, or one shell command. *"Being able to run all the tests is so fundamental and so important that it should be quick, easy, and obvious to do."* |

## Functions (F1–F4)

| # | Smell | Rule |
|---|---|---|
| **F1** | **Too Many Arguments** | None is best, then one, two, three. **More than three is very questionable and should be avoided with prejudice.** |
| **F2** | **Output Arguments** | Counterintuitive — readers expect inputs. If the function must change state, have it change the state of the object it is called on. |
| **F3** | **Flag Arguments** | *"Boolean arguments loudly declare that the function does more than one thing."* Eliminate them. |
| **F4** | **Dead Function** | Never-called methods should be discarded. **Don't be afraid to delete** — source control remembers. |

## General (G1–G36)

| # | Smell | Rule |
|---|---|---|
| **G1** | **Multiple Languages in One Source File** | A Java file may carry XML, HTML, YAML, Javadoc, English, JavaScript. *"Confusing at best and carelessly sloppy at worst."* Ideal: one language per file; realistically, **minimize both the number and the extent** of extra languages. |
| **G2** | **Obvious Behavior Is Unimplemented** | The **Principle of Least Surprise**. `StringToDay("Monday")` should also handle abbreviations and ignore case. Otherwise *"readers lose their trust in the original author and must fall back on reading the details of the code."* |
| **G3** | **Incorrect Behavior at the Boundaries** | *"Don't rely on your intuition. Look for every boundary condition and write a test for it."* There is no replacement for due diligence. |
| **G4** | **Overridden Safeties** | Chernobyl melted down because the manager overrode safeties one by one to run an experiment. Manual `serialVersionUID`, disabled compiler warnings, turned-off failing tests — *"as bad as pretending your credit cards are free money."* |
| **G5** | **Duplication** | **"One of the most important rules in this book."** DRY (Hunt & Thomas); "Once, and only once" (Beck); Jeffries ranks it second only to passing tests. **Every duplication is a missed opportunity for abstraction.** Three forms, three cures: identical clumps → **methods**; repeated `switch`/`if-else` chains on the same conditions → **polymorphism**; similar algorithms without similar lines → **Template Method or Strategy**. *"Most of the design patterns that have appeared in the last fifteen years are simply well-known ways to eliminate duplication."* |
| **G6** | **Code at Wrong Level of Abstraction** | Separate general from detailed concepts **completely** — constants, variables and utilities that pertain only to the implementation must not be in the base class. Example: `percentFull()` on `Stack` belongs on `BoundedStack`. And returning 0 for an unbounded stack *"would be telling a lie."* **"You cannot lie or fake your way out of a misplaced abstraction."** |
| **G7** | **Base Classes Depending on Their Derivatives** | *"In general, base classes should know nothing about their derivatives."* Exception: a strictly fixed set of derivatives that always deploy in the same jar (finite state machines). Otherwise separate jars let you redeploy derivatives without rebuilding bases. |
| **G8** | **Too Much Information** | *"Well-defined modules have very small interfaces that allow you to do a lot with a little."* Hide data, utility functions, constants, temporaries. The fewer methods, variables, instance variables and protected members, the better. **Limit information to keep coupling low.** |
| **G9** | **Dead Code** | `if` branches for impossible conditions, `catch` blocks for exceptions never thrown, uncalled utilities, unreachable `switch` cases. It still compiles but doesn't follow current conventions — *"it was written at a time when the system was different."* **Give it a decent burial.** |
| **G10** | **Vertical Separation** | Locals declared just above first use with small vertical scope; private functions defined just below their first use. *"Finding a private function should just be a matter of scanning downward."* |
| **G11** | **Inconsistency** | Do similar things the same way. If `response` holds an `HttpServletResponse` in one function, use it in all of them. If you have `processVerificationRequest`, name the sibling `processDeletionRequest`. |
| **G12** | **Clutter** | Default constructors with no implementation, unused variables, uncalled functions, information-free comments. Remove them. |
| **G13** | **Artificial Coupling** | A coupling that serves no direct purpose — a general enum nested inside a specific class, or a general-purpose static in a specific class, forcing the whole application to know about that class. *"This is lazy and careless."* Take the time to decide where things belong. |
| **G14** | **Feature Envy** (Fowler) | A method using another object's accessors/mutators to manipulate its data — it *"wishes it were inside that other class."* **But sometimes a necessary evil:** `HourlyEmployeeReport.reportHours()` envies `HourlyEmployee`, yet moving the format string into `HourlyEmployee` would couple it to the report format and violate SRP, OCP, and the Common Closure Principle. |
| **G15** | **Selector Arguments** | *"Hardly anything more abominable than a dangling `false` argument at the end of a function call."* Not only hard to remember — each selector **combines many functions into one**. Not just booleans: enums, ints, any behavior-selecting argument. **Better to have many functions than to pass a code into one.** |
| **G16** | **Obscured Intent** | Run-on expressions, Hungarian notation and magic numbers. `public int m_otCalc() { return iThsWkd * iThsRte + (int) Math.round(0.5 * iThsRte * Math.max(0, iThsWkd - 400)); }` — *"small and dense… also virtually impenetrable."* |
| **G17** | **Misplaced Responsibility** | *"One of the most important decisions a software developer can make is where to put code."* Principle of least surprise: `PI` goes with the trig functions; `OVERTIME_RATE` in `HourlyPayCalculator`. **Test by name:** which of `getTotalHours` or `saveTimeCard` implies it computes the total? If performance forces the other choice, rename accordingly (`computeRunningTotalOfHours`). |
| **G18** | **Inappropriate Static** | `Math.max(a,b)` is a good static — all data comes from arguments, and *"there is almost no chance we'd want it to be polymorphic."* `HourlyPayCalculator.calculatePay(employee, overtimeRate)` looks similar but **might** want `OvertimeHourlyPayCalculator` / `StraightTimeHourlyPayCalculator`, so it should be a non-static member of `Employee`. **Prefer non-static; when in doubt, non-static.** |
| **G19** | **Use Explanatory Variables** | Break calculations into intermediate values with meaningful names. *"It is hard to overdo this. More explanatory variables are generally better than fewer. It is remarkable how an opaque module can suddenly become transparent."* |
| **G20** | **Function Names Should Say What They Do** | `date.add(5)` — days? weeks? hours? Mutating or returning new? Mutating → `addDaysTo`/`increaseByDays`; pure → `daysLater`/`daysSince`. **If you must read the implementation or docs to know what it does, find a better name or rearrange the functionality.** |
| **G21** | **Understand the Algorithm** | Poking at `if`s and flags until tests pass is a legitimate way to *get* there — *"but it is not sufficient to leave the quotation marks around the word 'work.'"* **You must know the solution is correct.** Best way to gain that: refactor until it's obvious how it works. (Footnote: being unsure whether an algorithm suits the job is a fact of life; *"being unsure what your code does is just laziness."*) |
| **G22** | **Make Logical Dependencies Physical** | A dependent module must not *assume* things about what it depends on — it must **ask**. Example: `HourlyReporter` holding `PAGE_SIZE = 55` assumes `HourlyReportFormatter` can handle 55. Fix: add `getMaxPageSize()` to the formatter. |
| **G23** | **Prefer Polymorphism to If/Else or Switch/Case** | *"Most people use switch statements because it's the obvious brute force solution, not because it's the right solution."* Cases where functions are more volatile than types are **rare**, so every switch is suspect. **The ONE SWITCH rule: there may be no more than one switch statement for a given type of selection, and its cases must create the polymorphic objects that replace every other such switch in the system.** |
| **G24** | **Follow Standard Conventions** | A team standard based on industry norms — variable placement, naming, braces. *"The team should not need a document to describe these conventions because their code provides the examples."* Each member must be mature enough to realize **it doesn't matter a whit where you put your braces so long as you all agree.** |
| **G25** | **Replace Magic Numbers with Named Constants** | `86400` → `SECONDS_PER_DAY`; `55` → `LINES_PER_PAGE`. **But use judgment:** `feetWalked/5280.0`, `hourlyRate * 8`, `radius * Math.PI * 2` — *"there are some formulae in which constants are simply better written as raw numbers."* π is the counter-case: *"Every time someone sees 3.1415927535890793, they know that it is π, and so they fail to scrutinize it. (Did you catch the single-digit error?)"* **"Magic Number" applies to any non-self-describing token**, including strings: `assertEquals(7777, Employee.find("John Doe")...)` → `assertEquals(HOURLY_EMPLOYEE_ID, Employee.find(HOURLY_EMPLOYEE_NAME)...)`. |
| **G26** | **Be Precise** | *"Expecting the first match to be the only match to a query is probably naive. Using floating point numbers to represent currency is almost criminal. Avoiding locks… because you don't think concurrent update is likely is lazy at best. Declaring a variable to be an `ArrayList` when a `List` will do is overly constraining. Making all variables protected by default is not constraining enough."* **Ambiguity and imprecision come from disagreement or laziness; eliminate both.** |
| **G27** | **Structure over Convention** | Naming conventions are good but **inferior to structures that force compliance**. A `switch` over nicely named enums is inferior to a base class with abstract methods — nobody is forced to write the switch the same way twice, but the compiler forces every derivative to implement the abstract methods. |
| **G28** | **Encapsulate Conditionals** | `if (shouldBeDeleted(timer))` beats `if (timer.hasExpired() && !timer.isRecurrent())`. |
| **G29** | **Avoid Negative Conditionals** | `if (buffer.shouldCompact())` beats `if (!buffer.shouldNotCompact())`. |
| **G30** | **Functions Should Do One Thing** | A function with multiple sections performing a series of operations does more than one thing. `pay()` that loops, tests payday, and pays → `pay()` → `payIfNecessary(e)` → `calculateAndDeliverPay(e)`. |
| **G31** | **Hidden Temporal Couplings** | Temporal coupling is often necessary — **hiding it is not.** `saturateGradient(); reticulateSplines(); diveForMoog(reason);` can be called out of order. Fix with a **bucket brigade**: each function produces what the next needs. *"You might complain that this increases the complexity of the functions, and you'd be right. But that extra syntactic complexity exposes the true temporal complexity of the situation."* |
| **G32** | **Don't Be Arbitrary** | *"If a structure appears arbitrary, others will feel empowered to change it. If a structure appears consistently throughout the system, others will use it and preserve the convention."* Example: a public class needlessly nested inside another; **public classes that are not utilities of another class belong at the top level of their package.** |
| **G33** | **Encapsulate Boundary Conditions** | *"We don't want swarms of `+1`s and `-1`s scattered hither and yon."* `level + 1` appearing twice → `int nextLevel = level + 1;` |
| **G34** | **Functions Should Descend Only One Level of Abstraction** | *"This may be the hardest of these heuristics to interpret and follow… humans are just far too good at seamlessly mixing levels of abstraction."* The `<hr>` example mixes "a rule has a size" with HTML tag syntax; extracting `HtmlTag` **caught a real bug** (missing XHTML closing slash). And the first attempt *still* mixed levels — **"when you break a function along lines of abstraction, you often uncover new lines of abstraction that were obscured by the previous structure."** |
| **G35** | **Keep Configurable Data at High Levels** | Defaults and config known at a high level must not be buried in low-level functions — pass them down as arguments. FitNesse parses command-line args on the first executable line, with `DEFAULT_PATH`, `DEFAULT_ROOT`, `DEFAULT_PORT`, `DEFAULT_VERSION_DAYS` at the top of `Arguments`. **"The lower levels of the application do not own the values of these constants."** |
| **G36** | **Avoid Transitive Navigation** | If A collaborates with B and B with C, users of A must not know about C — no `a.getB().getC().doSomething()`. The **Law of Demeter**; the Pragmatic Programmers call it *"Writing Shy Code."* **Why it matters architecturally:** interposing a `Q` between B and C would require finding and rewriting every `a.getB().getC()`. *"This is how architectures become rigid."* |

## Java (J1–J3)

| # | Smell | Rule |
|---|---|---|
| **J1** | **Avoid Long Import Lists by Using Wildcards** | Two or more classes from a package → `import package.*;`. **The real argument is coupling:** a specific import is a *hard dependency* (that class must exist); a wildcard just adds the package to the name search path, creating no true dependency. Caveats: useful for finding classes to mock in legacy code (rare, and IDEs can expand wildcards on command), and name conflicts across packages need specific imports. |
| **J2** | **Don't Inherit Constants** | *"This is a hideous practice!"* Constants hidden at the top of an inheritance hierarchy (`Employee implements PayrollConstants`) leave the reader hunting for where `TENTHS_PER_WEEK` came from. **Don't use inheritance to cheat the scoping rules of the language — use a static import.** |
| **J3** | **Constants versus Enums** | *"Now that enums have been added to the language, use them!"* The meaning of `int`s gets lost; the meaning of an enum cannot, because it belongs to a named enumeration. **Study the syntax carefully — enums can have methods and fields**, e.g. `HourlyPayGrade` with an abstract `rate()` implemented per constant. |

## Names (N1–N7)

| # | Smell | Rule |
|---|---|---|
| **N1** | **Choose Descriptive Names** | *"Names in software are 90 percent of what make software readable."* Meanings drift as software evolves — **frequently reevaluate**. The bowling example: `public int x()` with `q`, `z`, `kk`, `l[]` is a hodge-podge; `score()` with `isStrike(frame)`, `nextTwoBallsForStrike(frame)`, `isSpare(frame)` is *less complete* and yet immediately inferable. **"The power of carefully chosen names is that they overload the structure of the code with description."** |
| **N2** | **Choose Names at the Appropriate Level of Abstraction** | Don't name after the implementation. `Modem.dial(String phoneNumber)` / `getConnectedPhoneNumber()` breaks for hardwired or USB-switched modems → `connect(String connectionLocator)` / `getConnectedLocator()`. *"Each time you make a pass over your code, you will likely find some variable that is named at too low a level."* |
| **N3** | **Use Standard Nomenclature Where Possible** | Pattern names (`AutoHangupModemDecorator`), language conventions (`toString`), and the team's own **ubiquitous language** (Evans, *DDD*). *"Better to follow conventions like these than to invent your own."* |
| **N4** | **Unambiguous Names** | `doRename()` containing `renamePage()` tells the reader nothing about the difference. Better: `renamePageAndOptionallyAllReferences`. *"This may seem long, and it is, but it's only called from one place… its explanatory value outweighs the length."* |
| **N5** | **Use Long Names for Long Scopes** | `for (int i=0; i<n; i++)` in a 2-line method is perfectly clear and *"would be obfuscated if the variable `i` were replaced with something annoying like `rollCount`."* Short names lose meaning over long distances. |
| **N6** | **Avoid Encodings** | No `m_`, no `f`, no subsystem prefixes like `vis_`. *"Keep your names free of Hungarian pollution."* |
| **N7** | **Names Should Describe Side-Effects** | `getOos()` that also *creates* the stream should be `createOrReturnOos`. **Don't use a simple verb for a function that does more than that simple action.** |

## Tests (T1–T9)

| # | Smell | Rule |
|---|---|---|
| **T1** | **Insufficient Tests** | The common metric is *"that seems like enough."* **A test suite should test everything that could possibly break** — tests are insufficient so long as conditions remain unexplored or calculations unvalidated. |
| **T2** | **Use a Coverage Tool!** | Coverage reports gaps in your *strategy*. Most IDEs mark covered lines green and uncovered red, making it quick to find `if`/`catch` bodies never checked. |
| **T3** | **Don't Skip Trivial Tests** | *"They are easy to write and their documentary value is higher than the cost to produce them."* |
| **T4** | **An Ignored Test Is a Question about an Ambiguity** | When requirements are unclear, express the question as a commented-out or `@Ignore`d test. Which form depends on whether the ambiguity is about something that would compile. |
| **T5** | **Test Boundary Conditions** | *"We often get the middle of an algorithm right but misjudge the boundaries."* |
| **T6** | **Exhaustively Test Near Bugs** | **Bugs congregate.** Found one in a function? Test that function exhaustively — *"you'll probably find that the bug was not alone."* |
| **T7** | **Patterns of Failure Are Revealing** | Diagnose by finding patterns in *how* tests fail: all inputs over five characters fail; any negative second argument fails. *"Sometimes just seeing the pattern of red and green on the test report is enough to spark the 'Aha!'"* An argument for making test cases as complete and well-ordered as possible. |
| **T8** | **Test Coverage Patterns Can Be Revealing** | What the *passing* tests do and don't execute gives clues to why the *failing* ones fail. |
| **T9** | **Tests Should Be Fast** | *"A slow test is a test that won't get run. When things get tight, it's the slow tests that will be dropped from the suite."* |

---

## How to use this catalogue

- **As a review checklist**: walk C → E → F → G → J → N → T over a diff.
- **As a vocabulary**: cite the tag in review comments (`[G31] hidden temporal coupling`)
  the way Ch15 and Ch16 do throughout.
- **As a refactoring prompt**: when something feels wrong but you can't name it, scan the
  G-series — most code smells live there.
- **Appendix C** of the book cross-references every heuristic to where it is discussed
  in the text.

## The highest-leverage entries

If you only internalize a handful: **G5 (Duplication)**, **G30 (Do One Thing)**,
**G34 (One Level of Abstraction)**, **N1 (Descriptive Names)**, **C5 (Commented-Out
Code)**, **G25 (Magic Numbers)**, **F3/G15 (Flag & Selector Arguments)**,
**G23 (Polymorphism over Switch)**, **T1/T5 (Insufficient Tests, Boundaries)**.

## Connects To
- **Every chapter** — this is the book's index in heuristic form.
- **Ch15 (JUnit Internals)** and **Ch16 (SerialDate)**: each refactoring step there cites
  a tag from here; read them together to see the heuristics applied.
- **Fowler, *Refactoring***; **Hunt & Thomas, *The Pragmatic Programmer***; **GoF**;
  **Beck, *Smalltalk Best Practice Patterns* / *Implementation Patterns***;
  **Martin, *PPP*** (SOLID); **Evans, *Domain Driven Design*** (ubiquitous language).
