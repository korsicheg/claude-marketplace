# Chapter 3: Naming — Functions and Variables

## Core Idea
Function names and variable names run on **opposite gradients**. A function high in the call tree gets a short, broad name (`Parse`, `Run`) and the functions beneath it get progressively more specific ones (`parseJSON`, `fileExtension`). A variable in a wide scope gets a specific name, and the narrower its scope, the shorter and more generic it can be (`brands` → `b`).

## Frameworks Introduced
- **Function names: broad at the top, specific further down** — "we want to start with a very broad and short function name, such as `Run` or `Parse`, that describes the general functionality." One layer deeper, names get "slightly more specific."
  - When to use: naming any function in a layered call tree, especially an exported entry point and its unexported helpers.
  - How: name the top level by its general purpose (`configuration.Parse`); name each helper so it is distinct from its parent "without being overly specific," and so it "make[s] sense on its own as well as within the context of the parent." A helper whose job is narrow (`fileExtension`) earns a narrow name.
  - Why it works: the reader can stop at the altitude they care about. The alternative — a top-level name "that attempts to cover all bases," like `DetermineFileExtensionAndParseConfigurationFile` — is "trying to be too specific too soon."
  - ⚠ The article's one-line statement of this rule reads "the more specific the function, the more general its name," which says the opposite of its own examples and of its summary ("the smaller the scope of a function, the more specific its name"). **Follow the examples and the summary.**
- **Keep the verb** — naming `parseJSON` just `json` would mean "we would no longer be able to tell whether this function is parsing, creating, or marshalling JSON." Short is good; ambiguous is not.
- **Variable names: specific in wide scopes, short in narrow ones** — "Unlike functions, our variables should be named from more to less specific the deeper we go into nested scopes."
  - When to use: every local, loop variable and parameter.
  - How: the wider a variable's reach, the more its name must explain; inside a three-line loop, `b` is enough. In `fileExtension`, "we could even shorten the name of the variable `segments` to `s`."
  - Why it works: "as a variable's scope becomes smaller, it becomes increasingly clear for the reader what that variable represents, thereby eliminating the need for specific naming."
- **Don't name variables after their types** — the article quotes Dave Cheney: *"You shouldn't name your variables after their types for the same reason you wouldn't name your pets 'dog' or 'cat'."*

## Key Concepts
- **Level of abstraction (for names)** — how high a function sits in the call tree; it sets how broad its name may be.
- **Name gradient** — the direction in which specificity changes with depth; functions and variables run in opposite directions.
- **Too specific too soon** — a top-level name that tries to describe every step beneath it.
- **Standalone readability** — a helper's name must make sense out of context (`parseJSON`, not `json`).
- **Scope-proportional naming** — a variable's name length tracks how far it reaches.
- **Inconsistent brevity** — mixing short and long names in the wrong places; it can "spiral into full-blown confusion."

## Mental Models
- **Think of function names as a table of contents and helper names as section headings**: the top is short and general; detail lives further in.
- **Think of a variable name as a label read from a distance**: the farther away its uses, the more the label must say.
- **Use the pet test** for type-named variables: `user`, not `userStruct`; `brands`, not `brandSlice`.

## Anti-patterns
- **A kitchen-sink top-level name** — `DetermineFileExtensionAndParseConfigurationFile`: "horrendously difficult to read."
- **Verbless helper names** — `json` instead of `parseJSON`; the action vanishes.
- **Inverted variable naming** — a terse parameter (`b []BeerBrand`) and accumulator (`bl`) at function scope, with long names (`beerBrandBeerName`) inside the innermost loop.
- **Type-named variables** — the Cheney "dog / cat" smell.

## Code Examples
The configuration parser, one layer at a time:

```go
func main() {
    configpath := flag.String("config-path", "", "configuration file path")
    flag.Parse()

    config, err := configuration.Parse(*configpath)
    // ...
}
```

```go
func Parse(filepath string) (Config, error) {
    switch fileExtension(filepath) {
    case "json":
        return parseJSON(filepath)
    case "yaml":
        return parseYAML(filepath)
    case "toml":
        return parseTOML(filepath)
    default:
        return Config{}, ErrUnknownFileExtension
    }
}

func fileExtension(filepath string) string {
    segments := strings.Split(filepath, ".")
    return segments[len(segments)-1]
}
```
- **What it demonstrates**: `Parse` is short and broad because it sits on top; `parseJSON`/`parseYAML`/`parseTOML` are distinguishable from their parent and from each other; `fileExtension` is specific because its job is.

## Reference Tables

| | Wide scope / top of the call tree | Narrow scope / deep in the call tree |
|---|---|---|
| **Function names** | short and general — `Parse`, `Run` | more specific — `parseJSON`, `fileExtension` |
| **Variable names** | specific — `beerBrands`, `beerList` | short and generic — `brand`, `b`, `s` |

## Worked Example
The article's beer-brand function, named both ways.

**Right gradient** — specific names at function scope, shorter ones as loops nest:

```go
func BeerBrandListToBeerList(beerBrands []BeerBrand) []Beer {
    var beerList []Beer
    for _, brand := range beerBrands {
        for _, beer := range brand {
            beerList = append(beerList, beer)
        }
    }
    return beerList
}
```

**Wrong gradient** — the same logic with the gradient inverted:

```go
func BeerBrandListToBeerList(b []BeerBrand) []Beer {
    var bl []Beer
    for _, beerBrand := range b {
        for _, beerBrandBeerName := range beerBrand {
            bl = append(bl, beerBrandBeerName)
        }
    }
    return bl
}
```

The second version works, but "the excessive brevity of the variable names makes it difficult to follow the logic as we travel deeper," and the long innermost name adds nothing its two-line scope doesn't already show. The smaller case confirms the rule: in a one-loop function, `for _, b := range brands` is fine — "the scope of the variable `b` is so small that we don't need to spend any additional brain power on remembering what exactly it represents," while `brands`, with a slightly larger scope, stays specific.

## Key Takeaways
1. **Top-level functions get short, broad names**; helpers get more specific as they go deeper.
2. Every helper name must **make sense on its own** — keep the verb (`parseJSON`, not `json`).
3. Never try to describe the whole call tree in one name; that is "too specific too soon."
4. **Variables run the other way**: specific in wide scopes, short (`b`, `s`) in tiny ones.
5. **Don't put the type in the name.**
6. Be consistent: inverted or mixed brevity is worse than either extreme.

## Connects To
- **Ch 2**: the rename that retires a comment (`i` → `workerID`) applies these gradients.
- **Ch 4**: the same top-down layering, applied to function bodies, gives the "onion" structure.
- **Ch 5**: narrow scopes are what make short variable names safe; this chapter and Ch 5 are two halves of one rule.
- **clean-code-java ch02**: the book's naming chapter (intention-revealing, searchable, pronounceable names); its "length of a name should correspond to the size of its scope" is the same variable rule.
