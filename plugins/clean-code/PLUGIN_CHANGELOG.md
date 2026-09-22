# clean-code plugin changelog

Version history for the **plugin package** (`.claude-plugin/plugin.json` + the marketplace
entry) and the five skills it ships.

Format follows [Keep a Changelog](https://keepachangelog.com/); newest first. Semver on the
plugin: **major** = removed/renamed skill or breaking routing change, **minor** = new skill
or capability, **patch** = content fix or doc change with no new surface.

Sources and licensing for the shipped content are recorded in [NOTICE.md](NOTICE.md).

## [1.1.0] — 2026-09-22

### Added

- **A `SessionStart` gateway hook** (`hooks/`), so the family fires without being asked for.
  Five well-described skills turned out not to be enough: in practice the model reads past
  them, because nothing in a session names *when* to load one. The gateway injects a short
  rule at the top of each context window — a language-to-skill dispatch table, the
  before-not-after ordering, and a red-flags table rebutting the specific rationalisations
  used to skip ("it's a one-line change", "I'm matching the surrounding style", "I'm
  reviewing, not writing"). Mechanism copied from the `superpowers` plugin, which solves the
  same problem the same way.
  - `hooks/clean-code-gateway.md` — the rule, 360 words. **Edit this to change behaviour;**
    the script only escapes and emits it.
  - `hooks/session-start` — reads the gateway, JSON-escapes it, emits it as
    `hookSpecificOutput.additionalContext`. An unreadable gateway is reported *into the
    session* with the failing operation and `cat`'s own message, never swallowed — a silent
    exit is indistinguishable from the hook not being installed.
  - `hooks/hooks.json` — one registration, matcher `startup|clear|compact`. Fires once per
    context window rather than per turn, so the recurring cost is ~2.2 kB of context and no
    extra model calls. `clear` and `compact` are in the matcher because compaction would
    otherwise drop the injected text mid-session.

### Notes

- **Two deliberate departures from the `superpowers` original.** Its gateway asserts
  "questions are tasks, check for skills"; copied literally that fires clean-code on
  codebase questions and trace reading, so this one carries an explicit **Scope** section
  exempting them — a rule that cries wolf gets tuned out. And a **Precedence** section
  gives the project's own `CLAUDE.md` and the user priority over the skill, requiring any
  set-aside rule to be named, since house conventions legitimately contradict the book.
- **No Windows polyglot wrapper.** `superpowers` ships a `cmd.exe`/bash polyglot for native
  Windows without Git Bash; `"shell": "bash"` covers macOS, Linux, WSL and Git Bash, and the
  remaining case degrades to no injection rather than an error. Left out as speculative
  until someone reports needing it.
- **Verification.** `bash -n` clean; happy path and missing-gateway path both exercised; the
  escaped payload round-trips byte-identical to the source (`diff -q`), so backticks, quotes
  and the markdown table pipes survive. `shellcheck` was **not** run — not installed in the
  authoring environment.

## [1.0.0] — 2026-09-21

First release. Five skills, 82 files, ~16k lines.

### Added

- **`clean-code-java`** — the original book (Java examples): naming, functions, comments,
  formatting, error handling, classes/SRP, unit tests/TDD, systems, concurrency, the
  refactoring case studies, and the 66-item smells-and-heuristics catalogue.
- **`clean-code-typescript`** — the labs42io adaptation: SOLID in TS, `type` vs `interface`,
  `readonly`/`as const` immutability, unions over `instanceof`, `Failable` result types,
  async/await and `Promise.all`, ESLint/Prettier.
- **`clean-code-javascript`** — the Ryan McDermott adaptation: argument counts and flag
  parameters, side effects and argument mutation, polymorphism over conditionals, closure
  privacy, ES6 classes and chaining, SOLID in an untyped language, callbacks → promises →
  async/await.
- **`clean-code-python`** — the zedr adaptation: type hints over type-prefixes, named regex
  groups, the two-argument limit with dataclass/NamedTuple/TypedDict parameter objects,
  generators, SOLID through ABCs and mixins, mypy-enforced LSP, duck-typed dependency
  inversion, DRY with the bad-abstraction caveat.
- **`clean-code-universal`** — the family's shared core, and the reason the set is published
  together. A language-agnostic distillation of the book cross-checked against the three
  adaptations above, organised on a **three-tier spine**: Tier 1 rules assume only that you
  can name something and run some verification; Tier 2 rules bind where a specific construct
  exists (parameter list, type system, substitutability mechanism, exception, test runner,
  thread, branching construct); Tier 3 is language-specific idiom, out of scope by name.
  Covers the languages with no dedicated sibling — Go, Rust, C#, C++, Kotlin, Ruby, PHP,
  Swift, Scala — and the declarative languages the book never addresses: YAML (Kubernetes,
  Helm, CI pipelines), Terraform/HCL, SQL, Bash, Dockerfile. Ships
  `references/declarative-translation.md`, a 53-row table stating per rule what it means
  where there are no functions, no classes and no unit tests, including the rules that
  genuinely **do not apply**.
- **Reciprocal routing across all five.** Every description names its siblings and ends by
  routing anything else to `clean-code-universal`, so the model loads one skill rather than
  guessing between five. Measured before release: universal fires on 45/45 prompts no
  sibling covers and 0/55 sibling-owned or oblique ones.
- **`NOTICE.md`** — per-skill sources and licences. The three community adaptations are MIT
  (notices reproduced verbatim); the book-derived material is not open source and is
  distributed as independently written restatement with citations.
