# Chapter 1: Introduction

## Core Idea
"Software engineering principles, from Robert C. Martin's book *Clean Code*, adapted for PHP. This is not a style guide. It's a guide to producing readable, reusable, and refactorable software in PHP." The guide is a port of Ryan McDermott's clean-code-javascript, so the fastest way to understand what is *PHP-specific* in it is to see where it keeps, reverses, adds to, or drops its parent's rules.

## Frameworks Introduced
- **The 3 Rs — readable, reusable, refactorable**: the quality bar every later rule serves.
  - When to use: whenever a proposed change needs justifying as "cleaner" rather than merely different.
  - How: name which of the three the change improves. If it improves none, it's taste — and taste belongs to the formatter, not to review.
- **Guidelines, not laws**: "Not every principle herein has to be strictly followed, and even fewer will be universally agreed upon. These are guidelines and nothing more, but they are ones codified over many years of collective experience by the authors of *Clean Code*."
  - When to use: when a rule fights the problem in front of you.
  - How: deviate on purpose, with a reason you could state in a code review — never by accident.
- **The PHP 7.1 floor**: "Although many developers still use PHP 5, most of the examples in this article only work with PHP 7.1+."
  - Why 7.1: the snippets rely on `void` and nullable (`?string`) return types and on skipping list destructuring (`[, $city, $zipCode] = $matches`) — all PHP 7.1 additions. The repo's `composer.json` declares `php >=7.2`, and its CI runs on PHP 8.0.
  - Consequence: nothing from PHP 7.4 onward appears in the examples — properties are untyped (`private $name;`), there is no constructor promotion, no `readonly`, no enums, no `match`.
- **Not a style guide — but linted**: the repository runs `vendor/bin/ecs check-markdown README.md` in CI, applying Symplify's Easy Coding Standard sets `COMMON`, `CLEAN_CODE`, `PSR_12` and `SYMPLIFY` to every PHP block in the README.
  - The config deliberately skips `DeclareStrictTypesFixer`, `StrictComparisonFixer` and `BlankLineAfterOpeningTagFixer` — so no snippet carries `declare(strict_types=1)`, and the deliberately loose `!=` example in the Comparison section survives the fixer.
  - Unlike the Python sibling, whose snippets are executed and type-checked, these snippets are **style-checked only**. Several examples would not run as written (Ch 4, Ch 7 and Ch 8 note where).

## Key Concepts
- **Clean Code** — Robert C. Martin's 2008 book; the source of the principles this guide adapts.
- **3 Rs** — readable, reusable, refactorable: the guide's stated quality standard.
- **Bad / Not bad / Good ladder** — the guide's teaching unit; some rules add "Not good", "Bad too" or "Very good" rungs.
- **Port lineage** — "Inspired from clean-code-javascript"; the section skeleton, many examples, and even the MIT licence's copyright line (Ryan McDermott, 2016) come from the parent.
- **ECS (Easy Coding Standard)** — the Symplify tool that lints the README's PHP blocks against PSR-12 and related rule sets.
- **PSR-12** — the PHP-FIG extended coding style; formatting is delegated to it, not argued in the guide.

## Mental Models
- **Think of the guide as clean-code-javascript re-cut for PHP.** Same skeleton (Variables → Functions → Objects → Classes → SOLID → DRY); PHP-specific rules added; the parent's testing, concurrency, error-handling, formatting and comments sections dropped.
- **Use the ladder, not just the endpoints.** The middle rung ("Not bad", "Bad too") usually names the most common real-world mistake — the half-refactor.
- **Prefer the language feature over the convention.** Where JavaScript needed discipline (closures for privacy, `typeof` guards), PHP has keywords — `private`, `final`, `interface`, type declarations — and the guide reaches for them.

## Anti-patterns
- **Treating the guide as a style guide**: it explicitly isn't one; brace placement and spacing are PSR-12's job.
- **Treating every rule as mandatory**: the authors disclaim universal agreement up front.
- **Copying snippets verbatim into production**: they are lint-clean, not run — check the notes in Ch 5 and Ch 8.

