"""Native shortcut editing and read-only diagnostics for owned pie keymaps.

Registration templates belong to ``keyconfigs.addon``. Only their merged,
possibly customized counterparts in ``keyconfigs.user`` may be drawn for editing.
No lookup, diagnostic or draw helper mutates a key configuration.
"""

from dataclasses import dataclass


MODIFIERS = ("shift", "ctrl", "alt", "oskey", "hyper")
GESTURES = {"CLICK", "CLICK_DRAG", "DOUBLE_CLICK"}
GLOBAL_MAPS = {"Window", "Screen", "Screen Editing"}
MODE_MAPS = {
    "Object Mode": ("OBJECT",),
    "Mesh": ("EDIT_MESH",),
    "Curve": ("EDIT_CURVE",),
    "Curves": ("EDIT_CURVES",),
    "Armature": ("EDIT_ARMATURE",),
    "Metaball": ("EDIT_METABALL",),
    "Lattice": ("EDIT_LATTICE",),
    "Font": ("EDIT_TEXT",),
    "Pose": ("POSE",),
    "Sculpt": ("SCULPT",),
    "Sculpt Curves": ("SCULPT_CURVES",),
    "Vertex Paint": ("PAINT_VERTEX",),
    "Weight Paint": ("PAINT_WEIGHT",),
    "Particle": ("PARTICLE",),
    "Paint Vertex Selection (Weight, Vertex)": ("PAINT_VERTEX", "PAINT_WEIGHT"),
    "Paint Face Mask (Weight, Vertex, Texture)": ("PAINT_VERTEX", "PAINT_WEIGHT", "PAINT_TEXTURE"),
    "Grease Pencil Paint Mode": ("PAINT_GREASE_PENCIL",),
    "Grease Pencil Brush Stroke": ("PAINT_GREASE_PENCIL",),
    "Grease Pencil Fill Tool": ("PAINT_GREASE_PENCIL",),
    "Grease Pencil Edit Mode": ("EDIT_GREASE_PENCIL",),
    "Grease Pencil Sculpt Mode": ("SCULPT_GREASE_PENCIL",),
    "Grease Pencil Weight Paint": ("WEIGHT_GREASE_PENCIL",),
    "Grease Pencil Vertex Paint": ("VERTEX_GREASE_PENCIL",),
}
EDITOR_MAPS = {
    "UV Editor": ("IMAGE_EDITOR",),
    "UV Sculpt": ("IMAGE_EDITOR",),
    "Image Paint": ("IMAGE_EDITOR", "VIEW_3D"),
    "Object Non-modal": ("VIEW_3D",),
    "Grease Pencil": ("VIEW_3D",),
    "Mask Editing": ("IMAGE_EDITOR", "CLIP_EDITOR"),
    "Frames": ("VIEW_3D", "IMAGE_EDITOR", "NODE_EDITOR", "SEQUENCE_EDITOR", "CLIP_EDITOR",
               "DOPESHEET_EDITOR", "GRAPH_EDITOR", "NLA_EDITOR"),
    "Markers": ("DOPESHEET_EDITOR", "GRAPH_EDITOR", "NLA_EDITOR", "SEQUENCE_EDITOR"),
    "Animation": ("DOPESHEET_EDITOR", "GRAPH_EDITOR", "NLA_EDITOR", "SEQUENCE_EDITOR"),
    "Animation Channels": ("DOPESHEET_EDITOR", "GRAPH_EDITOR", "NLA_EDITOR"),
}
TOOL_MODES = {
    "Object": "OBJECT", "Edit Mesh": "EDIT_MESH", "Edit Curve": "EDIT_CURVE",
    "Edit Armature": "EDIT_ARMATURE", "Edit Metaball": "EDIT_METABALL",
    "Edit Lattice": "EDIT_LATTICE", "Pose": "POSE", "Sculpt": "SCULPT",
    "Sculpt Curves": "SCULPT_CURVES", "Paint Vertex": "PAINT_VERTEX",
    "Paint Weight": "PAINT_WEIGHT", "Paint Texture": "PAINT_TEXTURE",
    "Particle": "PARTICLE", "UV": "UV", "Paint": "PAINT_TEXTURE", "View": "IMAGE_VIEW",
}


def keymap_identity(km):
    return km.name, km.space_type, km.region_type, bool(getattr(km, "is_modal", False))


def _same_rna(left, right):
    try:
        return left == right or left.as_pointer() == right.as_pointer()
    except (AttributeError, ReferenceError, RuntimeError):
        return left is right


def _find_keymap(config, reference):
    if config is None:
        return None
    identity = keymap_identity(reference)
    return next((km for km in config.keymaps if keymap_identity(km) == identity), None)


