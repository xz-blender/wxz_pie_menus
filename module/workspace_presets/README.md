# 工作区预设

本模块集中管理预设路径、工作区名称和 Blender 加载操作符。

## 模板文件

模板位于插件根目录的 `assets/blends/workspace/`：

- `workspace_base.blend`：原 `workspace.blend`，供单个工作区按需加载。
- `workspace_custom.blend`：原 `workspace_online.blend`，供批量补齐工作区。

两者均为本地资源，不涉及联网。迁移只改动路径和文件名，不修改 blend 内容。

## 加载规则

- `PIE_WorkspaceSwapOperator`：目标已存在时直接切换；不存在时从基础模板追加并激活。
- `PIE_Workspace_Import_Online_Operator`：按 `WORKSPACE_NAMES` 顺序从自定义模板追加缺少的工作区；跳过已有工作区，不覆盖用户布局，最终激活最后追加的工作区。全部存在时保持当前工作区。
- 保留原操作符 ID `pie.workspaceswapper` 和 `pie.workspace_online_batch_import`，兼容已有快捷键配置。
- 预设名称为 `0-LIB`、`1-MOD`、`2-GN`、`3-MAT`、`4-UV`、`5-MOTION`、`6-RENDER`、`7-COMPO`、`8-SETTING`；模板内工作区名称需与之匹配。

## 菜单与注册

`pie/Tab_ctrl_pie.py` 保留饼菜单和生命周期入口，导入本模块操作符并统一注册、注销：

- Ctrl + Tab 拖动：工作区饼菜单。
- Alt + 0～8：切换或追加对应基础工作区。
- Alt + 9：补齐自定义工作区。

本模块不单独注册，避免重复注册操作符。
