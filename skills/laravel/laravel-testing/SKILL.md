---
name: laravel-testing
description: Follow Pest testing conventions, factory/seeder patterns, and test-database safety before writing or running Laravel tests. Use when writing feature/unit tests, generating test data, or running the test suite.
---

# Laravel Testing

Use this when writing, changing, or running tests in a Laravel codebase.

## Test-Database Safety — Non-Negotiable

- Tests must run against disposable storage or a dedicated test database whose name **clearly contains `test`** (e.g. `app_test`, `myapp_testing`). Never run tests against staging, production, demo, or any shared operational database.
- Verify `phpunit.xml` / `.env.testing` points at a test-only connection before running the suite for the first time in a new environment. Sqlite in-memory (`:memory:`) is the safest default for fast feature/unit tests when the app doesn't rely on database-specific SQL.
- If a test requires a real MySQL/PostgreSQL instance (e.g. testing vendor-specific SQL), the connection's database name must still contain `test` — do not point `DB_DATABASE` at a copy of production data to "make tests realistic."
- Never seed a test run from a staging/production backup. Build realistic data with factories/seeders instead (see below).
- This rule overrides convenience. A fast local hack that points tests at a real environment is not an acceptable shortcut, even temporarily.

## Pest Conventions

- Prefer Pest's functional syntax (`it('does x', function () { ... })` or `test('...', function () { ... })`) over PHPUnit class-based tests for new test files.
- Use `expect()` assertions (`expect($value)->toBe(...)`, `->toBeTrue()`, `->toContain(...)`) instead of raw PHPUnit `assert*` calls — they read closer to the behavior being described and chain cleanly.
- Use `beforeEach()` for setup shared across `it()` blocks in a file instead of repeating the same arrange steps in every test.
- Use datasets (`->with([...])`) when the same assertion needs to run against multiple inputs, instead of copy-pasting near-identical tests.
- Group related tests with `describe()` blocks when a file covers multiple behaviors of the same subject, so failures are easy to locate by name.
- Name tests by behavior, not by method (`it('rejects an order with no line items')`, not `it('tests store method')`).

## Factories And Seeders

- Use model factories (`SomeModel::factory()`) to generate realistic per-test data. Every Eloquent model that's exercised in tests should have a factory with sensible fake defaults.
- Use `->state([...])` (or a named state method) to express variants (`User::factory()->admin()->create()`) instead of overriding raw attributes inline at every call site.
- Use `->count(n)` / `->has()` / `->for()` to build related records through factories rather than manually looping and creating child models.
- Reserve seeders (`database/seeders/`) for baseline data a test run needs to exist regardless of the specific test — reference/lookup tables, roles, permissions. Do not use seeders to create the per-test fixtures a single test needs; that's what factories are for.
- Keep factory definitions deterministic enough that `->create()` never violates a unique constraint or FK by default; use `fake()` helpers for varying fields, not hardcoded values that collide across tests.

## Feature Vs Unit Test Boundaries

- **Feature tests** exercise the full request lifecycle: HTTP routes, middleware, controllers, validation, and the database, via `$this->get(...)`, `$this->post(...)`, `$this->actingAs(...)`, etc. Use these for anything a user or API consumer can trigger — confirm the observable behavior (status code, response shape, database state, dispatched jobs/events), not internal implementation details.
- **Unit tests** isolate a single class or method with no framework bootstrapping beyond what's needed — a service class, a value object, a calculation, a trait's behavior. Use these for logic with meaningful branching or edge cases that doesn't need HTTP/DB to verify.
- Default to a feature test when in doubt: it proves the behavior a user actually depends on. Reach for a unit test when a feature test would be slow or indirect for testing pure logic (e.g. a pricing calculator with a dozen edge cases) — write one feature test for the integration and unit tests for the edge cases.
- Don't unit-test framework glue (a Form Request that just calls `$this->authorize()` and returns `true`, a thin controller that delegates to a service) — a feature test covering the endpoint already proves it works.

## RefreshDatabase Vs DatabaseTransactions

- Use `RefreshDatabase` by default for feature tests that touch the database — it migrates once per test run and resets state between tests, giving a clean, predictable database for every test.
- Use `DatabaseTransactions` instead only when the schema is already guaranteed present and stable (e.g. a persistent test database migrated out-of-band) and the overhead of `RefreshDatabase`'s migration/seeding step is a proven bottleneck — it wraps each test in a transaction and rolls back after, which is faster but assumes the schema doesn't change between tests.
- Never disable both and rely on manual cleanup; a test that leaks state into the next test is a bug, not an optimization.
- If a test spans multiple database connections (e.g. testing a queue-backed job against a separate connection), verify the trait actually resets all connections used — `RefreshDatabase` only resets the connections it's configured for.

## Mocking And Faking External Services

- Never let a test hit real infrastructure: no live HTTP calls, no real emails sent, no real queue jobs dispatched to a live worker, no real third-party API calls (payment gateways, SMS, etc.).
- Use Laravel's fakes for framework-native async work: `Queue::fake()` / `Bus::fake()` before asserting a job was dispatched, `Mail::fake()` before asserting a mailable was sent, `Event::fake()` for events, `Notification::fake()` for notifications, `Storage::fake('disk')` for file uploads.
- Use `Http::fake([...])` to stub outbound HTTP calls to third-party APIs; assert on the request shape with `Http::assertSent(...)` rather than trusting the call happened.
- For external SDKs that don't go through Laravel's `Http` facade (a vendor SDK client), bind a fake/mock implementation via the service container in the test, or wrap the SDK behind an interface the app already depends on so it can be swapped in tests.
- A test that requires network access or a live third-party sandbox to pass is not a unit or feature test — it's an integration/smoke test and belongs in a separate, explicitly-labeled suite that isn't run on every `php artisan test`.

## Verification

- Run `php artisan test --filter=<Name>` for the tests affected by a change; run the full suite only when asked or before a release gate.
- Confirm the active database connection during test runs is the disposable/test one (see Test-Database Safety above) before trusting results from a new environment.