def _freeze(value):
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    if hasattr(value, "keys"):
        return tuple(sorted((key, _freeze(getattr(value, key, value[key]))) for key in value.keys()))
    try:
        return tuple(_freeze(part) for part in value)
    except TypeError:
        return repr(value)


def operator_signature(kmi):
    """Include explicit operator properties, notably wm.call_menu_pie's name."""
    props = getattr(kmi, "properties", None)
    return kmi.idname, _freeze(props) if props is not None else ()


def _legacy_merged_id_offset(base_map, addon_map, user_map):
    """Infer Blender's private base-id counter without assuming max(id)==counter.

    Native merging gives add-on items consecutive positive ids, in original
    add-on order. User-created items have negative ids; preset ids are retained.
    Infer the offset from the complete positive-id layout, validating unchanged
    operator/property identities. Deletions can make that inference ambiguous:
    return None in that case, never guess which customized user item to expose.
    Event values and modifiers are deliberately irrelevant to this lookup.
    """
    base_ids = {abs(item.id) for item in base_map.keymap_items}
    templates = tuple(addon_map.keymap_items)
    extras = [item for item in user_map.keymap_items if item.id > 0 and item.id not in base_ids]
    if not templates or not extras or len(extras) > len(templates):
        return None
    minimum = max(max(base_ids, default=0), max(item.id for item in extras) - len(templates))
    maximum = min(item.id for item in extras) - 1
    possible = []
    for offset in range(minimum, maximum + 1):
        valid = True
        for item in extras:
            index = item.id - offset - 1
            if (not 0 <= index < len(templates)
                    or (not getattr(item, "is_user_modified", False)
                        and operator_signature(item) != operator_signature(templates[index]))):
                valid = False
                break
        if valid:
            possible.append(offset)
            if len(possible) > 1:
                return None
    return possible[0] if possible else None


def resolve_user_item(keyconfigs, addon_map, template):
    """Return the native user map/item, independent of the customized event.

    New Blender versions expose exact native identity mapping via find_match.
    The legacy fallback infers the merged-id offset from the complete keymap,
    and refuses ambiguous mappings. It never uses shortcut defaults to locate a
    customized item, and never falls back to editing the registration template.
    """
    try:
        user_map = _find_keymap(getattr(keyconfigs, "user", None), addon_map)
        if user_map is None:
            return None
        native_match = getattr(user_map.keymap_items, "find_match", None)
        if native_match is not None:
            item = native_match(addon_map, template)
            return (user_map, item) if item is not None else None
        base_map = _find_keymap(getattr(keyconfigs, "active", None), addon_map)
        if base_map is None:
            base_map = _find_keymap(getattr(keyconfigs, "default", None), addon_map)
        if base_map is None:
            return None
        index = next((i for i, item in enumerate(addon_map.keymap_items) if _same_rna(item, template)), None)
        if index is None:
            return None
        offset = _legacy_merged_id_offset(base_map, addon_map, user_map)
        if offset is None:
            return None
        item = user_map.keymap_items.from_id(offset + index + 1)
        return (user_map, item) if item is not None else None
    except (ReferenceError, RuntimeError):
        # An item may have just been removed by native UI or a module toggle.
        return None


@dataclass(frozen=True)
class Scope:
    spaces: frozenset | None
    modes: frozenset | None
    region: str
    unknown: str = ""
    tool: str = ""


def keymap_scope(km):
    name, space, region, _modal = keymap_identity(km)
    if name in GLOBAL_MAPS:
        return Scope(None, None, "ANY")
    spaces = frozenset({space}) if space != "EMPTY" else None
    modes = None
    unknown = ""
    tool = ""
    if name in MODE_MAPS:
        spaces, modes = frozenset({"VIEW_3D"}), frozenset(MODE_MAPS[name])
    elif name in EDITOR_MAPS:
        spaces = frozenset(EDITOR_MAPS[name])
    if name in {"UV Editor", "UV Sculpt"}:
        modes = frozenset({"UV"})
    elif name == "Image Paint":
        modes = frozenset({"PAINT_TEXTURE"})
    elif name == "Image View":
        modes = frozenset({"IMAGE_VIEW"})
    if " Tool: " in name:
        detail = name.split(" Tool: ", 1)[1]
        mode, separator, tool = detail.partition(", ")
        if mode in TOOL_MODES:
            modes = frozenset({TOOL_MODES[mode]})
        elif not separator:
            tool = detail
        if name.startswith("3D View Tool: "):
            spaces = frozenset({"VIEW_3D"})
        elif name.startswith("Image Editor Tool: "):
            spaces = frozenset({"IMAGE_EDITOR"})
    if spaces is None:
        # RNA does not expose a keymap's poll callback. Keep unknown EMPTY
        # contexts as *uncertain*, rather than silently omitting possible peers.
        unknown = name
    return Scope(spaces, modes, region, unknown, tool)


