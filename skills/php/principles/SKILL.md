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

## SOLID

- **S**ingle Responsibility: one reason to change per class.
- **O**pen/Closed: extend behavior without modifying existing code.
- **L**iskov Substitution: derived types must honor the base contract.
- **I**nterface Segregation: small, role-specific interfaces beat large generic ones.
- **D**ependency Inversion: depend on abstractions, inject concrete implementations.

## Dependency Hygiene

- Pin versions in `composer.json` with care; avoid `*` constraints.
- Verify a package's maintenance, license, and issue load before adding it.
- Prefer well-maintained standards over trendy micro-packages.
- Run `composer audit` after adding or updating dependencies.

## Verification

- Static analysis passes (`phpstan`, `psalm`, or project equivalent).
- Tests cover new behavior and existing tests still pass.
- No new warnings in CI.
