# Chapter 10: Formatting

## Core Idea
**"Formatting is subjective… The main point is *DO NOT ARGUE* over formatting."** Automate it
with ESLint + Prettier, then spend the recovered attention on the two formatting decisions a
tool *can't* make for you: **vertical ordering** (caller above callee) and **import
organization**.

## Frameworks Introduced

- **Don't argue — automate.** *"There are tons of tools to automate this. Use one! It's a waste
  of time and money for engineers to argue over formatting."* The general rule: **keep consistent
  formatting rules.**
  - The named tool for TypeScript is **ESLint** (`typescript-eslint`) — *"a static analysis tool
    that can help you improve dramatically the readability and maintainability of your code."*
  - Ready-to-use configurations the source recommends:
    | Config | What it is |
    |---|---|
    | `eslint-config-airbnb-typescript` | Airbnb style guide |
    | `eslint-plugin-base-style-config` | essential ESLint rules for JS, TS and React |
    | `eslint-config-prettier` | lint rules for the **Prettier** formatter |
  - Also cited as a reference: *TypeScript StyleGuide and Coding Conventions* (basarat).
  - **Migrating from TSLint**: TSLint is deprecated; the source points at
    `typescript-eslint/tslint-to-eslint-config` to do the conversion.

- **Consistent capitalization** — subjective, *"so your team can choose whatever they want. The
  point is, no matter what you all choose, just *be consistent*."* The source's own preferences:
  | Case | Applies to |
  |---|---|
  | **`PascalCase`** | class, interface, **type** and namespace names |
  | **`camelCase`** | variables, functions, class members |
  | **`SNAKE_CASE`** (capitalized) | constants |
  - Note what the Good example does: `daysInMonth` → `DAYS_IN_MONTH` and `songs` → `SONGS`
    because they're constants, while `discography` and `beatlesSongs` stay `camelCase` because
    they're computed values. **The case encodes the category, not the spelling habit.**

- **The newspaper rule for vertical ordering** — *"If a function calls another, keep those
  functions vertically close in the source file. Ideally, keep the caller right above the
  callee. We tend to read code from top-to-bottom, like a newspaper. Because of this, make your
  code read that way."*
  - When to use: on every class or module with private helpers.
  - How: public entry point first, then each helper immediately below its first caller.

- **Organize imports** — the stated benefit: *"With clean and easy to read import statements you
  can quickly see the dependencies of current code."* The full rule set:
  1. Import statements should be **alphabetized and grouped**.
  2. **Unused imports should be removed.**
  3. **Named imports** must be alphabetized — `import {A, B, C} from 'foo';`
  4. **Import sources** must be alphabetized within groups.
  5. Prefer **`import type`** instead of `import` when importing only types, **to avoid
     dependency cycles, as these imports are erased at runtime**.
  6. Groups are **delineated by blank lines**, in this order:
     | # | Group | Example |
     |---|---|---|
     | 1 | Polyfills | `import 'reflect-metadata';` |
     | 2 | Node builtin modules | `import fs from 'fs';` |
     | 3 | External modules | `import { query } from 'itiriri';` |
     | 4 | Internal modules | `import { UserService } from 'src/services/userService';` |
     | 5 | Parent directory | `import foo from '../foo';` |
     | 6 | Same or sibling directory | `import bar from './bar';` |

- **TypeScript path aliases** — define `baseUrl` and `paths` in `tsconfig.json`'s
  `compilerOptions` to *"avoid long relative paths when doing imports"* and create prettier
  imports.

## Key Concepts
- **ESLint** — the static analysis tool for TypeScript; replaced the now-deprecated TSLint.
- **Prettier** — the opinionated formatter; `eslint-config-prettier` reconciles the two.
- **Newspaper metaphor** — read top-to-bottom, general to specific; the basis of vertical ordering.
- **`import type`** — a type-only import, **erased at runtime**, which is why it breaks
  dependency cycles.
- **Path alias** — `@services/UserService` instead of `../../../services/UserService`, via
  `baseUrl` + `paths`.
- **Import group** — a blank-line-separated block of imports of the same kind.

