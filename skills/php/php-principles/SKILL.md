---
name: php-principles
description: Apply core PHP engineering principles before writing new code. Use when designing classes, refactoring logic, adding dependencies, or reviewing PHP code.
---

# PHP Principles

Use this when writing or reviewing PHP code in any project.

## Defaults

- Prefer typed properties, parameters, and return types.
- Favor composition over inheritance.
- Keep classes small and focused on one responsibility.
- Avoid global state and static helpers that hide dependencies.
- Write unit tests for pure logic; use integration tests at boundaries.

## DRY

- Extract duplication only after the third similar occurrence, or when the duplicate is non-trivial.
- Do not DRY prematurely; similar code with different reasons to change should stay separate.
- Shared logic belongs in a named class or trait with a clear responsibility, not copied inline.

## SOLID — applied as review smells

Flag these instead of reciting the principles:

- A class name containing "Manager", "Helper", or "Service" doing three unrelated things → split by reason to change.
- A growing `match`/`if` chain switching on type → extract an interface and move each branch into an implementation.
- A subclass that throws on, no-ops, or narrows an inherited method → the hierarchy is wrong; prefer composition.
- An interface forcing empty method implementations on consumers → split into role-specific interfaces.
- A class calling `new` on collaborators it doesn't own, or reaching for a facade inside domain logic → inject the dependency.

## Dependency Hygiene

- Pin versions in `composer.json` with care; avoid `*` constraints.
- Verify a package's maintenance, license, and issue load before adding it.
- Prefer well-maintained standards over trendy micro-packages.
- Run `composer audit` after adding or updating dependencies.

## Verification

- Static analysis passes: `vendor/bin/phpstan analyse` (or `vendor/bin/psalm`), at the project's configured level.
- Affected tests pass: `vendor/bin/pest --filter=<Name>` or `vendor/bin/phpunit --filter=<Name>`.
- `composer audit` is clean after dependency changes.
- No new warnings in CI.
