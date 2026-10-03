"""Encode native Blender captures for the README; requires FFmpeg on PATH."""

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path, help="Output directory from capture_blender.py")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--font", type=Path, default=Path("C:/Windows/Fonts/segoeui.ttf"))
    args = parser.parse_args()
    raw = args.raw.resolve()
    output = Path(__file__).resolve().parent
    if not args.font.is_file():
        parser.error("Caption font not found; provide --font with a local TTF file")
    font = args.font.resolve().as_posix().replace(":", r"\:")

    evidence = {}
    for name in ("crease", "f-object", "f-edit", "preferences"):
        evidence[name] = json.loads((raw / f"{name}.json").read_text(encoding="utf-8"))
        if not evidence[name].get("success"):
            raise RuntimeError(f"Capture did not complete: {name}")
        for capture in evidence[name]["captures"]:
            if not (raw / capture).is_file():
                raise FileNotFoundError(raw / capture)
    assert evidence["crease"]["cancel_restored_attribute"]
    assert len(evidence["crease"]["crease_values"]) == 21

    def ffmpeg(*arguments):
        subprocess.run([args.ffmpeg, "-hide_banner", "-loglevel", "error", "-y", *map(str, arguments)], check=True)

    # Captions describe the scene; all menu entries, geometry and HUD are native.
    def frame_filter(caption):
        return (
            "crop=1040:720:200:160,scale=960:-1:flags=lanczos,"
            f"drawtext=fontfile='{font}':text='{caption}':fontsize=23:fontcolor=0xF5BF83:x=28:y=22"
        )

    def still(source, destination, caption):
        ffmpeg("-i", raw / source, "-vf", frame_filter(caption), "-frames:v", "1", output / destination)

    still("f-object.png", "f-object.png", "F  /  OBJECT MODE")
    still("f-edit.png", "f-edit.png", "F  /  EDIT MODE")
    still("crease-007.png", "quick-crease.png", "SHIFT + E  /  EDGE CREASE")
    # Isolate the real preference panel from the temporary test harness chrome.
    ffmpeg("-i", raw / "preferences.png", "-vf", "crop=1180:455:250:130", "-frames:v", "1", output / "preferences.png")

    palette = "split[a][b];[a]palettegen=max_colors=192[p];[b][p]paletteuse=dither=sierra2_4a"
    ffmpeg(
        "-framerate",
        "5",
        "-i",
        raw / "crease-%03d.png",
        "-filter_complex",
        frame_filter("SHIFT + E  /  EDGE CREASE") + "," + palette,
        "-loop",
        "0",
        "-final_delay",
        "100",
        output / "quick-crease.gif",
    )
    with tempfile.TemporaryDirectory(prefix="wxz-readme-gif-") as folder:
        sequence = Path(folder)
        for index, name in enumerate(("f-object.png", "f-edit.png")):
            shutil.copyfile(output / name, sequence / f"{index:02d}.png")
        ffmpeg(
            "-framerate",
            "1/3",
            "-i",
            sequence / "%02d.png",
            "-filter_complex",
            palette,
            "-loop",
            "0",
            "-final_delay",
            "300",
            output / "context-menu.gif",
        )
    for name in (
        "hero.svg",
        "f-object.png",
        "f-edit.png",
        "preferences.png",
        "quick-crease.png",
        "context-menu.gif",
        "quick-crease.gif",
    ):
        file = output / name
        print(f"{name}: {file.stat().st_size / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
