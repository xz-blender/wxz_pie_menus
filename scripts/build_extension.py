"""Build and validate the extension, optionally using an isolated set of wheels."""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def replace_manifest_wheels(text: str, paths: list[str]) -> str:
    """Replace the root wheels assignment without changing other manifest values."""
    manifest = tomllib.loads(text)
    if not isinstance(manifest.get("wheels"), list):
        raise ValueError("The source manifest must contain a wheels list")

    match = re.search(r"(?m)^[ \t]*wheels[ \t]*=", text)
    if match is None:
        raise ValueError("Could not find the source manifest's wheels assignment")

    block = "wheels = [\n" + "".join(f"  {json.dumps(path, ensure_ascii=False)},\n" for path in paths) + "]\n"
    end = match.start()
    for line in text[match.start():].splitlines(keepends=True):
        end += len(line)
        try:
            assignment = tomllib.loads(text[match.start():end])
        except tomllib.TOMLDecodeError:
            continue
        if set(assignment) != {"wheels"}:
            break
        updated = text[:match.start()] + block + text[end:]
        if tomllib.loads(updated) != {**manifest, "wheels": paths}:
            break
        return updated
    raise ValueError("Could not replace the source manifest's wheels assignment safely")


def stage_source(root: Path, destination: Path, wheel_dir: Path) -> None:
    """Copy source and supplied wheels into a disposable build tree."""
    root = root.resolve()
    wheel_dir = wheel_dir.resolve()
    if not wheel_dir.is_dir():
        raise ValueError(f"Wheel directory does not exist: {wheel_dir}")
    wheels = sorted(path for path in wheel_dir.glob("*.whl") if path.is_file())
    if not wheels:
        raise ValueError(f"No wheel files found in: {wheel_dir}")

    ignore_generated = shutil.ignore_patterns(
        ".git", ".venv", "dist", "__pycache__", ".cache", ".pytest_cache", ".ruff_cache", ".mypy_cache",
        "*.pyc", "*.pyo",
    )

    def ignore(directory, names):
        ignored = set(ignore_generated(directory, names))
        directory = Path(directory)
        if directory == root / "wheels":
            ignored.update(name for name in names if name.endswith(".whl"))
        # A prepared directory may live inside the checkout. Do not bundle a
        # second copy alongside the wheels selected for the staged manifest.
        ignored.update(name for name in names if directory / name == wheel_dir and wheel_dir != root / "wheels")
        return ignored

    shutil.copytree(root, destination, ignore=ignore)
    staged_wheels = destination / "wheels"
    staged_wheels.mkdir(exist_ok=True)
    for wheel in wheels:
        shutil.copyfile(wheel, staged_wheels / wheel.name)

    manifest_path = destination / "blender_manifest.toml"
    updated = replace_manifest_wheels(
        manifest_path.read_text(encoding="utf-8"),
        [f"wheels/{wheel.name}" for wheel in wheels],
    )
    manifest_path.write_text(updated, encoding="utf-8")


@contextmanager
def build_source(wheel_dir: Path | None):
    if wheel_dir is None:
        yield ROOT
        return
    with tempfile.TemporaryDirectory(prefix="wxz-extension-") as directory:
        source = Path(directory) / ROOT.name
        stage_source(ROOT, source, wheel_dir)
        yield source


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", default="blender", help="Blender executable (default: blender on PATH)")
    parser.add_argument(
        "--wheel-dir", type=Path,
        help="Prepared directory of *.whl files for the target Blender Python/platform; stage without changing source",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=DIST,
        help="Archive destination (default: repository dist directory)",
    )
    args = parser.parse_args(argv)

    command = [args.blender, "--background", "--factory-startup", "--command", "extension"]
    output_dir = args.output_dir.resolve()
    try:
        with build_source(args.wheel_dir) as source:
            with (source / "blender_manifest.toml").open("rb") as manifest_file:
                manifest = tomllib.load(manifest_file)
            archive = output_dir / f"{manifest['id']}-{manifest['version']}.zip"
            output_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [*command, "build", "--source-dir", str(source), "--output-dir", str(output_dir)],
                cwd=ROOT,
                check=True,
            )
            subprocess.run([*command, "validate", str(archive)], cwd=ROOT, check=True)
    except ValueError as error:
        parser.error(str(error))
    print(f"Built and validated: {archive}")


if __name__ == "__main__":
    main()
