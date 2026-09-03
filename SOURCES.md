# Source and Claim Ledger

Last reviewed: 2026-09-03

Each normative statement in this skillpack citing an ID below can be verified against the linked first-party documentation. Open the source to check the associated instruction. Source pages can change; verify against your installed framework and language versions before production use.

| ID | Publisher | Source | Supports |
|---|---|---|---|
| `LARAVEL-ELOQUENT-01` | Laravel | [Eloquent: Mass Assignment (Laravel 12.x)](https://laravel.com/docs/12.x/eloquent#mass-assignment) | Mass-assignment protection via `$fillable` and `$guarded`; the risk of unexpected request fields passed to `create()`; and hand-crafting arrays passed to `fill()`, `create()`, and `update()` when a model is unguarded. |
| `LARAVEL-SECURITY-CSRF-01` | Laravel | [CSRF Protection](https://laravel.com/docs/csrf) | Automatic CSRF token generation and verification via `ValidateCsrfToken` middleware; `@csrf` Blade directive for HTML forms; explicit URI exclusion for external webhooks. |
| `LARAVEL-BLADE-XSS-01` | Laravel | [Blade Templates (Displaying Data)](https://laravel.com/docs/blade#displaying-data) | Automatic XSS escaping with `{{ $var }}` (passing output through PHP `htmlspecialchars` with UTF-8); risks of unescaped data via `{!! $var !!}`; requirement to sanitize or strip tags when unescaped HTML output is strictly required. |
| `LARAVEL-AUTHORIZATION-01` | Laravel | [Authorization (Laravel 10.x): Authorizing Resource Controllers](https://laravel.com/docs/10.x/authorization#authorizing-resource-controllers) | Controller authorization via `$this->authorize()` and `Gate::authorize()`; in Laravel 10 resource controllers, `authorizeResource()` attaches the corresponding `can` middleware to controller methods. |
| `LARAVEL-ROUTING-CONTROLLERS-01` | Laravel | [Controllers & Routing](https://laravel.com/docs/controllers) | Single-action controllers using `__invoke()`, RESTful resource controllers, explicit route-model binding, and offloading validation to Form Requests. |
| `LARAVEL-MIGRATIONS-01` | Laravel | [Migrations: Forcing Production Migrations](https://laravel.com/docs/12.x/migrations#forcing-migrations-to-run-in-production); [Configuration: Maintenance Mode](https://laravel.com/docs/12.x/configuration#maintenance-mode) | Production migration commands prompt before potentially destructive operations unless `--force` is supplied; maintenance mode is controlled with `artisan down` / `up`, with secret bypasses and pre-rendered templates available. |
| `LARAVEL-QUEUES-01` | Laravel | [Queues: Unique Jobs](https://laravel.com/docs/12.x/queues#unique-jobs); [Queues: Worker Timeouts](https://laravel.com/docs/12.x/queues#worker-timeouts) | `ShouldBeUnique` suppresses dispatch while the same unique job lock is held; timeout and `retry_after` configuration can otherwise cause a job to be processed twice. |
| `LARAVEL-TESTING-DB-01` | Laravel | [Database Testing: Resetting the Database](https://laravel.com/docs/12.x/database-testing#resetting-the-database-after-each-test) | `RefreshDatabase` resets state and, when the schema is current, runs tests in transactions instead of migrating again; `DatabaseMigrations` and `DatabaseTruncation` perform a total reset at higher cost. |
| `LARAVEL-TESTING-FAKES-01` | Laravel | [Events: Testing](https://laravel.com/docs/12.x/events#testing); [Mail: Testing Mailable Sending](https://laravel.com/docs/12.x/mail#testing-mailable-sending); [Notifications: Testing](https://laravel.com/docs/12.x/notifications#testing); [Queues: Testing](https://laravel.com/docs/12.x/queues#testing) | `Event::fake()`, `Mail::fake()`, `Notification::fake()`, `Queue::fake()`, and `Bus::fake()` prevent the corresponding listeners, deliveries, or jobs from running while allowing dispatch assertions. |
| `LARAVEL-HTTP-TESTING-01` | Laravel | [HTTP Client: Testing](https://laravel.com/docs/12.x/http-client#testing) | Stubbing outbound HTTP responses with `Http::fake()`, inspecting requests with `Http::assertSent()`, and preventing stray requests. |
| `LARAVEL-STORAGE-TESTING-01` | Laravel | [File Storage: Testing](https://laravel.com/docs/12.x/filesystem#testing) | Creating a temporary test disk with `Storage::fake()` and asserting that files exist or are missing. |
| `FILAMENT-SCHEMAS-01` | Filament | [Filament 4.x Upgrade Guide](https://filamentphp.com/docs/4.x/upgrade-guide); [Filament 4.x Schemas Overview](https://filamentphp.com/docs/4.x/schemas) | Filament v4 migration requirements and automated upgrade tooling; moved schema layout-component namespaces and changed component factory signatures; `Filament\Schemas\Schema` as the v4 container for form, infolist, layout, and action components. |
| `LIVEWIRE-LIFECYCLE-01` | Livewire | [Livewire 3.x: Lifecycle Hooks](https://livewire.laravel.com/docs/3.x/lifecycle-hooks) | Livewire request lifecycle: initial render execution in `mount()`; rehydration in `hydrate()`; property mutation hooks; teardown and snapshotting in `dehydrate()`. |
| `LIVEWIRE-KEYS-01` | Livewire | [Livewire 3.x: Nesting Components](https://livewire.laravel.com/docs/3.x/nesting#forcing-a-child-component-to-re-render) | Stable keys track nested components across renders; changing a child component key discards the old instance and re-initializes it from scratch. |
| `LIVEWIRE-BINDING-01` | Livewire | [Livewire Documentation: Wire Model](https://livewire.laravel.com/docs/wire-model) | `wire:model` client-to-server synchronization; deferred binding by default; `.live` modifier with default 150ms debounce; `.blur` modifier for change-on-unfocus. |
| `PHP-TYPING-01` | PHP Group | [PHP Manual: Type Declarations](https://www.php.net/manual/en/language.types.declarations.php) | Native property, return, and parameter types; union and nullable types; strict typing with `declare(strict_types=1)`. |
| `PHP-CONSTRUCTOR-PROMOTION-01` | PHP Group | [PHP Manual: Constructor Promotion](https://www.php.net/manual/en/language.oop5.decon.php#language.oop5.decon.constructor.promotion) | Constructor property promotion, available from PHP 8.0, declares and assigns a property from a promoted constructor parameter. |
| `PHP-ENUMS-01` | PHP Group | [PHP Manual: Enumerations](https://www.php.net/manual/en/language.types.enumerations.php) | Enumerations, available from PHP 8.1, define a closed set of possible values for a type. |

## Which skills cite this ledger

| Skill | IDs cited |
|---|---|
| [`laravel-security`](skills/laravel/laravel-security/SKILL.md) | `LARAVEL-ELOQUENT-01`, `LARAVEL-SECURITY-CSRF-01`, `LARAVEL-BLADE-XSS-01`, `LARAVEL-AUTHORIZATION-01` |
| [`laravel-conventions`](skills/laravel/laravel-conventions/SKILL.md) | `LARAVEL-ROUTING-CONTROLLERS-01`, `LARAVEL-ELOQUENT-01`, `LARAVEL-AUTHORIZATION-01`, `LARAVEL-MIGRATIONS-01`, `LARAVEL-QUEUES-01` |
| [`laravel-testing`](skills/laravel/laravel-testing/SKILL.md) | `LARAVEL-TESTING-DB-01`, `LARAVEL-TESTING-FAKES-01`, `LARAVEL-HTTP-TESTING-01`, `LARAVEL-STORAGE-TESTING-01` |
| [`filament-conventions`](skills/filament/filament-conventions/SKILL.md) | `FILAMENT-SCHEMAS-01` |
| [`livewire-conventions`](skills/filament/livewire-conventions/SKILL.md) | `LIVEWIRE-LIFECYCLE-01`, `LIVEWIRE-KEYS-01`, `LIVEWIRE-BINDING-01` |
| [`php-principles`](skills/php/php-principles/SKILL.md) | `PHP-TYPING-01`, `PHP-CONSTRUCTOR-PROMOTION-01`, `PHP-ENUMS-01` |
