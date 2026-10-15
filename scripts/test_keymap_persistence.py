"""Two real-window Blender launches sharing only a new, isolated test profile."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import zipfile
from blender_dev import ROOT, blender_info, dependency_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", default="blender")
    parser.add_argument("--profile", type=Path, required=True, help="New directory; never an existing user profile")
    parser.add_argument("--archive", type=Path, default=ROOT / "dist/linux/wxz_pie_menus-0.2.4.zip")
    args = parser.parse_args()
    if not args.archive.is_file():
        parser.error("Build the ABI-matched extension archive first")
    profile = args.profile.resolve()
    if profile.exists():
        parser.error("Use a new empty profile path; existing profiles are never changed")
    profile.mkdir(parents=True)
    env = os.environ.copy()
    for kind in ("CONFIG", "SCRIPTS", "DATAFILES", "EXTENSIONS"):
        path = profile / kind.lower()
        path.mkdir()
        env["BLENDER_USER_" + kind] = str(path)
    repo = profile / "extension-repo"
    target = repo / "wxz_pie_menus"
    target.mkdir(parents=True)
    with zipfile.ZipFile(args.archive) as archive:
        archive.extractall(target)
    env["WXZ_TEST_EXTENSION_REPO"] = str(repo)
    setup = profile / "setup-extension.py"
    setup.write_text(
        "import bpy\n"
        f"bpy.ops.preferences.extension_repo_add(name='WXZ Test', type='LOCAL', "
        f"use_custom_directory=True, custom_directory={str(repo)!r})\n"
    )
    env["PYTHONPATH"] = dependency_path(ROOT / ".venv", blender_info(args.blender))
    env["PYTHONNOUSERSITE"] = "1"
    for stage in ("write", "read"):
        command = [
            args.blender,
            "--offline-mode",
            "--disable-autoexec",
            "--python-use-system-env",
            "--python-exit-code",
            "1",
        ]
        if stage == "write":
            command.extend(["--factory-startup", "--python", str(setup)])
        command.extend(["--python", str(ROOT / "tests/blender_keymap_persistence_ui.py"), "--", stage])
        with (profile / (stage + ".log")).open("w") as log:
            result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
        report = profile / "config" / ("keymap-" + stage + ".json")
        if result.returncode or not report.exists():
            raise RuntimeError(f"{stage} startup failed; see {profile}")
        data = json.loads(report.read_text())
        print(json.dumps(data))
        if not data.get("passed"):
            raise RuntimeError(f"{stage} assertions failed; see {profile}")
    print("PASS: native user mapping persists through toggles, reload and restart:", profile)


if __name__ == "__main__":
    main()
