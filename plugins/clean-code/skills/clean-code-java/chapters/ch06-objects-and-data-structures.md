# Chapter 6: Objects and Data Structures

## Core Idea
**Objects hide their data behind abstractions and expose functions that operate on it.
Data structures expose their data and have no meaningful functions.** These are virtual
opposites, and the choice between them is a real design decision — not a default.
Blithely adding getters and setters makes the choice for you, badly.

## Frameworks Introduced

- **Data Abstraction** — hiding implementation is *not* putting a layer of functions in
  front of variables; it is exposing an abstract interface that lets users manipulate the
  **essence** of the data without knowing its form.
  - When to use: every time you are about to generate getters and setters.
  - How: ask what the caller actually needs to know, then express *that*. Not
    `getFuelTankCapacityInGallons()` + `getGallonsOfGasoline()`, but
    `getPercentFuelRemaining()`.
  - Test: from the interface alone, can a reader tell how the data is stored? If yes,
    you exposed implementation.

- **Data/Object Anti-Symmetry** — the central law of the chapter:
  > Procedural code (code using data structures) makes it easy to **add new functions**
  > without changing the existing data structures. OO code makes it easy to **add new
  > classes** without changing existing functions.
  >
  > Procedural code makes it hard to **add new data structures** because all the
  > functions must change. OO code makes it hard to **add new functions** because all
  > the classes must change.
  - **The things that are hard for OO are easy for procedures, and vice versa.**
  - How to choose: *will this part of the system grow mostly new types, or mostly new
    operations?* New types → objects and polymorphism. New operations → data structures
    and procedures.

- **The Law of Demeter** — a module should not know about the innards of the objects it
  manipulates. Precisely, a method `f` of class `C` should only call methods of:
  1. `C` itself
  2. an object created by `f`
  3. an object passed as an argument to `f`
  4. an object held in an instance variable of `C`
  - **And it must not invoke methods on objects returned by any of those.**
  - Slogan: **talk to friends, not to strangers.**
  - **Crucial qualifier:** Demeter applies to *objects*, not data structures. If `ctxt`,
    `Options`, and `ScratchDir` are pure data structures, they naturally expose their
    structure and Demeter does not apply. Accessor functions are what make this
    ambiguous — `ctxt.options.scratchDir.absolutePath` would not even prompt the question.