## Reference Tables

**Adaptation map — how the PHP guide relates to its JavaScript parent**

| Kind | Rules | Chapter |
|---|---|---|
| **Added for PHP** | Use identical comparison · Null coalescing operator · Avoid nesting too deeply and return early (×2) · Don't use a Singleton pattern · Prefer final classes | Ch 3, Ch 2, Ch 4, Ch 7 |
| **Reversed** | JS "Use method chaining" → PHP **"Avoid fluent interfaces"** | Ch 7 |
| **Reinterpreted** | "Don't write to global functions" — JS: don't patch `Array.prototype`; PHP: don't define global helpers like `config()` · "Avoid type-checking (part 2)" — JS: use TypeScript; PHP: use type declarations or strict mode · "Make objects have private members" — JS: closures; PHP: the `private` keyword, with `protected` argued to be as exposed as `public` | Ch 4, Ch 5, Ch 6 |
| **Kept** | naming, searchable names, explanatory variables, mental mapping, unneeded context, default arguments, ≤2 arguments, function names, one level of abstraction, flags, side effects, encapsulate/negative/avoid conditionals, type-checking (part 1), dead code, encapsulation, composition over inheritance, SOLID, DRY | Ch 2–Ch 9 |
| **Dropped** | "Functions should do one thing" as its own rule (still cited inside two others) · don't mutate arguments · favor functional programming · don't over-optimize · ES6 classes · Testing · Concurrency · Error handling · Formatting · Comments | — |

**Section → chapter map**

| README section | Rules | Chapter |
|---|---|---|
| Introduction | — | Ch 1 |
| Variables | 9 | Ch 2 |
| Comparison | 2 | Ch 3 |
| Functions (first half) | 8 | Ch 4 |
| Functions (second half) | 6 | Ch 5 |
| Objects and Data Structures | 2 | Ch 6 |
| Classes | 3 | Ch 7 |
| SOLID | 5 | Ch 8 |
| Don't repeat yourself (DRY) | 1 | Ch 9 |

## Worked Example
How one rule changes shape across the port — **type-checking primitives**:

- **JavaScript parent**: guarding `typeof val1 === "number"` is noise; the remedy offered is a *different language* — "use TypeScript".
- **PHP guide**: the same guard (`is_numeric($val1)`) is noise, but the remedy is *already in the language*:

```php
// Bad
function combine($val1, $val2): int
{
    if (! is_numeric($val1) || ! is_numeric($val2)) {
        throw new Exception('Must be of type Number');
    }

    return $val1 + $val2;
}

// Good
function combine(int $val1, int $val2): int
{
    return $val1 + $val2;
}
```

The lesson generalizes across the whole guide: **when PHP has a keyword for a JavaScript convention, use the keyword.** `private` replaces closure privacy (Ch 6), `interface` replaces implicit duck-typed contracts (Ch 8), `final` replaces "please don't extend this" (Ch 7), and type declarations replace hand-written guards (Ch 5). The one thing the guide stops short of is saying *which* typing mode to run in — it mentions "strict mode" but never shows `declare(strict_types=1)` (Ch 5).

## Key Takeaways
1. The bar is **readable, reusable, refactorable** — not consistency with a style.
2. These are **guidelines**; deviate deliberately and say why.
3. Examples target **PHP 7.1+**; nothing from 7.4 or 8.x appears, so modernize the syntax, not the principle.
4. Formatting is **delegated to tooling** (ECS / PSR-12), which the repo itself runs on the README.
5. Read the guide as **clean-code-javascript adapted**: the PHP-only rules (comparison, return early, Singleton, final, private-by-default, no fluent interfaces) are where its distinct value lies.

## Connects To
- **Ch 3 (Comparison)** and **Ch 7 (Classes)**: the largest PHP-only additions; **Ch 6** for the `protected` argument.
- **Ch 5**: the type-checking rule, where the port's reinterpretation is clearest.
- **clean-code-javascript**: the parent document; every "Kept" rule above has its original there.
- **PSR-12 / ECS**: the formatting authority this guide defers to.
