"""Build and validate the Blender extension in the repository's dist directory."""

import argparse
from pathlib import Path
import subprocess
import tomllib


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", default="blender", help="Blender executable (default: blender on PATH)")
    args = parser.parse_args()

    with (ROOT / "blender_manifest.toml").open("rb") as manifest_file:
        manifest = tomllib.load(manifest_file)
    archive = DIST / f"{manifest['id']}-{manifest['version']}.zip"
    command = [args.blender, "--background", "--factory-startup", "--command", "extension"]

    DIST.mkdir(exist_ok=True)
    subprocess.run(
        [*command, "build", "--source-dir", str(ROOT), "--output-dir", str(DIST)],
        cwd=ROOT,
        check=True,
    )
    subprocess.run([*command, "validate", str(archive)], cwd=ROOT, check=True)
    print(f"Built and validated: {archive}")


if __name__ == "__main__":
    main()
