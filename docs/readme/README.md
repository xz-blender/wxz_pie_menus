# README 媒体

这组素材随仓库保存，不依赖旧版 README 使用的外部图床。

| 文件 | 内容与来源 |
| --- | --- |
| `hero.svg` | 手工绘制的矢量封面，右侧为菜单入口示意，并非 Blender 界面截图 |
| `context-menu.gif` | 当前 F 饼菜单的物体／网格编辑模式截图轮播，每张停留 3 秒 |
| `f-object.png` / `f-edit.png` | 上述菜单的静态版本 |
| `quick-crease.gif` | 真实折痕工具的脚本驱动演示：在带细分修改器的立方体上将边折痕由 0 调至 1，再回到 0 |
| `quick-crease.png` | 折痕为 0.7 时的静态帧 |
| `preferences.png` | 用当前 `prefs.panels.draw_addon_menus` 在临时面板中绘制的偏好界面，裁掉测试面板外的 Blender 界面 |

采集环境：Windows x64，Blender **5.3.0 Alpha** 本地构建（`affde7624e7f`），插件代码基于 `7565f4fb1bfbbcaadea9dfea5e9eb9bedbf779f4`。脚本固定界面缩放为 1.5、窗口为 1440 × 960。演示会话未安装外部扩展清单中的插件，菜单可见项不代表完整发行包的全部项目。

菜单和 HUD 均来自真实 Blender 绘制。GIF 不是人工操作录屏：菜单以原生操作符打开，折痕动画调用真实工具的数值更新方法。采集脚本逐帧检查所选边的实际属性，并验证取消后移除了本次新建的属性。字幕、裁切、缩放和 GIF 编码由 FFmpeg 完成。

## 重新生成

需要可启动图形界面的 Blender、普通 Python、支持 `drawtext` 的 FFmpeg，以及本地字体。不需要图床、AI 图像服务或 Pillow。运行时会短暂打开独立 Blender 窗口，请勿在采集窗口中操作。

在仓库根目录执行以下 PowerShell 命令，先把 Blender 路径替换成自己的路径：

```powershell
$readmeBlender = 'C:\path\to\blender.exe'
$readmeRaw = Join-Path $env:TEMP 'wxz-readme-capture'
foreach ($scene in @('f-object', 'f-edit', 'crease', 'preferences')) {
    & $readmeBlender --factory-startup --window-geometry 0 0 1440 960 `
        --python docs/readme/capture_blender.py -- $readmeRaw $scene
    if ($LASTEXITCODE -ne 0) { throw "Blender capture failed: $scene" }
}
python docs/readme/build_media.py $readmeRaw
```

`build_media.py` 默认从 PATH 查找 FFmpeg、使用 `C:/Windows/Fonts/segoeui.ttf`；可通过 `--ffmpeg` 和 `--font` 指定其他位置。源码目录名称应为有效的 Python 包名。

采集使用 `--factory-startup`，不保存用户偏好或工作文件。每个场景独立运行，原始帧、结果 JSON 与失败诊断保存在仓库外的临时目录；编码前必须具备四个成功的采集结果。失败时请查看该目录的 `failure.txt`，不要提交原始帧。

生成后检查：

1. 两张菜单图没有弹窗叠加；中文、操作项与模式一致。
2. 折痕动画有 21 个数值帧，HUD 与模型共同变化；对应 JSON 中 `cancel_restored_attribute` 为 `true`。
3. GIF 循环正常，静态链接可打开，偏好面板没有被裁断。
4. 在 README 的实际显示宽度下检查文字可读性；所有媒体合计控制在 1 MB 左右。

仅提交最终图片、GIF、SVG 与生成脚本。Blender 版本、字体、UI 缩放和代码更新都可能影响画面；发生变化时应重新采集并核对裁切范围。
