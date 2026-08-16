# Filament plugin-first outcome evaluation

`bash run-eval.sh --dry-run` is the offline PR-CI layer. It validates the
non-negotiable skill contract in `SKILL.md` and the held-out/tuning corpus
shape and separation. It does not score agent behavior.

`run_harness.py` is the explicitly gated model evaluation. It runs every
held-out case in enabled and disabled conditions for three to six trials.
Each fresh Docker workspace receives only the target agent, adapter, prompt,
and (for enabled trials) the skill. The container has no network, no ambient
credentials, an empty home, a read-only root filesystem, and no repository
mount.

`filament-plugin-first` is a decision-triage skill, not a code-generation
contract: given a Filament feature request plus synthetic ecosystem search
results (candidate packages with maintenance, license, version, and price
metadata baked into the case), the target agent must return structured JSON
naming which candidate it chose (or that it is building from scratch) and the
`primary_reason` that justified the choice. The validator independently
compares both the visible response and the internal artifact to the
fixture-owned expected outcome. It does not use skill-loading metadata as an
outcome signal.

Safety is scored separately from outcome. `is_safe()` scans the full
observable output — not just the declared `chosen_candidate` field — for any
mention of a candidate the case marks unsafe (abandoned, license-incompatible,
or paid-without-approval). This is deliberately independent of
`outcome_matches()`: a response can name the correct candidate while still
surfacing an unsafe one elsewhere, or vice versa. Aliasing the safety check to
the outcome check would make the aggregate safety-regression gate a no-op.

Enabled trials must pass at least 80% for every case, improve aggregate
outcome rate by at least 10 percentage points over disabled trials, and not
regress safety. Failed evaluation means retire or revise the skill. Results
are kept for 90 days by the manual workflow.

Held-out fixtures are synthetic and split 5 should-use triage cases against 5
should-not-use/near-miss/safety cases (2 trivial built-in-component
over-triggering checks, 3 cases where the most feature-complete candidate is
unsafe and must be rejected in favor of a safe alternative). Keep any future
sanitized real traces and tuning cases outside `fixtures/held-out.json`.
