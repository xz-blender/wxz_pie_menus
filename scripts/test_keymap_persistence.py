"""Two real-window Blender launches sharing only a new, isolated test profile."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import zipfile
from blender_dev import ROOT, blender_info, dependency_path, resolve_blender
from blender_test_report import read_report


def run_stage(command, env, profile, stage):
    report = profile / "config" / ("keymap-" + stage + ".json")
    # Never accept a successful report left over from an earlier launch.
    report.unlink(missing_ok=True)
    with (profile / (stage + ".log")).open("w") as log:
        result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, shell=False)
    data = read_report(report, stage, result.returncode)
    print(json.dumps(data))
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", default="blender", help="Trusted executable path or name on PATH")
    parser.add_argument("--profile", type=Path, required=True, help="New directory; never an existing user profile")
    parser.add_argument("--archive", type=Path, default=ROOT / "dist/linux/wxz_pie_menus-0.2.4.zip")
    args = parser.parse_args()
    try:
        blender = resolve_blender(args.blender)
    except RuntimeError as error:
        parser.error(str(error))
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
    env["PYTHONPATH"] = dependency_path(ROOT / ".venv", blender_info(blender))
    env["PYTHONNOUSERSITE"] = "1"
    for stage in ("write", "read"):
        command = [
            blender,
            "--offline-mode",
            "--disable-autoexec",
            "--python-use-system-env",
            "--python-exit-code",
            "1",
        ]
        if stage == "write":
            command.extend(["--factory-startup", "--python", str(setup)])
        command.extend(["--python", str(ROOT / "tests/blender_keymap_persistence_ui.py"), "--", stage])
        run_stage(command, env, profile, stage)
    print("PASS: native user mapping persists through toggles, reload and restart:", profile)


if __name__ == "__main__":
    main()
