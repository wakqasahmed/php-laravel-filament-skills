---
name: laravel-security
description: Harden Laravel/PHP code against mass-assignment, SQL injection, XSS, CSRF, and authorization bypass. Use when writing or reviewing models, controllers, raw queries, Blade views, or any endpoint that accepts user input.
---

# Laravel Security

Use this when writing or reviewing code that touches user input, models, raw queries, Blade output, or authorization.

This pack has no evidence/citation registry (no `SOURCES.md`-equivalent exists in this repo). The guidance below is written directly from Laravel's documented behavior; if a claim needs a citation for a specific PR, verify it against the installed framework version rather than assuming an ID exists here.

## Mass Assignment

- `$fillable`/`$guarded` control what `Model::create()`/`update()`/`fill()` accept, but they are not the first line of defense — a Form Request that only allows specific validated keys through is. Never pass `$request->all()` into `fill()`/`create()`/`update()`; pass `$request->validated()` (or an explicit array) so an attacker can't add unexpected keys the request happens to receive even if the model's fillable list is later loosened.
- `forceFill()` and `forceCreate()` bypass `$fillable`/`$guarded` entirely. Only use them for trusted, hardcoded internal values (e.g. system-set fields in a job or seeder) — never with any value derived from request input.
- Mass assignment risk isn't limited to the model being written directly. `update([...])` calls through a relationship (`$user->posts()->create($request->validated())`) inherit the related model's fillable list, so a validated array that happens to include a foreign key or owner column (e.g. `user_id`) can let a caller reassign a record to another owner. Keep relationship-scoped writes to only the columns that relationship should ever set — validate the request against an explicit allowlist, not the model's full fillable set.
- Prefer `$fillable` (allowlist) over `$guarded` for any model reachable from user input. `protected $guarded = []` disables mass-assignment protection entirely — treat it as equivalent to no protection, not a stricter default.

## SQL Injection

- Eloquent and the query builder parameterize bindings by default (`where('email', $value)`, `whereIn`, etc.) — prefer them over raw SQL for anything touching user input.
- `DB::raw()`, `whereRaw()`, `havingRaw()`, `orderByRaw()`, and `selectRaw()` insert the string you give them directly into the query. Any of these built with string interpolation or concatenation of user input is a SQL injection vector: `DB::raw("name = '$name'")` and `orderByRaw("$column $direction")` are both exploitable if `$name`/`$column`/`$direction` come from a request.
- If a raw clause is unavoidable, pass user values as bindings, not interpolated strings: `whereRaw('price > ?', [$minPrice])` or `whereRaw('price > :min', ['min' => $minPrice])`. Bindings are parameterized even inside a raw clause.
- Dynamic column and table names (sort column, sort direction, groupable field) can never be safely parameterized — bindings only work for values, not identifiers. Allowlist the identifier against a fixed set of permitted values before use, never interpolate the request value directly: `$column = in_array($request->sort, ['name', 'created_at']) ? $request->sort : 'created_at';` then use `$column` in `orderBy()`/`orderByRaw()`.
- Treat any `DB::raw()`/`*Raw()` call in review as a place that needs an explicit justification for why the builder couldn't express it, plus confirmation every interpolated value is either a binding or an allowlisted identifier.

## Blade XSS

- `{{ $value }}` HTML-escapes output automatically — this is the default and correct choice for any user-controllable string.
- `{!! $value !!}` prints raw, unescaped HTML. Only use it for content the application itself controls or that has been sanitized through a dedicated HTML purifier (e.g. rendering trusted CMS/rich-text content stored after purification) — never for a raw request value, a user's display name, a comment, or anything else an end user typed without a sanitization step in between.
- If a feature genuinely needs to render user-authored HTML (rich text editor output, markdown-to-HTML), sanitize it server-side with an allowlist-based purifier before storage or before render — don't rely on trusting the client-side editor to only produce safe markup.
- `{{ }}` inside `<script>` tags, HTML attributes without quotes, or `href`/`src` attributes still needs context-appropriate escaping; Blade's default escaping covers HTML body context, not every sink — be deliberate when interpolating into JS or URL contexts.

## CSRF

- Every state-changing form rendered by Blade must include `@csrf`; `VerifyCsrfToken` middleware (in the `web` group) rejects POST/PUT/PATCH/DELETE requests without a matching token.
- Routes are legitimately excluded from CSRF verification for endpoints that can't carry a session-bound token — primarily inbound webhooks (Stripe, payment gateways, third-party callbacks) added to the `except` array in `VerifyCsrfToken` (or `validateCsrfTokens(except: [...])` in Laravel 11+ bootstrap).
- A CSRF exclusion is only safe if the route verifies the request some other way. For webhooks, that means signature verification (e.g. Stripe's `Stripe-Signature` header verified against the raw payload and the webhook secret) on every request before any side effect runs — never leave an excluded route trusting the payload solely because it "looks like" it came from the expected source. If a route is CSRF-excluded and has no independent authenticity check, that's a bug, not an accepted tradeoff.

## Authorization Bypass

- Route-model binding resolving a model by ID proves the record exists — it proves nothing about whether the current user is allowed to see or modify it. A controller method that accepts `Post $post` via binding and never calls `$this->authorize('update', $post)` (or an equivalent policy check) is vulnerable to IDOR: any authenticated user can change the URL's ID and reach another user's resource.
- Every controller action that reads or mutates a specific record must have an explicit authorization check tied to that record — `$this->authorize()`, `Gate::authorize()`, a policy method invoked directly, or `authorizeResource()` for full resource controllers. "The route required auth" is not the same as "the route checked ownership."
- Form Requests should authorize inside `authorize()` using the bound route model (`$this->route('post')`), not just return `true` unconditionally — a Form Request with `authorize() { return true; }` provides validation but zero access control, and it's easy to mistake its presence for an authorization check.
- In Filament, prefer policies (`viewAny`, `view`, `update`, `delete`, etc.) registered against the model over inline `->visible()`/`->hidden()` closures for gating actions — inline closures are easy to get inconsistent across resource, relation manager, and bulk actions, while a policy is enforced everywhere Filament checks authorization automatically. See `filament-conventions` for the broader "policies over inline gate checks" convention this extends.
- When in doubt, treat "does this record belong to/is this action permitted for the current user" as a separate question from "does this record exist" — resolve existence via binding, resolve permission via an explicit policy check, every time.

## Verification

- Run the affected feature/Pest tests, including tests that assert a non-owner/unauthorized user gets a 403 (or equivalent) on protected routes, not just that an authorized user succeeds.
- For any new or changed raw query, write a test with an adversarial input (e.g. a value containing `'`, `--`, or SQL keywords) and assert it doesn't alter query behavior.
- Run `vendor/bin/pint --dirty` (or project equivalent) after changes.
