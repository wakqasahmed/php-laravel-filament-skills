---
name: laravel-conventions
description: Follow Laravel conventions before adding routes, controllers, models, validation, or background work. Use when working in a Laravel codebase.
---

# Laravel Conventions

Use this when writing or changing Laravel application code.

## Defaults

- Eloquent over raw SQL unless the query is too complex for the ORM.
- Form Request classes for all validation; never inline validate in controllers.
- `config('key')` instead of `env('KEY')` outside config files.
- Queue jobs (`ShouldQueue`) for anything slow, external, or async.
- Service classes for business logic; keep controllers thin.

## Models

- Use explicit fillable or guarded declarations.
- Define relationships, casts, and scopes on the model.
- Avoid N+1 queries; eager load relationships in resources and controllers.
- Use database transactions when modifying multiple related records.

## Foreign Keys And Migrations

- Match the foreign key column's type exactly to the referenced table's primary key type (`foreignId` for `bigIncrements`/`id()`, not a mismatched `unsignedInteger`).
- Set an explicit `onDelete`/`onUpdate` policy (`cascade`, `restrict`, `nullOnDelete`) — don't leave it at the database default.
- Index every foreign key column and any column used in a frequent `WHERE`/`JOIN`/`ORDER BY`; verify with `php artisan schema:dump` or by reviewing the migration diff against the referenced table before merge.
- Idempotent job handling on retry is covered in Background Work above — apply it to anything a migration or FK change feeds into a queue.

## Validation

- Create a Form Request for every non-trivial store/update endpoint.
- Keep rules declarative; extract reusable rules into custom Rule classes.
- Authorize inside the request, not the controller.

## Configuration

- Centralize environment access in config files.
- Cache config in production; never commit `.env` files.
- Use feature flags or config values instead of environment checks scattered through code.

## Background Work

- Dispatch jobs for external API calls, emails, exports, and heavy computations.
- Use queues with retry limits and failed-job handling.
- Keep job classes single-purpose and idempotent where possible.

## Generated Files

- Use `php artisan make:<type> --no-interaction` for all generated classes (models, requests, jobs, policies, migrations) instead of hand-writing boilerplate.
- Tests must use disposable storage or a dedicated test database whose name contains `test`; never staging, production, or shared operational databases.

## Verification

- Run `php artisan test --filter=<Name>` for affected code.
- Run `php artisan route:list` and `php artisan about` after structural changes.
- Run project linting: `vendor/bin/pint --dirty` (or `duster`, or project equivalent).
