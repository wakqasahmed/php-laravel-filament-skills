# Source and Claim Ledger

Last reviewed: 2026-09-03

Each normative statement in this skillpack citing an ID below can be verified against the linked first-party documentation. Open the source to check the associated instruction. Source pages can change; verify against your installed framework and language versions before production use.

| ID | Publisher | Source | Supports |
|---|---|---|---|
| `LARAVEL-ELOQUENT-01` | Laravel | [Eloquent: Mutators & Casting (Mass Assignment)](https://laravel.com/docs/eloquent-mutators#mass-assignment) | Mass-assignment protection via `$fillable` (allowlist) and `$guarded` (denylist); danger of `$request->all()` into model writes; bypassing with `forceFill()` / `forceCreate()`; validating input via Form Requests (`$request->validated()`) before passing to `create()`/`update()`. |
| `LARAVEL-SECURITY-CSRF-01` | Laravel | [CSRF Protection](https://laravel.com/docs/csrf) | Automatic CSRF token generation and verification via `ValidateCsrfToken` middleware; `@csrf` Blade directive for HTML forms; explicit URI exclusion for external webhooks. |
| `LARAVEL-BLADE-XSS-01` | Laravel | [Blade Templates (Displaying Data)](https://laravel.com/docs/blade#displaying-data) | Automatic XSS escaping with `{{ $var }}` (passing output through PHP `htmlspecialchars` with UTF-8); risks of unescaped data via `{!! $var !!}`; requirement to sanitize or strip tags when unescaped HTML output is strictly required. |
| `LARAVEL-AUTHORIZATION-01` | Laravel | [Authorization (Gates & Policies)](https://laravel.com/docs/authorization) | Separating identity authentication from record authorization; route-model binding ownership validation; controller action checks via `$this->authorize()`, `Gate::authorize()`, and `authorizeResource()`. |
| `LARAVEL-ROUTING-CONTROLLERS-01` | Laravel | [Controllers & Routing](https://laravel.com/docs/controllers) | Single-action controllers using `__invoke()`, RESTful resource controllers, explicit route-model binding, and offloading validation to Form Requests. |
| `LARAVEL-TESTING-DB-01` | Laravel | [Database Testing](https://laravel.com/docs/database-testing) | Resetting test database state with `RefreshDatabase` trait (migrating once per run, resetting in transaction) vs. `DatabaseTransactions` on persistent migrated test databases. |
| `LARAVEL-TESTING-FAKES-01` | Laravel | [Mocking & Fakes](https://laravel.com/docs/mocking) | Stubbing external framework interactions with `Http::fake()`, `Mail::fake()`, `Queue::fake()`, `Event::fake()`, `Notification::fake()`, and `Storage::fake()`; testing async workflows without real network or infrastructure. |
| `FILAMENT-SCHEMAS-01` | Filament | [Filament Documentation: Schemas & Panels](https://filamentphp.com/docs) | Declarative panel, resource, form, and table schemas; schema configuration and class layout; defining form components, table columns, filters, and actions declaratively. |
| `LIVEWIRE-LIFECYCLE-01` | Livewire | [Livewire Documentation: Lifecycle Hooks](https://livewire.laravel.com/docs/lifecycle-hooks) | Livewire request lifecycle: initial render execution in `mount()`; rehydration in `hydrate()`; property mutation hooks (`updatedFoo()`); teardown and snapshotting in `dehydrate()`; `wire:key` DOM diffing and remount semantics. |
| `LIVEWIRE-BINDING-01` | Livewire | [Livewire Documentation: Wire Model](https://livewire.laravel.com/docs/wire-model) | `wire:model` client-to-server synchronization; deferred binding by default; `.live` modifier with default 150ms debounce; `.blur` modifier for change-on-unfocus. |
| `PHP-TYPING-01` | PHP Group | [PHP Manual: Type Declarations](https://www.php.net/manual/en/language.types.declarations.php) | Native property types, return types, parameter types, union types, and nullable types; constructor property promotion; strict typing with `declare(strict_types=1)`. |

## Which skills cite this ledger

| Skill | IDs cited |
|---|---|
| [`laravel-security`](skills/laravel/laravel-security/SKILL.md) | `LARAVEL-ELOQUENT-01`, `LARAVEL-SECURITY-CSRF-01`, `LARAVEL-BLADE-XSS-01`, `LARAVEL-AUTHORIZATION-01` |
| [`laravel-conventions`](skills/laravel/laravel-conventions/SKILL.md) | `LARAVEL-ROUTING-CONTROLLERS-01`, `LARAVEL-ELOQUENT-01`, `LARAVEL-AUTHORIZATION-01` |
| [`laravel-testing`](skills/laravel/laravel-testing/SKILL.md) | `LARAVEL-TESTING-DB-01`, `LARAVEL-TESTING-FAKES-01` |
| [`filament-conventions`](skills/filament/filament-conventions/SKILL.md) | `FILAMENT-SCHEMAS-01` |
| [`livewire-conventions`](skills/filament/livewire-conventions/SKILL.md) | `LIVEWIRE-LIFECYCLE-01`, `LIVEWIRE-BINDING-01` |
| [`php-principles`](skills/php/php-principles/SKILL.md) | `PHP-TYPING-01` |
