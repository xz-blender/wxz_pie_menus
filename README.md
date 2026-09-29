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

## 模块开关与重试

偏好列表中的开关记录希望启用的功能；启用失败时保留开关，并显示本次会话的错误状态。
点击失败项旁的“重试”，会先处理未完成的清理，再按当前开关尝试启用。其他功能模块会继续正常处理。
错误详情写入控制台；错误状态不保存到偏好文件。

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
