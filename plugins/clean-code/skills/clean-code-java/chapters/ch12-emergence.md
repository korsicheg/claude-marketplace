# Chapter 12: Emergence
*by Jeff Langr*

## Core Idea
**Good design emerges from four simple rules, applied in priority order.** You don't need
to know SRP, DIP, and the pattern catalogue in advance — following the rules *pushes* you
toward them. *"Following the practice of simple design can and does encourage and enable
developers to adhere to good principles and patterns that otherwise take years to learn."*

## Frameworks Introduced

- **Kent Beck's Four Rules of Simple Design** — **given in order of importance**:

| # | Rule | What it forces |
|---|---|---|
| **1** | **Runs all the tests** | Testability → small, single-purpose classes → SRP; and low coupling → DIP, DI, interfaces |
| **2** | **Contains no duplication** | Extraction → new methods → new classes → reuse in the small |
| **3** | **Expresses the intent of the programmer** | Good names, small units, standard nomenclature, expressive tests |
| **4** | **Minimizes the number of classes and methods** | A brake on over-application of rules 2 and 3 |

  - **The priority order is the whole point.** Rule 4 never overrides rules 1–3:
    *"although it's important to keep class and function count low, it's more important
    to have tests, eliminate duplication, and express yourself."*

- **Rule 1's hidden mechanism** — this is the chapter's best argument, and it runs in two
  steps:
  1. **Making systems testable pushes toward SRP.** It is simply easier to test classes
     that conform to SRP, so the more tests you write, the more you push toward things
     that are simpler to test.
  2. **Tight coupling makes tests hard to write.** So the more tests you write, the more
     you reach for DIP, dependency injection, interfaces and abstraction.
  - *"Remarkably, following a simple and obvious rule that says we need to have tests and
    run them continuously impacts our system's adherence to the primary OO goals of low
    coupling and high cohesion. **Writing tests leads to better designs.**"*
  - And the corollary: *"a system that cannot be verified should never be deployed."*

- **The Refactoring Step (rules 2–4)** — once tests exist you are *empowered* to keep the
  code clean.
  - How: **for each few lines of code you add, pause and reflect on the new design. Did
    you just degrade it? If so, clean it up and run the tests to prove nothing broke.**
  - *"The fact that we have these tests eliminates the fear that cleaning up the code
    will break it."*
  - In this step you may apply the entire body of design knowledge: increase cohesion,
    decrease coupling, separate concerns, modularize, shrink functions and classes,
    choose better names.

- **Reuse in the Small** — the causal chain that makes duplication removal so valuable:
  extract commonality at a tiny level → start recognizing SRP violations → move the
  extracted method to another class → **that elevates its visibility** → someone else on
  the team spots a further abstraction and reuses it elsewhere → *"system complexity can
  shrink dramatically."*
  - **"Understanding how to achieve reuse in the small is essential to achieving reuse
    in the large."**

- **Template Method** [GoF] — the standard technique for removing *higher-level*
  duplication, where the algorithm is shared but one step varies.

## Worked Example 1: duplication of implementation

Not all duplication is textual. Two methods on a collection:

```java
int size() {}
boolean isEmpty() {}
```

`isEmpty` could track its own boolean while `size` tracks a counter — **two
implementations of one fact.** Tie one to the other:

```java
boolean isEmpty() {
    return 0 == size();
}
```

## Worked Example 2: eliminating three duplicated lines

**Before** — `scaleToOneDimension` and `rotate` share a three-line image-replacement dance:

```java
public void scaleToOneDimension(float desiredDimension, float imageDimension) {
    if (Math.abs(desiredDimension - imageDimension) < errorThreshold)
        return;
    float scalingFactor = desiredDimension / imageDimension;
    scalingFactor = (float)(Math.floor(scalingFactor * 100) * 0.01f);

    RenderedOp newImage = ImageUtilities.getScaledImage(
        image, scalingFactor, scalingFactor);
    image.dispose();
    System.gc();
    image = newImage;
}

public synchronized void rotate(int degrees) {
    RenderedOp newImage = ImageUtilities.getRotatedImage(image, degrees);
    image.dispose();
    System.gc();
    image = newImage;
}
```

**After:**

```java
public void scaleToOneDimension(float desiredDimension, float imageDimension) {
    if (Math.abs(desiredDimension - imageDimension) < errorThreshold)
        return;
    float scalingFactor = desiredDimension / imageDimension;
    scalingFactor = (float)(Math.floor(scalingFactor * 100) * 0.01f);
    replaceImage(ImageUtilities.getScaledImage(
        image, scalingFactor, scalingFactor));
}

public synchronized void rotate(int degrees) {
    replaceImage(ImageUtilities.getRotatedImage(image, degrees));
}

private void replaceImage(RenderedOp newImage) {
    image.dispose();
    System.gc();
    image = newImage;
}
```

