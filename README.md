# claude-marketplace

A personal [Claude Code](https://claude.com/claude-code) plugin marketplace.

## Add this marketplace

```
/plugin marketplace add korsicheg/claude-marketplace
```

(or with the full URL: `/plugin marketplace add https://github.com/korsicheg/claude-marketplace`)

## Plugins

### persona-dialog-eval

Measure whether a conversational agent makes the **right decision** (category /
team / intent / severity) — and whether that decision **holds up across user
personalities and languages**. Hold the underlying case (with a fixed
ground-truth label) constant and vary only the speaker; an LLM plays that speaker
in a real dialog with the **actual agent**, and the agent's emitted decision is
scored per persona and language.

Install:

```
/plugin install persona-dialog-eval@korsicheg-marketplace
```

Ships one skill:

- **`persona-dialog-eval`** — scaffolds a complete, validated `eval/` into your
  project: a reusable scoring engine (`aggregate` → accuracy per field, a
  per-expected-value breakdown, per-persona/-language/-scenario breakdowns, dialog
  metrics, miss list) plus a corpus validator, a dialog-loop `runner`, the six
  stress personas, and the enforced **anti-fabrication driving** CLIs
  (`drive-turn` / `finalize` / `scenario-state` / `assemble`) that make a driver
  structurally unable to fake a dialog. You wire four seams (scenarios, label
  space, the one-real-turn agent adapter, config), generate a committed corpus,
  then drive a slice and aggregate the report.

### clean-code

Robert C. Martin's **Clean Code** as five routing knowledge-base skills — one per
language family, covering **any** language between them. Each is a chaptered
reference with worked examples, a cheatsheet, a glossary and a pattern catalogue,
and each description routes to the right sibling, so the model loads the one skill
that fits the file it is editing rather than guessing between five.

Install:

```
/plugin install clean-code@korsicheg-marketplace
```

Ships five skills:

- **`clean-code-java`** — the original book (Java examples): naming, functions,
  comments, formatting, error handling, classes/SRP, unit tests/TDD, systems,
  concurrency, the refactoring case studies, and the 66-item
  smells-and-heuristics catalogue.
- **`clean-code-typescript`** — the labs42io adaptation: SOLID in TS, `type` vs
  `interface`, `readonly`/`as const` immutability, unions over `instanceof`,
  `Failable` result types, async/await, ESLint/Prettier.
- **`clean-code-javascript`** — the Ryan McDermott adaptation: argument counts and
  flag parameters, side effects and argument mutation, polymorphism over
  conditionals, closure privacy, SOLID in an untyped language, callbacks →
  promises → async/await.
- **`clean-code-python`** — the zedr adaptation: type hints over type-prefixes,
  the two-argument limit with dataclass/NamedTuple/TypedDict parameter objects,
  generators, SOLID through ABCs and mixins, mypy-enforced LSP, duck-typed
  dependency inversion.
- **`clean-code-universal`** — the family's shared core, and the reason these ship
  together. A language-agnostic distillation cross-checked against all four, built
  on a **three-tier spine**: Tier 1 rules assume only that you can name something
  and run some verification; Tier 2 rules bind only where a construct exists (a
  parameter list, a type system, an exception, a test runner, a thread). It covers
  the languages with no dedicated sibling — Go, Rust, C#, C++, Kotlin, Ruby, PHP,
  Swift, Scala — and the declarative ones the book never addresses: **YAML**
  (Kubernetes, Helm, CI pipelines), **Terraform/HCL**, **SQL**, **Bash**,
  **Dockerfile**. Its translation table states, per rule, what it means where there
  are no functions, no classes and no unit tests — including the rules that
  genuinely *do not apply*.

> **Sources and licensing differ per skill.** The three community adaptations are
> MIT; the book-derived material is not open source and is shipped as
> independently written restatement with citations. See
> [`plugins/clean-code/NOTICE.md`](plugins/clean-code/NOTICE.md).

## Layout

```
.claude-plugin/marketplace.json          # marketplace manifest (lists plugins)
plugins/
├── clean-code/
│   ├── .claude-plugin/plugin.json        # plugin manifest
│   ├── NOTICE.md                         # per-skill sources and licences
│   ├── PLUGIN_CHANGELOG.md
│   └── skills/
│       ├── clean-code-java/              # SKILL.md + chapters/ + cheatsheet + glossary + patterns
│       ├── clean-code-typescript/
│       ├── clean-code-javascript/
│       ├── clean-code-python/
│       └── clean-code-universal/         # + references/declarative-translation.md
└── persona-dialog-eval/
    ├── .claude-plugin/plugin.json        # plugin manifest
    └── skills/
        └── persona-dialog-eval/
            ├── SKILL.md                  # the skill
            ├── lib/                       # reusable engine + runner + personas (copied verbatim into a project's eval/)
            └── templates/eval/            # fill-in seams + CLIs (copied + adapted per project)
```
