"""Run Blender with ABI-matched development dependencies and disposable preferences."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MARKER = "WXZ_PYTHON_INFO="


def blender_info(blender):
    expression = (
        "import json,sys,platform,bpy; print('" + MARKER + "'+json.dumps({"
        "'python':list(sys.version_info[:3]),'executable':sys.executable,"
        "'machine':platform.machine(),'blender':bpy.app.version_string}))"
    )
    output = subprocess.check_output(
        [blender, "--background", "--factory-startup", "--offline-mode", "--python-exit-code", "1",
         "--python-expr", expression], text=True,
    )
    for line in output.splitlines():
        if line.startswith(MARKER):
            return json.loads(line[len(MARKER):])
    raise RuntimeError("Blender did not report its Python interpreter")


def dependency_path(venv, info):
    executable = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not executable.is_file():
        raise RuntimeError(f"Missing {executable}; see docs/linux-development.md")
    data = json.loads(subprocess.check_output([
        str(executable), "-c", "import sys,sysconfig,json,platform; print(json.dumps({"
        "'python':list(sys.version_info[:2]),'machine':platform.machine(),"
        "'site':sysconfig.get_path('purelib')}))",
    ], text=True))
    if data["python"] != info["python"][:2] or data["machine"] != info["machine"]:
        raise RuntimeError(f"Blender/venv ABI mismatch: Blender {info}, venv {data}")
    return data["site"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", default="blender")
    parser.add_argument("--venv", type=Path, default=ROOT / ".venv")
    parser.add_argument("--info", action="store_true", help="Report Blender's actual Python before creating a venv")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--test", type=Path, help="Run a Blender integration script")
    group.add_argument("--test-all", action="store_true", help="Run all non-UI integration scripts")
    parser.add_argument("--ui", action="store_true", help="Open a real window; requires a display")
    args = parser.parse_args()
    info = blender_info(args.blender)
    print(json.dumps(info, indent=2), flush=True)
    if args.info:
        return 0
    site = dependency_path(args.venv.resolve(), info)
    tests = sorted((ROOT / "tests").glob("blender_*.py")) if args.test_all else [args.test]
    if args.test_all:
        tests = [path for path in tests if not path.stem.endswith("_ui")]
    failed = []
    for test in tests:
        with tempfile.TemporaryDirectory(prefix="wxz-blender-") as directory:
            env = os.environ.copy()
            for kind in ("CONFIG", "SCRIPTS", "DATAFILES", "EXTENSIONS"):
                path = Path(directory) / kind.lower()
                path.mkdir()
                env[f"BLENDER_USER_{kind}"] = str(path)
            env["PYTHONNOUSERSITE"] = "1"
            env["PYTHONPATH"] = site
            command = [args.blender, "--factory-startup", "--offline-mode", "--disable-autoexec",
                       "--python-use-system-env", "--python-exit-code", "1"]
            if not args.ui:
                command.append("--background")
            else:
                command.append("--enable-event-simulate")
            if test:
                command.extend(["--python", str(test.resolve())])
            else:
                command.extend(["--python-expr", f"import sys,addon_utils; sys.path.insert(0,{str(ROOT.parent)!r}); "
                                f"addon_utils.enable({ROOT.name!r}, default_set=True)"])
            print("RUN:", test or "isolated add-on session", flush=True)
            result = subprocess.run(command, cwd=ROOT, env=env)
            if result.returncode:
                failed.append(str(test or "session"))
    if failed:
        print("FAILED:", ", ".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
