# PR #2 quality review

This follow-up addresses the checks reported for `59a670c2652ae90002adeb30da49bc204a48f35c` without changing Sonar configuration or suppressing findings.

## Timer failures are observable

Blender timer callbacks can print an exception and still exit successfully. The GUI persistence verifier now has a separate validation function and a reusable report boundary. The launcher accepts a stage only when all of these hold:

- The child process exits with status zero.
- A new, parseable object report exists (an earlier report is removed before launch).
- `passed` is the boolean `true`, not merely a truthy value.
- The report stage matches the requested launch.

Unit and real child-process regressions intentionally raise an assertion, emit `passed: false`, omit reports, leave stale success reports, produce invalid or mismatched reports, and exit nonzero despite writing success. Each failure is rejected. Report-write failures propagate instead of silently succeeding.

## Developer CLI trust boundary

`--blender` intentionally chooses executable code, `--venv` chooses executable Python/dependencies, and `--test` intentionally executes a Python script. Only trusted developer-controlled inputs are supported. These launchers must not be exposed to untrusted requests. See [Linux development](linux-development.md).

Commands use argument lists and explicit `shell=False`; tests verify spaces and shell punctuation remain literal arguments. The Blender path is now resolved once before both probing and changing the working directory, fixing inconsistent relative-path resolution. Absolute paths and availability checks do **not** certify code as safe or create a sandbox. Windows batch wrappers have separate shell semantics and were not tested here.

The two original command-injection findings require review against this intended local execution boundary if Sonar continues to flag them. No false-positive or reviewed disposition has been applied automatically.

## Maintainability

Keymap cleanup, legacy identity matching, event overlap, conflict discovery/rendering, and CLI orchestration have been split into focused helpers while retaining the existing behavior. Regression tests cover retry after failed cleanup and preservation of unrelated items, unavailable native editors, conflict labels, CLI session failures and test discovery. The added HUD cleanup helper uses snake_case; all repository callers were updated. Repeated F-gesture operator identifiers share a constant. Test assertions use boolean assertions and consistent actual/expected ordering.

The final follow-up renames only the Python classes to `WxzKeymapTypeRefresh` and `PieMeshFGesture`; their explicit `bl_idname` values remain unchanged. Real Blender registration confirmed that Python class names and operator RNA identifiers are independent. Lifecycle lookup now derives the operator RNA identifier from its explicit ID, so an old class object can still find and clean up a replacement after a rename or hot reload. A real-Blender regression verifies old-name registration, new-name replacement, operator invocation, cleanup through the old object, and absence of the transient refresh operator. The existing full-reload test now checks the actual RNA identifier of that transient operator instead of its Python name.

The remaining event-overlap complexity is split into a modifier-overlap helper, and both exception tests prepare their subprocess source before entering the assertion context. No rule, quality profile, security setting, or issue disposition is changed.

## Reproduction

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
python scripts/blender_dev.py --test-all
python scripts/build_extension.py --wheel-dir dist/linux-wheels --output-dir dist/linux
python scripts/test_keymap_persistence.py --profile /path/to/new-isolated-profile
```

The last command requires a real display, performs two GUI launches against the newly built archive, and rejects existing profile directories. No user profile is used. The previous full platform/gesture validation remains documented in [keymap-refactor.md](keymap-refactor.md); this follow-up does not claim Windows or macOS validation.

## Verified in the Linux cloud environment

- Blender 4.3.2 / embedded CPython 3.13.5.
- 137 standard-library unit tests completed: 132 passed, 5 environment-specific skips (28 new tests relative to the previous 109).
- All 18 background integration scripts passed.
- All 26 native keymap UI/RNA tests passed both in background Blender and an isolated real GUI session (2 new tests relative to the previous 24).
- The real GUI persistence write and restart/read stages both returned explicit success for Ctrl J, after repeated feature toggles and module reload.
- The 16 Quick Crease Weight RNA tests also passed in a real GUI session.
- ABI-matched build and extension manifest validation passed; `pip check`, compileall, and `git diff --check` passed.
- Ruff passed for changed Python files except the pre-existing E402 import layout in `parts_addons/m4_tools/__init__.py`; those 10 baseline diagnostics were not disabled or broadened into unrelated cleanup.

The remote Sonar check must be read against the pushed commit before claiming its gate passed. Passing local tests alone does not establish that result.

## Expanded-menu follow-up

Real keyboard/mouse QA reproduced a Shift+E interruption bug: switching to another window with Alt+Tab left the weight modal and HUD active. Alt could first set the preview to zero. `WINDOW_DEACTIVATE` now follows the existing cancel/restore path before reading motion state. Added real-mesh regressions verify restoration of mixed original values after Alt, removal of a newly created preview layer, empty active-modal state, and released edit/HUD references.

The quality follow-up was tested with 138 standard-library unit tests (133 passed, 5 environment-specific skips), 19 background integration scripts including the new operator-name lifecycle test, 26 native keymap UI/RNA tests, and 18 Quick Crease Weight RNA tests. Expanded real-window coverage and final commit/check results are recorded in the accompanying validation report.

### Remaining real-input limitation

Expanded manual input testing found that A in Object Mode and E in Edit Mesh do not reliably open their original `CLICK_DRAG` pies with factory keymaps: A PRESS followed by a 31-pixel mouse move and release selected the scene objects; E with the same gesture started Blender's default extrude modal. Event logs confirmed the press/move/release sequence. These paths must not be reported as passing based on direct `wm.call_menu_pie` calls or RNA draw tests. Their default PRESS actions need a separate, context-aware dispatch design that preserves normal short-key behavior and user/custom bindings; no default or user keymap was disabled or overwritten as a workaround.
