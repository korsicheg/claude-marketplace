# Chapter 11: Comments

## Core Idea
"Comments are an apology, not a requirement. Good code *mostly* documents itself." **Comment only what has business-logic complexity**, and delete the rest: commented-out code, journal comments, and positional-marker banners all belong to version control or to better names.

## Frameworks Introduced
- **Only comment things that have business logic complexity**:
  - When to comment: the line a competent reader would still get wrong — in the guide's example, the one step that depends on the data's format: `// Gets only the string before the comma`.
  - When not to: comments that restate the code (`// Loop through every city`, `// Returns the cities names list`).
- **Don't leave commented out code in your codebase**: "Version control exists for a reason. Leave old code in your history."
- **Don't have journal comments**: "Remember, use version control! There's no need for dead code, commented code, and especially journal comments. Use `git log` to get history!"
- **Avoid positional markers**: "They usually just add noise. Let the functions and variable names along with the proper indentation and formatting give the visual structure to your code."

## Key Concepts
- **Comment as apology** — a comment exists because the code couldn't say something by itself.
- **Business-logic complexity** — the guide's only stated reason to keep a comment: a rule of the domain or the data that the code's names can't carry.
- **Redundant comment** — one that says what the next line already says.
- **Commented-out code** — disabled lines left in place; version control already keeps them.
- **Journal comment** — a dated change log inside the source (`2016-12-20: …`); `git log` already keeps it.
- **Positional marker** — a banner such as `/////` lines around a section title.

## Mental Models
- **Ask "would a careful reader get this wrong?"** If not, the comment is noise. The guide keeps exactly one comment in its example, on the comma split.
- **Think of version control as the place for the past.** Old code, who changed what and when, and why — all of it has a home that isn't the file.
- **Let structure do the sectioning.** If a file needs banners to be navigable, it needs smaller functions, better names or another file (Ch 3, Ch 10).

## Anti-patterns
- **Narrating comments** — `// Cities names list`, `// Loop through every city`, `// Add the filtered city name`.
- **Commented-out calls** — `// doOtherStuff();` and friends left below `doStuff();`.
- **Journal headers** — the guide's example is a block of dated entries (left in Portuguese) above a two-line `combine` function.
- **Banner comments** — `////////…` lines around "Programmer Instantiation" and "startProject implementation".

## Code Examples
Only business-logic comments:

```dart
// Bad
List<String> getCitiesNames(List<String> cities) {
  // Cities names list
  final citiesNames = <String>[];

  // Loop through every city
  for (final city in cities) {
    // Gets only the string before the comma
    final filteredCityName = city.split(',')[0];

    // Add the filtered city name
    citiesNames.add(filteredCityName);
  }

  // Returns the cities names list
  return citiesNames;
}

// Good
List<String> getCitiesNames(List<String> cities) {
  final citiesNames = <String>[];

  for (final city in cities) {
    // Gets only the string before the comma
    final filteredCityName = city.split(',')[0];

    citiesNames.add(filteredCityName);
  }

  return citiesNames;
}
```
- **What it demonstrates**: four of five comments go; the survivor explains the one thing the code can't — that a city entry carries extra text after a comma, and only the part before it is the name.

## Reference Tables

| Comment | Keep? | Where it belongs instead |
|---|---|---|
| Explains a business or data rule the code can't name | yes | — |
| Restates the next line | no | nowhere; delete it |
| Commented-out code | no | version history |
| Dated change log | no | `git log` |
| Section banner | no | function names, formatting, smaller files |

## Worked Example
**Journal comments**, before and after:

```dart
// Bad
/**
 * 2016-12-20: Removidas monads, não entendia elas (RM)
 * 2016-10-01: Melhoria utilizando monads especiais (JP)
 * 2016-02-03: Removido checagem de tipos (LI)
 * 2015-03-14: Adicionada checagem de tipos (JR)
 */
int combine(int a, int b) {
  return a + b;
}

// Good
int combine(int a, int b) {
  return a + b;
}
```

The header records four changes by four people over two years (in English: removed monads, didn't understand them; improved using special monads; removed type checking; added type checking). None of it describes what `combine` does *now*, and every entry is already in the commit history with more context than one line can hold. The four lines of history sit above a two-line function: the comment is longer than the code and says nothing about it.

**The same logic applies to the other two deletions.** Commented-out calls (`// doSoMuchStuff();`) are history too. Banners (`// Programmer Instantiation` between `////` rules) describe structure that names and spacing already show: `final programmer = Programmer(…)` and `void startProject()` need no headings.

## Key Takeaways
1. **Comments are an apology**: write the code so it doesn't need one.
2. **Keep a comment only for business-logic complexity** — the rule a careful reader would otherwise miss.
3. **Delete commented-out code**; version control has it.
4. **No journal comments**; use `git log`.
5. **No positional markers**; let names and formatting structure the file.

## Connects To
- **Ch 2**: meaningful names are what make narrating comments unnecessary.
- **Ch 3**: "Remove dead code" is the same rule as "Don't leave commented-out code", one level up.
- **Ch 10**: newspaper ordering and formatting replace section banners.
- **`clean-code-java`** ch. 4 (Comments): the book's full catalogue of good and bad comments.
- **`clean-code-javascript` Ch 11**: the parent chapter, rule for rule.
