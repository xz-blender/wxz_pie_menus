import site
import subprocess
import sys
from pathlib import Path

import bpy

RETRUNCODE_DICT = {
    0: "成功",
    1: "通用错误",
    2: "误用 shell 命令",
    126: "命令不可执行",
    127: "命令未找到",
    128: "无效的参数",
}

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _resolve_python_bin() -> str:
    try:
        base = Path(bpy.utils.system_resource("PYTHON"))
        candidates = [
            base / "bin" / "python.exe",
            base / "bin" / "python",
            base / "bin" / f"python{sys.version_info.major}.{sys.version_info.minor}",
        ]
        for c in candidates:
            if c.exists():
                return str(c)
    except Exception:
        pass

    return sys.executable


python_bin = _resolve_python_bin()
app_path = site.getusersitepackages()
site.addsitedir(app_path)


def build_pip_command(*cmds, run_module="pip", use_china_mirror=False) -> list[str]:
    cmds = [c for c in cmds if c is not None]
    if run_module == "pip" and cmds and cmds[0] == "install" and "--no-warn-script-location" not in cmds:
        cmds = [cmds[0], "--no-warn-script-location", *cmds[1:]]
    command = [python_bin, "-m", run_module, *cmds]
    if use_china_mirror and run_module == "pip":
        command += ["-i", "https://mirrors.aliyun.com/pypi/simple/"]
    return command


def run_pip_command(*cmds, run_module="pip", use_china_mirror=False, debug=False, clear_output=True):
    """使用 user site 命令运行 PIP 进程"""
    pip_output = bpy.context.scene.PIE_pip_output

    if clear_output:
        pip_output.RETRUNCODE_OUTPUT = ""
        pip_output.ERROR_OUTPUT.clear()
        pip_output.TEXT_OUTPUT.clear()

    command = build_pip_command(*cmds, run_module=run_module, use_china_mirror=use_china_mirror)

    output = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )

    pip_output.RETRUNCODE_OUTPUT = RETRUNCODE_DICT.get(output.returncode, "其他错误")
    for line in output.stderr.splitlines():
        if line.strip() == "":
            continue
        item = pip_output.ERROR_OUTPUT.add()
        item.line = line

    for line in output.stdout.splitlines():
        if line.strip() == "":
            continue
        item = pip_output.TEXT_OUTPUT.add()
        item.line = line

    if debug:
        print(">>> run_pip_command调试信息 <<<")
        print("RUN_CMD:", command)
        print(">>> 返回代码 :\n", output.returncode)
        print(">>> 输出信息 :\n", output.stdout)
        print(">>> STD信息 :\n", output.stderr)
    return output.returncode


def _persistent_console_lines(text: str) -> list[str]:
    return text.replace("\r\n", "\n").replace("\r", "\n").splitlines(keepends=True)


def _print_command_output_line(line: str) -> None:
    if not line:
        return
    prefix = "" if line.startswith("[WXZ PIP]") else "[WXZ PIP] "
    end = "" if line.endswith("\n") else "\n"
    print(f"{prefix}{line}", end=end, flush=True)


def run_command_capture(
    command: list[str],
    cwd: Path | None = None,
    env: dict | None = None,
    cancel_event=None,
    on_process=None,
) -> dict:
    command_text = " ".join(command)
    cwd_text = str(cwd) if cwd is not None else ""
    print(f"[WXZ PIP] Running command: {command_text}", flush=True)
    if cwd_text:
        print(f"[WXZ PIP] Working directory: {cwd_text}", flush=True)

    process = subprocess.Popen(
        command,
        cwd=str(cwd) if cwd is not None else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
        env=env,
        bufsize=1,
    )
    if on_process is not None:
        on_process(process)
    if cancel_event is not None and cancel_event.is_set() and process.poll() is None:
        process.terminate()
    output_lines: list[str] = []
    if process.stdout is not None:
        with process.stdout:
            for chunk in process.stdout:
                if cancel_event is not None and cancel_event.is_set() and process.poll() is None:
                    process.terminate()
                for line in _persistent_console_lines(chunk):
                    output_lines.append(line)
                    _print_command_output_line(line)
    returncode = process.wait()
    cancelled = bool(cancel_event is not None and cancel_event.is_set())
    stdout = "".join(output_lines)
    if cancelled:
        print(f"[WXZ PIP] Command cancelled: {command_text}", flush=True)
    elif returncode != 0:
        print(f"[WXZ PIP] Command failed with code {returncode}: {command_text}", flush=True)
    else:
        print(f"[WXZ PIP] Command finished: {command_text}", flush=True)
    return {
        "command": command_text,
        "cwd": cwd_text,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stdout if returncode != 0 else "",
        "cancelled": cancelled,
    }


def internal_command_result(label: str, stdout: str = "", stderr: str = "", returncode: int = 0) -> dict:
    return {
        "label": label,
        "command": "internal",
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
    }


def write_command_results_to_pip_output(results: list[dict]) -> None:
    pip_output = bpy.context.scene.PIE_pip_output
    pip_output.RETRUNCODE_OUTPUT = ""
    pip_output.ERROR_OUTPUT.clear()
    pip_output.TEXT_OUTPUT.clear()

    failed = [r for r in results if r.get("returncode", 1) != 0]
    pip_output.RETRUNCODE_OUTPUT = "成功" if not failed else RETRUNCODE_DICT.get(failed[-1]["returncode"], "其他错误")

    for result in results:
        title = pip_output.TEXT_OUTPUT.add()
        title.line = f">>> {result.get('label', 'pip')}"
        for line in str(result.get("stdout", "")).splitlines():
            if line.strip():
                item = pip_output.TEXT_OUTPUT.add()
                item.line = line
        for line in str(result.get("stderr", "")).splitlines():
            if line.strip():
                item = pip_output.ERROR_OUTPUT.add()
                item.line = line
