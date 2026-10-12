# Chapter 1: Introduction

## Core Idea
Robert C. Martin's *Clean Code* principles, adapted for Swift: "This is not a style guide. It is a guide for producing readable, reusable, and refactorable code in Swift." The rules are a **criterion for evaluating the quality of Swift code that you and your team produce** — guidelines, not laws.

## Frameworks Introduced
- **The 3 Rs (readable, reusable, refactorable)**: the stated quality bar. The phrase links to the author's companion repo, *3rs-of-software-architecture-for-iOS*.
  - When to use: as the tie-breaker when two designs both compile and pass tests.
  - How: name which R a change improves. If it improves none, it's taste, not cleanliness.
- **Guidelines, not laws**: "It is not necessary to strictly follow all the principles demonstrated, and even less are they a universal consensus." They are "codified over many years of collective experience by the authors of *Clean Code*."
  - When to use: whenever a rule collides with a real constraint (an Apple framework's API shape, performance, a deadline).
  - How: override deliberately and say why; never by accident.
- **Wet clay — draft, then refine with peers**: "Each portion of code starts as a draft, like wet clay being shaped into its final form. Finally, we carve out imperfections by reviewing with our peers. Don't feel guilty about the first drafts that still need improvement."
  - When to use: on every first draft, and in code review.
  - How: get it working, then apply these rules as a refinement pass; review is where the carving happens.
- **Bad → named consequences → Good → named benefits**: the guide's distinctive format. Most rules show a `Bad:` and a `Good:` Swift snippet, and many attach bolded consequence labels — *Unclear Variable Name*, *Potential for Mistakes*, *Risk of Runtime Errors* on the bad side; *Clear Intent*, *Improved Testability*, *Easier Maintenance* on the good side.
  - When to use: when reviewing — the labels are a vocabulary for review comments.
  - How: name the consequence, not just the rule ("this force-unwrap is a *Risk of Runtime Errors*").

## Key Concepts
- **Readable** — a reader can reconstruct intent without running the code.
- **Reusable** — the unit can be called from a second site unchanged.
- **Refactorable** — the unit can change without a cascade of edits elsewhere.
- **Not a style guide** — yet, unlike the Python adaptation, it *does* carry a formatting chapter (Ch 10), framed as "let the tools handle it".
- **Adaptation lineage** — the repository's MIT LICENSE reads "Copyright (c) 2017 Ryan McDermott, Felipe Santos", the line of the Brazilian-Portuguese translation of Ryan McDermott's *clean-code-javascript*; the PR template is in Portuguese and asks that suggestions also go to "the original repository". The Swift text was built on that JavaScript guide.
- **JavaScript carryover** — a sentence or snippet that survived the port unchanged and is false or meaningless in Swift (see the table below).
- **Author** — Matheus Gois (GitHub: MaatheusGois), sole committer, December 2023 – July 2024.

## Mental Models
- **Think of the rules as detectors for one root rule**: "Functions should do one thing" (Ch 3). Flags, a third argument, `if`/`switch` on a type string, side effects — each is a symptom.
- **Read the lesson from the code, not the carried-over prose.** Where the prose and the Swift snippet disagree, the snippet usually holds the Swift lesson (e.g., "Swift does not have types" sits above a Good example that accepts a protocol-typed parameter — Ch 4).
- **Treat every snippet as illustrative, not compilable.** Several Good examples don't build as written (Ch 4, 7, 8, 9 flag each one). Copy the shape, then let the compiler check it.

## Reference Tables

What the source covers and leans on:

| Property | Value |
|---|---|
| Size | ~8,850 words, 11 sections, 45 rule headings, 89 Swift snippets |
| Swift features used | `struct`/`class`/`enum`/`protocol`, optionals with `if let`/`guard`, `??`, closures and `$0`, `map`/`filter`/`reduce`, `extension`, `private`, `@discardableResult`, `do`/`try`/`catch`, `async`/`await`, `Task` |
| Newest feature | `async`/`await` (Swift 5.5) |
| Frameworks in examples | Foundation, UIKit (`UIFont`, `UIColor`, `UIView`), XCTest |
| Tools named | SwiftLint, Google Swift Style Guide, SonarQube, apple/swift-collections |

JavaScript carryovers to recognize (each is handled in its chapter):

| Rule | Carried-over text | What holds in Swift |
|---|---|---|
| Searchable names (Ch 2) | `setTimeout(blastOff, 86400000)`; constants "in uppercase letters" | No `setTimeout`; the snippet itself uses lowerCamelCase `millisecondsPerDay` |
| Default arguments (Ch 3) | defaults apply only to "nullable" args; "falsy" `""`, `false`, `0` | Swift has no falsy values; a default applies when the argument is omitted |
| Side effects 2 (Ch 4) | "objects/arrays are passed by reference" | `Array` is a value type; class instances are the shared references |
| Global functions (Ch 4) | `Array.prototype` | Swift `extension`; the Good snippet subclasses `Array`, a struct, which can't compile |
| Type checking 1–2 (Ch 4) | "Swift does not have types" (part 1); "you should consider using TypeScript" (part 2) | Swift is statically typed; accept a protocol instead of `Any` |
| ISP / DIP (Ch 8) | "duck typing prevails"; "Swift doesn't have interfaces"; "AngularSwift" | Protocol conformance is declared and compiler-checked |
| OCP, Concurrency (Ch 7, 9) | `Promise<Response>`, `.then` | Not in the standard library; `async`/`await` is the native form |

## Worked Example
How to read one rule — "Use meaningful and pronounceable variable names" (Ch 2) — in the guide's own format.

**Bad**, with the consequences the guide names:

```swift
let currentDateStr = DateFormatter.localizedString(from: Date(), dateStyle: .short, timeStyle: .none)
```

- *Unclear Variable Name* — the `Str` suffix makes the name about its type, not its meaning.
- *Inconsistent Naming* — "Str" invites `currentDateInt`, `currentDateObj` elsewhere.
- *Potential for Mistakes* — a later reader may treat it as a `Date`.

**Good**, with the benefits:

```swift
let currentDate = DateFormatter.localizedString(from: Date(), dateStyle: .short, timeStyle: .none)
```

- *Clear Variable Name*, *Enhanced Readability*, *Easier Maintenance*.

**Reading it critically**: the value is still a `String`. In Swift the type lives in the declaration (`let currentDate: String`, or Xcode's Quick Help), so the name is free to carry meaning; but the Bad side's *Potential for Mistakes* label is a fair warning about the Good name too. The transferable rule is "no type tags in names"; pick the noun that says what the value *is* to its reader.

## Anti-patterns
- **Treating the guide as a style guide**: it says it isn't. Formatting gets its own tool-driven chapter.
- **Strict, unexamined application**: "even less are they a universal consensus."
- **Copy-pasting the snippets into production**: several don't compile, and some carry JavaScript assumptions. Take the shape; let `swiftc` check it.
- **Feeling guilty about first drafts**: the guide explicitly calls drafts wet clay.

## Key Takeaways
1. Judge Swift code by **readable, reusable, refactorable**; name the R a change improves.
2. These are **guidelines**; override with a stated reason.
3. **Draft, then refine** — review is where the carving happens.
4. Use the guide's **consequence labels** as review vocabulary.
5. **Recognize JavaScript carryovers** and apply the Swift lesson instead.
6. **Compile every snippet you borrow.**

## Connects To
- **Ch 2–4**: naming and functions, the bulk of the guide (23 of 45 rules).
- **Ch 3**: "Functions should do one thing", the root rule the others detect.
- **Ch 7–8**: SOLID, where protocols carry the Swift-specific weight.
- **Ch 10**: the formatting chapter that a "not a style guide" document still includes.
- **`clean-code-javascript`**: the guide this one was ported from, through its Brazilian-Portuguese translation; see a carried-over rule in its original form there.
- **`clean-code-java`**: Martin's book, which every rule here descends from.
