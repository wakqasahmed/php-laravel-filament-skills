# PHP, Laravel, and Filament Skills [![skills.sh](https://skills.sh/b/wakqasahmed/php-laravel-filament-skills)](https://skills.sh/wakqasahmed/php-laravel-filament-skills)

Reusable technical skills for PHP engineering, Laravel conventions, and Filament admin panel development.

## Skills

- `php-principles` — core PHP engineering principles: DRY, SOLID, typing, dependency hygiene.
- `laravel-conventions` — Laravel defaults for models, validation, config, queues, and controllers.
- `laravel-security` — mass-assignment, SQL injection, Blade XSS, CSRF, and authorization bypass hardening.
- `filament-plugin-first` — search the Filament plugin ecosystem before building custom components.
- `filament-conventions` — Filament patterns for resources, forms, tables, actions, widgets, and multi-tenancy.
- `livewire-conventions` — Livewire component lifecycle, `wire:model` performance, and nested state pitfalls for custom Filament components.

## Install

```bash
npx skills@latest add wakqasahmed/php-laravel-filament-skills
```

## Security

Skills are markdown instruction files, not executable code — see [SECURITY.md](SECURITY.md) for what that means, how to report a concern, and known limitations.

## Scope

This pack is intentionally narrow: it covers the PHP → Laravel → Filament stack. General engineering workflow guidance belongs in `ai-engineering-workflow-skills`.

## Marketplace And Discovery

- Public install command: `npx skills@latest add wakqasahmed/php-laravel-filament-skills`
- skills.sh page: `https://skills.sh/wakqasahmed/php-laravel-filament-skills`
- GitHub repo: `https://github.com/wakqasahmed/php-laravel-filament-skills`

## Verification

Each skill names the minimum verification commands. Run the smallest relevant checks for the layer you changed:

- PHP logic: static analysis + unit tests
- Laravel changes: feature tests + `php artisan about`
- Filament changes: feature tests + render checks
