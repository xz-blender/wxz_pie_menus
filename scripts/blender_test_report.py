"""Fail-closed reports for Blender timer callbacks, whose exceptions do not exit Blender."""

import json
import traceback


def write_report(check, report, stage):
    """Capture an explicit validation failure for the parent process to reject.

    Assertions belong in ``check``. Blender timer exceptions alone do not reliably
    affect the process exit code, so the launcher must also validate this report.
    Failure to write the report propagates; the launcher rejects a missing report.
    """
    try:
        details = check()
    except Exception:
        data = {"passed": False, "stage": stage, "error": traceback.format_exc()}
        traceback.print_exc()
    else:
        data = {**details, "passed": True, "stage": stage}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(data), encoding="utf-8")


def read_report(report, stage, returncode):
    """Accept only a successful process and an explicit, matching success report."""
    if returncode:
        raise RuntimeError(f"{stage} Blender exited with status {returncode}; see {report.parent.parent}")
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise RuntimeError(f"{stage} report missing or invalid: {report}") from error
    if not isinstance(data, dict) or data.get("passed") is not True or data.get("stage") != stage:
        raise RuntimeError(f"{stage} validation failed or report mismatched: {data!r}; see {report}")
    return data