def keymaps_overlap(left, right):
    if getattr(left, "is_modal", False) or getattr(right, "is_modal", False):
        return keymap_identity(left) == keymap_identity(right)
    a, b = keymap_scope(left), keymap_scope(right)
    if a.region != "ANY" and b.region != "ANY" and a.region != b.region:
        return False
    if a.spaces is not None and b.spaces is not None and not a.spaces & b.spaces:
        return False
    if a.modes is not None and b.modes is not None and not a.modes & b.modes:
        return False
    if a.tool and b.tool and a.tool != b.tool:
        return False
    return True


def _modifier_values(kmi):
    if getattr(kmi, "any", False):
        return (-1,) * len(MODIFIERS)
    return tuple(getattr(kmi, name, 0) for name in MODIFIERS)


def event_relation(left, right):
    """SAME_EVENT, PRESS_BLOCKS_GESTURE, GESTURE_BLOCKED_BY_PRESS, or None."""
    if not left.active or not right.active:
        return None
    if left.type != "ANY" and right.type != "ANY" and left.type != right.type:
        return None
    if getattr(left, "key_modifier", "NONE") != getattr(right, "key_modifier", "NONE"):
        return None
    for a, b in zip(_modifier_values(left), _modifier_values(right)):
        if a != -1 and b != -1 and a != b:
            return None
    if left.value == right.value or "ANY" in {left.value, right.value}:
        if left.value == right.value == "CLICK_DRAG":
            a, b = getattr(left, "direction", "ANY"), getattr(right, "direction", "ANY")
            if a != "ANY" and b != "ANY" and a != b:
                return None
        return "SAME_EVENT"
    if left.value == "PRESS" and right.value in GESTURES:
        return "PRESS_BLOCKS_GESTURE"
    if right.value == "PRESS" and left.value in GESTURES:
        return "GESTURE_BLOCKED_BY_PRESS"
    return None


def event_label(kmi):
    modifiers = []
    if getattr(kmi, "any", False):
        modifiers.append("Any modifiers")
    else:
        for name in MODIFIERS:
            value = getattr(kmi, name, 0)
            if value:
                modifiers.append(name.title() + (":*" if value == -1 else ""))
    key_modifier = getattr(kmi, "key_modifier", "NONE")
    if key_modifier != "NONE":
        modifiers.append(key_modifier)
    modifiers.extend((kmi.type, kmi.value))
    if kmi.value == "CLICK_DRAG" and getattr(kmi, "direction", "ANY") != "ANY":
        modifiers.append(kmi.direction)
    return " + ".join(modifiers)


def operator_label(kmi):
    properties = operator_signature(kmi)[1]
    if not properties:
        return kmi.idname
    detail = ", ".join(f"{key}={value!r}" for key, value in properties)
    return f"{kmi.idname} ({detail})"


@dataclass(frozen=True)
class KeymapConflict:
    keymap: object
    item: object
    kind: str
    same_action: bool = False
    context_uncertain: bool = False


def _expected_mesh_fallback(own_map, own, other_map, other, keyconfigs):
    if (own_map.name != "Mesh" or own.idname != "pie.mesh_f_gesture" or own.type != "F"
            or own.value != "PRESS" or other_map.name != "Mesh" or other.idname != "mesh.edge_face_add"
            or other.type != "F" or other.value != "PRESS"
            or getattr(other, "is_user_modified", False) or getattr(other, "is_user_defined", False)):
        return False
    if any(_modifier_values(own)) or any(_modifier_values(other)):
        return False
    if any(getattr(item, "key_modifier", "NONE") != "NONE" for item in (own, other)):
        return False
    default_map = _find_keymap(getattr(keyconfigs, "default", None), other_map)
    default_item = default_map.keymap_items.from_id(other.id) if default_map is not None else None
    return (default_item is not None and operator_signature(default_item) == operator_signature(other)
            and event_label(default_item) == event_label(other))


def find_conflicts(keyconfigs, own_map, own, candidate_maps=None):
    """Inspect only the effective user configuration; never disable/remap a peer.

    These are potential event collisions. Operator polls, active tools and modal
    handlers can still decide runtime dispatch; this is not proof of failure.
    """
    user = getattr(keyconfigs, "user", None)
    if user is None or not own.active:
        return []
    conflicts = []
    for km in user.keymaps if candidate_maps is None else candidate_maps:
        if not keymaps_overlap(own_map, km):
            continue
        for item in km.keymap_items:
            if keymap_identity(km) == keymap_identity(own_map) and item.id == own.id:
                continue
            relation = event_relation(own, item)
            if relation is None:
                continue
            if _expected_mesh_fallback(own_map, own, km, item, keyconfigs):
                relation = "EXPECTED_FALLBACK"
            uncertain = bool(keymap_scope(own_map).unknown or keymap_scope(km).unknown)
            conflicts.append(KeymapConflict(km, item, relation,
                                            operator_signature(own) == operator_signature(item), uncertain))
    return conflicts


