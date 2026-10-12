# Chapter 3: Comparison

## Core Idea
PHP converts types when it compares loosely, so **compare with `===` / `!==`, which check type and value**, and replace `isset()` ladders with the **null coalescing operator `??`**. This whole section has no counterpart in the JavaScript parent — it exists because PHP's type juggling is a daily hazard.

## Frameworks Introduced
- **Use identical comparison**: "The simple comparison will convert the string into an integer." "The identical comparison will compare type and value."
  - When to use: every equality test, by default. Reach for `==` only when you deliberately want PHP's conversion rules — and say so.
  - How: `!=` → `!==`, `==` → `===`. The same applies to functions that compare internally: `in_array($needle, $haystack, true)` (the guide's Ch 2 example passes the `true`).
  - Why it works: with `$a = '42'` and `$b = 42`, `$a != $b` is **false** — loose comparison converts the numeric string and finds them equal — while `$a !== $b` is **true**, because a string is not an integer. In the guide's words, "The string `42` is different than the integer `42`."
- **Null coalescing operator**: "syntactic sugar for the common case of needing to use a ternary in conjunction with `isset()`. It returns its first operand if it exists and is not `null`; otherwise it returns its second operand." Introduced in PHP 7.
  - When to use: reading optional input — request arrays, config keys, optional array offsets — with a fallback.
  - How: chain it. `$name = $_GET['name'] ?? $_POST['name'] ?? 'nobody';` replaces an `if (isset(…)) / elseif (isset(…)) / else` ladder of seven lines.
  - Also used inside the guide's `Configuration::get()` (Ch 4): `return $this->configuration[$key] ?? null;`.

## Key Concepts
- **Loose comparison (`==`, `!=`)** — compares after type juggling; `'42' == 42` is true.
- **Identical comparison (`===`, `!==`)** — true only if both type and value match.
- **Type juggling** — PHP's implicit conversion between strings, numbers, booleans and null during comparison and arithmetic.
- **Null coalescing (`??`)** — returns the left operand if it is set and not `null`, otherwise the right; never raises an undefined-index notice.
- **Short ternary (`?:`)** — returns the left operand if it is *truthy*; appears in the guide's "Not bad" default-argument example (Ch 4) and is **not** the same as `??`.

## Mental Models
- **Default to `===`; treat `==` as a deliberate, commented exception.** The reader of `==` must run PHP's conversion table in their head.
- **`??` asks "is it there?"; `?:` asks "is it truthy?".** Pick by the question you mean: `'0'`, `''`, `0` and `[]` survive `??` but fall through `?:`.
- **A chain of `??` is a priority list.** Read left to right: first source that has a value wins, the last operand is the default.

## Anti-patterns
- **`==` / `!=` on mixed types**: the branch silently means something other than it says.
- **`in_array()` / `array_search()` without the strict flag**: the same loose comparison, hidden inside a function call.
- **`isset()` ladders for fallbacks**: seven lines and three branches for what `??` says in one expression.
- **Using `?:` where `??` was meant**: a legitimate `'0'` or empty string gets replaced by the default.

## Code Examples
```php
$a = '42';
$b = 42;

if ($a !== $b) {
    // The expression is verified
}
```
- **What it demonstrates**: the guide's "Good" case. `!==` sees a `string` and an `int` and reports them different, which is the truth. The loose `!=` version reports them equal, so its branch never runs. (The source's own comment on the loose version, "The expression will always pass", is best read as "the comparison silently passes as equal".)

```php
// Bad
if (isset($_GET['name'])) {
    $name = $_GET['name'];
} elseif (isset($_POST['name'])) {
    $name = $_POST['name'];
} else {
    $name = 'nobody';
}

// Good
$name = $_GET['name'] ?? $_POST['name'] ?? 'nobody';
```
- **What it demonstrates**: `??` collapses an `isset()` ladder into a single prioritized expression.

## Reference Tables

| Expression | Result | Why |
|---|---|---|
| `'42' == 42` | `true` | numeric string converted, values equal |
| `'42' != 42` | `false` | the guide's "Not good" case |
| `'42' === 42` | `false` | types differ |
| `'42' !== 42` | `true` | the guide's "Good" case |
| `in_array('42', [42])` | `true` | loose by default |
| `in_array('42', [42], true)` | `false` | strict flag |

| Operator | Falls back when the left side is… | Notice on missing key? | Use for |
|---|---|---|---|
| `??` | unset or `null` | no | optional input, config lookups |
| `?:` | falsy (`null`, `false`, `0`, `'0'`, `''`, `[]`) | yes, if the key is missing | "empty means use the default" |
| `isset() ? … : …` | unset or `null` | no | pre-PHP 7 code; replace with `??` |

Background beyond the guide: PHP 8.0 changed how a number compares loosely with a *non-numeric* string (`0 == 'foo'` was `true` in PHP 7 and is `false` in PHP 8), while `'42' == 42` is `true` in both. Loose comparison results can differ across versions; `===` results never do — one more reason for the rule.

## Worked Example
Reading an optional request parameter, three ways:

1. **`isset()` ladder** (the guide's Bad): correct, but seven lines and three branches; adding a third source means another `elseif`.
2. **Short ternary** — `$name = $_GET['name'] ?: 'nobody';`: shorter, but wrong twice. A missing key raises an "undefined index" notice (warning in PHP 8), and a user who submits `name=0` gets `'nobody'`.
3. **Null coalescing** (the guide's Good): `$name = $_GET['name'] ?? $_POST['name'] ?? 'nobody';` — no notice, no truthiness surprise, and a third source is one more `??`.

## Key Takeaways
1. **Use `===` and `!==` by default**; `'42' != 42` is `false` in PHP.
2. **Pass `true` as the strict flag** to `in_array()` and friends.
3. **Replace `isset()` ladders with chained `??`**, read as a priority list ending in the default.
4. **Don't confuse `??` with `?:`** — one tests presence, the other truthiness.

## Connects To
- **Ch 2**: `in_array(strtolower($day), $openingDays, true)` applies the strict flag.
- **Ch 4**: the default-argument rule's "Not bad" rung uses `?:`; `Configuration::get()` uses `??`.
- **Ch 5**: type declarations attack the same problem — type juggling — at the function boundary instead of at the comparison.
- **PHP manual, Comparison Operators**: the full loose-comparison table the guide links to.
