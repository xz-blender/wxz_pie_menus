# SPDX-License-Identifier: GPL-3.0-or-later
"""Edit the host's existing key bindings, including saved user overrides."""
import rna_keymap_ui


def draw(layout, context):
    config = context.window_manager.keyconfigs.user
    keymap = config.keymaps.get("Mesh") if config else None
    for kind, label in (("crease", "折痕"), ("bevel_weight", "倒角权重")):
        box = layout.box()
        box.label(text=label)
        items = [
            item for item in keymap.keymap_items
            if item.idname == "pie.shift_e" and item.properties.attr_name == kind
        ] if keymap else []
        if items:
            for item in items:
                box.context_pointer_set("keymap", keymap)
                rna_keymap_ui.draw_kmi([], config, keymap, item, box, 0)
        else:
            box.label(text="请启用 E_pie；快捷键将在 Blender 更新键位配置后显示", icon="INFO")
