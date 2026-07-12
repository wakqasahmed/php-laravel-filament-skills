# Security Policy

## What a skill is

Each skill in this repo is a `SKILL.md` file: a markdown instruction document read by an AI coding agent (Claude, Codex, Cursor, Copilot, etc.). A skill is **not executable code** — installing or loading a `SKILL.md` cannot itself run arbitrary code on your machine.

Some skills do instruct the agent to run shell commands or browse external sites as part of following the guidance (see "Known limitations" below). Whether those commands actually execute is gated by the **agent's own permission system**, not by anything in this repo. Review an agent's tool-use permissions before granting it broad shell or network access, regardless of which skills are installed.

## Reporting a security concern

If you believe a skill in this repo contains misleading, unsafe, or malicious instructions, please open a [GitHub issue](https://github.com/wakqasahmed/php-laravel-filament-skills/issues) on this repository.

For a report you'd prefer not to make public initially, use [GitHub's private vulnerability reporting](https://github.com/wakqasahmed/php-laravel-filament-skills/security/advisories/new) on this repo instead.

## Known limitations

- `skills/php/principles/SKILL.md` instructs the agent to run `composer audit`.
- `skills/laravel/conventions/SKILL.md` instructs the agent to run `php artisan test`, `php artisan route:list`, `php artisan about`, and `vendor/bin/pint` (or `duster`).
- `skills/filament/conventions/SKILL.md` instructs the agent to run affected Pest/feature tests.
- `skills/filament/plugin-first/SKILL.md` instructs the agent to search external sites (`filamentphp.com/plugins`, `github.com/spekulatius/awesome-filament`, `packagist.org`, GitHub code search) when evaluating plugins, and to run `composer show`, `composer why`, and `php artisan about`.

None of these commands are executed by this repo itself — they are recommendations for the agent to carry out under its own permission model, in the context of the project it's operating on.
