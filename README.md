# PHP, Laravel, and Filament Skills

Canonical source for PHP, Laravel, Filament, and Livewire engineering skills.

**In plain terms:** you're writing or reviewing PHP/Laravel/Filament code and want your agent to follow this ecosystem's actual conventions — routing, validation, security hardening, testing patterns, plugin-first Filament components — instead of generic textbook PHP.

## Install

Pick whichever fits how you work. All three end up in the same place: the skill files sitting where your agent looks for them.

### 1. Everything, via npx (recommended)

```bash
npx skills@latest add wakqasahmed/php-laravel-filament-skills
```

This installs every skill in the pack for whichever agent you're using (Claude Code, Cursor, Codex, and 70+ others — see the [`skills` CLI](https://github.com/vercel-labs/skills)). Add `-g` to install once for every project instead of per-project, or `-a claude-code` to target one agent specifically.

### 2. Just one skill

Don't need the whole pack? Install a single skill by its name (skill names match their folder, e.g. `laravel-conventions`):

```bash
npx skills@latest add wakqasahmed/php-laravel-filament-skills --skill laravel-conventions
```

Or point straight at one skill's folder on GitHub:

```bash
npx skills add https://github.com/wakqasahmed/php-laravel-filament-skills/tree/main/skills/laravel/laravel-conventions
```

### 3. No Node/npx available — manual zip install

1. On this repo's GitHub page: **Code → Download ZIP**.
2. Unzip it.
3. Copy whichever `skills/<category>/<name>/` folder(s) you want into your agent's own skills directory (for Claude Code, that's `.claude/skills/` in your project, or `~/.claude/skills/` for a global install; other agents use their own equivalent path).

No installer, no dependency — just files your agent already knows how to read.

## Use it — step by step

| Skill | What it covers |
|---|---|
| [`filament-conventions`](skills/filament/filament-conventions/SKILL.md) | Follow Filament conventions when building resources, forms, tables, actions, and widgets. |
| [`filament-plugin-first`](skills/filament/filament-plugin-first/SKILL.md) | Before building custom Filament components, search the plugin ecosystem and triage reuse vs. build. |
| [`livewire-conventions`](skills/filament/livewire-conventions/SKILL.md) | Reason about Livewire component lifecycle, state, and performance when Filament's declarative API isn't enough. |
| [`laravel-conventions`](skills/laravel/laravel-conventions/SKILL.md) | Follow Laravel conventions before adding routes, controllers, models, validation, or background work. |
| [`laravel-security`](skills/laravel/laravel-security/SKILL.md) | Harden Laravel/PHP code against mass-assignment, SQL injection, XSS, CSRF, and authorization bypass. |
| [`laravel-testing`](skills/laravel/laravel-testing/SKILL.md) | Follow Pest testing conventions, factory/seeder patterns, and test-database safety before writing or running Laravel tests. |
| [`php-principles`](skills/php/php-principles/SKILL.md) | Apply core PHP engineering principles before writing new code. |

## Contents

The installable skills live in [`skills/php/`](skills/php/), [`skills/laravel/`](skills/laravel/), and [`skills/filament/`](skills/filament/).

## Aggregate catalogue

Changes merged to this repository are automatically synchronized to [wakqasahmed/skills](https://github.com/wakqasahmed/skills). Treat this repository as the source of truth for PHP, Laravel, and Filament skills.

## Outcome-eval harness status

No skill in this repo has an outcome-based eval yet. Six open issues track building the deterministic + gated model-harness layers used elsewhere in this portfolio: [#26](https://github.com/wakqasahmed/php-laravel-filament-skills/issues/26)–[#31](https://github.com/wakqasahmed/php-laravel-filament-skills/issues/31).

### Fund the real harness runs

This skill's deterministic checks run free on every PR. Proving its outcome-eval harness with real, metered model calls costs money:

- **Bitcoin (BTC):** `bc1p5xqamscrz7nu0d8jdmj748rj75sk8khtyxypn3qvsdjms4t4uw2qsjn0he`
- **Ethereum (ETH) / any ERC-20 including stablecoins:** `0x59bc573e414D62d44461234dEf438247dfc3Cf6A`

Double-check every character against this page before sending. Full portfolio picture and rationale: [wakqasahmed/skills](https://github.com/wakqasahmed/skills#fund-the-real-harness-runs).
