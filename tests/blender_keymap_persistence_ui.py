"""GUI-only persistence regression. Run twice with same isolated BLENDER_USER_CONFIG.
First: --python this_file -- write
Second: --python this_file -- read
It changes only the isolated test profile, saves it and exits Blender.
"""

import importlib
import json
import os
import sys
from pathlib import Path
import addon_utils
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
MODE = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "write"
RESULT = Path(bpy.utils.user_resource("CONFIG")) / ("keymap-" + MODE + ".json")


def run():
    try:
        repo_path = os.environ.get("WXZ_TEST_EXTENSION_REPO")
        if repo_path:
            repo = next(repo for repo in bpy.context.preferences.extensions.repos if repo.directory == repo_path)
            package = f"bl_ext.{repo.module}.wxz_pie_menus"
        else:
            package = ROOT.name
        # A restart test must inspect the automatically loaded extension first;
        # enabling it a second time would test an additional full reload instead.
        addon = sys.modules.get(package) if addon_utils.check(package)[1] else None
        if addon is None:
            if MODE == "read":
                raise AssertionError("Saved extension failed to load automatically at startup")
            addon = addon_utils.enable(package, default_set=True)
        assert addon is not None
        addon._lifecycle.set_enabled("F_pie", True)
        kc = bpy.context.window_manager.keyconfigs
        kc.update()

        def effective():
            matches = [k for k in kc.user.keymaps["Mesh"].keymap_items if k.idname == "pie.mesh_f_gesture"]
            assert len(matches) == 1, len(matches)
            return matches[0]

        if MODE == "write":
            k = effective()
            k.type = "J"
            k.ctrl = True
            kc.update()
        assert (effective().type, effective().ctrl) == ("J", 1), (effective().type, effective().ctrl)
        for i in range(3):
            addon._lifecycle.set_enabled("F_pie", False)
            kc.update()
            addon._lifecycle.set_enabled("F_pie", True)
            kc.update()
            assert (effective().type, effective().ctrl) == ("J", 1)
        F = importlib.import_module(package + ".pie.F_pie")
        F.unregister()
        importlib.reload(F)
        F.register()
        kc.update()
        assert (effective().type, effective().ctrl) == ("J", 1)
        if MODE == "write":
            bpy.ops.wm.save_userpref()
        RESULT.parent.mkdir(parents=True, exist_ok=True)
        RESULT.write_text(
            json.dumps({"passed": True, "stage": MODE, "key": effective().type, "ctrl": bool(effective().ctrl)})
        )
        print("PASS: user custom Ctrl J survives feature toggles, module reload, stage", MODE)
    except Exception:
        import traceback

        RESULT.parent.mkdir(parents=True, exist_ok=True)
        RESULT.write_text(json.dumps({"passed": False, "error": traceback.format_exc()}))
        traceback.print_exc()
    bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(run, first_interval=1.0)
