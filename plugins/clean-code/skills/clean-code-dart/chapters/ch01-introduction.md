# Chapter 1: Introduction

## Core Idea
Robert C. Martin's *Clean Code* principles, ported from Ryan McDermott's `clean-code-javascript` to Dart: a guide to producing **readable, reusable, and refactorable** Dart. It is explicitly **not a style guide** — formatting questions are handed to *Effective Dart* (Ch 10).

*(A short chapter: it states the standard and the lineage; the rules start in Ch 2.)*

## Frameworks Introduced
- **The 3 Rs (readable, reusable, refactorable)**: "This is not a style guide. It's a guide to producing readable, reusable, and refactorable software in Dart."
  - When to use: as the tie-breaker when two designs both work.
  - How: name which of the three a proposed change improves. If you can't name one, the change is taste, not cleanliness.
- **Guidelines, not laws**: "Not every principle herein has to be strictly followed, and even fewer will be universally agreed upon."
  - When to use: when a rule collides with a real constraint — a Flutter API shape, a performance budget, a deadline.
  - How: override deliberately, with a stated reason. Never override by accident.
- **The wet-clay model of drafts**: "Every piece of code starts as a first draft, like wet clay getting shaped into its final form." Imperfections are chiselled away in peer review.
  - When to use: in review, and on your own first drafts.
  - How: write the draft, then refactor against these rules. "Don't beat yourself up for first drafts that need improvement. Beat up the code instead!"

## Key Concepts
- **Readable** — a reader can reconstruct the intent without running the code or asking the author.
- **Reusable** — the unit can be called from a second site without modification.
- **Refactorable** — the unit can be changed without a cascade of edits elsewhere.
- **Not a style guide** — whitespace, line length and naming *case* are delegated to *Effective Dart*; this guide governs structure.
- **Adaptation lineage** — Martin's book (Java) → `ryanmcdermott/clean-code-javascript` → this Dart port, which the README opens by naming: "an adaptation of ryanmcdermott/clean-code-javascript for Dart language."
- **Translation** — the guide also exists in Brazilian Portuguese (`williambarreiro/clean-code-dart-pt`), and the English text keeps a little Portuguese (the journal-comment example in Ch 11, "setWidth e setHeight" in Ch 6).

## Mental Models
- **Think of the rules as detectors, not commandments.** Almost every rule downstream — "2 or fewer arguments", "no flags", "one level of abstraction", "avoid conditionals" — is a symptom test for the root rule in Ch 3: *functions should do one thing*.
- **Think of this as a port, not a rethink.** The Dart guide keeps the JavaScript guide's chapter order, most of its examples, and its voice. What is Dart-specific is *how* each rule is satisfied: named `required` parameters, `const`/`final`, the `_` prefix, cascades, `fold`, `Future`, `on Exception catch (e, s)`, `package:test`. Read each rule for the Dart mechanism it reaches for.
- **Use the language feature before the discipline.** Where JavaScript needed a convention (closures for privacy, `return this` for chaining), Dart has syntax (`_name`, `..`). The Dart guide consistently prefers the syntax.

## Anti-patterns
- **Treating the guide as a style guide**: it says it isn't one. Formatting arguments made under its banner waste the authority its structural rules earn (Ch 10: "DO NOT ARGUE over formatting").
- **Unexamined, mechanical application**: the text pre-empts this — these are "guidelines and nothing more".
- **Assuming JavaScript advice transfers unchanged**: the Dart port *reverses* at least two of its parent's rules — getters and setters (use them only when they add logic, Ch 4) and constant capitalization (`daysInWeek`, not `DAYS_IN_WEEK`, Ch 10).

## Reference Tables

| Property | Value | Evidence |
|---|---|---|
| Language | Dart, sound null safety | `required`, `String?`, `??`, `EmployeeTaxData?` throughout |
| Minimum version (inferred) | Dart 2.17+ | super-initializer parameters (`required super.name`, `super.width = 0`) |
| Era | Written Feb–Mar 2023, before Dart 3 | no records, patterns, `sealed`, or class modifiers |
| Test library | `package:test` | `import 'package:test/test.dart';` (Ch 7) |
| Style authority | *Effective Dart* | linked from the Formatting section (Ch 10) |
| Scope | Structure and design | "This is not a style guide." |
| Size | 39 rules in 10 sections | the JavaScript parent has 46; Ch 3 lists what was dropped |

The guide never states a Dart version; the table infers it from the syntax its examples use.

## Worked Example
The guide's own framing paragraph is the worked example: rules are a *touchstone*, not a gate.

> "Our craft of software engineering is just a bit over 50 years old, and we are still learning a lot. When software architecture is as old as architecture itself, maybe then we will have harder rules to follow. For now, let these guidelines serve as a touchstone by which to assess the quality of the Dart code that you and your team produce."

Applied in a review, that means a comment of the form *"this violates rule X; it costs us readability/reusability/refactorability because Y; fix or justify"* — never a bare *"rule X says so"*. The reviewer names the R; the author either fixes the code or states the constraint that justifies the exception.

## Key Takeaways
1. Judge Dart code on **readable, reusable, refactorable**; name the R a change improves before defending it.
2. These are **guidelines**: override them with a stated reason, never by accident.
3. It is **not a style guide** — use *Effective Dart* for style, and keep this guide for structure.
4. It is a **port of clean-code-javascript**: same rules, Dart mechanisms. Look for the mechanism.
5. Prefer the **language feature over the convention** where Dart has one (`_`, `..`, named parameters, `const`).
6. First drafts are clay. **Beat up the code, not yourself.**

## Connects To
- **Ch 3**: "Functions should do one thing" — the root rule the rest of the guide detects violations of.
- **Ch 4, Ch 10**: the two places the Dart port reverses its JavaScript parent.
- **Ch 6**: SOLID worked through Dart's `abstract class`, `implements`, and `@override`.
- ***Clean Code*** (Robert C. Martin, 2008): the source of every principle here, with Java examples.
- **`clean-code-javascript`**: the direct parent document, credited in the README's first line.
