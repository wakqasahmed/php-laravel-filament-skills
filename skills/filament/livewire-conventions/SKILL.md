---
name: livewire-conventions
description: Reason about Livewire component lifecycle, state, and performance when Filament's declarative API isn't enough. Use when writing custom Livewire components inside a Filament panel, debugging state that resets or fails to sync, or diagnosing wire:model performance problems.
---

# Livewire Conventions

Filament's resources, forms, tables, and widgets are Livewire components under the hood. Most
Filament work stays inside the declarative schema/table API and never needs this skill. Reach
for it when building a custom Livewire component for a Filament page, a plugin, or a heavily
customized action/widget — and when debugging state or performance issues that trace back to
Livewire's request/render cycle rather than to Filament's API.

## When to stay in Filament vs. drop to raw Livewire

- Stay declarative (forms, table columns/actions, widgets) for anything the schema API already
  expresses: fields, validation, relationships, filters, bulk actions, KPI widgets.
- Drop to a custom Livewire component when you need: a UI element with no Filament equivalent,
  fine-grained control over partial re-renders, a component that must be embedded outside a
  Filament page (e.g. a public-facing page), or plugin authoring that extends Filament's own
  base components.
- Filament's own form fields, table columns, and pages are Livewire components; reading
  `vendor/filament/filament/src` for a similar built-in component is often the fastest way to
  learn the right pattern before writing one from scratch (see `filament-plugin-first`).

## Component Lifecycle

Livewire re-instantiates the component class on every request (initial load and every subsequent
interaction) and rehydrates its public properties from the client-side snapshot. Understand which
hook runs when:

- `mount()` — runs once, only on the component's initial render (the first HTTP request that
  creates it). Use it to set up initial public property state from route params, models, or
  defaults. Never rely on `mount()` running again after an update — it won't.
- `hydrate()` — runs on every subsequent request, before the property values are restored,
  letting you react to the component being rebuilt. Rarely needed directly; Filament resources
  use lifecycle interfaces (`HasForms`, `InteractsWithTable`) that hook in here for you.
- Action/update methods (`updatedFoo()`, action handlers) — run after a property changes via
  `wire:model` or after a called method, on the request that carries that interaction.
- `dehydrate()` — runs at the end of every request, after render, to snapshot public property
  state back to the client for the next round trip.
- `render()` — runs on every request that touches the component, producing the HTML diff sent
  back to the browser.

The practical consequence for a Filament developer: anything not stored as a public property (or
persisted to the database/session) does not survive between requests. If state "resets"
unexpectedly after an action, check whether it lives in a public property vs. a local variable
computed only during `mount()`. If state "won't update", check whether the property is actually
bound with `wire:model` (or explicitly set from a listener) rather than assumed to update itself.

## `wire:model` performance

`wire:model` triggers a full round trip to the server (network request, component rehydration,
re-render, DOM diff/patch) on the configured event:

- `wire:model.live` — fires on every `input` event, i.e. every keystroke. This is a real
  performance problem on anything with meaningful per-keystroke cost: components with expensive
  `render()` queries, large tables, or components nested inside other stateful components that
  also re-render. Avoid it on free-text fields unless you specifically need live validation or a
  live-filtering UI and have confirmed the render cost is cheap.
- Deferred binding (the default, unmodified `wire:model`) — batches the value client-side and
  only sends it with the next network request the component makes anyway (e.g. a button click,
  another `wire:model.live` field, or `wire:submit`). This is almost always the right default for
  form inputs: no network chatter while typing, value is still current when an action actually
  fires.
- `wire:model.blur` — sends the update on blur. A middle ground when you want the value synced
  before the user leaves the field (e.g. for validation feedback) without a request per keystroke.
- `wire:model.live.debounce.500ms` — for cases that genuinely need live updates (search-as-you-type,
  live filters) but shouldn't fire on every keystroke; debounce collapses rapid keystrokes into one
  request.

Filament form fields default to deferred/lazy behavior appropriate to their use; only override
this when you have a specific reason (e.g. a live-search field or a field that drives conditional
visibility of other fields via `->live()`).

## Nested component state pitfalls

- **Public properties don't auto-sync from parent to child.** Passing a value into a child
  component's constructor/`mount()` only sets its initial value; if the parent's property changes
  later, the child does not automatically pick up the new value unless you explicitly re-key or
  re-render the child, or pass the value via an event/listener instead of relying on prop-drilling.
- **`wire:key` controls whether Livewire treats an element as the same instance or a new one.**
  When rendering a list of nested components (or list items with their own local state) without
  a unique, stable `wire:key` per item, Livewire's DOM diffing can reuse the wrong element after
  the list changes — surfacing as state "leaking" between rows, wrong item being edited, or
  animations/inputs pointing at the wrong record. Always key dynamic/looped components on a
  stable identifier (e.g. the model's primary key), not the loop index.
- **Changing `wire:key` forces a full remount.** This is the deliberate escape hatch when you
  want a child component to fully reset (rerun `mount()`) in response to a parent value changing
  — e.g. keying a form component on a record ID so switching records gives you a clean component
  instance instead of stale state.
- In Filament specifically, this shows up when customizing repeaters, table row actions with
  embedded Livewire components, or relation manager tables: if a custom sub-component inside a
  repeated block behaves inconsistently after add/remove/reorder, suspect a missing or
  index-based `wire:key` before suspecting Filament itself.

## Filament panel context for custom components

A custom Livewire component embedded in a Filament panel (a custom page, an infolist/table
extension, or a plugin) runs inside Filament's authorization and asset context, not a bare
Livewire context:

- Filament panel pages enforce authorization via policies/`canAccess()` checks at the page and
  resource level. A raw Livewire component embedded inside a panel page does not automatically
  inherit fine-grained authorization for its own actions — guard sensitive actions/methods on the
  component explicitly (e.g. `Gate::authorize()` or a policy check) rather than assuming the
  panel's page-level check covers everything the component does.
- Filament loads its own CSS/JS asset bundle and expects components to register additional assets
  (custom JS, Alpine components, CSS) through Filament's asset registration APIs (e.g.
  `FilamentAsset::register()`) rather than raw `@livewireStyles`/manual asset tags, so the assets
  load correctly within the panel's layout and are versioned/cached consistently with the rest of
  the panel.
- Custom components should extend/implement the same conventions Filament's own components use
  (`HasForms`, `InteractsWithForms`, etc.) when they need to embed a Filament schema, rather than
  reimplementing form state handling — mixing raw Livewire property binding with a Filament schema
  in the same component is a common source of the "properties won't sync" pitfall above.

## Verification

- Confirm the installed Livewire major version (`composer show livewire/livewire`) before relying
  on version-specific lifecycle hook names or attribute syntax — check the project's own
  `vendor/livewire/livewire` source or changelog if behavior seems off, since hook names and
  some binding modifiers have changed across major versions.
- Manually reproduce the interaction in the browser and check the network tab: verify a
  `wire:model.live` field is producing a request per keystroke, and confirm deferred fields only
  send their value with the next real action.
- For nested/looped components, test add/remove/reorder operations and confirm each item's state
  stays attached to the correct record, not the render position.
