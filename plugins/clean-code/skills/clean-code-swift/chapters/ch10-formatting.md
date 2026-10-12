# Chapter 10: Formatting

## Core Idea
"Formatting is subjective… The main idea is NOT to argue about formatting. There are tools that automate this process; let them handle it." The guide points to the **Google Swift Style Guide** and **SwiftLint**, then names six concrete whitespace rules: spaces over tabs, sparing blank lines, an 80-character line, consistent spacing around operators and commas, no excess whitespace, and SwiftLint enforcement. This section is the source's own — the JavaScript original's formatting rules (capitalization, caller/callee order) were replaced.

## Frameworks Introduced
- **Don't argue; automate**: "Like many of the rules here, there's no hard and fast rule you need to follow." "Most Swift code should follow the Google Swift Style Guide."
  - How: pick a style, encode it in a tool, and stop discussing it in review.
- **Use spaces instead of tabs**: "Despite the epic struggle between spaces and tabs, the important thing is to be consistent. Swift uses spaces, and it's a common practice in other Swift projects. Do the same."
- **Use blank lines effectively**: "Separating code blocks with blank lines can make the code more readable and organized. However, excessive blank lines can have the opposite effect, creating a sense of fragmentation. Use blank lines sparingly."
  - How: one blank line between logical steps (setup, loop, output); none padding the inside of a block.
- **Limit line length**: "The recommended length for a code line is 80 characters. This ensures that you don't have to scroll horizontally… It's common in many development environments to have two files side by side."
- **Use consistent spacing**: "Maintaining consistency in the use of spaces around operators and after commas contributes to code readability." `1+2` → `1 + 2`; `[1 , 2,3, 4]` → `[1, 2, 3, 4]`.
- **Avoid excessive whitespace**: "Excessive whitespace can visually clutter the code… Maintain a moderate use of whitespace." `func   foo  (   a : Int  , b   :   Int   )` → `func foo(a: Int, b: Int)`.
- **Follow the formatting recommended by SwiftLint**: "SwiftLint is a helpful tool for enforcing formatting standards. Integrate SwiftLint into your workflow to ensure the code follows recommended practices."

## Key Concepts
- **Google Swift Style Guide** — the style guide the source recommends most Swift code follow.
- **SwiftLint** — the linter the source recommends integrating to enforce formatting.
- **Indentation consistency** — the point of the tabs/spaces rule: one convention, applied everywhere.
- **Vertical whitespace** — blank lines; used to separate logical steps, not to pad.
- **Line length** — the source's figure is 80 characters, justified by side-by-side editing.
- **Type-annotation spacing** — `name: String?`, not `name:String?` (the Bad tabs example also shows this).

## Mental Models
- **Formatting debates are a tooling bug.** If a reviewer comments on spacing, the linter config is missing a rule.
- **Blank lines are paragraph breaks.** Each one should mark a change of step; a blank line inside a two-line block is noise.
- **The side-by-side test.** The line-length rule exists so two files fit on one screen; that's the constraint to reason from, whatever number your tool enforces.

## Code Examples
Consistent spacing and no excess whitespace:

```swift
let sum = 1 + 2
let array = [1, 2, 3, 4]

func foo(a: Int, b: Int) -> Int {
    return a + b
}
```

Spaces, consistently indented (the guide's Good version):

```swift
func good() {
    var name: String?
    guard let unwrappedName = name else {
        return
    }
}
```

## Reference Tables

| Rule | Bad | Good |
|---|---|---|
| Spaces, not tabs | inconsistent indent (4 then 7), `name:String?` | 4 spaces per level, `name: String?` |
| Blank lines | a blank line around every statement | blank lines only between steps |
| Line length | one 147-character line (a string literal) | under 80 characters |
| Operator/comma spacing | `1+2`, `[1 , 2,3, 4]` | `1 + 2`, `[1, 2, 3, 4]` |
| Excess whitespace | `func   foo  (   a : Int  , b   :   Int   )` | `func foo(a: Int, b: Int)` |
| Tooling | hand-formatting, review arguments | SwiftLint in the workflow |

## Worked Example
"Use blank lines effectively", before and after.

**Bad** — every statement isolated:

```swift
func calculateTotalScore(score: Int) {
    
    var totalScore = 0
    
    for i in 1...score {
        
        totalScore += i
        
    }
    
    print("The total score is: \(totalScore)")
    
}
```

**Good** — blank lines mark the three steps (initialize, accumulate, report) and nothing else:

```swift
func calculateTotalScore(score: Int) {
    var totalScore = 0
    
    for i in 1...score {
        totalScore += i
    }
    
    print("The total score is: \(totalScore)")
}
```

The same function reappears in Ch 11, where the loop itself is replaced by a formula and a comment explains why — formatting tidies the shape; the next chapter questions the content.

## Source Caveats
- **80 characters vs the cited guide**: the Google Swift Style Guide the source recommends sets a 100-column limit, and SwiftLint's default `line_length` rule warns at 120. Pick one number, configure it in the tool, and move on — which is the guide's own first rule.
- **Long string literals**: the Good line-length example shortens the message's text. That changes behaviour; Swift's other options (a multi-line `"""` literal, or building the string in parts) aren't discussed.
- **Tabs example**: the Bad snippet shows its indentation as `∙` characters with inconsistent depth; the lesson is consistency and the `name: String?` spacing rather than the dots.
- Apple's own formatter, swift-format, isn't mentioned; SwiftLint is the only tool named.

## Anti-patterns
- **Arguing about formatting in review**: the tool should have settled it.
- **Mixed or inconsistent indentation.**
- **Blank lines around every statement**: "a sense of fragmentation."
- **Lines that force horizontal scrolling.**
- **Inconsistent spacing around `+`, `:` and `,`.**

## Key Takeaways
1. **Don't argue about formatting — automate it** with SwiftLint, following the Google Swift Style Guide.
2. **Spaces, consistently.**
3. **Blank lines separate steps**, sparingly.
4. **Keep lines short enough for two files side by side** (the source says 80; set the number in your linter).
5. **One space around binary operators and after commas and colons; no padding elsewhere.**

## Connects To
- **Ch 1**: "This is not a style guide" — this chapter is the exception, and it defers to tools.
- **Ch 11**: comments, the other half of how code reads on the page; `calculateTotalScore` continues there.
- **`clean-code-java`** (ch05, Formatting): the newspaper metaphor and vertical distance — the ordering rules this guide's whitespace rules don't replace.
