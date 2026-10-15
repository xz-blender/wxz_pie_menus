# Linux 开发环境（会话重建）

## 来源和验证边界

本变更从仓库基线 `1dd9a2f90fc24a676c7f2aae0253250cb68ad90e` 重建此前 Linux 适配；不是此前临时构建产物的逐字节恢复。验证以本次源码和重新运行的测试为准。菜单快捷键重构说明见 [keymap-refactor.md](keymap-refactor.md)。

新环境 Blender 4.3.2 实际嵌入 CPython 3.13.5（终端默认 Python 3.12）。已重新建立隔离 .venv，依赖固定到 uv.lock。运行依赖 NumPy 2.3.4、Pillow 12.0.0、Shapely 2.1.2、Requests 2.32.5；开发工具 Ruff 0.14.0、pip 25.2。

## 建立与运行

```sh
python scripts/blender_dev.py --info
UV_CACHE_DIR=/tmp/wxz-uv-cache uv sync --locked --python /usr/bin/python3.13
.venv/bin/python -m pip check
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
python scripts/blender_dev.py --test-all
python scripts/blender_dev.py --ui
```

解释器路径以 --info 的实际输出为准；不要按 Blender 版本猜 Python ABI。项目允许 Python 3.11–3.13，并不代表已跨版本验证。启动器验证 venv 与 Blender Python 主/次版本及架构匹配，使用 factory-startup、离线模式、禁用自动脚本，且将配置/脚本/数据/扩展目录重定向到临时目录。不会保存日常 Blender 偏好。

开发启动器的信任边界：`--blender`、`PATH`、`--venv` 和 `--test` 必须由开发者选择并信任；这些输入可以执行本地代码，隔离偏好和离线模式并不是安全沙箱。`--blender` 支持 PATH 中的程序名及相对/绝对可执行路径（包括空格），在启动前解析为同一个绝对路径，避免后续切换工作目录后运行不同程序。子进程使用参数列表及显式 `shell=False`，不拼接 shell 命令；这不验证所选程序或测试脚本是否可信。Windows 的 `.bat`/`.cmd` 包装脚本仍可能由系统 shell 处理，只应使用可信包装脚本和参数。

--test-all 排除 *_ui.py。真实显示环境中可单独执行：

```sh
python scripts/blender_dev.py --ui --test tests/blender_quick_crease_weight_ui.py
```

源码临时 sys.path 启用并非正式 bl_ext 扩展安装，可能在 Add-ons 列表显示 Missing Add-ons；正式偏好面板应使用隔离 profile 安装或加载下节 ZIP。

## Linux 资源路径

默认同步与本地资源目录分别为 `$XDG_DATA_HOME/wxz_pie_menus/assets/sync` 和 `.../local`；未设 XDG_DATA_HOME 时使用 `~/.local/share`。桌面从 XDG user-dirs.dirs 读取，无法读取时回退 `~/Desktop`。只给出路径、不自动创建目录或配置同步服务。Windows/macOS 原默认值保持不变。

## 安全构建当前 Linux ABI 的 ZIP

根 manifest 与 wheels 仍保留 Windows 发行依赖。不要运行旧 wheels/_update_wheels.py 来建立 Linux 环境，它会替换原 wheels。

```sh
mkdir -p dist/linux-wheels
uv export --locked --no-dev --no-emit-project --format requirements-txt --output-file dist/linux-requirements.txt
.venv/bin/python -m pip download --only-binary=:all: --index-url https://pypi.org/simple \
  -r dist/linux-requirements.txt --dest dist/linux-wheels
python scripts/build_extension.py --wheel-dir dist/linux-wheels --output-dir dist/linux
```

导出含哈希；仅下载 binary wheels。构建使用临时副本替换 wheel 列表并由 Blender 验证 ZIP，不改原 Windows manifest/wheels。最终包仅适合对应 OS/ABI/架构。依赖安装应在隔离 venv 中完成，不改系统 Python、不使用 --break-system-packages。

## 重建的生命周期修复

- 禁止导入时创建扩展仓库，避免正常 addon_utils.enable 的 _RestrictContext 错误；仓库 ID 改为使用时只读解析。
- 具体 RNA 基类 lookup 返回 None 即终止，不再继续 generic bpy_struct 查询；此前真实扩展禁用后重启用在该处段错误。
- M4 Focus HUD 初始化幂等，停用时取消 timer 并移除 draw handler，防止重复启停泄漏。
- tests/blender_extension_lifecycle.py 使用临时本地扩展库进行十轮真实扩展启停；tests/blender_focus_handler.py 覆盖 timer/handler 的实际 RNA 清理。

本轮重建完成时：72 项标准库测试中70通过、2条件跳过（Blender专用/Windows ACL）；14个Blender后台集成脚本通过。全菜单重构后的测试及 GUI 结果以快捷键验证报告为准。

全仓库既存严格Ruff F821问题未在此扩大范围修复；M4入口保留原有E402导入布局。源码、完整 patch 与验证附件应独立保存，避免依赖临时工作区。