def draw_keymaps(preferences, context, layout):
    """Draw user-owned customization through Blender's own keymap editor."""
    import rna_keymap_ui
    from ..items import All_Pie_keymaps

    box = layout.box()
    expanded = preferences.show_pie_keymaps
    box.prop(preferences, "show_pie_keymaps", text="饼菜单快捷键（Blender 原生编辑）",
             icon="TRIA_DOWN" if expanded else "TRIA_RIGHT", emboss=False)
    if not expanded:
        return
    box.label(text="除 Mesh F 的点击/拖动分派外，其他菜单触发方式保持原样。", icon="INFO")
    box.label(text="冲突只读检查：需要您明确改键；不会自动禁用或改写其他快捷键。")
    box.label(text="编辑的是当前用户键位；可展开修改或恢复，按 Blender 偏好保存方式保存。")
    box.prop(preferences, "show_pie_keymap_conflicts", text="显示潜在冲突（含 PRESS 拦截点击/拖动）")
    if preferences.show_pie_keymap_conflicts:
        box.label(text="仅比较事件与编辑器/模式/区域；操作轮询、工具或模态状态可能避免冲突。")
    box.prop(preferences, "pie_keymap_filter", text="筛选菜单 / 操作 / 编辑器 / 按键", icon="VIEWZOOM")
    wm = getattr(context, "window_manager", None)
    keyconfigs = getattr(wm, "keyconfigs", None)
    if keyconfigs is None or getattr(keyconfigs, "user", None) is None:
        box.label(text="当前没有可编辑的用户键位配置。", icon="INFO")
        return
    if not All_Pie_keymaps:
        box.label(text="启用饼菜单后，这里会显示其快捷键。", icon="INFO")
        return
    query = preferences.pie_keymap_filter.strip().casefold()
    grouped = {}
    for addon_map, template in tuple(All_Pie_keymaps):
        try:
            resolved = resolve_user_item(keyconfigs, addon_map, template)
            km, item = resolved if resolved is not None else (addon_map, template)
            haystack = " ".join((km.name, operator_label(item), event_label(item))).casefold()
            if query and query not in haystack:
                continue
            grouped.setdefault(keymap_identity(km), []).append((template, resolved))
        except (ReferenceError, RuntimeError):
            continue
    if not grouped:
        box.label(text="没有匹配的已启用快捷键。", icon="INFO")
    labels = {
        "SAME_EVENT": "同一事件可能冲突",
        "PRESS_BLOCKS_GESTURE": "此 PRESS 可能拦截对方点击/拖动",
        "GESTURE_BLOCKED_BY_PRESS": "对方 PRESS 可能拦截此点击/拖动",
        "EXPECTED_FALLBACK": "预期回退：Mesh F 点击建面（保留 Blender 默认键位）",
    }
    for identity, entries in sorted(grouped.items()):
        group = box.box()
        group.label(text=f"{identity[0]} · {identity[1]} / {identity[2]}")
        for template, resolved in entries:
            if resolved is None:
                group.label(text=f"{operator_label(template)}：用户键位已移除、尚未合并或身份无法安全确认。", icon="INFO")
                group.label(text="可在 Blender 偏好设置 > 键位映射中检查或恢复。")
                continue
            km, item = resolved
            col = group.column()
            col.context_pointer_set("keymap", km)
            col.context_pointer_set("keyconfig", keyconfigs.user)
            rna_keymap_ui.draw_kmi([], keyconfigs.user, km, item, col, 0)
            if not preferences.show_pie_keymap_conflicts:
                continue
            for conflict in find_conflicts(keyconfigs, km, item):
                expected = conflict.kind == "EXPECTED_FALLBACK"
                row = col.row()
                row.alert = not expected
                label = labels[conflict.kind]
                if conflict.same_action:
                    label += "（相同操作/属性）"
                if conflict.context_uncertain:
                    label += "（上下文未知，请手动核对）"
                row.label(text=label, icon="INFO" if expected else "ERROR")
                col.label(text=f"{conflict.keymap.name} · {operator_label(conflict.item)} · {event_label(conflict.item)}")
                if (item.idname == "pie.mesh_f_gesture" and not expected
                        and conflict.keymap.name == "Mesh" and conflict.item.value in {"PRESS", "ANY"}):
                    col.label(text="Mesh 自定义 PRESS 优先；请手动选择保留的绑定或改键。")
