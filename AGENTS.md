# PHP, Laravel, and Filament Skills

Reusable technical guidance for PHP engineering, Laravel conventions, and Filament admin panel development.

## Trigger Map

- Use `php-principles` when designing classes, refactoring logic, adding dependencies, or reviewing PHP code.
- Use `laravel-conventions` when adding routes, controllers, models, validation, or background work in a Laravel project.
- Use `laravel-security` when writing or reviewing code that touches user input, models, raw queries, Blade views, or authorization.
- Use `laravel-testing` when writing or running tests, generating test data, or deciding feature-vs-unit boundaries in a Laravel project.
- Use `filament-plugin-first` before building custom Filament components.
- Use `filament-conventions` when adding or changing Filament resources, forms, tables, actions, or widgets.
- Use `livewire-conventions` when building custom Livewire components for Filament panels, debugging state synchronization issues, or diagnosing wire:model performance.

## Summary

- Prefer typed, tested, small classes with clear responsibilities.
- Follow Laravel conventions before reaching for custom solutions.
- Harden endpoints against mass-assignment, SQL injection, XSS, CSRF, and authorization bypass by default.
- Search the Filament plugin ecosystem before writing non-trivial components from scratch.
- Prefer Filament's declarative API before writing custom Livewire components.
- Verify changes with the minimum relevant test and lint commands.
