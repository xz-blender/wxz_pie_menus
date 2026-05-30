from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None


ROOT_DIR = Path(__file__).resolve().parents[1]
WHEELS_DIR = ROOT_DIR / "wheels"
MANIFEST_PATH = ROOT_DIR / "blender_manifest.toml"
VENV_PYTHON = ROOT_DIR / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

WHEELS = (
    "requests",
    "shapely",
    "pillow",
)


def run(cmd: list[str | Path]) -> None:
    print("+", " ".join(str(part) for part in cmd), flush=True)
    subprocess.run([str(part) for part in cmd], check=True)


def ensure_venv_python() -> None:
    if not VENV_PYTHON.exists():
        raise SystemExit(f"Missing virtualenv Python: {VENV_PYTHON}")


def ensure_pip() -> None:
    result = subprocess.run(
        [str(VENV_PYTHON), "-m", "pip", "--version"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        return

    run([VENV_PYTHON, "-m", "ensurepip", "--upgrade"])


def download_wheels(packages: tuple[str, ...]) -> None:
    WHEELS_DIR.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="_wheel_download_", dir=WHEELS_DIR) as temp_dir:
        temp_path = Path(temp_dir)
        run(
            [
                VENV_PYTHON,
                "-m",
                "pip",
                "download",
                "--only-binary=:all:",
                "--dest",
                temp_path,
                *packages,
            ]
        )

        downloaded_wheels = sorted(temp_path.glob("*.whl"))
        if not downloaded_wheels:
            raise SystemExit("pip did not download any wheel files")

        for wheel in WHEELS_DIR.glob("*.whl"):
            wheel.unlink()

        for wheel in downloaded_wheels:
            shutil.move(str(wheel), str(WHEELS_DIR / wheel.name))


def manifest_wheel_paths() -> list[str]:
    return [f"wheels/{wheel.name}" for wheel in sorted(WHEELS_DIR.glob("*.whl"))]


def wheels_block(paths: list[str]) -> str:
    if not paths:
        raise SystemExit("No wheel files found to write into blender_manifest.toml")

    lines = ["wheels = ["]
    lines.extend(f'  "{path}",' for path in paths)
    lines.append("]")
    return "\n".join(lines)


def is_wheels_assignment(line: str) -> bool:
    stripped = line.strip()
    if "=" not in stripped:
        return False

    key, _value = stripped.split("=", 1)
    return key.strip() == "wheels"


def replace_wheels_assignment(text: str, block: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    index = 0
    replaced = False

    while index < len(lines):
        line = lines[index]

        if not replaced and is_wheels_assignment(line):
            output.extend(block.splitlines())
            replaced = True

            bracket_depth = line.count("[") - line.count("]")
            index += 1
            while bracket_depth > 0 and index < len(lines):
                bracket_depth += lines[index].count("[") - lines[index].count("]")
                index += 1
            continue

        output.append(line)
        index += 1

    if not replaced:
        if output and output[-1].strip():
            output.append("")
        output.extend(block.splitlines())

    return "\n".join(output) + "\n"


def update_manifest() -> None:
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"Missing manifest: {MANIFEST_PATH}")

    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    updated_text = replace_wheels_assignment(manifest_text, wheels_block(manifest_wheel_paths()))

    if tomllib is not None:
        tomllib.loads(updated_text)

    MANIFEST_PATH.write_text(updated_text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download project wheels and update blender_manifest.toml.")
    parser.add_argument(
        "packages",
        nargs="*",
        help="Packages to download. Defaults to the WHEELS tuple in this script.",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Only refresh blender_manifest.toml from existing wheels/*.whl files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    packages = tuple(args.packages) or WHEELS

    if not args.manifest_only:
        ensure_venv_python()
        ensure_pip()
        download_wheels(packages)

    update_manifest()

    print(f"Updated {MANIFEST_PATH.relative_to(ROOT_DIR)}")
    for path in manifest_wheel_paths():
        print(f"  {path}")


if __name__ == "__main__":
    main()
