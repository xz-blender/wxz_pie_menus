from pathlib import Path

_IMPORT_NAME_OVERRIDES = {
    "pillow": "PIL",
    "opencv_python": "cv2",
    "opencv-python": "cv2",
    "fonttools": "fontTools",
    "typing_extensions": "typing_extensions",
}


def _parse_wheels_from_manifest() -> dict:
    manifest_path = Path(__file__).resolve().parents[2] / "blender_manifest.toml"
    result = {}
    if not manifest_path.exists():
        return result

    in_wheels = False
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("wheels"):
            in_wheels = True
            continue
        if in_wheels:
            if stripped == "]":
                break
            if ".whl" in stripped:
                whl = stripped.strip(' ",')
                filename = whl.rsplit("/", 1)[-1]
                pkg_name = filename.split("-")[0]
                pkg_name_normalized = pkg_name.replace("-", "_").lower()
                import_name = _IMPORT_NAME_OVERRIDES.get(
                    pkg_name_normalized,
                    _IMPORT_NAME_OVERRIDES.get(pkg_name.lower(), pkg_name_normalized),
                )
                result[pkg_name] = import_name
    return result


PIP_Packeges_Dict = _parse_wheels_from_manifest()
