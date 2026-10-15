# 菜单快捷键重构（Linux 重建工作区）

## 范围与基线

基线：`1dd9a2f90fc24a676c7f2aae0253250cb68ad90e`。本次从该提交在新工作区重建此前 Linux 适配，再进行快捷键重构；不是旧临时工作区或旧 ZIP 的逐字节恢复。在独立审阅分支开发；不直接修改 main。

## 实现

- 37 个 `pie/*` 注册函数使用同一个 ownership/rollback 管理器；其中 36 个由插件实际加载，`Brush_key` 仍保持原先排除状态。
- 只在 `keyconfigs.addon` 新增自有项。重复注册不重复添加；按保存的 RNA 引用逐项删除，不删共享 KeyMap，不按 operator 名误删其他插件项。注册中途失败回滚本次新增项。残项清理失败保留引用供生命周期重试。
- 统一登记此前漏记的菜单项（包括 B、Ctrl B、Shift G、Space 等），关闭后清空偏好 UI 注册表。
- 修正 `MESH` 拼写及 Node/UV/Shift Space 等错误的 editor space 标识，键、修饰键、事件类型保持原触发方式；唯一特意改变的触发入口是网格编辑模式 F。
- 插件偏好提供 Blender 原生有效用户键位编辑 UI；从 `keyconfigs.user` 解析对应项，不把 addon 模板当成用户设置。诊断只读，不自动停用冲突项。
- 移除自有键位后、注销类之前，通过 `keyconfigs.update(keep_properties=True)` 完成原生合并，避免 Blender 4.3 在 operator 暂时不存在时清除属性造成自定义丢失；没有写入或重建 default/user 的快捷键字段。
- 原 XZ 全套预设改成显式创建独立 `XZ Pie (Independent)` 配置。它不会自动选择、覆盖既有同名配置，也不修改当前 default/user；需用户在原生键位偏好中选择并导出以持久保存。旧自动加载开关不再执行，未注册任何快捷键文件加载 handler。

- Blender <4.5.3 的 operator 注册未标记原生键位类型刷新的上游问题（#143838）通过立即注册并注销自有 INTERNAL 空 operator 触发原生刷新。该类不运行、不创建键位、不残留；4.5.3 起不执行兼容路径。

## F 手势

网格编辑模式使用自有 `pie.mesh_f_gesture` 的 F/PRESS 入口；Object/Curve 保持 F/CLICK_DRAG。

- 按下后释放，移动不足 Blender 键盘拖动阈值：执行官方 `mesh.edge_face_add`，显式创建撤销步骤。
- 按住 F 移动超过 Blender 阈值：调用官方 `wm.call_menu_pie`。不是长按计时器；停在原地一直按住不会弹菜单。
- Blender 4.3.2 使用输入偏好的 `drag_threshold`（本测试默认为 30 像素），不硬编码鼠标距离。
- Esc、窗口失焦、模式/区域切换取消；重复按键不重复填面。中途修饰键变化或其他快捷键交回 Blender。
- 显式用户 F/PRESS 自定义或其他 addon 的同键 PRESS（例如 F2 插件的 `mesh.f2`）优先保留。此时 F pie 不抢走该快捷键，应在原生 UI 中为 pie 另选键位或由用户处理冲突。
- 原生 pie 的松键方向确认行为仍由 Blender 控制。快速移动到扇区再释放可能直接选中该项。

## 验证与复现

环境：Blender 4.3.2；其嵌入 CPython 3.13.5；隔离 `.venv` 同 ABI。系统默认 Python 3.12 不是 Blender 的依赖解释器。

```sh
python scripts/blender_dev.py --info
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
python scripts/blender_dev.py --test-all
# 需要显示器，创建全新隔离profile，两次真实GUI启动：
python scripts/test_keymap_persistence.py --profile /tmp/wxz-keymap-new-profile
```

本次最终自动验证：109 项普通测试（5 项需 RNA/特定环境跳过），18 个 Blender 后台集成脚本通过；原生 UI 专项在 Blender 中 24 项通过。

重点脚本：

- `tests/blender_keymap_ownership.py`：实际 RNA，自有项、重复注册、残项清理、同图 peer 保留。
- `tests/blender_all_menu_keymaps.py`：36 模块开关/重开，逐项对照 Blender 官方 keymap hierarchy 的模式/space/region。
- `tests/blender_independent_keymap_preset.py`：独立预设、modal 项复制、default/user/active/handler 不变、拒绝覆盖。
- `tests/blender_keymap_persistence_ui.py`：需 GUI；相同隔离配置先 `-- write` 再 `-- read`，验证 Ctrl J 自定义、三次开关、Python 模块重载和重启。第二轮不能加 `--factory-startup`。
- `tests/blender_keymap_full_reload.py`：跨功能暂停后重开、3 次全插件轮换、2 次重复启用、原生偏好禁启，验证自定义保留、default 不变、兼容类无残留。
- `tests/test_f_gesture.py`：tap/drag 阈值、重复键、Esc/失焦、卸载中止、修饰键与 F2 行为。

真实 GUI 手势和原生键位修改另有独立记录，见交付验证报告和 随构建提供的验证附件。后台成功不能替代真实手势或重启持久化验证。

## 边界

- 其他菜单原有 CLICK/CLICK_DRAG 行为保持，若与默认 PRESS 或第三方插件冲突，诊断会提示；不会为解决冲突自动改默认键位。
- 无法由静态冲突扫描证明任意工作区、modal operator、活动工具或所有第三方插件的优先级。未知上下文按潜在冲突提示，不自动修改。
- 不擅自恢复旧版本已经改写的默认键位，因为其原始用户配置未知；需要用户自行从原生偏好恢复或选取自己的备份。
- 未在用户自己的 Blender 或 Windows/macOS 上运行本轮测试。