## Mental Models
- **Treat formatting arguments as a budget line.** The source frames it as *"a waste of time and
  money for engineers."* The fix is committing a config, not winning the debate.
- **Think of capitalization as type information.** `DAYS_IN_WEEK` says "constant" before you read
  the value; `Animal` says "type"; `beatlesSongs` says "computed". Case is a channel — the bad
  example (`const DAYS_IN_WEEK` next to `const daysInMonth`, `songs` next to `Artists`,
  `eraseDatabase` next to `restore_database`) wastes it.
- **Order code so a reader can stop early.** Put `review()` at the top and a reader who only
  needs the overview never scrolls. Put `lookupPeers()` first and they must read the mechanics
  to find the point.
- **Use `import type` reflexively for type-only imports.** It's not stylistic — it's how you
  break a cycle, because the import doesn't exist at runtime.
- **A `../../../` chain is a signal, not just an eyesore.** Aliases fix the symptom; deep
  relative paths often also mean the module is in the wrong place.
- **This chapter is the one with the loudest stated licence to disagree** — "subjective",
  "your team can choose whatever they want". Consistency is the actual requirement.

## Code Examples

Consistent capitalization — case as category:

```ts
// Bad — same category, different cases; different categories, same case.
const DAYS_IN_WEEK = 7;
const daysInMonth = 30;

const songs = ['Back In Black', 'Stairway to Heaven', 'Hey Jude'];
const Artists = ['ACDC', 'Led Zeppelin', 'The Beatles'];

function eraseDatabase() {}
function restore_database() {}

type animal = { /* ... */ }
type Container = { /* ... */ }

// Good
const DAYS_IN_WEEK = 7;
const DAYS_IN_MONTH = 30;

const SONGS = ['Back In Black', 'Stairway to Heaven', 'Hey Jude'];
const ARTISTS = ['ACDC', 'Led Zeppelin', 'The Beatles'];

const discography = getArtistDiscography('ACDC');        // computed → camelCase
const beatlesSongs = SONGS.filter((song) => isBeatlesSong(song));

function eraseDatabase() {}
function restoreDatabase() {}

type Animal = { /* ... */ }
type Container = { /* ... */ }
```

Organized imports:

```ts
// Bad — no grouping, no order; the dependency shape is invisible.
import { TypeDefinition } from '../types/typeDefinition';
import { AttributeTypes } from '../model/attribute';
import { Customer, Credentials } from '../model/types';
import { ApiCredentials, Adapters } from './common/api/authorization';
import fs from 'fs';
import { ConfigPlugin } from './plugins/config/configPlugin';
import { BindingScopeEnum, Container } from 'inversify';
import 'reflect-metadata';

// Good — polyfill / builtin+external / parent / sibling, each alphabetized.
import 'reflect-metadata';

import fs from 'fs';
import { BindingScopeEnum, Container } from 'inversify';

import { AttributeTypes } from '../model/attribute';
import { TypeDefinition } from '../types/typeDefinition';
import type { Customer, Credentials } from '../model/types';

import { ApiCredentials, Adapters } from './common/api/authorization';
import { ConfigPlugin } from './plugins/config/configPlugin';
```
- **What it demonstrates**: `Customer, Credentials` became **`import type`** — they're only used
  as types, so the import vanishes at compile time and cannot participate in a cycle.

Path aliases:

```ts
// Bad
import { UserService } from '../../../services/UserService';

// Good
import { UserService } from '@services/UserService';
```

```js
// tsconfig.json
  "compilerOptions": {
    "baseUrl": "src",
    "paths": {
      "@services": ["services/*"]
    }
  }
```

## Reference Tables

| Decision | Tool's job | Yours |
|---|---|---|
| Braces, quotes, semicolons, width | Prettier / ESLint | commit the config, stop arguing |
| Import order & grouping | ESLint (import plugin) | choose the 6-group order |
| Unused imports | ESLint | — |
| Casing conventions | ESLint (naming-convention) | pick the mapping, be consistent |
| **Caller/callee vertical order** | — | **yours; no tool does this** |
| **Where a module lives** (aliases hide depth) | — | **yours** |