**What it demonstrates:** *"Creating a clean system requires the will to eliminate
duplication, **even in just a few lines of code**."* Three lines were worth extracting —
and the extraction is what makes the SRP violation visible.

## Worked Example 3: Template Method on vacation policy

**Before** — two methods that differ in exactly one step:

```java
public class VacationPolicy {
    public void accrueUSDivisionVacation() {
        // code to calculate vacation based on hours worked to date
        // code to ensure vacation meets US minimums
        // code to apply vacation to payroll record
    }
    public void accrueEUDivisionVacation() {
        // code to calculate vacation based on hours worked to date
        // code to ensure vacation meets EU minimums
        // code to apply vacation to payroll record
    }
}
```

**After** — the algorithm lives once; subclasses fill the hole:

```java
abstract public class VacationPolicy {
    public void accrueVacation() {
        calculateBaseVacationHours();
        alterForLegalMinimums();
        applyToPayroll();
    }
    private void calculateBaseVacationHours() { /* ... */ }
    abstract protected void alterForLegalMinimums();
    private void applyToPayroll() { /* ... */ }
}

public class USVacationPolicy extends VacationPolicy {
    @Override protected void alterForLegalMinimums() { /* US specific logic */ }
}

public class EUVacationPolicy extends VacationPolicy {
    @Override protected void alterForLegalMinimums() { /* EU specific logic */ }
}
```

**What it demonstrates:** *"The subclasses fill in the 'hole' in the `accrueVacation`
algorithm, supplying the only bits of information that are not duplicated."*

## The four ways to be expressive (rule 3)

1. **Choose good names** — *"we want to be able to hear a class or function name and not
   be surprised when we discover its responsibilities."*
2. **Keep functions and classes small** — small units are easy to name, write and
   understand.
3. **Use standard nomenclature** — design patterns *"are largely about communication and
   expressiveness."* Naming a class after the pattern it implements (`Command`,
   `Visitor`) describes your design to other developers in one word.
4. **Write expressive unit tests** — *"a primary goal of tests is to act as documentation
   by example."* A reader should understand what a class is about from its tests.

**But the most important way is to try.** *"All too often we get our code working and
then move on to the next problem without giving sufficient thought to making that code
easy for the next person to read. Remember, the most likely next person to read the code
will be you."*

## Anti-patterns

- **Stopping when the code works** — the failure mode behind almost every violation here.
- **Pointless dogmatism producing class/method bloat** — an example each:
  - a coding standard insisting on **an interface for every class**;
  - developers insisting that **fields and behavior must always be separated** into data
    classes and behavior classes.
  - *"Such dogma should be resisted and a more pragmatic approach adopted."*
- **Taking rules 2 and 3 too far** — *"Even concepts as fundamental as elimination of
  duplication, code expressiveness, and the SRP can be taken too far."* Rule 4 exists
  precisely as this brake.
- **Deploying an unverifiable system.**

## Mental Models

- **Duplication is "the primary enemy of a well-designed system"** — additional work,
  additional risk, additional unnecessary complexity.
- **Near-duplicates are duplicates.** *"Lines of code that are similar can often be
  massaged to look even more alike so that they can be more easily refactored."* Make
  them identical first, then extract.
- **Design emerges; it isn't decreed.** The rules are a process, applied a few lines at
  a time, not a blueprint.
- **The economics argument for expressiveness:** the majority of a project's cost is
  long-term maintenance. Clearer code costs others less time to understand, which reduces
  defects and shrinks maintenance cost.
- **"Care is a precious resource."** Take pride in workmanship; spend a little time with
  each function and class.
- **Rules ≠ experience.** *"Is there a set of simple practices that can replace
  experience? Clearly not."* The rules are decades of experience crystallized — a
  shortcut to principles that otherwise take years to internalize.

## Key Takeaways

1. **Run all the tests** — testability is the forcing function for good design, not a
   consequence of it.
2. **Eliminate duplication relentlessly**, including implementation duplication and
   three-line duplication.
3. **Express intent** through names, small units, pattern nomenclature and readable tests.
4. **Minimize class and method count — but only after the first three rules are met.**
5. **Refactor every few lines**, under green tests, asking "did I just degrade this?"
6. **Extract small, then let the extraction reveal the missing class.**
7. **Use Template Method** when an algorithm is shared and one step varies.
8. **Resist dogma** — pragmatism beats rules applied without judgment.

## Connects To
- **Ch1 (Clean Code)**: Ron Jeffries cites these same four rules; this chapter is their
  expansion.
- **Ch9 (Unit Tests)**: rule 1 in full; tests enable the -ilities.
- **Ch3 (Functions)** / **Ch10 (Classes)**: the extraction loop that duplication removal
  drives.
- **Ch17 (Smells)**: G5 "Duplication" — *"the root of all evil in software"*.
- **Beck, *Extreme Programming Explained***; **GoF** (Template Method, Command, Visitor).
