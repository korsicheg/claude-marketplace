# Chapter 11: Comments

## Core Idea
"**Comments are an apology, not a requirement.** Good code _mostly_ documents itself." Comment only genuine **business logic complexity** — and let version control carry everything you were tempted to leave behind.

## Frameworks Introduced
- **Only comment things that have business logic complexity**: the single test for whether a comment earns its place.
  - When to use: before writing any comment.
  - How: if the comment restates what the code says, delete the comment. If it explains *why* a non-obvious operation is necessary, keep it.
  - The surviving example: `// Convert to 32-bit integer` above `hash &= hash;` — the code is a bitwise idiom whose *purpose* is genuinely not self-evident.
- **Don't leave commented out code in your codebase**: "Version control exists for a reason. Leave old code in your history."
  - When to use: every time you comment out a line "just in case".
  - How: delete it. Git has it.
- **Don't have journal comments**: no changelog blocks at the top of functions.
  - When to use: whenever you're about to append a dated line to a header comment.
  - How: "Use `git log` to get history!" The version control system already records author, date, and the actual diff — the journal comment records a lossy summary that drifts from reality.
- **Avoid positional markers**: no `////////` banner separators.
  - When to use: when tempted to visually section a file.
  - How: "Let the functions and variable names along with the proper indentation and formatting give the visual structure to your code." If a file needs banners to be navigable, the problem is the file, not the absence of banners.

## Key Concepts
- **Comment as apology** — the framing: a comment concedes the code failed to explain itself.
- **Self-documenting code** — code whose names and structure make intent legible without prose.
- **Business logic complexity** — domain or algorithmic subtlety that no naming can express; the only justified comment.
- **Commented-out code** — dead code wearing a disguise; see Ch 3's "Remove dead code".
- **Journal comment** — a dated changelog block inside the source (`2016-12-20: Removed monads...`).
- **Positional marker** — a `////////` banner used to fake structure.
- **`git log`** — the actual, authoritative history; the replacement for journal comments.

## Mental Models
- **Think of every comment as a small admission of defeat.** Sometimes defeat is correct — the bitwise hash trick — but reach for a better name first.
- **Use "does this restate the code?" as the delete test.** `// The hash` above `let hash = 0` restates. `// Convert to 32-bit integer` above `hash &= hash` explains.
- **Comment the *why*, never the *what*.** The what is already present, in a language the machine checks; the why is the thing that gets lost.
- **Think of `git` as the comment you don't have to maintain.** Journal comments and commented-out code both duplicate what version control already stores — and unlike git, they silently rot.
- **Banner separators are a smell about file size.** If structure needs drawing, extract instead of decorate.

## Anti-patterns
- **Line-by-line narration**: `// The hash`, `// Length of string`, `// Loop through every character in data`, `// Get character code.`, `// Make the hash` — five comments that say what five obvious lines already say.
- **Commented-out code**: `doStuff(); // doOtherStuff(); // doSomeMoreStuff();` — nobody will ever uncomment it, and nobody dares delete it.
- **Journal comments**: a dated block above `combine(a, b)` listing four historical changes — information git holds more accurately.
- **Positional markers**: `////////////////////////////////////////` banners around "Scope Model Instantiation" — "They usually just add noise."
- **Comments compensating for bad names**: fix the name (Ch 2) instead of annotating it.
- **Stale comments**: the failure mode all of the above share — prose is not checked by anything and drifts from the code beneath it.

## Code Examples
Narration vs. the one comment that earns its place:

```javascript
// Bad
function hashIt(data) {
  // The hash
  let hash = 0;

  // Length of string
  const length = data.length;

  // Loop through every character in data
  for (let i = 0; i < length; i++) {
    // Get character code.
    const char = data.charCodeAt(i);
    // Make the hash
    hash = (hash << 5) - hash + char;
    // Convert to 32-bit integer
    hash &= hash;
  }
}

// Good
function hashIt(data) {
  let hash = 0;
  const length = data.length;

  for (let i = 0; i < length; i++) {
    const char = data.charCodeAt(i);
    hash = (hash << 5) - hash + char;

    // Convert to 32-bit integer
    hash &= hash;
  }
}
```
- **What it demonstrates**: six comments become one. The survivor is the only line whose *purpose* isn't recoverable from reading it — `hash &= hash` looks like a no-op unless you know it truncates to 32 bits.

Journal comments — delete the block, keep the function:

