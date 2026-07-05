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

## Verification

- Run `php artisan test --filter=<Name>` for affected code.
- Run `php artisan route:list` and `php artisan about` after structural changes.
- Run project linting (`pint`, `duster`, or equivalent).