## Worked Example
**The newspaper rule, walked** — the one formatting decision no linter makes for you.

**Before** — helpers first, entry point buried in the middle:

```ts
class PerformanceReview {
  constructor(private readonly employee: Employee) {}

  private lookupPeers() { return db.lookup(this.employee.id, 'peers'); }

  private lookupManager() { return db.lookup(this.employee, 'manager'); }

  private getPeerReviews() { const peers = this.lookupPeers(); /* ... */ }

  review() {
    this.getPeerReviews();
    this.getManagerReview();
    this.getSelfReview();
  }

  private getManagerReview() { const manager = this.lookupManager(); }

  private getSelfReview() { /* ... */ }
}
```

To learn what a performance review *is*, you read three private helpers, hit `review()` in the
middle, then jump back down for the other two. `getPeerReviews` and `lookupPeers` are adjacent
by luck; `getManagerReview` and `lookupManager` are five methods apart.

**After** — caller immediately above callee, entry point first:

```ts
class PerformanceReview {
  constructor(private readonly employee: Employee) {}

  review() {                                  // 1. the point, at the top
    this.getPeerReviews();
    this.getManagerReview();
    this.getSelfReview();
  }

  private getPeerReviews() {                  // 2. called by review()
    const peers = this.lookupPeers();
  }

  private lookupPeers() {                     // 3. called by getPeerReviews()
    return db.lookup(this.employee.id, 'peers');
  }

  private getManagerReview() {                // 4. called by review()
    const manager = this.lookupManager();
  }

  private lookupManager() {                   // 5. called by getManagerReview()
    return db.lookup(this.employee, 'manager');
  }

  private getSelfReview() { /* ... */ }       // 6. called by review()
}
```

**Why it works**: the file now descends one level of abstraction at a time. A reader who wants
the summary reads `review()` and stops. A reader chasing peer reviews reads two methods in a
row without scrolling. Each helper sits directly beneath its first caller, so *"we tend to read
code from top-to-bottom, like a newspaper"* is actually true of this file.

**The connection worth noticing**: this ordering is only achievable because the methods are
small and single-purpose (ch03). A 200-line `review()` has no callees to order. **Vertical
ordering is a readability payoff you collect for having extracted functions** — which is why
ESLint can't give it to you.

**Failure mode**: strict caller-above-callee breaks down when a helper has several callers
(`lookupManager` called from two places). Then put it below the *first* caller and accept it;
the rule is "keep them vertically close", not a total order.

## Key Takeaways
1. **DO NOT ARGUE over formatting.** Commit an ESLint + Prettier config and move on; consistency
   is the requirement, not any particular choice.
2. Use **`typescript-eslint`**; migrate off TSLint with `tslint-to-eslint-config`.
3. **Case encodes category**: `PascalCase` types, `camelCase` values and members, `SNAKE_CASE`
   constants. Be consistent above all.
4. **Caller directly above callee**, entry point at the top — the newspaper rule, and the one
   thing no tool automates.
5. **Organize imports into six blank-line-separated groups**, alphabetized within each, named
   imports alphabetized too, unused ones removed.
6. **`import type` for type-only imports** — erased at runtime, so it breaks dependency cycles.
7. **Path aliases** (`baseUrl` + `paths`) kill `../../../` chains.
8. Vertical ordering is the **payoff for having small functions** (ch03).

## Connects To
- **Ch 2 (Variables)**: the casing rules here govern the names chosen there — especially the
  `SNAKE_CASE` named constants that replace magic numbers.
- **Ch 3 (Functions)**: small single-purpose functions are the precondition for the newspaper
  rule; ESLint is also how you find the dead code ch03 tells you to delete.
- **Ch 1 (Introduction)**: *"this is not a style guide"* is why this chapter delegates to tooling
  instead of legislating.
- **Ch 6 (SOLID)**: `import type` breaking cycles is the module-level echo of DIP's
  decoupling — and a cycle usually means an abstraction is missing.
- **`clean-code-java` ch05 (Formatting)**: the fuller treatment — vertical openness and density,
  the **newspaper metaphor** in its original form, **vertical distance** between related
  concepts, declaration order, and **team rules beat personal preference**.
