# Laravel security outcome evaluation

`bash eval/laravel/laravel-security/run-eval.sh --dry-run` is the offline PR-CI layer. It validates the
non-negotiable skill contract in `SKILL.md` and the held-out/tuning corpus
shape and separation. It does not score agent behavior.

`run_harness.py` is the explicitly gated model evaluation. It runs every
held-out case in enabled and disabled conditions for three to six trials.
Each fresh Docker workspace receives only the target agent, adapter, prompt,
and (for enabled trials) the skill. The container has no network, no ambient
credentials, an empty home, a read-only root filesystem, and no repository
mount.

`laravel-security` is a security hardening and vulnerability review skill:
given a Laravel input handling, query execution, Blade template, CSRF, or authorization request, the target agent
must return structured JSON naming its `decision` (`enforce_security`, `refactor_vulnerability`, or `preserve_existing`),
the `chosen_pattern`, and the `primary_reason` justifying the choice. The validator
independently compares both the visible response and the internal artifact to the
fixture-owned expected outcome. It does not use skill-loading metadata as an
outcome signal.

Safety is scored separately from outcome. `is_safe()` scans the full
observable output for any mention of security vulnerabilities the case marks unsafe
(e.g., passing `$request->all()`, raw SQL interpolation, unpurified `{!! !!}` echoes, IDOR bypasses, unverified webhooks, or empty guarded arrays).

Enabled trials must pass at least 80% for every case, improve aggregate
outcome rate by at least 10 percentage points over disabled trials, and not
regress safety. Failed evaluation means retire or revise the skill. Results
are kept for 90 days by the manual workflow.

Held-out fixtures are split 5 should-use cases against 5 should-not-use / near-miss / safety cases.
Keep any future sanitized real traces and tuning cases outside `fixtures/held-out.json`.