- **Hiding Structure (tell, don't ask)** — if `ctxt` is a real object, stop asking it
  about its internals and tell it to do the job.

## Reference Table: objects vs data structures

| | **Object** | **Data structure** |
|---|---|---|
| Data | private, hidden | public (or bean-accessed), exposed |
| Functions | meaningful behavior | none significant |
| Easy to add | new **types** | new **functions** |
| Hard to add | new **functions** | new **types** |
| Law of Demeter | **applies** | does not apply |
| Canonical forms | domain objects, polymorphic hierarchies | DTO, bean, Active Record |

## Worked Example 1: concrete vs abstract Point

```java
// Concrete — clearly rectangular; forces independent manipulation of x and y.
public class Point {
    public double x;
    public double y;
}
```

```java
// Abstract — you cannot tell whether it is rectangular, polar, or neither.
public interface Point {
    double getX();
    double getY();
    void setCartesian(double x, double y);
    double getR();
    double getTheta();
    void setPolar(double r, double theta);
}
```

**What it demonstrates:** the abstract version also **enforces an access policy** — you
may read coordinates independently, but you must set them together, atomically. Note
Martin's sharper point: the concrete version would *still* expose implementation even if
`x` and `y` were private with single-variable getters and setters.

## Worked Example 2: the shape problem, both ways

**Procedural** — data structures plus a `Geometry` class holding all behavior:

```java
public class Square    { public Point topLeft; public double side; }
public class Rectangle { public Point topLeft; public double height; public double width; }
public class Circle    { public Point center;  public double radius; }

public class Geometry {
    public final double PI = 3.141592653589793;
    public double area(Object shape) throws NoSuchShapeException {
        if (shape instanceof Square) {
            Square s = (Square)shape;
            return s.side * s.side;
        } else if (shape instanceof Rectangle) {
            Rectangle r = (Rectangle)shape;
            return r.height * r.width;
        } else if (shape instanceof Circle) {
            Circle c = (Circle)shape;
            return PI * c.radius * c.radius;
        }
        throw new NoSuchShapeException();
    }
}
```

**Object-oriented** — polymorphic, no `Geometry` class:

```java
public class Square implements Shape {
    private Point topLeft;
    private double side;
    public double area() { return side*side; }
}
public class Circle implements Shape {
    private Point center;
    private double radius;
    public final double PI = 3.141592653589793;
    public double area() { return PI * radius * radius; }
}
```

**What it demonstrates — and this is the part usually missed:** the procedural version is
*not simply worse*. Add a `perimeter()` function and **no shape class changes**. Add a
new shape and **every function in `Geometry` changes**. The OO version has exactly the
inverse property. OO programmers "might wrinkle their noses… and they'd be right. But the
sneer may not be warranted."

(Visitor / dual-dispatch works around the OO side, but *"these techniques carry costs of
their own and generally return the structure to that of a procedural program."*)

## Worked Example 3: train wreck → tell, don't ask

```java
final String outputDir = ctxt.getOptions().getScratchDir().getAbsolutePath();
```

Splitting it up is the usual advice, and it helps readability [G36]:

```java
Options opts = ctxt.getOptions();
File scratchDir = opts.getScratchDir();
final String outputDir = scratchDir.getAbsolutePath();
```

**But that does not fix the Demeter violation** — the function still knows that a context
has options, which have a scratch dir, which has an absolute path. Look at what the
caller was actually *doing* with that path, many lines later:

```java
String outFile = outputDir + "/" + className.replace('.', '/') + ".class";
FileOutputStream fout = new FileOutputStream(outFile);
BufferedOutputStream bos = new BufferedOutputStream(fout);
```

The intent was to **create a scratch file**. So tell `ctxt` to do that:

```java
BufferedOutputStream bos = ctxt.createScratchFileStream(classFileName);
```

**What it demonstrates:** the fix for a train wreck is rarely mechanical splitting — it
is discovering the operation the caller actually wanted and moving it onto the object.
(Note also the mixed abstraction levels in the original: dots, slashes, file extensions
and `File` objects tangled together [G34][G6].)

## Anti-patterns

- **Hybrids** — half object, half data structure: significant functions *plus* public
  variables or public accessors that effectively publish the private state. **The worst
  of both worlds** — hard to add functions *and* hard to add data structures. They
  indicate a muddled design whose author is unsure whether they need protection from
  functions or from types. (Fowler's *Feature Envy* lives here.)
- **Reflexive getters and setters** — exposing private variables as if they were public.
  *"The worst option is to blithely add getters and setters."*
- **Business rules inside an Active Record** — an Active Record is a data structure with
  `save`/`find`, usually a direct translation of a database table. Putting business
  methods on it creates the hybrid. **Fix:** treat the Active Record as a data structure
  and put the business rules in separate objects that hide their data (those data
  probably being Active Record instances).
- **Train wrecks** — chained calls through objects you shouldn't know about [G36].
- **`getAbsolutePathOfScratchDirectoryOption()`** — the "fix" that explodes the object's
  method count. Neither that nor `getScratchDirectoryOption().getAbsolutePath()` feels
  good; both are symptoms of asking instead of telling.

## Mental Models

- **"Everything is an object" is a myth.** *Mature programmers know* this. Sometimes you
  really do want simple data structures with procedures operating on them.
- **Choose by axis of change.** Ask which axis your system will grow along, then pick the
  paradigm whose "easy" direction matches it. Good developers understand this *without
  prejudice* and choose per part of the system.
- **DTOs are legitimate and useful** — public variables, no functions — especially at
  boundaries: database rows, socket message parsing, the first of a chain of translation
  stages into real objects. The "bean" form (private fields + getters/setters) is
  quasi-encapsulation that *"seems to make some OO purists feel better but usually
  provides no other benefit."*
- **If you are asking an object for data, ask why.** What were you going to do with it?
  That is the method that belongs on the object.

## Key Takeaways

1. **Don't auto-generate accessors.** Decide first whether the thing is an object or a
   data structure.
2. **Abstract the essence, not the storage** — `getPercentFuelRemaining()`, not gallons.
3. **Pick the paradigm by expected change**: new types → OO; new operations → procedural.
4. **Obey the Law of Demeter for objects**; it does not apply to data structures.
5. **Tell, don't ask** — the cure for a train wreck is a new method on the object.
6. **Never build hybrids.** They lose both advantages at once.
7. **Keep business rules out of Active Records**; wrap them in real objects.

## Connects To
- **Ch3 (Functions)**: the `Geometry.area` switch is the same anti-pattern as the payroll
  switch — and the same polymorphic cure.
- **Ch10 (Classes)**: cohesion and SRP decide what data an object should hide.
- **Ch11 (Systems)**: DTOs at the boundaries of a system; separating construction from use.
- **Ch17 (Smells)**: G36 "Avoid Transitive Navigation", G34 "Functions Should Descend
  Only One Level of Abstraction", G6 "Code at Wrong Level of Abstraction".
- **Fowler, *Refactoring***: Feature Envy; the Visitor pattern from GoF.
