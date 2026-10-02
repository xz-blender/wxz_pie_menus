<h2 align="center">
    符合鄙人操作习惯的饼菜单们，以及众多实用工具的合集<br>
    仅适配4.2+ Blender 版本 <br>
    and more quick operators... <br>
</h2>

<h5 align="center">
    !!!<br>
    This plugin contains some setting presets for personal use, 
    and shortcut configurations that may change the way you are familiar with blender operation, 
    please backup your personal configuration before installation<br>
    !!!<br>
</h5>
<h4 align="center">
    <b>请打开此插件前保存好您的个人配置文件!!!<b><br>
    <h5>本插件会自动应用 偏好设置、场景设置、快捷键设置!!!</h5>
</h4>

# wxz_pie_menus

## 整包分发

插件随完整发行包提供，使用本地随包资源；不再单独打包插件，也不会在首次启用或资源缺失时从 123 盘补下载本体或节点库。
分发时请包含 `assets/blends/nodes/`、`wheels/`、工作区文件和字体等运行资源；依赖由 Blender 根据 `blender_manifest.toml` 安装随包 wheel。
缺少文件时请重新获取完整发行包。

外部插件清单及其配置保存在 `operator/addons_lib_presets.json` 的 `org_ex` 中，包含原自建源清单。
在资源配置中点击“安装所需插件（官方源）”，即可通过 Blender 默认官方扩展源安装、启用并应用预设；单项失败会提示并继续处理其余插件。

## 快速折痕 / 倒角权重

`E_pie` 内置 Quick Crease Weight 1.2.1 的网格编辑与 HUD 逻辑。编辑模式下，`Shift + E` 调整折痕，`Ctrl + Shift + E` 调整倒角权重；点选择作用于顶点，边／面选择作用于边，支持多物体编辑。

左右移动鼠标调整；松开调用工具时按住的修饰键后，`Shift` 按 0.1 吸附、`Ctrl` 设为 1、`Alt` 设为 0。左键／Enter 确认，右键／Esc 逐项还原原值（并移除本次新建的属性）；确认后支持撤销。不移动鼠标直接确认会保留各元素原值。

在“其他插件设置 → 快速折痕 / 倒角权重”中调整快捷键、灵敏度和 HUD 的位置、字号、橙／蓝主题色、背景及右侧按键提示。设置随 Blender 偏好设置保存；关闭 `E_pie` 会取消当前操作并清理快捷键。原 E 拖动饼菜单及 `pie.shift_e` 接口保持兼容。

核心来源：WXZ 的 Quick Crease Weight 1.2.1，保留源文件的 GPL-3.0-or-later 标注及 `module/quick_crease_weight/LICENSE`；宿主适配位于同目录的操作符、偏好设置和快捷键模块。

## -偏好设置菜单-
<div align="center">
    <img src="https://img.picgo.net/2024/07/12/pref_1e65a9cba62b0014a.png" style="width:80%"/>
    <img src="https://img.picgo.net/2024/07/12/pref_2b50987f0340c021a.png" style="width:80%"/>
</div>

## -Object Mode-
<div align="center">
    <img src="https://img.picgo.net/2024/07/12/ctrl-S-pieedfa413d3e090a1e.jpg" style="width:80%"/>
    <img src="https://img.picgo.net/2024/07/12/Ctrl_Alt_X-pie020ff4c2042021ff.jpg" style="width:80%"/>
    <img src="https://img.picgo.net/2024/07/12/W-pie_Object6899aa0b91c50af8.jpg" style="width:80%"/>
    <img src="https://img.picgo.net/2024/07/12/F-pie_Objectca870a8b94a6f516.jpg" style="width:80%"/>
    <img src="https://img.picgo.net/2024/07/12/A-pie_Object1e36a89025939cbd.jpg" style="width:80%"/>
    <img src="https://img.picgo.net/2024/07/12/D-pie16e5803b84398815.jpg" style="width:80%"/>
</div>

## -Edit Mode-
<div align="center">
    <img src="https://img.picgo.net/2024/07/12/E-pie_Editeb7383ba83755573.jpg" style="width:80%"/>
    <img src="https://img.picgo.net/2024/07/12/F-pie_Edit0c7109958503dda8.jpg" style="width:80%"/>
    <img src="https://img.picgo.net/2024/07/12/A-pie_Edit912e514f84bf7af6.jpg" style="width:80%"/>
    <img src="https://img.picgo.net/2024/07/12/X-pie33da556db77b2046.jpg" style="width:80%"/>
</div>
