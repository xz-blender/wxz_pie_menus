"""Exercise Blender's real restricted-context add-on enable/disable path offline."""
import sys
from pathlib import Path

import addon_utils
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))


def repository_snapshot():
    return [(repo.name, repo.module, repo.remote_url, repo.enabled, repo.use_sync_on_startup)
            for repo in bpy.context.preferences.extensions.repos]


before = repository_snapshot()
for cycle in range(2):
    errors = []
    addon = addon_utils.enable(ROOT.name, default_set=True, handle_error=lambda: errors.append(sys.exc_info()))
    assert addon is not None, errors
    assert not errors, errors
    try:
        assert addon_utils.check(ROOT.name)[1]
        statuses = [addon._lifecycle.status(module.__name__.rsplit(".", 1)[-1]) for module in addon.all_modules]
        assert all(not status.errors for status in statuses), statuses
        assert all(status.state.value == ("active" if status.desired else "disabled")
                   for status in statuses), statuses
        assert repository_snapshot() == before, "Enabling must not create or change extension repositories"
    finally:
        addon_utils.disable(ROOT.name, default_set=True)
    assert not addon_utils.check(ROOT.name)[1]
    assert all(addon._lifecycle.status(module.__name__.rsplit(".", 1)[-1]).state.value == "disabled"
               for module in addon.all_modules), "Feature cleanup incomplete"
    assert repository_snapshot() == before
    print(f"PASS: real addon_utils.enable/disable, module states, unchanged repositories, cycle {cycle + 1}")
