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

## Production Migration Safety

- Take a database backup immediately before running any migration that drops a column/table, renames a column, or transforms data in place. A destructive migration with no preceding backup is not deployable — document the backup step in the PR or deploy runbook, not just in your head.
- `php artisan migrate` refuses to run against an environment where `app.env` is `production` unless you pass `--force`. Treat that prompt as a guardrail, not friction to script around — never bake `--force` into a deploy step that isn't gated by its own review/approval (CI job, deploy script) that a human or protected pipeline controls.
- For any migration with meaningful table-lock time (adding an index or column to a large table, an unbounded `UPDATE` inside a migration) or any downtime-sensitive change, put the app in maintenance mode first: `php artisan down --secret=...` before, `php artisan up` after. Prefer `php artisan down --render="errors::503"` (or a custom view) over a bare 503, and confirm the app supports zero-downtime alternatives (online DDL tools, additive-then-backfill-then-cleanup migrations) before assuming `down` is required.
- MySQL DDL (`ALTER TABLE`, `CREATE TABLE`, `DROP TABLE`) is not transactional — unlike PostgreSQL, a failed statement partway through a multi-statement migration can leave the schema partially applied, and Laravel's migration wrapping transaction will not roll back the already-committed DDL. Keep migrations small and single-purpose (one schema change per migration) so a failure is easy to diagnose and the blast radius is one operation, not five.
- Test the migration's `down()` locally (`php artisan migrate:rollback`) before merging, not just `up()`. Do not ship a migration you can't cleanly reverse; if a migration is genuinely irreversible (e.g. it drops a column with data that isn't recoverable from the backup taken above), leave `down()` throwing `\RuntimeException` with a one-line explanation instead of a silent no-op, so a future rollback attempt fails loud instead of pretending to succeed.
- Never let a migration silently truncate or drop data as a side effect of a schema change (e.g. changing a column type in a way that MySQL will truncate on conversion) without an explicit backup step called out in the PR description or deploy checklist.

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
