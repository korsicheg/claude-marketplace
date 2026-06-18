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

## Layout

```
.claude-plugin/marketplace.json          # marketplace manifest (lists plugins)
plugins/
└── persona-dialog-eval/
    ├── .claude-plugin/plugin.json        # plugin manifest
    └── skills/
        └── persona-dialog-eval/
            ├── SKILL.md                  # the skill
            ├── lib/                       # reusable engine + runner + personas (copied verbatim into a project's eval/)
            └── templates/eval/            # fill-in seams + CLIs (copied + adapted per project)
```