```javascript
// Bad
/**
 * 2016-12-20: Removed monads, didn't understand them (RM)
 * 2016-10-01: Improved using special monads (JP)
 * 2016-02-03: Removed type-checking (LI)
 * 2015-03-14: Added combine with type-checking (JR)
 */
function combine(a, b) {
  return a + b;
}

// Good
function combine(a, b) {
  return a + b;
}
```
- **What it demonstrates**: every fact in that block — author, date, what changed — is in `git log`, where it is accurate and cannot be forgotten on the next edit.

Positional markers — let structure come from names:

```javascript
// Bad
////////////////////////////////////////////////////////////////////////////////
// Scope Model Instantiation
////////////////////////////////////////////////////////////////////////////////
$scope.model = { menu: "foo", nav: "bar" };

////////////////////////////////////////////////////////////////////////////////
// Action setup
////////////////////////////////////////////////////////////////////////////////
const actions = function() {};

// Good
$scope.model = { menu: "foo", nav: "bar" };

const actions = function() {};
```

## Reference Tables

The four rules and their replacements:

| Anti-pattern | Why it's wrong | Replacement |
|---|---|---|
| Narrating comments | Restates self-evident code; rots silently | Better names (Ch 2) |
| Commented-out code | Dead code nobody will restore or delete | `git` history — just delete it |
| Journal comments | Lossy, manual duplicate of the commit log | `git log` |
| Positional markers | Noise; fakes structure | Names, indentation, formatting (Ch 10) |

The keep/delete test:

| Comment | Verdict | Reason |
|---|---|---|
| `// The hash` above `let hash = 0` | Delete | Restates the code |
| `// Loop through every character` above a `for` | Delete | Restates the code |
| `// Convert to 32-bit integer` above `hash &= hash` | **Keep** | Explains non-obvious intent |
| `// 2016-12-20: Removed monads (RM)` | Delete | `git log` has it |
| `// doOtherStuff();` | Delete | Dead code |
| `//////// Action setup ////////` | Delete | Noise |

## Worked Example
Run `hashIt` through the delete test line by line — this is the chapter's whole method in one pass.

| Comment | Code beneath it | Does the code already say this? | Verdict |
|---|---|---|---|
| `// The hash` | `let hash = 0;` | Yes — the variable is named `hash` | Delete |
| `// Length of string` | `const length = data.length;` | Yes — twice over, `length` and `.length` | Delete |
| `// Loop through every character in data` | `for (let i = 0; i < length; i++)` | Yes — it's a standard indexed loop | Delete |
| `// Get character code.` | `const char = data.charCodeAt(i);` | Yes — `charCodeAt` is the method's own name | Delete |
| `// Make the hash` | `hash = (hash << 5) - hash + char;` | Partly — assignment to `hash` is obvious; the *formula* isn't explained by the comment either | Delete |
| `// Convert to 32-bit integer` | `hash &= hash;` | **No** | **Keep** |

The last row is the interesting one. `hash &= hash` reads as a tautology — ANDing a value with itself. It is not: JavaScript's bitwise operators coerce to 32-bit signed integers, so the "no-op" is doing the truncation. Nothing in the syntax says that, and no rename can fix it, because the name isn't the unclear part — the *semantics of the operator* are.

**The generalizable test:** a comment survives when deleting it would lose information that isn't recoverable from the code. Note also that `// Make the hash` fails even though the line *is* cryptic — the comment doesn't explain the shift-and-subtract formula, it just labels it. A bad comment on a confusing line is still a bad comment.

**The corollary from Ch 2:** four of these five deletions were free because the names were already good (`hash`, `length`, `char`). When a comment is load-bearing because a name is poor, fix the name — don't keep the apology.

## Key Takeaways
1. Comments are an **apology**; good code mostly documents itself.
2. Comment only genuine **business logic complexity** — the *why*, never the *what*.
3. Delete a comment that restates the code; if the code needs the restatement, fix the names instead.
4. Never leave commented-out code — version control has it, and nobody will ever restore it.
5. No journal comments — `git log` is accurate, automatic, and doesn't rot.
6. No positional-marker banners — names, indentation, and formatting supply structure.
7. The survivor test: would deleting this lose information the code can't express? `// Convert to 32-bit integer` passes; almost nothing else does.

## Connects To
- **Ch 2 (Variables)**: good names are what make comments unnecessary — `MILLISECONDS_PER_DAY` retires `// What the heck is 86400000 for?`.
- **Ch 3 (Functions)**: "Remove dead code" is the same rule as "don't leave commented out code"; "Encapsulate conditionals" replaces an explanatory comment with a named predicate.
- **Ch 10 (Formatting)**: positional markers are a formatting problem solved by structure, not decoration.
- **Ch 1 (Introduction)**: "readable" is the first of the 3 Rs — a file needing narration isn't readable yet.
