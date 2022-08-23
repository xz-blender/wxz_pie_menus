keyconfig_version = (3, 3, 6)
keyconfig_data = [
    (
        "3D View",
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "wm.call_menu_pie",
                    {"type": 'Z', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_Z_Shift'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'Z', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_Z_Overlay'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'X', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_X'),
                        ],
                    },
                ),
                ("pie.x_key", {"type": 'X', "value": 'CLICK'}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'W', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_W'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'TAB', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Ctrl_Tab'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'SPACE', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Space_KEY_shift'),
                        ],
                    },
                ),
                ("screen.animation_play", {"type": 'SPACE', "value": 'CLICK', "shift": True}, None),
                ("pie.key_space", {"type": 'SPACE', "value": 'CLICK'}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'R', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_R'),
                        ],
                    },
                ),
                ("pie.q_alt_key", {"type": 'Q', "value": 'CLICK', "alt": True}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'Q', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_Q'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'E', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_E'),
                        ],
                    },
                ),
                ("pie.c_key", {"type": 'C', "value": 'CLICK'}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'C', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_C'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'A', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'PIE_MT_Bottom_A_Ctrl'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'A', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'PIE_MT_Bottom_A'),
                        ],
                    },
                ),
                (
                    "wm.super_import",
                    {"type": 'V', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                ("friendly.origin", {"type": 'D', "value": 'DOUBLE_CLICK'}, None),
                ("view3d.modifier_popup", {"type": 'SPACE', "value": 'PRESS', "alt": True}, None),
                (
                    "bagapie.duplicatelinkedgroup",
                    {"type": 'N', "value": 'PRESS', "alt": True},
                    None,
                ),
                ("bagapie.duplicategroup", {"type": 'J', "value": 'PRESS', "alt": True}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'J', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'BAGAPIE_MT_pie_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'C', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("name", 'PHOTOGRAPHER_MT_Pie_Camera'),
                        ],
                    },
                ),
                (
                    "view3d.rotate_canvas",
                    {"type": 'MIDDLEMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                ("object.drop_it", {"type": 'V', "value": 'CLICK'}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'Z', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_Z_Shift'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'Z', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_Z_Overlay'),
                        ],
                    },
                ),
                ("pie.x_key", {"type": 'X', "value": 'CLICK'}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'W', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_W'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'TAB', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Ctrl_Tab'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'T', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_T'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'SPACE', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Space_KEY_shift'),
                        ],
                    },
                ),
                ("screen.animation_play", {"type": 'SPACE', "value": 'CLICK', "shift": True}, None),
                ("pie.key_space", {"type": 'SPACE', "value": 'CLICK'}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'S', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_S_ctrl'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'R', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_R'),
                        ],
                    },
                ),
                ("pie.q_alt_key", {"type": 'Q', "value": 'CLICK', "alt": True}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'Q', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_Q'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'E', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_E'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'D', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_D'),
                        ],
                    },
                ),
                ("pie.c_key", {"type": 'C', "value": 'CLICK'}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'C', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_C'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'A', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'PIE_MT_Bottom_A_Ctrl'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'A', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'PIE_MT_Bottom_A'),
                        ],
                    },
                ),
                ("view3d.cursor3d", {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True}, None),
                (
                    "transform.translate",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("cursor_transform", True),
                            ("release_confirm", True),
                        ],
                    },
                ),
                ("view3d.localview", {"type": 'NUMPAD_SLASH', "value": 'PRESS'}, None),
                ("view3d.localview", {"type": 'SLASH', "value": 'PRESS'}, None),
                ("view3d.localview", {"type": 'MOUSESMARTZOOM', "value": 'ANY'}, None),
                (
                    "view3d.localview_remove_from",
                    {"type": 'NUMPAD_SLASH', "value": 'PRESS', "alt": True},
                    None,
                ),
                (
                    "view3d.localview_remove_from",
                    {"type": 'SLASH', "value": 'PRESS', "alt": True},
                    None,
                ),
                ("view3d.rotate", {"type": 'MOUSEROTATE', "value": 'ANY'}, None),
                ("view3d.rotate", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
                ("view3d.move", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "shift": True}, None),
                ("view3d.rotate", {"type": 'TRACKPADPAN', "value": 'ANY'}, None),
                ("view3d.move", {"type": 'TRACKPADPAN', "value": 'ANY', "shift": True}, None),
                ("view3d.zoom", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "ctrl": True}, None),
                (
                    "view3d.dolly",
                    {"type": 'MIDDLEMOUSE', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "view3d.view_selected",
                    {"type": 'NUMPAD_PERIOD', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("use_all_regions", True),
                        ],
                    },
                ),
                (
                    "view3d.view_selected",
                    {"type": 'NUMPAD_PERIOD', "value": 'PRESS'},
                    {
                        "properties": [
                            ("use_all_regions", False),
                        ],
                    },
                ),
                ("view3d.smoothview", {"type": 'TIMER1', "value": 'ANY', "any": True}, None),
                ("view3d.zoom", {"type": 'TRACKPADZOOM', "value": 'ANY'}, None),
                ("view3d.zoom", {"type": 'TRACKPADPAN', "value": 'ANY', "ctrl": True}, None),
                (
                    "view3d.zoom",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("delta", 1),
                        ],
                    },
                ),
                (
                    "view3d.zoom",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("delta", -1),
                        ],
                    },
                ),
                (
                    "view3d.zoom",
                    {"type": 'EQUAL', "value": 'PRESS', "ctrl": True, "repeat": True},
                    {
                        "properties": [
                            ("delta", 1),
                        ],
                    },
                ),
                (
                    "view3d.zoom",
                    {"type": 'MINUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    {
                        "properties": [
                            ("delta", -1),
                        ],
                    },
                ),
                (
                    "view3d.zoom",
                    {"type": 'WHEELINMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("delta", 1),
                        ],
                    },
                ),
                (
                    "view3d.zoom",
                    {"type": 'WHEELOUTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("delta", -1),
                        ],
                    },
                ),
                (
                    "view3d.dolly",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("delta", 1),
                        ],
                    },
                ),
                (
                    "view3d.dolly",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("delta", -1),
                        ],
                    },
                ),
                (
                    "view3d.dolly",
                    {
                        "type": 'EQUAL',
                        "value": 'PRESS',
                        "shift": True,
                        "ctrl": True,
                        "repeat": True,
                    },
                    {
                        "properties": [
                            ("delta", 1),
                        ],
                    },
                ),
                (
                    "view3d.dolly",
                    {
                        "type": 'MINUS',
                        "value": 'PRESS',
                        "shift": True,
                        "ctrl": True,
                        "repeat": True,
                    },
                    {
                        "properties": [
                            ("delta", -1),
                        ],
                    },
                ),
                ("view3d.view_center_camera", {"type": 'HOME', "value": 'PRESS'}, None),
                ("view3d.view_center_lock", {"type": 'HOME', "value": 'PRESS'}, None),
                (
                    "view3d.view_all",
                    {"type": 'HOME', "value": 'PRESS'},
                    {
                        "properties": [
                            ("center", False),
                        ],
                    },
                ),
                (
                    "view3d.view_all",
                    {"type": 'HOME', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("use_all_regions", True),
                            ("center", False),
                        ],
                    },
                ),
                (
                    "view3d.view_all",
                    {"type": 'C', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("center", True),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'ACCENT_GRAVE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_view_pie'),
                        ],
                    },
                ),
                (
                    "view3d.navigate",
                    {"type": 'ACCENT_GRAVE', "value": 'PRESS', "shift": True},
                    None,
                ),
                ("view3d.view_camera", {"type": 'NUMPAD_0', "value": 'PRESS'}, None),
                (
                    "view3d.view_axis",
                    {"type": 'NUMPAD_1', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'FRONT'),
                        ],
                    },
                ),
                (
                    "view3d.view_orbit",
                    {"type": 'NUMPAD_2', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("type", 'ORBITDOWN'),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NUMPAD_3', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'RIGHT'),
                        ],
                    },
                ),
                (
                    "view3d.view_orbit",
                    {"type": 'NUMPAD_4', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("type", 'ORBITLEFT'),
                        ],
                    },
                ),
                ("view3d.view_persportho", {"type": 'NUMPAD_5', "value": 'PRESS'}, None),
                (
                    "view3d.view_orbit",
                    {"type": 'NUMPAD_6', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("type", 'ORBITRIGHT'),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NUMPAD_7', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'TOP'),
                        ],
                    },
                ),
                (
                    "view3d.view_orbit",
                    {"type": 'NUMPAD_8', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("type", 'ORBITUP'),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NUMPAD_1', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("type", 'BACK'),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NUMPAD_3', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("type", 'LEFT'),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NUMPAD_7', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("type", 'BOTTOM'),
                        ],
                    },
                ),
                (
                    "view3d.view_pan",
                    {"type": 'NUMPAD_2', "value": 'PRESS', "ctrl": True, "repeat": True},
                    {
                        "properties": [
                            ("type", 'PANDOWN'),
                        ],
                    },
                ),
                (
                    "view3d.view_pan",
                    {"type": 'NUMPAD_4', "value": 'PRESS', "ctrl": True, "repeat": True},
                    {
                        "properties": [
                            ("type", 'PANLEFT'),
                        ],
                    },
                ),
                (
                    "view3d.view_pan",
                    {"type": 'NUMPAD_6', "value": 'PRESS', "ctrl": True, "repeat": True},
                    {
                        "properties": [
                            ("type", 'PANRIGHT'),
                        ],
                    },
                ),
                (
                    "view3d.view_pan",
                    {"type": 'NUMPAD_8', "value": 'PRESS', "ctrl": True, "repeat": True},
                    {
                        "properties": [
                            ("type", 'PANUP'),
                        ],
                    },
                ),
                (
                    "view3d.view_roll",
                    {"type": 'NUMPAD_4', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("type", 'LEFT'),
                        ],
                    },
                ),
                (
                    "view3d.view_roll",
                    {"type": 'NUMPAD_6', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("type", 'RIGHT'),
                        ],
                    },
                ),
                (
                    "view3d.view_orbit",
                    {"type": 'NUMPAD_9', "value": 'PRESS'},
                    {
                        "properties": [
                            ("angle", 3.1415927),
                            ("type", 'ORBITRIGHT'),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NUMPAD_1', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("type", 'FRONT'),
                            ("align_active", True),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NUMPAD_3', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("type", 'RIGHT'),
                            ("align_active", True),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NUMPAD_7', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("type", 'TOP'),
                            ("align_active", True),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NUMPAD_1', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("type", 'BACK'),
                            ("align_active", True),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NUMPAD_3', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("type", 'LEFT'),
                            ("align_active", True),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NUMPAD_7', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("type", 'BOTTOM'),
                            ("align_active", True),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {
                        "type": 'MIDDLEMOUSE',
                        "value": 'CLICK_DRAG',
                        "alt": True,
                        "direction": 'NORTH',
                    },
                    {
                        "properties": [
                            ("type", 'TOP'),
                            ("relative", True),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {
                        "type": 'MIDDLEMOUSE',
                        "value": 'CLICK_DRAG',
                        "alt": True,
                        "direction": 'SOUTH',
                    },
                    {
                        "properties": [
                            ("type", 'BOTTOM'),
                            ("relative", True),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {
                        "type": 'MIDDLEMOUSE',
                        "value": 'CLICK_DRAG',
                        "alt": True,
                        "direction": 'EAST',
                    },
                    {
                        "properties": [
                            ("type", 'RIGHT'),
                            ("relative", True),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {
                        "type": 'MIDDLEMOUSE',
                        "value": 'CLICK_DRAG',
                        "alt": True,
                        "direction": 'WEST',
                    },
                    {
                        "properties": [
                            ("type", 'LEFT'),
                            ("relative", True),
                        ],
                    },
                ),
                (
                    "view3d.view_center_pick",
                    {"type": 'MIDDLEMOUSE', "value": 'CLICK', "alt": True},
                    None,
                ),
                ("view3d.ndof_orbit_zoom", {"type": 'NDOF_MOTION', "value": 'ANY'}, None),
                ("view3d.ndof_orbit", {"type": 'NDOF_MOTION', "value": 'ANY', "ctrl": True}, None),
                ("view3d.ndof_pan", {"type": 'NDOF_MOTION', "value": 'ANY', "shift": True}, None),
                (
                    "view3d.ndof_all",
                    {"type": 'NDOF_MOTION', "value": 'ANY', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "view3d.view_selected",
                    {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'},
                    {
                        "properties": [
                            ("use_all_regions", False),
                        ],
                    },
                ),
                (
                    "view3d.view_roll",
                    {"type": 'NDOF_BUTTON_ROLL_CW', "value": 'PRESS'},
                    {
                        "properties": [
                            ("angle", 1.5707964),
                        ],
                    },
                ),
                (
                    "view3d.view_roll",
                    {"type": 'NDOF_BUTTON_ROLL_CCW', "value": 'PRESS'},
                    {
                        "properties": [
                            ("angle", -1.5707964),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NDOF_BUTTON_FRONT', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'FRONT'),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NDOF_BUTTON_BACK', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'BACK'),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NDOF_BUTTON_LEFT', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'LEFT'),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NDOF_BUTTON_RIGHT', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'RIGHT'),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NDOF_BUTTON_TOP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'TOP'),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NDOF_BUTTON_BOTTOM', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'BOTTOM'),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NDOF_BUTTON_FRONT', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("type", 'FRONT'),
                            ("align_active", True),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NDOF_BUTTON_RIGHT', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("type", 'RIGHT'),
                            ("align_active", True),
                        ],
                    },
                ),
                (
                    "view3d.view_axis",
                    {"type": 'NDOF_BUTTON_TOP', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("type", 'TOP'),
                            ("align_active", True),
                        ],
                    },
                ),
                (
                    "view3d.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK'},
                    {
                        "properties": [
                            ("deselect_all", True),
                        ],
                    },
                ),
                (
                    "view3d.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("toggle", True),
                        ],
                    },
                ),
                (
                    "view3d.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            ("center", True),
                            ("object", True),
                        ],
                    },
                ),
                (
                    "view3d.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "alt": True},
                    {
                        "properties": [
                            ("enumerate", True),
                        ],
                    },
                ),
                (
                    "view3d.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("toggle", True),
                            ("center", True),
                        ],
                    },
                ),
                (
                    "view3d.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("center", True),
                            ("enumerate", True),
                        ],
                    },
                ),
                (
                    "view3d.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("toggle", True),
                            ("enumerate", True),
                        ],
                    },
                ),
                (
                    "view3d.select",
                    {
                        "type": 'LEFTMOUSE',
                        "value": 'CLICK',
                        "shift": True,
                        "ctrl": True,
                        "alt": True,
                    },
                    {
                        "properties": [
                            ("toggle", True),
                            ("center", True),
                            ("enumerate", True),
                        ],
                    },
                ),
                ("view3d.select_box", {"type": 'B', "value": 'PRESS'}, None),
                (
                    "view3d.select_lasso",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'ADD'),
                        ],
                    },
                ),
                (
                    "view3d.select_lasso",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'SUB'),
                        ],
                    },
                ),
                (
                    "view3d.select_circle",
                    {"type": 'C', "value": 'CLICK'},
                    {
                        "active": False,
                    },
                ),
                ("view3d.clip_border", {"type": 'B', "value": 'PRESS', "alt": True}, None),
                ("view3d.zoom_border", {"type": 'B', "value": 'PRESS', "shift": True}, None),
                ("view3d.render_border", {"type": 'B', "value": 'PRESS', "ctrl": True}, None),
                (
                    "view3d.clear_render_border",
                    {"type": 'B', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "view3d.camera_to_view",
                    {"type": 'NUMPAD_0', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "view3d.object_as_camera",
                    {"type": 'NUMPAD_0', "value": 'PRESS', "ctrl": True},
                    None,
                ),
                ("view3d.copybuffer", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
                ("view3d.pastebuffer", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
                ("transform.translate", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'}, None),
                ("transform.translate", {"type": 'G', "value": 'PRESS'}, None),
                ("transform.rotate", {"type": 'R', "value": 'CLICK'}, None),
                ("transform.resize", {"type": 'S', "value": 'CLICK'}, None),
                (
                    "transform.tosphere",
                    {"type": 'S', "value": 'PRESS', "shift": True, "alt": True},
                    None,
                ),
                (
                    "transform.shear",
                    {"type": 'S', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
                    None,
                ),
                ("transform.bend", {"type": 'W', "value": 'PRESS', "shift": True}, None),
                ("transform.mirror", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
                (
                    "object.transform_axis_target",
                    {"type": 'T', "value": 'PRESS', "shift": True},
                    None,
                ),
                ("transform.skin_resize", {"type": 'A', "value": 'CLICK', "ctrl": True}, None),
                (
                    "wm.context_toggle",
                    {"type": 'TAB', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.use_snap'),
                        ],
                    },
                ),
                (
                    "wm.call_panel",
                    {"type": 'TAB', "value": 'CLICK', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PT_snapping'),
                            ("keep_open", True),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'S', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_snap_pie'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'ACCENT_GRAVE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("data_path", 'space_data.show_gizmo'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'PERIOD', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_pivot_pie'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'COMMA', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_orientations_pie'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'Z', "value": 'CLICK'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_shading_pie'),
                        ],
                    },
                ),
                (
                    "view3d.toggle_shading",
                    {"type": 'Z', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("type", 'WIREFRAME'),
                        ],
                        "active": False,
                    },
                ),
                ("view3d.toggle_xray", {"type": 'Z', "value": 'PRESS', "alt": True}, None),
                (
                    "wm.context_toggle",
                    {"type": 'Z', "value": 'CLICK', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("data_path", 'space_data.overlay.show_overlays'),
                        ],
                    },
                ),
                (
                    "wm.tool_set_by_id",
                    {"type": 'W', "value": 'CLICK'},
                    {
                        "properties": [
                            ("name", 'builtin.select_box'),
                            ("cycle", True),
                        ],
                    },
                ),
            ],
        },
    ),
    (
        "3D View Generic",
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "wm.context_toggle",
                    {"type": 'T', "value": 'CLICK'},
                    {
                        "properties": [
                            ("data_path", 'space_data.show_region_toolbar'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'N', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.show_region_ui'),
                        ],
                    },
                ),
            ],
        },
    ),
    (
        "Animation Channels",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {
            "items": [
                ("anim.channels_click", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
                (
                    "anim.channels_click",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "anim.channels_click",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("children_only", True),
                        ],
                    },
                ),
                (
                    "anim.channels_rename",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
                    None,
                ),
                ("anim.channels_rename", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK'}, None),
                ("anim.channel_select_keys", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK'}, None),
                (
                    "anim.channel_select_keys",
                    {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK', "shift": True},
                    {
                        "properties": [
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "anim.channels_select_filter",
                    {"type": 'F', "value": 'PRESS', "ctrl": True},
                    None,
                ),
                (
                    "anim.channels_select_all",
                    {"type": 'A', "value": 'CLICK'},
                    {
                        "properties": [
                            ("action", 'SELECT'),
                        ],
                    },
                ),
                (
                    "anim.channels_select_all",
                    {"type": 'A', "value": 'CLICK', "alt": True},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                (
                    "anim.channels_select_all",
                    {"type": 'I', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("action", 'INVERT'),
                        ],
                    },
                ),
                (
                    "anim.channels_select_all",
                    {"type": 'A', "value": 'DOUBLE_CLICK'},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                ("anim.channels_select_box", {"type": 'B', "value": 'PRESS'}, None),
                ("anim.channels_select_box", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'}, None),
                (
                    "anim.channels_select_box",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "anim.channels_select_box",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("deselect", True),
                        ],
                    },
                ),
                ("anim.channels_delete", {"type": 'X', "value": 'PRESS'}, None),
                ("anim.channels_delete", {"type": 'DEL', "value": 'PRESS'}, None),
                (
                    "anim.channels_setting_toggle",
                    {"type": 'W', "value": 'PRESS', "shift": True},
                    None,
                ),
                (
                    "anim.channels_setting_enable",
                    {"type": 'W', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "anim.channels_setting_disable",
                    {"type": 'W', "value": 'PRESS', "alt": True},
                    None,
                ),
                ("anim.channels_editable_toggle", {"type": 'TAB', "value": 'PRESS'}, None),
                ("anim.channels_expand", {"type": 'NUMPAD_PLUS', "value": 'PRESS'}, None),
                ("anim.channels_collapse", {"type": 'NUMPAD_MINUS', "value": 'PRESS'}, None),
                (
                    "anim.channels_expand",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("all", False),
                        ],
                    },
                ),
                (
                    "anim.channels_collapse",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("all", False),
                        ],
                    },
                ),
                (
                    "anim.channels_move",
                    {"type": 'PAGE_UP', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("direction", 'UP'),
                        ],
                    },
                ),
                (
                    "anim.channels_move",
                    {"type": 'PAGE_DOWN', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("direction", 'DOWN'),
                        ],
                    },
                ),
                (
                    "anim.channels_move",
                    {"type": 'PAGE_UP', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("direction", 'TOP'),
                        ],
                    },
                ),
                (
                    "anim.channels_move",
                    {"type": 'PAGE_DOWN', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("direction", 'BOTTOM'),
                        ],
                    },
                ),
                ("anim.channels_group", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
                (
                    "anim.channels_ungroup",
                    {"type": 'G', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "wm.call_menu",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'DOPESHEET_MT_channel_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'APP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'DOPESHEET_MT_channel_context_menu'),
                        ],
                    },
                ),
            ],
        },
    ),
    (
        "Curve",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "wm.call_menu_pie",
                    {"type": 'V', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_V'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'T', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_T'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'F', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_F'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'A', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'TOPBAR_MT_edit_curve_add'),
                        ],
                    },
                ),
                ("curve.handle_type_set", {"type": 'V', "value": 'CLICK'}, None),
                ("curve.vertex_add", {"type": 'RIGHTMOUSE', "value": 'CLICK', "ctrl": True}, None),
                (
                    "curve.select_all",
                    {"type": 'A', "value": 'CLICK'},
                    {
                        "properties": [
                            ("action", 'SELECT'),
                        ],
                    },
                ),
                (
                    "curve.select_all",
                    {"type": 'A', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                (
                    "curve.select_all",
                    {"type": 'I', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("action", 'INVERT'),
                        ],
                    },
                ),
                (
                    "curve.select_all",
                    {"type": 'A', "value": 'DOUBLE_CLICK'},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                ("curve.select_row", {"type": 'R', "value": 'CLICK', "shift": True}, None),
                (
                    "curve.select_more",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    None,
                ),
                (
                    "curve.select_less",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    None,
                ),
                ("curve.select_linked", {"type": 'L', "value": 'PRESS', "ctrl": True}, None),
                ("curve.select_similar", {"type": 'G', "value": 'PRESS', "shift": True}, None),
                (
                    "curve.select_linked_pick",
                    {"type": 'Q', "value": 'CLICK'},
                    {
                        "properties": [
                            ("deselect", False),
                        ],
                    },
                ),
                (
                    "curve.select_linked_pick",
                    {"type": 'Q', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("deselect", True),
                        ],
                    },
                ),
                (
                    "curve.shortest_path_pick",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True},
                    None,
                ),
                ("curve.separate", {"type": 'P', "value": 'PRESS'}, None),
                ("curve.split", {"type": 'Y', "value": 'PRESS'}, None),
                ("curve.extrude_move", {"type": 'E', "value": 'CLICK'}, None),
                ("curve.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
                ("curve.make_segment", {"type": 'F', "value": 'PRESS'}, None),
                ("curve.cyclic_toggle", {"type": 'C', "value": 'PRESS', "alt": True}, None),
                (
                    "wm.call_menu",
                    {"type": 'X', "value": 'CLICK'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_curve_delete'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'DEL', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_curve_delete'),
                        ],
                    },
                ),
                ("curve.dissolve_verts", {"type": 'X', "value": 'CLICK', "ctrl": True}, None),
                ("curve.dissolve_verts", {"type": 'DEL', "value": 'PRESS', "ctrl": True}, None),
                ("curve.tilt_clear", {"type": 'T', "value": 'PRESS', "alt": True}, None),
                ("transform.tilt", {"type": 'T', "value": 'PRESS', "ctrl": True}, None),
                (
                    "transform.transform",
                    {"type": 'S', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("mode", 'CURVE_SHRINKFATTEN'),
                        ],
                    },
                ),
                ("curve.reveal", {"type": 'H', "value": 'PRESS', "alt": True}, None),
                (
                    "curve.hide",
                    {"type": 'H', "value": 'PRESS'},
                    {
                        "properties": [
                            ("unselected", False),
                        ],
                    },
                ),
                (
                    "curve.hide",
                    {"type": 'H', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("unselected", True),
                        ],
                    },
                ),
                (
                    "curve.normals_make_consistent",
                    {"type": 'N', "value": 'PRESS', "shift": True},
                    None,
                ),
                ("object.vertex_parent_set", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
                (
                    "wm.call_menu",
                    {"type": 'H', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_hook'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'O', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_proportional_editing_falloff_pie'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'O', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.use_proportional_edit'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'O', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.use_proportional_connected'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_curve_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'APP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_curve_context_menu'),
                        ],
                    },
                ),
            ],
        },
    ),
    (
        "Dopesheet",
        {"space_type": 'DOPESHEET_EDITOR', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "wm.call_menu_pie",
                    {"type": 'SPACE', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Space_KEY_shift'),
                        ],
                    },
                ),
                (
                    "screen.animation_play",
                    {"type": 'SPACE', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("reverse", True),
                        ],
                    },
                ),
                ("pie.key_space", {"type": 'SPACE', "value": 'CLICK'}, None),
                ("anim.change_frame", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "alt": True}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'SPACE', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Space_KEY_shift'),
                        ],
                    },
                ),
                (
                    "screen.animation_play",
                    {"type": 'SPACE', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("reverse", True),
                        ],
                        "active": False,
                    },
                ),
                ("pie.key_space", {"type": 'SPACE', "value": 'CLICK'}, None),
                (
                    "action.clickselect",
                    {"type": 'LEFTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("deselect_all", True),
                        ],
                    },
                ),
                (
                    "action.clickselect",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("column", True),
                        ],
                    },
                ),
                (
                    "action.clickselect",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "action.clickselect",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("extend", True),
                            ("column", True),
                        ],
                    },
                ),
                (
                    "action.clickselect",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("channel", True),
                        ],
                    },
                ),
                (
                    "action.clickselect",
                    {
                        "type": 'LEFTMOUSE',
                        "value": 'PRESS',
                        "shift": True,
                        "ctrl": True,
                        "alt": True,
                    },
                    {
                        "properties": [
                            ("extend", True),
                            ("channel", True),
                        ],
                    },
                ),
                (
                    "action.select_leftright",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'CHECK'),
                        ],
                    },
                ),
                (
                    "action.select_leftright",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'CHECK'),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "action.select_leftright",
                    {"type": 'LEFT_BRACKET', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'LEFT'),
                        ],
                    },
                ),
                (
                    "action.select_leftright",
                    {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'RIGHT'),
                        ],
                    },
                ),
                (
                    "action.select_all",
                    {"type": 'A', "value": 'PRESS'},
                    {
                        "properties": [
                            ("action", 'SELECT'),
                        ],
                    },
                ),
                (
                    "action.select_all",
                    {"type": 'A', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                (
                    "action.select_all",
                    {"type": 'I', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("action", 'INVERT'),
                        ],
                    },
                ),
                (
                    "action.select_all",
                    {"type": 'A', "value": 'DOUBLE_CLICK'},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                (
                    "action.select_box",
                    {"type": 'B', "value": 'PRESS'},
                    {
                        "properties": [
                            ("axis_range", False),
                        ],
                    },
                ),
                (
                    "action.select_box",
                    {"type": 'B', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("axis_range", True),
                        ],
                    },
                ),
                (
                    "action.select_box",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("mode", 'SET'),
                            ("tweak", True),
                        ],
                    },
                ),
                (
                    "action.select_box",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("mode", 'ADD'),
                            ("tweak", True),
                        ],
                    },
                ),
                (
                    "action.select_box",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'SUB'),
                            ("tweak", True),
                        ],
                    },
                ),
                (
                    "action.select_lasso",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'ADD'),
                        ],
                    },
                ),
                (
                    "action.select_lasso",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'SUB'),
                        ],
                    },
                ),
                ("action.select_circle", {"type": 'C', "value": 'PRESS'}, None),
                (
                    "action.select_column",
                    {"type": 'K', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'KEYS'),
                        ],
                    },
                ),
                (
                    "action.select_column",
                    {"type": 'K', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'CFRA'),
                        ],
                    },
                ),
                (
                    "action.select_column",
                    {"type": 'K', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("mode", 'MARKERS_COLUMN'),
                        ],
                    },
                ),
                (
                    "action.select_column",
                    {"type": 'K', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("mode", 'MARKERS_BETWEEN'),
                        ],
                    },
                ),
                (
                    "action.select_more",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    None,
                ),
                (
                    "action.select_less",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    None,
                ),
                ("action.select_linked", {"type": 'L', "value": 'PRESS'}, None),
                ("action.frame_jump", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'S', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'DOPESHEET_MT_snap_pie'),
                        ],
                    },
                ),
                ("action.mirror", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
                ("action.handle_type", {"type": 'V', "value": 'PRESS'}, None),
                ("action.interpolation_type", {"type": 'T', "value": 'PRESS'}, None),
                ("action.extrapolation_type", {"type": 'E', "value": 'PRESS', "shift": True}, None),
                ("action.easing_type", {"type": 'E', "value": 'PRESS', "ctrl": True}, None),
                ("action.keyframe_type", {"type": 'R', "value": 'PRESS'}, None),
                (
                    "action.sample",
                    {"type": 'O', "value": 'PRESS', "shift": True, "alt": True},
                    None,
                ),
                (
                    "wm.call_menu",
                    {"type": 'X', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'DOPESHEET_MT_delete'),
                        ],
                    },
                ),
                (
                    "action.delete",
                    {"type": 'DEL', "value": 'PRESS'},
                    {
                        "properties": [
                            ("confirm", False),
                        ],
                    },
                ),
                ("action.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
                ("action.keyframe_insert", {"type": 'I', "value": 'PRESS'}, None),
                ("action.copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
                ("action.paste", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
                (
                    "action.paste",
                    {"type": 'V', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("flipped", True),
                        ],
                    },
                ),
                (
                    "action.previewrange_set",
                    {"type": 'P', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                ("action.view_all", {"type": 'HOME', "value": 'PRESS'}, None),
                ("action.view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
                ("action.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
                ("action.view_frame", {"type": 'NUMPAD_0', "value": 'PRESS'}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'ACCENT_GRAVE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'DOPESHEET_MT_view_pie'),
                        ],
                    },
                ),
                ("anim.channels_editable_toggle", {"type": 'TAB', "value": 'PRESS'}, None),
                (
                    "anim.channels_select_filter",
                    {"type": 'F', "value": 'PRESS', "ctrl": True},
                    None,
                ),
                (
                    "transform.transform",
                    {"type": 'G', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'TIME_TRANSLATE'),
                        ],
                    },
                ),
                (
                    "transform.transform",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("mode", 'TIME_TRANSLATE'),
                        ],
                    },
                ),
                (
                    "transform.transform",
                    {"type": 'E', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'TIME_EXTEND'),
                        ],
                    },
                ),
                (
                    "transform.transform",
                    {"type": 'S', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'TIME_SCALE'),
                        ],
                    },
                ),
                (
                    "transform.transform",
                    {"type": 'T', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("mode", 'TIME_SLIDE'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'O', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_proportional_editing_falloff_pie'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'O', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.use_proportional_action'),
                        ],
                    },
                ),
                ("marker.add", {"type": 'M', "value": 'PRESS'}, None),
                ("marker.camera_bind", {"type": 'B', "value": 'PRESS', "ctrl": True}, None),
                (
                    "wm.call_menu",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'DOPESHEET_MT_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'APP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'DOPESHEET_MT_context_menu'),
                        ],
                    },
                ),
                (
                    "anim.change_frame",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True},
                    None,
                ),
            ],
        },
    ),
    (
        "File Browser",
        {"space_type": 'FILE_BROWSER', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "wm.super_export",
                    {"type": 'E', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "wm.super_import",
                    {"type": 'V', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "wm.context_toggle",
                    {"type": 'T', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.show_region_toolbar'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'N', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.show_region_tool_props'),
                        ],
                    },
                ),
                ("file.parent", {"type": 'UP_ARROW', "value": 'PRESS', "alt": True}, None),
                ("file.previous", {"type": 'LEFT_ARROW', "value": 'PRESS', "alt": True}, None),
                ("file.next", {"type": 'RIGHT_ARROW', "value": 'PRESS', "alt": True}, None),
                ("file.refresh", {"type": 'R', "value": 'PRESS'}, None),
                ("asset.library_refresh", {"type": 'R', "value": 'PRESS'}, None),
                ("file.parent", {"type": 'P', "value": 'PRESS'}, None),
                ("file.previous", {"type": 'BACK_SPACE', "value": 'PRESS'}, None),
                ("file.next", {"type": 'BACK_SPACE', "value": 'PRESS', "shift": True}, None),
                (
                    "wm.context_toggle",
                    {"type": 'H', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.params.show_hidden'),
                        ],
                    },
                ),
                (
                    "file.directory_new",
                    {"type": 'I', "value": 'PRESS'},
                    {
                        "properties": [
                            ("confirm", False),
                        ],
                    },
                ),
                ("file.rename", {"type": 'F2', "value": 'PRESS'}, None),
                ("file.delete", {"type": 'X', "value": 'PRESS'}, None),
                ("file.delete", {"type": 'DEL', "value": 'PRESS'}, None),
                ("file.smoothscroll", {"type": 'TIMER1', "value": 'ANY', "any": True}, None),
                ("file.bookmark_add", {"type": 'B', "value": 'PRESS', "ctrl": True}, None),
                ("file.start_filter", {"type": 'F', "value": 'PRESS', "ctrl": True}, None),
                ("file.edit_directory_path", {"type": 'L', "value": 'PRESS', "ctrl": True}, None),
                (
                    "file.filenum",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("increment", 1),
                        ],
                    },
                ),
                (
                    "file.filenum",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("increment", 10),
                        ],
                    },
                ),
                (
                    "file.filenum",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    {
                        "properties": [
                            ("increment", 100),
                        ],
                    },
                ),
                (
                    "file.filenum",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("increment", -1),
                        ],
                    },
                ),
                (
                    "file.filenum",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("increment", -10),
                        ],
                    },
                ),
                (
                    "file.filenum",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    {
                        "properties": [
                            ("increment", -100),
                        ],
                    },
                ),
                (
                    "file.select",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("open", False),
                            ("only_activate_if_selected", True),
                            ("pass_through", True),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'FILEBROWSER_MT_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'APP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'FILEBROWSER_MT_context_menu'),
                        ],
                    },
                ),
            ],
        },
    ),
    (
        "Frames",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "power_sequencer.jump_to_cut",
                    {"type": 'DOWN_ARROW', "value": 'PRESS'},
                    {
                        "properties": [
                            ("direction", 'LEFT'),
                        ],
                    },
                ),
                (
                    "power_sequencer.jump_to_cut",
                    {"type": 'UP_ARROW', "value": 'PRESS'},
                    {
                        "properties": [
                            ("direction", 'RIGHT'),
                        ],
                    },
                ),
                (
                    "power_sequencer.jump_time_offset",
                    {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("direction", 'backward'),
                        ],
                    },
                ),
                (
                    "power_sequencer.jump_time_offset",
                    {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("direction", 'forward'),
                        ],
                    },
                ),
                (
                    "screen.amaranth_frame_jump",
                    {"type": 'DOWN_ARROW', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("forward", False),
                        ],
                    },
                ),
                (
                    "screen.amaranth_frame_jump",
                    {"type": 'UP_ARROW', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("forward", True),
                        ],
                    },
                ),
                (
                    "screen.amth_keyframe_jump_inbetween",
                    {"type": 'DOWN_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("backwards", True),
                        ],
                    },
                ),
                (
                    "screen.amth_keyframe_jump_inbetween",
                    {"type": 'UP_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("backwards", False),
                        ],
                    },
                ),
                (
                    "screen.frame_offset",
                    {"type": 'LEFT_ARROW', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("delta", -1),
                        ],
                    },
                ),
                (
                    "screen.frame_offset",
                    {"type": 'RIGHT_ARROW', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("delta", 1),
                        ],
                    },
                ),
                (
                    "screen.frame_jump",
                    {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("end", True),
                        ],
                    },
                ),
                (
                    "screen.frame_jump",
                    {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("end", False),
                        ],
                    },
                ),
                (
                    "screen.keyframe_jump",
                    {"type": 'UP_ARROW', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("next", True),
                        ],
                    },
                ),
                (
                    "screen.keyframe_jump",
                    {"type": 'DOWN_ARROW', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("next", False),
                        ],
                    },
                ),
                (
                    "screen.keyframe_jump",
                    {"type": 'MEDIA_LAST', "value": 'PRESS'},
                    {
                        "properties": [
                            ("next", True),
                        ],
                    },
                ),
                (
                    "screen.keyframe_jump",
                    {"type": 'MEDIA_FIRST', "value": 'PRESS'},
                    {
                        "properties": [
                            ("next", False),
                        ],
                    },
                ),
                (
                    "screen.frame_offset",
                    {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("delta", 1),
                        ],
                    },
                ),
                (
                    "screen.frame_offset",
                    {"type": 'WHEELUPMOUSE', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("delta", -1),
                        ],
                    },
                ),
                (
                    "screen.animation_play",
                    {"type": 'SPACE', "value": 'PRESS'},
                    {
                        "active": False,
                    },
                ),
                (
                    "screen.animation_play",
                    {"type": 'SPACE', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("reverse", True),
                        ],
                        "active": False,
                    },
                ),
                ("screen.animation_cancel", {"type": 'ESC', "value": 'PRESS'}, None),
                ("screen.animation_play", {"type": 'MEDIA_PLAY', "value": 'PRESS'}, None),
                ("screen.animation_cancel", {"type": 'MEDIA_STOP', "value": 'PRESS'}, None),
            ],
        },
    ),
    (
        "Graph Editor",
        {"space_type": 'GRAPH_EDITOR', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "wm.call_menu_pie",
                    {"type": 'SPACE', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Space_KEY_shift'),
                        ],
                    },
                ),
                (
                    "screen.animation_play",
                    {"type": 'SPACE', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("reverse", True),
                        ],
                    },
                ),
                ("pie.key_space", {"type": 'SPACE', "value": 'CLICK'}, None),
                ("graph.delete_static_channels", {"type": 'D', "value": 'PRESS'}, None),
                ("graph.cursor_set", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "alt": True}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'SPACE', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Space_KEY_shift'),
                        ],
                    },
                ),
                (
                    "screen.animation_play",
                    {"type": 'SPACE', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("reverse", True),
                        ],
                        "active": False,
                    },
                ),
                ("pie.key_space", {"type": 'SPACE', "value": 'CLICK'}, None),
                (
                    "wm.context_toggle",
                    {"type": 'H', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("data_path", 'space_data.show_handles'),
                        ],
                    },
                ),
                (
                    "graph.clickselect",
                    {"type": 'LEFTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("deselect_all", True),
                        ],
                    },
                ),
                (
                    "graph.clickselect",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("column", True),
                        ],
                    },
                ),
                (
                    "graph.clickselect",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "graph.clickselect",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("extend", True),
                            ("column", True),
                        ],
                    },
                ),
                (
                    "graph.clickselect",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("curves", True),
                        ],
                    },
                ),
                (
                    "graph.clickselect",
                    {
                        "type": 'LEFTMOUSE',
                        "value": 'PRESS',
                        "shift": True,
                        "ctrl": True,
                        "alt": True,
                    },
                    {
                        "properties": [
                            ("extend", True),
                            ("curves", True),
                        ],
                    },
                ),
                (
                    "graph.select_leftright",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'CHECK'),
                        ],
                    },
                ),
                (
                    "graph.select_leftright",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'CHECK'),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "graph.select_leftright",
                    {"type": 'LEFT_BRACKET', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'LEFT'),
                        ],
                    },
                ),
                (
                    "graph.select_leftright",
                    {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'RIGHT'),
                        ],
                    },
                ),
                (
                    "graph.select_all",
                    {"type": 'A', "value": 'PRESS'},
                    {
                        "properties": [
                            ("action", 'SELECT'),
                        ],
                    },
                ),
                (
                    "graph.select_all",
                    {"type": 'A', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                (
                    "graph.select_all",
                    {"type": 'I', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("action", 'INVERT'),
                        ],
                    },
                ),
                (
                    "graph.select_all",
                    {"type": 'A', "value": 'DOUBLE_CLICK'},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                ("graph.select_box", {"type": 'B', "value": 'PRESS'}, None),
                (
                    "graph.select_box",
                    {"type": 'B', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("axis_range", True),
                        ],
                    },
                ),
                (
                    "graph.select_box",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("tweak", True),
                            ("mode", 'SET'),
                        ],
                    },
                ),
                (
                    "graph.select_box",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("tweak", True),
                            ("mode", 'ADD'),
                        ],
                    },
                ),
                (
                    "graph.select_box",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("tweak", True),
                            ("mode", 'SUB'),
                        ],
                    },
                ),
                (
                    "graph.select_lasso",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'ADD'),
                        ],
                    },
                ),
                (
                    "graph.select_lasso",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'SUB'),
                        ],
                    },
                ),
                ("graph.select_circle", {"type": 'C', "value": 'PRESS'}, None),
                (
                    "graph.select_column",
                    {"type": 'K', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'KEYS'),
                        ],
                    },
                ),
                (
                    "graph.select_column",
                    {"type": 'K', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'CFRA'),
                        ],
                    },
                ),
                (
                    "graph.select_column",
                    {"type": 'K', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("mode", 'MARKERS_COLUMN'),
                        ],
                    },
                ),
                (
                    "graph.select_column",
                    {"type": 'K', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("mode", 'MARKERS_BETWEEN'),
                        ],
                    },
                ),
                (
                    "graph.select_more",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    None,
                ),
                (
                    "graph.select_less",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    None,
                ),
                ("graph.select_linked", {"type": 'L', "value": 'PRESS'}, None),
                ("graph.frame_jump", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'S', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'GRAPH_MT_snap_pie'),
                        ],
                    },
                ),
                ("graph.mirror", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
                ("graph.handle_type", {"type": 'V', "value": 'PRESS'}, None),
                ("graph.interpolation_type", {"type": 'T', "value": 'PRESS'}, None),
                ("graph.easing_type", {"type": 'E', "value": 'PRESS', "ctrl": True}, None),
                ("graph.smooth", {"type": 'O', "value": 'PRESS', "alt": True}, None),
                ("graph.sample", {"type": 'O', "value": 'PRESS', "shift": True, "alt": True}, None),
                ("graph.bake", {"type": 'C', "value": 'PRESS', "alt": True}, None),
                (
                    "wm.call_menu",
                    {"type": 'X', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'GRAPH_MT_delete'),
                        ],
                    },
                ),
                (
                    "graph.delete",
                    {"type": 'DEL', "value": 'PRESS'},
                    {
                        "properties": [
                            ("confirm", False),
                        ],
                    },
                ),
                ("graph.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
                ("graph.keyframe_insert", {"type": 'I', "value": 'PRESS'}, None),
                (
                    "graph.click_insert",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK', "ctrl": True},
                    None,
                ),
                (
                    "graph.click_insert",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("extend", True),
                        ],
                    },
                ),
                ("graph.copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
                ("graph.paste", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
                (
                    "graph.paste",
                    {"type": 'V', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("flipped", True),
                        ],
                    },
                ),
                (
                    "graph.previewrange_set",
                    {"type": 'P', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                ("graph.view_all", {"type": 'HOME', "value": 'PRESS'}, None),
                ("graph.view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
                ("graph.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
                ("graph.view_frame", {"type": 'NUMPAD_0', "value": 'PRESS'}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'ACCENT_GRAVE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'GRAPH_MT_view_pie'),
                        ],
                    },
                ),
                (
                    "graph.fmodifier_add",
                    {"type": 'M', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("only_active", False),
                        ],
                    },
                ),
                ("anim.channels_editable_toggle", {"type": 'TAB', "value": 'PRESS'}, None),
                ("transform.translate", {"type": 'G', "value": 'PRESS'}, None),
                ("transform.translate", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'}, None),
                (
                    "transform.transform",
                    {"type": 'E', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'TIME_EXTEND'),
                        ],
                    },
                ),
                ("transform.rotate", {"type": 'R', "value": 'PRESS'}, None),
                ("transform.resize", {"type": 'S', "value": 'PRESS'}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'O', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_proportional_editing_falloff_pie'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'O', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.use_proportional_fcurve'),
                        ],
                    },
                ),
                ("marker.add", {"type": 'M', "value": 'PRESS'}, None),
                (
                    "wm.call_menu",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'GRAPH_MT_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'APP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'GRAPH_MT_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'PERIOD', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'GRAPH_MT_pivot_pie'),
                        ],
                    },
                ),
                ("graph.cursor_set", {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True}, None),
            ],
        },
    ),
    (
        "Image",
        {"space_type": 'IMAGE_EDITOR', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "wm.call_menu_pie",
                    {"type": 'TAB', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Ctrl_Tab'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'R', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'UV_PIE_MT_Bottom_R'),
                        ],
                    },
                ),
                (
                    "friendly.pivot2d",
                    {"type": 'D', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                ("image.view_all", {"type": 'HOME', "value": 'PRESS'}, None),
                (
                    "image.view_all",
                    {"type": 'HOME', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("fit_view", True),
                        ],
                    },
                ),
                ("image.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
                ("image.view_cursor_center", {"type": 'C', "value": 'PRESS', "shift": True}, None),
                ("image.view_pan", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
                ("image.view_pan", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "shift": True}, None),
                ("image.view_pan", {"type": 'TRACKPADPAN', "value": 'ANY'}, None),
                ("image.view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
                ("image.view_ndof", {"type": 'NDOF_MOTION', "value": 'ANY'}, None),
                ("image.view_zoom_in", {"type": 'WHEELINMOUSE', "value": 'PRESS'}, None),
                ("image.view_zoom_out", {"type": 'WHEELOUTMOUSE', "value": 'PRESS'}, None),
                (
                    "image.view_zoom_in",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "repeat": True},
                    None,
                ),
                (
                    "image.view_zoom_out",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "repeat": True},
                    None,
                ),
                ("image.view_zoom", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "ctrl": True}, None),
                ("image.view_zoom", {"type": 'TRACKPADZOOM', "value": 'ANY'}, None),
                ("image.view_zoom", {"type": 'TRACKPADPAN', "value": 'ANY', "ctrl": True}, None),
                ("image.view_zoom_border", {"type": 'B', "value": 'PRESS', "shift": True}, None),
                (
                    "image.view_zoom_ratio",
                    {"type": 'NUMPAD_8', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("ratio", 8.0),
                        ],
                    },
                ),
                (
                    "image.view_zoom_ratio",
                    {"type": 'NUMPAD_4', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("ratio", 4.0),
                        ],
                    },
                ),
                (
                    "image.view_zoom_ratio",
                    {"type": 'NUMPAD_2', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("ratio", 2.0),
                        ],
                    },
                ),
                (
                    "image.view_zoom_ratio",
                    {"type": 'NUMPAD_8', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("ratio", 8.0),
                        ],
                    },
                ),
                (
                    "image.view_zoom_ratio",
                    {"type": 'NUMPAD_4', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("ratio", 4.0),
                        ],
                    },
                ),
                (
                    "image.view_zoom_ratio",
                    {"type": 'NUMPAD_2', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("ratio", 2.0),
                        ],
                    },
                ),
                (
                    "image.view_zoom_ratio",
                    {"type": 'NUMPAD_1', "value": 'PRESS'},
                    {
                        "properties": [
                            ("ratio", 1.0),
                        ],
                    },
                ),
                (
                    "image.view_zoom_ratio",
                    {"type": 'NUMPAD_2', "value": 'PRESS'},
                    {
                        "properties": [
                            ("ratio", 0.5),
                        ],
                    },
                ),
                (
                    "image.view_zoom_ratio",
                    {"type": 'NUMPAD_4', "value": 'PRESS'},
                    {
                        "properties": [
                            ("ratio", 0.25),
                        ],
                    },
                ),
                (
                    "image.view_zoom_ratio",
                    {"type": 'NUMPAD_8', "value": 'PRESS'},
                    {
                        "properties": [
                            ("ratio", 0.125),
                        ],
                    },
                ),
                ("image.change_frame", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
                ("image.sample", {"type": 'RIGHTMOUSE', "value": 'PRESS'}, None),
                (
                    "image.curves_point_set",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("point", 'BLACK_POINT'),
                        ],
                    },
                ),
                (
                    "image.curves_point_set",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("point", 'WHITE_POINT'),
                        ],
                    },
                ),
                (
                    "object.mode_set",
                    {"type": 'TAB', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'EDIT'),
                            ("toggle", True),
                        ],
                    },
                ),
                (
                    "wm.context_set_int",
                    {"type": 'ONE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.image.render_slots.active_index'),
                            ("value", 0),
                        ],
                    },
                ),
                (
                    "wm.context_set_int",
                    {"type": 'TWO', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.image.render_slots.active_index'),
                            ("value", 1),
                        ],
                    },
                ),
                (
                    "wm.context_set_int",
                    {"type": 'THREE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.image.render_slots.active_index'),
                            ("value", 2),
                        ],
                    },
                ),
                (
                    "wm.context_set_int",
                    {"type": 'FOUR', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.image.render_slots.active_index'),
                            ("value", 3),
                        ],
                    },
                ),
                (
                    "wm.context_set_int",
                    {"type": 'FIVE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.image.render_slots.active_index'),
                            ("value", 4),
                        ],
                    },
                ),
                (
                    "wm.context_set_int",
                    {"type": 'SIX', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.image.render_slots.active_index'),
                            ("value", 5),
                        ],
                    },
                ),
                (
                    "wm.context_set_int",
                    {"type": 'SEVEN', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.image.render_slots.active_index'),
                            ("value", 6),
                        ],
                    },
                ),
                (
                    "wm.context_set_int",
                    {"type": 'EIGHT', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.image.render_slots.active_index'),
                            ("value", 7),
                        ],
                    },
                ),
                (
                    "wm.context_set_int",
                    {"type": 'NINE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.image.render_slots.active_index'),
                            ("value", 8),
                        ],
                    },
                ),
                ("image.render_border", {"type": 'B', "value": 'PRESS', "ctrl": True}, None),
                (
                    "image.clear_render_border",
                    {"type": 'B', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "wm.context_toggle",
                    {"type": 'ACCENT_GRAVE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("data_path", 'space_data.show_gizmo'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'IMAGE_MT_mask_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'APP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'IMAGE_MT_mask_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'PERIOD', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'IMAGE_MT_pivot_pie'),
                        ],
                    },
                ),
            ],
        },
    ),
    (
        "Image Generic",
        {"space_type": 'IMAGE_EDITOR', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "wm.super_export",
                    {"type": 'E', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "wm.context_toggle",
                    {"type": 'T', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.show_region_toolbar'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'N', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'space_data.show_region_ui'),
                        ],
                    },
                ),
                ("image.new", {"type": 'N', "value": 'PRESS', "alt": True}, None),
                ("image.open", {"type": 'O', "value": 'PRESS', "alt": True}, None),
                ("image.reload", {"type": 'R', "value": 'PRESS', "alt": True}, None),
                ("image.read_viewlayers", {"type": 'R', "value": 'PRESS', "ctrl": True}, None),
                ("image.save", {"type": 'S', "value": 'PRESS', "alt": True}, None),
                ("image.cycle_render_slot", {"type": 'J', "value": 'PRESS', "repeat": True}, None),
                (
                    "image.cycle_render_slot",
                    {"type": 'J', "value": 'PRESS', "alt": True, "repeat": True},
                    {
                        "properties": [
                            ("reverse", True),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'ACCENT_GRAVE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'IMAGE_MT_view_pie'),
                        ],
                    },
                ),
                (
                    "image.save_as",
                    {"type": 'S', "value": 'PRESS', "shift": True, "alt": True},
                    None,
                ),
            ],
        },
    ),
    (
        "Image Paint",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "paint.image_paint",
                    {"type": 'LEFTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'NORMAL'),
                        ],
                    },
                ),
                (
                    "paint.image_paint",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'INVERT'),
                        ],
                    },
                ),
                ("paint.brush_colors_flip", {"type": 'X', "value": 'PRESS'}, None),
                ("paint.grab_clone", {"type": 'RIGHTMOUSE', "value": 'PRESS'}, None),
                ("paint.sample_color", {"type": 'S', "value": 'PRESS'}, None),
                (
                    "brush.scale_size",
                    {"type": 'LEFT_BRACKET', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("scalar", 0.9),
                        ],
                    },
                ),
                (
                    "brush.scale_size",
                    {"type": 'RIGHT_BRACKET', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("scalar", 1.1111112),
                        ],
                    },
                ),
                (
                    "wm.radial_control",
                    {"type": 'F', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path_primary", 'tool_settings.image_paint.brush.size'),
                            ("data_path_secondary", 'tool_settings.unified_paint_settings.size'),
                            (
                                "use_secondary",
                                'tool_settings.unified_paint_settings.use_unified_size',
                            ),
                            (
                                "rotation_path",
                                'tool_settings.image_paint.brush.mask_texture_slot.angle',
                            ),
                            ("color_path", 'tool_settings.image_paint.brush.cursor_color_add'),
                            ("fill_color_path", 'tool_settings.image_paint.brush.color'),
                            (
                                "fill_color_override_path",
                                'tool_settings.unified_paint_settings.color',
                            ),
                            (
                                "fill_color_override_test_path",
                                'tool_settings.unified_paint_settings.use_unified_color',
                            ),
                            ("zoom_path", 'space_data.zoom'),
                            ("image_id", 'tool_settings.image_paint.brush'),
                            ("secondary_tex", True),
                        ],
                    },
                ),
                (
                    "wm.radial_control",
                    {"type": 'F', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("data_path_primary", 'tool_settings.image_paint.brush.strength'),
                            (
                                "data_path_secondary",
                                'tool_settings.unified_paint_settings.strength',
                            ),
                            (
                                "use_secondary",
                                'tool_settings.unified_paint_settings.use_unified_strength',
                            ),
                            (
                                "rotation_path",
                                'tool_settings.image_paint.brush.mask_texture_slot.angle',
                            ),
                            ("color_path", 'tool_settings.image_paint.brush.cursor_color_add'),
                            ("fill_color_path", 'tool_settings.image_paint.brush.color'),
                            (
                                "fill_color_override_path",
                                'tool_settings.unified_paint_settings.color',
                            ),
                            (
                                "fill_color_override_test_path",
                                'tool_settings.unified_paint_settings.use_unified_color',
                            ),
                            ("zoom_path", ''),
                            ("image_id", 'tool_settings.image_paint.brush'),
                            ("secondary_tex", True),
                        ],
                    },
                ),
                (
                    "wm.radial_control",
                    {"type": 'F', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            (
                                "data_path_primary",
                                'tool_settings.image_paint.brush.texture_slot.angle',
                            ),
                            ("data_path_secondary", ''),
                            ("use_secondary", ''),
                            ("rotation_path", 'tool_settings.image_paint.brush.texture_slot.angle'),
                            ("color_path", 'tool_settings.image_paint.brush.cursor_color_add'),
                            ("fill_color_path", 'tool_settings.image_paint.brush.color'),
                            (
                                "fill_color_override_path",
                                'tool_settings.unified_paint_settings.color',
                            ),
                            (
                                "fill_color_override_test_path",
                                'tool_settings.unified_paint_settings.use_unified_color',
                            ),
                            ("zoom_path", ''),
                            ("image_id", 'tool_settings.image_paint.brush'),
                            ("secondary_tex", False),
                        ],
                    },
                ),
                (
                    "wm.radial_control",
                    {"type": 'F', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            (
                                "data_path_primary",
                                'tool_settings.image_paint.brush.mask_texture_slot.angle',
                            ),
                            ("data_path_secondary", ''),
                            ("use_secondary", ''),
                            (
                                "rotation_path",
                                'tool_settings.image_paint.brush.mask_texture_slot.angle',
                            ),
                            ("color_path", 'tool_settings.image_paint.brush.cursor_color_add'),
                            ("fill_color_path", 'tool_settings.image_paint.brush.color'),
                            (
                                "fill_color_override_path",
                                'tool_settings.unified_paint_settings.color',
                            ),
                            (
                                "fill_color_override_test_path",
                                'tool_settings.unified_paint_settings.use_unified_color',
                            ),
                            ("zoom_path", ''),
                            ("image_id", 'tool_settings.image_paint.brush'),
                            ("secondary_tex", True),
                        ],
                    },
                ),
                (
                    "brush.stencil_control",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'TRANSLATION'),
                        ],
                    },
                ),
                (
                    "brush.stencil_control",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("mode", 'SCALE'),
                        ],
                    },
                ),
                (
                    "brush.stencil_control",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'ROTATION'),
                        ],
                    },
                ),
                (
                    "brush.stencil_control",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("mode", 'TRANSLATION'),
                            ("texmode", 'SECONDARY'),
                        ],
                    },
                ),
                (
                    "brush.stencil_control",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'SCALE'),
                            ("texmode", 'SECONDARY'),
                        ],
                    },
                ),
                (
                    "brush.stencil_control",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'ROTATION'),
                            ("texmode", 'SECONDARY'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'M', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'image_paint_object.data.use_paint_mask'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'S', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.image_paint.brush.use_smooth_stroke'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'R', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_angle_control'),
                        ],
                    },
                ),
                (
                    "wm.context_menu_enum",
                    {"type": 'E', "value": 'CLICK'},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.image_paint.brush.stroke_method'),
                        ],
                    },
                ),
                (
                    "wm.call_panel",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PT_paint_texture_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_panel",
                    {"type": 'APP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PT_paint_texture_context_menu'),
                        ],
                    },
                ),
            ],
        },
    ),
    (
        "Mesh",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "wm.call_menu_pie",
                    {"type": 'X', "value": 'CLICK_DRAG', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_X_ctrl_shift'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'U', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_U'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'T', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_T'),
                        ],
                    },
                ),
                ("pie.q_key_shift", {"type": 'Q', "value": 'CLICK', "shift": True}, None),
                ("pie.q_key", {"type": 'Q', "value": 'CLICK'}, None),
                ("mesh.vert_connect_path", {"type": 'F', "value": 'CLICK', "shift": True}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'F', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_F'),
                        ],
                    },
                ),
                (
                    "machin3.symmetrize",
                    {"type": 'X', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("flick", True),
                        ],
                    },
                ),
                (
                    "machin3.call_mesh_machine_menu",
                    {"type": 'Y', "value": 'PRESS'},
                    {
                        "properties": [
                            ("idname", 'mesh_machine'),
                        ],
                    },
                ),
                ("ls.select", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK', "shift": True}, None),
                ("ls.select", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK'}, None),
                (
                    "ls.select",
                    {"type": 'D', "value": 'PRESS'},
                    {
                        "active": False,
                    },
                ),
                (
                    "mesh.smart_fill_repeat",
                    {"type": 'WHEELUPMOUSE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("delta", 1),
                            ("mode", 'NUM_CUTS'),
                        ],
                        "active": False,
                    },
                ),
                (
                    "mesh.smart_fill_repeat",
                    {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("delta", -1),
                            ("mode", 'NUM_CUTS'),
                        ],
                        "active": False,
                    },
                ),
                (
                    "mesh.smart_fill_repeat",
                    {"type": 'WHEELUPMOUSE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("delta", 1),
                            ("mode", 'TWIST'),
                        ],
                        "active": False,
                    },
                ),
                (
                    "mesh.smart_fill_repeat",
                    {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("delta", -1),
                            ("mode", 'TWIST'),
                        ],
                        "active": False,
                    },
                ),
                ("mesh.smart_fill_popup", {"type": 'F', "value": 'DOUBLE_CLICK'}, None),
                (
                    "mesh.snap_utilities_line",
                    {"type": 'K', "value": 'PRESS'},
                    {
                        "properties": [
                            ("wait_for_input", True),
                        ],
                        "active": False,
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'C', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'MESH_MT_CopyFaceSettings'),
                        ],
                    },
                ),
                (
                    "mesh.loopcut_slide",
                    {"type": 'R', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            (
                                "TRANSFORM_OT_edge_slide",
                                [
                                    ("release_confirm", False),
                                ],
                            ),
                        ],
                    },
                ),
                (
                    "mesh.offset_edge_loops_slide",
                    {"type": 'R', "value": 'CLICK', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            (
                                "TRANSFORM_OT_edge_slide",
                                [
                                    ("release_confirm", False),
                                ],
                            ),
                        ],
                    },
                ),
                ("mesh.inset", {"type": 'I', "value": 'PRESS'}, None),
                (
                    "mesh.bevel",
                    {"type": 'B', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("affect", 'EDGES'),
                        ],
                    },
                ),
                ("transform.shrink_fatten", {"type": 'S', "value": 'CLICK', "alt": True}, None),
                (
                    "mesh.bevel",
                    {"type": 'B', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("affect", 'VERTICES'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'ONE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'VERT'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'TWO', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'EDGE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'THREE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'FACE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'ONE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("use_extend", True),
                            ("type", 'VERT'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'TWO', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("use_extend", True),
                            ("type", 'EDGE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'THREE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("use_extend", True),
                            ("type", 'FACE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'ONE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("use_expand", True),
                            ("type", 'VERT'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'TWO', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("use_expand", True),
                            ("type", 'EDGE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'THREE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("use_expand", True),
                            ("type", 'FACE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'ONE', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("use_extend", True),
                            ("use_expand", True),
                            ("type", 'VERT'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'TWO', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("use_extend", True),
                            ("use_expand", True),
                            ("type", 'EDGE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'THREE', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("use_extend", True),
                            ("use_expand", True),
                            ("type", 'FACE'),
                        ],
                    },
                ),
                ("mesh.loop_select", {"type": 'LEFTMOUSE', "value": 'CLICK', "alt": True}, None),
                (
                    "mesh.loop_select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("toggle", True),
                        ],
                    },
                ),
                (
                    "mesh.edgering_select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "mesh.edgering_select",
                    {
                        "type": 'LEFTMOUSE',
                        "value": 'CLICK',
                        "shift": True,
                        "ctrl": True,
                        "alt": True,
                    },
                    {
                        "properties": [
                            ("toggle", True),
                        ],
                    },
                ),
                (
                    "mesh.shortest_path_pick",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            ("use_fill", False),
                        ],
                    },
                ),
                (
                    "mesh.shortest_path_pick",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("use_fill", True),
                        ],
                    },
                ),
                (
                    "mesh.select_all",
                    {"type": 'A', "value": 'CLICK'},
                    {
                        "properties": [
                            ("action", 'SELECT'),
                        ],
                    },
                ),
                (
                    "mesh.select_all",
                    {"type": 'A', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                        "active": False,
                    },
                ),
                (
                    "mesh.select_all",
                    {"type": 'I', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("action", 'INVERT'),
                        ],
                    },
                ),
                (
                    "mesh.select_all",
                    {"type": 'A', "value": 'DOUBLE_CLICK'},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                (
                    "mesh.select_more",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    None,
                ),
                (
                    "mesh.select_less",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    None,
                ),
                (
                    "mesh.select_next_item",
                    {
                        "type": 'NUMPAD_PLUS',
                        "value": 'PRESS',
                        "shift": True,
                        "ctrl": True,
                        "repeat": True,
                    },
                    None,
                ),
                (
                    "mesh.select_prev_item",
                    {
                        "type": 'NUMPAD_MINUS',
                        "value": 'PRESS',
                        "shift": True,
                        "ctrl": True,
                        "repeat": True,
                    },
                    None,
                ),
                ("mesh.select_linked", {"type": 'L', "value": 'PRESS', "ctrl": True}, None),
                (
                    "mesh.select_linked_pick",
                    {"type": 'L', "value": 'PRESS'},
                    {
                        "properties": [
                            ("deselect", False),
                        ],
                    },
                ),
                (
                    "mesh.select_linked_pick",
                    {"type": 'L', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("deselect", True),
                        ],
                    },
                ),
                (
                    "mesh.select_mirror",
                    {"type": 'M', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "wm.call_menu",
                    {"type": 'G', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_mesh_select_similar'),
                        ],
                    },
                ),
                ("mesh.reveal", {"type": 'H', "value": 'PRESS', "alt": True}, None),
                (
                    "mesh.hide",
                    {"type": 'H', "value": 'PRESS'},
                    {
                        "properties": [
                            ("unselected", False),
                        ],
                    },
                ),
                (
                    "mesh.hide",
                    {"type": 'H', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("unselected", True),
                        ],
                    },
                ),
                (
                    "mesh.normals_make_consistent",
                    {"type": 'N', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("inside", False),
                        ],
                    },
                ),
                (
                    "mesh.normals_make_consistent",
                    {"type": 'N', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("inside", True),
                        ],
                    },
                ),
                ("view3d.edit_mesh_extrude_move_normal", {"type": 'E', "value": 'CLICK'}, None),
                (
                    "wm.call_menu",
                    {"type": 'E', "value": 'CLICK', "alt": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_mesh_extrude'),
                        ],
                    },
                ),
                ("transform.edge_crease", {"type": 'E', "value": 'CLICK', "shift": True}, None),
                ("mesh.fill", {"type": 'F', "value": 'CLICK', "alt": True}, None),
                (
                    "mesh.quads_convert_to_tris",
                    {"type": 'T', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("quad_method", 'BEAUTY'),
                            ("ngon_method", 'BEAUTY'),
                        ],
                    },
                ),
                (
                    "mesh.quads_convert_to_tris",
                    {"type": 'T', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("quad_method", 'FIXED'),
                            ("ngon_method", 'CLIP'),
                        ],
                    },
                ),
                ("mesh.tris_convert_to_quads", {"type": 'J', "value": 'PRESS', "alt": True}, None),
                (
                    "mesh.rip_move",
                    {"type": 'V', "value": 'PRESS'},
                    {
                        "properties": [
                            (
                                "MESH_OT_rip",
                                [
                                    ("use_fill", False),
                                ],
                            ),
                        ],
                    },
                ),
                (
                    "mesh.rip_move",
                    {"type": 'V', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            (
                                "MESH_OT_rip",
                                [
                                    ("use_fill", True),
                                ],
                            ),
                        ],
                    },
                ),
                ("mesh.rip_edge_move", {"type": 'D', "value": 'PRESS', "alt": True}, None),
                (
                    "wm.call_menu",
                    {"type": 'M', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_mesh_merge'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'M', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_mesh_split'),
                        ],
                    },
                ),
                ("mesh.edge_face_add", {"type": 'F', "value": 'CLICK'}, None),
                ("mesh.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
                (
                    "wm.call_menu",
                    {"type": 'A', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_mesh_add'),
                        ],
                    },
                ),
                ("mesh.separate", {"type": 'P', "value": 'PRESS'}, None),
                ("mesh.split", {"type": 'Y', "value": 'PRESS'}, None),
                ("mesh.vert_connect_path", {"type": 'J', "value": 'PRESS'}, None),
                ("mesh.point_normals", {"type": 'L', "value": 'PRESS', "alt": True}, None),
                ("transform.vert_slide", {"type": 'V', "value": 'PRESS', "shift": True}, None),
                (
                    "mesh.dupli_extrude_cursor",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            ("rotate_source", True),
                        ],
                    },
                ),
                (
                    "mesh.dupli_extrude_cursor",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("rotate_source", False),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'X', "value": 'CLICK'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_mesh_delete'),
                        ],
                        "active": False,
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'DEL', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_mesh_delete'),
                        ],
                    },
                ),
                ("mesh.dissolve_mode", {"type": 'X', "value": 'PRESS', "ctrl": True}, None),
                ("mesh.dissolve_mode", {"type": 'DEL', "value": 'PRESS', "ctrl": True}, None),
                (
                    "mesh.knife_tool",
                    {"type": 'K', "value": 'PRESS'},
                    {
                        "properties": [
                            ("use_occlude_geometry", True),
                            ("only_selected", False),
                        ],
                    },
                ),
                (
                    "mesh.knife_tool",
                    {"type": 'K', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("use_occlude_geometry", False),
                            ("only_selected", True),
                        ],
                    },
                ),
                ("object.vertex_parent_set", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
                (
                    "wm.call_menu",
                    {"type": 'F', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_mesh_faces'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'E', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_mesh_edges'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'V', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_mesh_vertices'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'H', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_hook'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'U', "value": 'CLICK'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_uv_map'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'G', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_vertex_group'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'N', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_mesh_normals'),
                        ],
                    },
                ),
                (
                    "object.vertex_group_remove_from",
                    {"type": 'G', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'O', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_proportional_editing_falloff_pie'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'O', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.use_proportional_edit'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'O', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.use_proportional_connected'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_mesh_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'APP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_edit_mesh_context_menu'),
                        ],
                    },
                ),
            ],
        },
    ),
    (
        "Node Editor",
        {"space_type": 'NODE_EDITOR', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "wm.call_menu_pie",
                    {"type": 'TAB', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Ctrl_Tab'),
                        ],
                    },
                ),
                (
                    "wm.super_export",
                    {"type": 'E', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "wm.super_import",
                    {"type": 'V', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "noodler.dependency_select",
                    {
                        "type": 'LEFTMOUSE',
                        "value": 'PRESS',
                        "shift": True,
                        "ctrl": True,
                        "alt": True,
                    },
                    {
                        "properties": [
                            ("mode", 'upstream'),
                            ("repsel", False),
                        ],
                        "active": False,
                    },
                ),
                (
                    "noodler.dependency_select",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'upstream'),
                            ("repsel", True),
                        ],
                    },
                ),
                (
                    "noodler.dependency_select",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'downstream'),
                            ("repsel", False),
                        ],
                        "active": False,
                    },
                ),
                (
                    "noodler.dependency_select",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'downstream'),
                            ("repsel", True),
                        ],
                    },
                ),
                ("noodler.favorite_add", {"type": 'Y', "value": 'PRESS', "ctrl": True}, None),
                ("short.favorite_loop", {"type": 'Y', "value": 'PRESS'}, None),
                ("noodler.chamfer", {"type": 'B', "value": 'PRESS', "ctrl": True}, None),
                ("noodler.draw_frame", {"type": 'J', "value": 'PRESS'}, None),
                ("noodler.draw_route", {"type": 'V', "value": 'PRESS'}, None),
                (
                    "wm.call_menu",
                    {"type": 'S', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'NODE_MT_nw_switch_node_type_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'C', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'NODE_MT_nw_copy_node_properties_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'BACK_SLASH', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'NODE_MT_nw_link_active_to_selected_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'NUMPAD_SLASH', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'NODE_MT_nw_add_reroutes_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'SLASH', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'NODE_MT_nw_add_reroutes_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'W', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'NODE_MT_nw_node_wrangler_menu'),
                        ],
                    },
                ),
                ("node.nw_reset_nodes", {"type": 'BACK_SPACE', "value": 'PRESS'}, None),
                ("node.nw_align_nodes", {"type": 'EQUAL', "value": 'PRESS', "shift": True}, None),
                ("node.nw_viewer_focus", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK'}, None),
                (
                    "node.nw_lazy_connect",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("with_menu", True),
                        ],
                    },
                ),
                (
                    "node.nw_lazy_connect",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("with_menu", False),
                        ],
                    },
                ),
                (
                    "node.nw_lazy_mix",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                ("node.nw_reload_images", {"type": 'R', "value": 'PRESS', "alt": True}, None),
                (
                    "node.nw_preview_node",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("run_in_geometry_nodes", True),
                        ],
                    },
                ),
                (
                    "node.nw_preview_node",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("run_in_geometry_nodes", False),
                        ],
                    },
                ),
                ("node.nw_swap_links", {"type": 'S', "value": 'PRESS', "alt": True}, None),
                ("node.nw_frame_selected", {"type": 'P', "value": 'PRESS', "shift": True}, None),
                ("node.nw_del_unused", {"type": 'X', "value": 'PRESS', "alt": True}, None),
                ("node.nw_bg_reset", {"type": 'Z', "value": 'PRESS'}, None),
                (
                    "node.nw_add_textures_for_principled",
                    {"type": 'T', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                ("node.nw_add_texture", {"type": 'T', "value": 'PRESS', "ctrl": True}, None),
                (
                    "node.nw_select_parent_child",
                    {"type": 'LEFT_BRACKET', "value": 'PRESS'},
                    {
                        "properties": [
                            ("option", 'PARENT'),
                        ],
                    },
                ),
                (
                    "node.nw_select_parent_child",
                    {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
                    {
                        "properties": [
                            ("option", 'CHILD'),
                        ],
                    },
                ),
                ("node.nw_link_out", {"type": 'O', "value": 'PRESS'}, None),
                (
                    "node.nw_detach_outputs",
                    {"type": 'D', "value": 'PRESS', "shift": True, "alt": True},
                    None,
                ),
                (
                    "node.nw_copy_label",
                    {"type": 'V', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("option", 'FROM_ACTIVE'),
                        ],
                    },
                ),
                (
                    "node.nw_modify_labels",
                    {"type": 'L', "value": 'PRESS', "shift": True, "alt": True},
                    None,
                ),
                (
                    "node.nw_clear_label",
                    {"type": 'L', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("option", False),
                        ],
                    },
                ),
                (
                    "node.nw_factor",
                    {"type": 'ONE', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("option", 1.0),
                        ],
                    },
                ),
                (
                    "node.nw_factor",
                    {
                        "type": 'NUMPAD_1',
                        "value": 'PRESS',
                        "shift": True,
                        "ctrl": True,
                        "alt": True,
                    },
                    {
                        "properties": [
                            ("option", 1.0),
                        ],
                    },
                ),
                (
                    "node.nw_factor",
                    {"type": 'ZERO', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("option", 0.0),
                        ],
                    },
                ),
                (
                    "node.nw_factor",
                    {
                        "type": 'NUMPAD_0',
                        "value": 'PRESS',
                        "shift": True,
                        "ctrl": True,
                        "alt": True,
                    },
                    {
                        "properties": [
                            ("option", 0.0),
                        ],
                    },
                ),
                (
                    "node.nw_factor",
                    {
                        "type": 'RIGHT_ARROW',
                        "value": 'PRESS',
                        "shift": True,
                        "ctrl": True,
                        "alt": True,
                    },
                    {
                        "properties": [
                            ("option", 1.0),
                        ],
                    },
                ),
                (
                    "node.nw_factor",
                    {
                        "type": 'LEFT_ARROW',
                        "value": 'PRESS',
                        "shift": True,
                        "ctrl": True,
                        "alt": True,
                    },
                    {
                        "properties": [
                            ("option", 0.0),
                        ],
                    },
                ),
                (
                    "node.nw_factor",
                    {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("option", 0.01),
                        ],
                    },
                ),
                (
                    "node.nw_factor",
                    {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("option", -0.01),
                        ],
                    },
                ),
                (
                    "node.nw_factor",
                    {"type": 'RIGHT_ARROW', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("option", 0.1),
                        ],
                    },
                ),
                (
                    "node.nw_factor",
                    {"type": 'LEFT_ARROW', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("option", -0.1),
                        ],
                    },
                ),
                (
                    "node.nw_link_active_to_selected",
                    {"type": 'SEMI_COLON', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("replace", True),
                            ("use_node_name", False),
                            ("use_outputs_names", True),
                        ],
                    },
                ),
                (
                    "node.nw_link_active_to_selected",
                    {"type": 'SEMI_COLON', "value": 'PRESS'},
                    {
                        "properties": [
                            ("replace", False),
                            ("use_node_name", False),
                            ("use_outputs_names", True),
                        ],
                    },
                ),
                (
                    "node.nw_link_active_to_selected",
                    {"type": 'QUOTE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("replace", True),
                            ("use_node_name", True),
                            ("use_outputs_names", False),
                        ],
                    },
                ),
                (
                    "node.nw_link_active_to_selected",
                    {"type": 'QUOTE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("replace", False),
                            ("use_node_name", True),
                            ("use_outputs_names", False),
                        ],
                    },
                ),
                (
                    "node.nw_link_active_to_selected",
                    {"type": 'K', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("replace", True),
                            ("use_node_name", False),
                            ("use_outputs_names", False),
                        ],
                    },
                ),
                (
                    "node.nw_link_active_to_selected",
                    {"type": 'K', "value": 'PRESS'},
                    {
                        "properties": [
                            ("replace", False),
                            ("use_node_name", False),
                            ("use_outputs_names", False),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'UP_ARROW', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'PREV'),
                            ("operation", 'PREV'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'DOWN_ARROW', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'NEXT'),
                            ("operation", 'NEXT'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'PERIOD', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'CURRENT'),
                            ("operation", 'GREATER_THAN'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'COMMA', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'CURRENT'),
                            ("operation", 'LESS_THAN'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'SLASH', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'DIVIDE'),
                            ("operation", 'DIVIDE'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'NUMPAD_SLASH', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'DIVIDE'),
                            ("operation", 'DIVIDE'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'MINUS', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'SUBTRACT'),
                            ("operation", 'SUBTRACT'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'SUBTRACT'),
                            ("operation", 'SUBTRACT'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'EIGHT', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'MULTIPLY'),
                            ("operation", 'MULTIPLY'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'NUMPAD_ASTERIX', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'MULTIPLY'),
                            ("operation", 'MULTIPLY'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'EQUAL', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'ADD'),
                            ("operation", 'ADD'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'ADD'),
                            ("operation", 'ADD'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'ZERO', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'MIX'),
                            ("operation", 'CURRENT'),
                        ],
                    },
                ),
                (
                    "node.nw_batch_change",
                    {"type": 'NUMPAD_0', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("blend_type", 'MIX'),
                            ("operation", 'CURRENT'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'PERIOD', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'GREATER_THAN'),
                            ("merge_type", 'MATH'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'COMMA', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'LESS_THAN'),
                            ("merge_type", 'MATH'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'SLASH', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'DIVIDE'),
                            ("merge_type", 'MATH'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_SLASH', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'DIVIDE'),
                            ("merge_type", 'MATH'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'MINUS', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'SUBTRACT'),
                            ("merge_type", 'MATH'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'SUBTRACT'),
                            ("merge_type", 'MATH'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'EIGHT', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'MULTIPLY'),
                            ("merge_type", 'MATH'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_ASTERIX', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'MULTIPLY'),
                            ("merge_type", 'MATH'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'EQUAL', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'ADD'),
                            ("merge_type", 'MATH'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'ADD'),
                            ("merge_type", 'MATH'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'SLASH', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'DIVIDE'),
                            ("merge_type", 'MIX'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_SLASH', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'DIVIDE'),
                            ("merge_type", 'MIX'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'MINUS', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'SUBTRACT'),
                            ("merge_type", 'MIX'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'SUBTRACT'),
                            ("merge_type", 'MIX'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'EIGHT', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'MULTIPLY'),
                            ("merge_type", 'MIX'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_ASTERIX', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'MULTIPLY'),
                            ("merge_type", 'MIX'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'EQUAL', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'ADD'),
                            ("merge_type", 'MIX'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'ADD'),
                            ("merge_type", 'MIX'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'ZERO', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'MIX'),
                            ("merge_type", 'ALPHAOVER'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_0', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'MIX'),
                            ("merge_type", 'ALPHAOVER'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_PERIOD', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'MIX'),
                            ("merge_type", 'ZCOMBINE'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'PERIOD', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'GREATER_THAN'),
                            ("merge_type", 'MATH'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'COMMA', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'LESS_THAN'),
                            ("merge_type", 'MATH'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'SLASH', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'DIVIDE'),
                            ("merge_type", 'AUTO'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_SLASH', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'DIVIDE'),
                            ("merge_type", 'AUTO'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'MINUS', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'SUBTRACT'),
                            ("merge_type", 'AUTO'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'SUBTRACT'),
                            ("merge_type", 'AUTO'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'EIGHT', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'MULTIPLY'),
                            ("merge_type", 'AUTO'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_ASTERIX', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'MULTIPLY'),
                            ("merge_type", 'AUTO'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'EQUAL', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'ADD'),
                            ("merge_type", 'AUTO'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'ADD'),
                            ("merge_type", 'AUTO'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'ZERO', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'MIX'),
                            ("merge_type", 'AUTO'),
                        ],
                    },
                ),
                (
                    "node.nw_merge_nodes",
                    {"type": 'NUMPAD_0', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'MIX'),
                            ("merge_type", 'AUTO'),
                        ],
                    },
                ),
                (
                    "node.show_active_node_image",
                    {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK'},
                    None,
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'TAB', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Ctrl_Tab'),
                        ],
                    },
                ),
                (
                    "node.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK'},
                    {
                        "properties": [
                            ("deselect_all", True),
                            ("select_passthrough", True),
                        ],
                    },
                ),
                ("node.select", {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True}, None),
                ("node.select", {"type": 'LEFTMOUSE', "value": 'CLICK', "alt": True}, None),
                (
                    "node.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "node.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("toggle", True),
                        ],
                    },
                ),
                (
                    "node.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("toggle", True),
                        ],
                    },
                ),
                (
                    "node.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("toggle", True),
                        ],
                    },
                ),
                (
                    "node.select",
                    {
                        "type": 'LEFTMOUSE',
                        "value": 'CLICK',
                        "shift": True,
                        "ctrl": True,
                        "alt": True,
                    },
                    {
                        "properties": [
                            ("toggle", True),
                        ],
                    },
                ),
                (
                    "node.select_box",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("tweak", True),
                        ],
                    },
                ),
                (
                    "node.select_lasso",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'ADD'),
                        ],
                    },
                ),
                (
                    "node.select_lasso",
                    {
                        "type": 'LEFTMOUSE',
                        "value": 'CLICK_DRAG',
                        "shift": True,
                        "ctrl": True,
                        "alt": True,
                    },
                    {
                        "properties": [
                            ("mode", 'SUB'),
                        ],
                    },
                ),
                (
                    "node.select_box",
                    {"type": 'B', "value": 'PRESS'},
                    {
                        "properties": [
                            ("tweak", False),
                        ],
                    },
                ),
                ("node.select_circle", {"type": 'C', "value": 'PRESS'}, None),
                (
                    "node.link",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("detach", False),
                        ],
                    },
                ),
                (
                    "node.link",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("detach", True),
                        ],
                    },
                ),
                ("node.resize", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'}, None),
                (
                    "node.add_reroute",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "shift": True},
                    None,
                ),
                (
                    "node.links_cut",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
                    None,
                ),
                (
                    "node.links_mute",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "node.select_link_viewer",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "node.backimage_move",
                    {"type": 'MIDDLEMOUSE', "value": 'PRESS', "alt": True},
                    None,
                ),
                (
                    "node.backimage_zoom",
                    {"type": 'V', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("factor", 0.8333333),
                        ],
                    },
                ),
                (
                    "node.backimage_zoom",
                    {"type": 'V', "value": 'PRESS', "alt": True, "repeat": True},
                    {
                        "properties": [
                            ("factor", 1.2),
                        ],
                    },
                ),
                ("node.backimage_fit", {"type": 'HOME', "value": 'PRESS', "alt": True}, None),
                (
                    "node.backimage_sample",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "alt": True},
                    None,
                ),
                (
                    "node.link_make",
                    {"type": 'F', "value": 'PRESS'},
                    {
                        "properties": [
                            ("replace", False),
                        ],
                    },
                ),
                (
                    "node.link_make",
                    {"type": 'F', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("replace", True),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'A', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'NODE_MT_add'),
                        ],
                    },
                ),
                (
                    "node.duplicate_move",
                    {"type": 'D', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            (
                                "NODE_OT_translate_attach",
                                [
                                    (
                                        "TRANSFORM_OT_translate",
                                        [
                                            ("view2d_edge_pan", True),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    },
                ),
                (
                    "node.duplicate_move_keep_inputs",
                    {"type": 'D', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            (
                                "NODE_OT_translate_attach",
                                [
                                    (
                                        "TRANSFORM_OT_translate",
                                        [
                                            ("view2d_edge_pan", True),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    },
                ),
                ("node.parent_set", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
                ("node.detach", {"type": 'P', "value": 'PRESS', "alt": True}, None),
                ("node.join", {"type": 'J', "value": 'PRESS', "ctrl": True}, None),
                ("node.hide_toggle", {"type": 'H', "value": 'PRESS'}, None),
                ("node.mute_toggle", {"type": 'M', "value": 'PRESS'}, None),
                ("node.preview_toggle", {"type": 'H', "value": 'PRESS', "shift": True}, None),
                ("node.hide_socket_toggle", {"type": 'H', "value": 'PRESS', "ctrl": True}, None),
                ("node.view_all", {"type": 'HOME', "value": 'PRESS'}, None),
                ("node.view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
                ("node.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'ACCENT_GRAVE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'NODE_MT_view_pie'),
                        ],
                    },
                ),
                ("node.delete", {"type": 'X', "value": 'PRESS'}, None),
                ("node.delete", {"type": 'DEL', "value": 'PRESS'}, None),
                ("node.delete_reconnect", {"type": 'X', "value": 'PRESS', "ctrl": True}, None),
                ("node.delete_reconnect", {"type": 'DEL', "value": 'PRESS', "ctrl": True}, None),
                (
                    "node.select_all",
                    {"type": 'A', "value": 'PRESS'},
                    {
                        "properties": [
                            ("action", 'SELECT'),
                        ],
                    },
                ),
                (
                    "node.select_all",
                    {"type": 'A', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                (
                    "node.select_all",
                    {"type": 'I', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("action", 'INVERT'),
                        ],
                    },
                ),
                (
                    "node.select_all",
                    {"type": 'A', "value": 'DOUBLE_CLICK'},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                ("node.select_linked_to", {"type": 'L', "value": 'PRESS', "shift": True}, None),
                ("node.select_linked_from", {"type": 'L', "value": 'PRESS'}, None),
                ("node.select_grouped", {"type": 'G', "value": 'PRESS', "shift": True}, None),
                (
                    "node.select_grouped",
                    {"type": 'G', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "node.select_same_type_step",
                    {"type": 'RIGHT_BRACKET', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("prev", False),
                        ],
                    },
                ),
                (
                    "node.select_same_type_step",
                    {"type": 'LEFT_BRACKET', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("prev", True),
                        ],
                    },
                ),
                ("node.find_node", {"type": 'F', "value": 'PRESS', "ctrl": True}, None),
                ("node.group_make", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
                (
                    "node.group_ungroup",
                    {"type": 'G', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                ("node.group_separate", {"type": 'P', "value": 'PRESS'}, None),
                (
                    "node.group_edit",
                    {"type": 'TAB', "value": 'CLICK'},
                    {
                        "properties": [
                            ("exit", False),
                        ],
                    },
                ),
                (
                    "node.group_edit",
                    {"type": 'TAB', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            ("exit", True),
                        ],
                    },
                ),
                ("node.read_viewlayers", {"type": 'R', "value": 'PRESS', "ctrl": True}, None),
                ("node.render_changed", {"type": 'Z', "value": 'PRESS'}, None),
                ("node.clipboard_copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
                ("node.clipboard_paste", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
                ("node.viewer_border", {"type": 'B', "value": 'PRESS', "ctrl": True}, None),
                (
                    "node.clear_viewer_border",
                    {"type": 'B', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "node.translate_attach",
                    {"type": 'G', "value": 'PRESS'},
                    {
                        "properties": [
                            (
                                "TRANSFORM_OT_translate",
                                [
                                    ("view2d_edge_pan", True),
                                ],
                            ),
                        ],
                    },
                ),
                (
                    "node.translate_attach",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            (
                                "TRANSFORM_OT_translate",
                                [
                                    ("view2d_edge_pan", True),
                                ],
                            ),
                        ],
                    },
                ),
                (
                    "transform.translate",
                    {"type": 'G', "value": 'PRESS'},
                    {
                        "properties": [
                            ("view2d_edge_pan", True),
                        ],
                    },
                ),
                (
                    "transform.translate",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("view2d_edge_pan", True),
                            ("release_confirm", True),
                        ],
                    },
                ),
                ("transform.rotate", {"type": 'R', "value": 'CLICK'}, None),
                ("transform.resize", {"type": 'S', "value": 'PRESS'}, None),
                (
                    "node.move_detach_links",
                    {"type": 'D', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            (
                                "TRANSFORM_OT_translate",
                                [
                                    ("view2d_edge_pan", True),
                                ],
                            ),
                        ],
                    },
                ),
                (
                    "node.move_detach_links_release",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "alt": True},
                    {
                        "properties": [
                            (
                                "NODE_OT_translate_attach",
                                [
                                    (
                                        "TRANSFORM_OT_translate",
                                        [
                                            ("view2d_edge_pan", True),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    },
                ),
                (
                    "node.move_detach_links",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "alt": True},
                    {
                        "properties": [
                            (
                                "TRANSFORM_OT_translate",
                                [
                                    ("view2d_edge_pan", True),
                                ],
                            ),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'TAB', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.use_snap_node'),
                        ],
                    },
                ),
                (
                    "wm.context_menu_enum",
                    {"type": 'TAB', "value": 'CLICK', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.snap_node_element'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'Z', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("data_path", 'space_data.overlay.show_overlays'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'NODE_MT_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'APP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'NODE_MT_context_menu'),
                        ],
                    },
                ),
            ],
        },
    ),
    (
        "Object Mode",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "wm.call_menu_pie",
                    {"type": 'X', "value": 'CLICK_DRAG', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_X_ctrl_shift'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'Q', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_make_links'),
                        ],
                    },
                ),
                (
                    "machin3.call_mesh_machine_menu",
                    {"type": 'Y', "value": 'PRESS'},
                    {
                        "properties": [
                            ("idname", 'mesh_machine'),
                        ],
                    },
                ),
                (
                    "object.booltool_auto_slice",
                    {"type": 'NUMPAD_SLASH', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "object.booltool_auto_intersect",
                    {"type": 'NUMPAD_ASTERIX', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "object.booltool_auto_difference",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "object.booltool_auto_union",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "btool.to_mesh",
                    {"type": 'NUMPAD_ENTER', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "btool.brush_to_mesh",
                    {"type": 'NUMPAD_ENTER', "value": 'PRESS', "ctrl": True},
                    None,
                ),
                (
                    "btool.boolean_slice",
                    {"type": 'NUMPAD_SLASH', "value": 'PRESS', "ctrl": True},
                    None,
                ),
                (
                    "btool.boolean_inters",
                    {"type": 'NUMPAD_ASTERIX', "value": 'PRESS', "ctrl": True},
                    None,
                ),
                (
                    "btool.boolean_diff",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True},
                    None,
                ),
                (
                    "btool.boolean_union",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True},
                    None,
                ),
                (
                    "wm.call_menu",
                    {"type": 'C', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_copypopup'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'O', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_proportional_editing_falloff_pie'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'O', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.use_proportional_edit_objects'),
                        ],
                    },
                ),
                (
                    "object.select_all",
                    {"type": 'A', "value": 'CLICK'},
                    {
                        "properties": [
                            ("action", 'TOGGLE'),
                        ],
                    },
                ),
                (
                    "object.select_all",
                    {"type": 'A', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                        "active": False,
                    },
                ),
                (
                    "object.select_all",
                    {"type": 'I', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("action", 'INVERT'),
                        ],
                    },
                ),
                (
                    "object.select_all",
                    {"type": 'A', "value": 'DOUBLE_CLICK'},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                (
                    "object.select_more",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    None,
                ),
                (
                    "object.select_less",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    None,
                ),
                ("object.select_linked", {"type": 'L', "value": 'PRESS', "shift": True}, None),
                ("object.select_grouped", {"type": 'G', "value": 'PRESS', "shift": True}, None),
                (
                    "object.select_hierarchy",
                    {"type": 'LEFT_BRACKET', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("direction", 'PARENT'),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.select_hierarchy",
                    {"type": 'LEFT_BRACKET', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("direction", 'PARENT'),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.select_hierarchy",
                    {"type": 'RIGHT_BRACKET', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("direction", 'CHILD'),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.select_hierarchy",
                    {"type": 'RIGHT_BRACKET', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("direction", 'CHILD'),
                            ("extend", True),
                        ],
                    },
                ),
                ("object.parent_set", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
                ("object.parent_clear", {"type": 'P', "value": 'PRESS', "alt": True}, None),
                (
                    "object.location_clear",
                    {"type": 'G', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("clear_delta", False),
                        ],
                    },
                ),
                (
                    "object.rotation_clear",
                    {"type": 'R', "value": 'CLICK', "alt": True},
                    {
                        "properties": [
                            ("clear_delta", False),
                        ],
                    },
                ),
                (
                    "object.scale_clear",
                    {"type": 'S', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("clear_delta", False),
                        ],
                    },
                ),
                (
                    "object.delete",
                    {"type": 'X', "value": 'CLICK'},
                    {
                        "properties": [
                            ("use_global", False),
                            ("confirm", False),
                        ],
                    },
                ),
                (
                    "object.delete",
                    {"type": 'X', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("use_global", True),
                        ],
                        "active": False,
                    },
                ),
                (
                    "object.delete",
                    {"type": 'DEL', "value": 'PRESS'},
                    {
                        "properties": [
                            ("use_global", False),
                            ("confirm", False),
                        ],
                    },
                ),
                (
                    "object.delete",
                    {"type": 'DEL', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("use_global", True),
                            ("confirm", False),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'A', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_add'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'A', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_object_apply'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'L', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_make_links'),
                        ],
                    },
                ),
                ("object.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
                (
                    "object.duplicate_move_linked",
                    {"type": 'D', "value": 'PRESS', "alt": True},
                    None,
                ),
                ("object.join", {"type": 'J', "value": 'PRESS', "ctrl": True}, None),
                (
                    "wm.context_toggle",
                    {"type": 'PERIOD', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.use_transform_data_origin'),
                        ],
                    },
                ),
                ("anim.keyframe_insert_menu", {"type": 'I', "value": 'PRESS'}, None),
                ("anim.keyframe_delete_v3d", {"type": 'I', "value": 'PRESS', "alt": True}, None),
                (
                    "anim.keying_set_active_set",
                    {"type": 'I', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
                    None,
                ),
                ("collection.create", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
                (
                    "collection.objects_remove",
                    {"type": 'G', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "collection.objects_remove_all",
                    {"type": 'G', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "collection.objects_add_active",
                    {"type": 'G', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "collection.objects_remove_active",
                    {"type": 'G', "value": 'PRESS', "shift": True, "alt": True},
                    None,
                ),
                (
                    "object.subdivision_set",
                    {"type": 'ZERO', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("level", 0),
                            ("relative", False),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'ONE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("level", 1),
                            ("relative", False),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'TWO', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("level", 2),
                            ("relative", False),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'THREE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("level", 3),
                            ("relative", False),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'FOUR', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("level", 4),
                            ("relative", False),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'FIVE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("level", 5),
                            ("relative", False),
                        ],
                    },
                ),
                ("object.move_to_collection", {"type": 'M', "value": 'PRESS'}, None),
                ("object.link_to_collection", {"type": 'M', "value": 'PRESS', "shift": True}, None),
                ("object.hide_view_clear", {"type": 'H', "value": 'PRESS', "alt": True}, None),
                (
                    "object.hide_view_set",
                    {"type": 'H', "value": 'PRESS'},
                    {
                        "properties": [
                            ("unselected", False),
                        ],
                    },
                ),
                (
                    "object.hide_view_set",
                    {"type": 'H', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("unselected", True),
                        ],
                    },
                ),
                ("object.hide_collection", {"type": 'H', "value": 'PRESS', "ctrl": True}, None),
                (
                    "object.hide_collection",
                    {"type": 'ONE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("collection_index", 1),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'TWO', "value": 'PRESS'},
                    {
                        "properties": [
                            ("collection_index", 2),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'THREE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("collection_index", 3),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'FOUR', "value": 'PRESS'},
                    {
                        "properties": [
                            ("collection_index", 4),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'FIVE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("collection_index", 5),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'SIX', "value": 'PRESS'},
                    {
                        "properties": [
                            ("collection_index", 6),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'SEVEN', "value": 'PRESS'},
                    {
                        "properties": [
                            ("collection_index", 7),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'EIGHT', "value": 'PRESS'},
                    {
                        "properties": [
                            ("collection_index", 8),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'NINE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("collection_index", 9),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'ZERO', "value": 'PRESS'},
                    {
                        "properties": [
                            ("collection_index", 10),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'ONE', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("collection_index", 11),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'TWO', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("collection_index", 12),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'THREE', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("collection_index", 13),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'FOUR', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("collection_index", 14),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'FIVE', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("collection_index", 15),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'SIX', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("collection_index", 16),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'SEVEN', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("collection_index", 17),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'EIGHT', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("collection_index", 18),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'NINE', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("collection_index", 19),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'ZERO', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("collection_index", 20),
                            ("extend", False),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'ONE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("collection_index", 1),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'TWO', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("collection_index", 2),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'THREE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("collection_index", 3),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'FOUR', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("collection_index", 4),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'FIVE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("collection_index", 5),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'SIX', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("collection_index", 6),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'SEVEN', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("collection_index", 7),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'EIGHT', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("collection_index", 8),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'NINE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("collection_index", 9),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'ZERO', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("collection_index", 10),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'ONE', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("collection_index", 11),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'TWO', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("collection_index", 12),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'THREE', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("collection_index", 13),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'FOUR', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("collection_index", 14),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'FIVE', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("collection_index", 15),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'SIX', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("collection_index", 16),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'SEVEN', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("collection_index", 17),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'EIGHT', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("collection_index", 18),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'NINE', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("collection_index", 19),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "object.hide_collection",
                    {"type": 'ZERO', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("collection_index", 20),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_object_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'APP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_object_context_menu'),
                        ],
                    },
                ),
            ],
        },
    ),
    (
        "Object Non-modal",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "object.transfer_mode",
                    {"type": 'Q', "value": 'PRESS', "alt": True},
                    {
                        "active": False,
                    },
                ),
                (
                    "object.mode_set",
                    {"type": 'TAB', "value": 'CLICK'},
                    {
                        "properties": [
                            ("mode", 'EDIT'),
                            ("toggle", True),
                        ],
                    },
                ),
                ("view3d.object_mode_pie_or_toggle", {"type": 'TAB', "value": 'CLICK_DRAG'}, None),
            ],
        },
    ),
    (
        "Outliner",
        {"space_type": 'OUTLINER', "region_type": 'WINDOW'},
        {
            "items": [
                ("outliner.show_active", {"type": 'F', "value": 'CLICK'}, None),
                (
                    "wm.call_menu_pie",
                    {"type": 'A', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("name", 'OUTLINER_PIE_MT_Bottom_A'),
                        ],
                    },
                ),
                (
                    "outliner.highlight_update",
                    {"type": 'MOUSEMOVE', "value": 'ANY', "any": True},
                    None,
                ),
                ("outliner.item_rename", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK'}, None),
                (
                    "outliner.item_rename",
                    {"type": 'F2', "value": 'PRESS'},
                    {
                        "properties": [
                            ("use_active", True),
                        ],
                    },
                ),
                (
                    "outliner.item_activate",
                    {"type": 'LEFTMOUSE', "value": 'CLICK'},
                    {
                        "properties": [
                            ("deselect_all", True),
                        ],
                    },
                ),
                (
                    "outliner.item_activate",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            ("extend", True),
                            ("deselect_all", True),
                        ],
                    },
                ),
                (
                    "outliner.item_activate",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("extend_range", True),
                            ("deselect_all", True),
                        ],
                    },
                ),
                (
                    "outliner.item_activate",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("extend", True),
                            ("extend_range", True),
                            ("deselect_all", True),
                        ],
                    },
                ),
                ("outliner.select_box", {"type": 'B', "value": 'PRESS'}, None),
                (
                    "outliner.select_box",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("tweak", True),
                        ],
                    },
                ),
                (
                    "outliner.select_box",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("tweak", True),
                            ("mode", 'ADD'),
                        ],
                    },
                ),
                (
                    "outliner.select_box",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("tweak", True),
                            ("mode", 'SUB'),
                        ],
                    },
                ),
                (
                    "outliner.select_walk",
                    {"type": 'UP_ARROW', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("direction", 'UP'),
                        ],
                    },
                ),
                (
                    "outliner.select_walk",
                    {"type": 'UP_ARROW', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("direction", 'UP'),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "outliner.select_walk",
                    {"type": 'DOWN_ARROW', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("direction", 'DOWN'),
                        ],
                    },
                ),
                (
                    "outliner.select_walk",
                    {"type": 'DOWN_ARROW', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("direction", 'DOWN'),
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "outliner.select_walk",
                    {"type": 'LEFT_ARROW', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("direction", 'LEFT'),
                        ],
                    },
                ),
                (
                    "outliner.select_walk",
                    {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("direction", 'LEFT'),
                            ("toggle_all", True),
                        ],
                    },
                ),
                (
                    "outliner.select_walk",
                    {"type": 'RIGHT_ARROW', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("direction", 'RIGHT'),
                        ],
                    },
                ),
                (
                    "outliner.select_walk",
                    {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True, "repeat": True},
                    {
                        "properties": [
                            ("direction", 'RIGHT'),
                            ("toggle_all", True),
                        ],
                    },
                ),
                (
                    "outliner.item_openclose",
                    {"type": 'LEFTMOUSE', "value": 'CLICK'},
                    {
                        "properties": [
                            ("all", False),
                        ],
                    },
                ),
                (
                    "outliner.item_openclose",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("all", True),
                        ],
                    },
                ),
                (
                    "outliner.item_openclose",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
                    {
                        "properties": [
                            ("all", False),
                        ],
                    },
                ),
                ("outliner.operation", {"type": 'RIGHTMOUSE', "value": 'PRESS'}, None),
                (
                    "wm.call_menu",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'OUTLINER_MT_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'ACCENT_GRAVE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'OUTLINER_MT_view_pie'),
                        ],
                    },
                ),
                ("outliner.item_drag_drop", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'}, None),
                (
                    "outliner.item_drag_drop",
                    {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True},
                    None,
                ),
                ("outliner.show_hierarchy", {"type": 'HOME', "value": 'PRESS'}, None),
                ("outliner.show_active", {"type": 'PERIOD', "value": 'PRESS'}, None),
                ("outliner.show_active", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
                (
                    "outliner.scroll_page",
                    {"type": 'PAGE_DOWN', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("up", False),
                        ],
                    },
                ),
                (
                    "outliner.scroll_page",
                    {"type": 'PAGE_UP', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("up", True),
                        ],
                    },
                ),
                ("outliner.show_one_level", {"type": 'NUMPAD_PLUS', "value": 'PRESS'}, None),
                (
                    "outliner.show_one_level",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS'},
                    {
                        "properties": [
                            ("open", False),
                        ],
                    },
                ),
                (
                    "outliner.select_all",
                    {"type": 'A', "value": 'PRESS'},
                    {
                        "properties": [
                            ("action", 'SELECT'),
                        ],
                    },
                ),
                (
                    "outliner.select_all",
                    {"type": 'A', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                (
                    "outliner.select_all",
                    {"type": 'I', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("action", 'INVERT'),
                        ],
                    },
                ),
                (
                    "outliner.select_all",
                    {"type": 'A', "value": 'DOUBLE_CLICK'},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                ("outliner.expanded_toggle", {"type": 'A', "value": 'PRESS', "shift": True}, None),
                ("outliner.keyingset_add_selected", {"type": 'K', "value": 'PRESS'}, None),
                (
                    "outliner.keyingset_remove_selected",
                    {"type": 'K', "value": 'PRESS', "alt": True},
                    None,
                ),
                ("anim.keyframe_insert", {"type": 'I', "value": 'PRESS'}, None),
                ("anim.keyframe_delete", {"type": 'I', "value": 'PRESS', "alt": True}, None),
                (
                    "outliner.drivers_add_selected",
                    {"type": 'D', "value": 'PRESS', "ctrl": True},
                    None,
                ),
                (
                    "outliner.drivers_delete_selected",
                    {"type": 'D', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                ("outliner.collection_new", {"type": 'C', "value": 'PRESS'}, None),
                ("outliner.delete", {"type": 'X', "value": 'CLICK'}, None),
                ("outliner.delete", {"type": 'DEL', "value": 'PRESS'}, None),
                ("object.move_to_collection", {"type": 'M', "value": 'PRESS'}, None),
                ("object.link_to_collection", {"type": 'M', "value": 'PRESS', "shift": True}, None),
                ("outliner.collection_exclude_set", {"type": 'E', "value": 'PRESS'}, None),
                (
                    "outliner.collection_exclude_clear",
                    {"type": 'E', "value": 'PRESS', "alt": True},
                    None,
                ),
                ("outliner.hide", {"type": 'H', "value": 'PRESS'}, None),
                ("outliner.unhide_all", {"type": 'H', "value": 'PRESS', "alt": True}, None),
                ("outliner.id_copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
                ("outliner.id_paste", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
            ],
        },
    ),
    (
        "Sculpt",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "sculpt.brush_stroke",
                    {"type": 'LEFTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'NORMAL'),
                        ],
                    },
                ),
                (
                    "sculpt.brush_stroke",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'INVERT'),
                        ],
                    },
                ),
                (
                    "sculpt.brush_stroke",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("mode", 'SMOOTH'),
                        ],
                    },
                ),
                (
                    "sculpt.expand",
                    {"type": 'A', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("target", 'MASK'),
                            ("falloff_type", 'GEODESIC'),
                            ("invert", True),
                        ],
                    },
                ),
                (
                    "sculpt.expand",
                    {"type": 'A', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("target", 'MASK'),
                            ("falloff_type", 'NORMALS'),
                            ("invert", False),
                        ],
                    },
                ),
                (
                    "sculpt.expand",
                    {"type": 'W', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("target", 'FACE_SETS'),
                            ("falloff_type", 'GEODESIC'),
                            ("invert", False),
                            ("use_modify_active", False),
                        ],
                    },
                ),
                (
                    "sculpt.expand",
                    {"type": 'W', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("target", 'FACE_SETS'),
                            ("falloff_type", 'BOUNDARY_FACE_SET'),
                            ("invert", False),
                            ("use_modify_active", True),
                        ],
                    },
                ),
                (
                    "sculpt.face_set_change_visibility",
                    {"type": 'H', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'TOGGLE'),
                        ],
                    },
                ),
                (
                    "sculpt.face_set_change_visibility",
                    {"type": 'H', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("mode", 'HIDE_ACTIVE'),
                        ],
                    },
                ),
                (
                    "sculpt.face_set_change_visibility",
                    {"type": 'H', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("mode", 'SHOW_ALL'),
                        ],
                    },
                ),
                (
                    "sculpt.face_set_edit",
                    {"type": 'W', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'GROW'),
                        ],
                    },
                ),
                (
                    "sculpt.face_set_edit",
                    {"type": 'W', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'SHRINK'),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'ZERO', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("level", 0),
                            ("relative", False),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'ONE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("level", 1),
                            ("relative", False),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'TWO', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("level", 2),
                            ("relative", False),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'THREE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("level", 3),
                            ("relative", False),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'FOUR', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("level", 4),
                            ("relative", False),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'FIVE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("level", 5),
                            ("relative", False),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'PAGE_UP', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("level", 1),
                            ("relative", True),
                        ],
                    },
                ),
                (
                    "object.subdivision_set",
                    {"type": 'PAGE_DOWN', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("level", -1),
                            ("relative", True),
                        ],
                    },
                ),
                (
                    "paint.mask_flood_fill",
                    {"type": 'M', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("mode", 'VALUE'),
                            ("value", 0.0),
                        ],
                    },
                ),
                (
                    "paint.mask_flood_fill",
                    {"type": 'I', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'INVERT'),
                        ],
                    },
                ),
                (
                    "paint.mask_box_gesture",
                    {"type": 'B', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'VALUE'),
                            ("value", 0.0),
                        ],
                    },
                ),
                (
                    "paint.mask_lasso_gesture",
                    {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "wm.context_toggle",
                    {"type": 'M', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("data_path", 'scene.tool_settings.sculpt.show_mask'),
                        ],
                    },
                ),
                (
                    "sculpt.dynamic_topology_toggle",
                    {"type": 'D', "value": 'PRESS', "ctrl": True},
                    None,
                ),
                (
                    "sculpt.dyntopo_detail_size_edit",
                    {"type": 'D', "value": 'PRESS', "shift": True},
                    None,
                ),
                (
                    "sculpt.set_detail_size",
                    {"type": 'D', "value": 'PRESS', "shift": True, "alt": True},
                    None,
                ),
                ("object.voxel_remesh", {"type": 'R', "value": 'PRESS', "ctrl": True}, None),
                ("object.voxel_size_edit", {"type": 'R', "value": 'PRESS', "shift": True}, None),
                (
                    "object.quadriflow_remesh",
                    {"type": 'R', "value": 'PRESS', "ctrl": True, "alt": True},
                    None,
                ),
                ("sculpt.sample_color", {"type": 'S', "value": 'PRESS'}, None),
                (
                    "brush.scale_size",
                    {"type": 'LEFT_BRACKET', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("scalar", 0.9),
                        ],
                    },
                ),
                (
                    "brush.scale_size",
                    {"type": 'RIGHT_BRACKET', "value": 'PRESS', "repeat": True},
                    {
                        "properties": [
                            ("scalar", 1.1111112),
                        ],
                    },
                ),
                (
                    "wm.radial_control",
                    {"type": 'F', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path_primary", 'tool_settings.sculpt.brush.size'),
                            ("data_path_secondary", 'tool_settings.unified_paint_settings.size'),
                            (
                                "use_secondary",
                                'tool_settings.unified_paint_settings.use_unified_size',
                            ),
                            ("rotation_path", 'tool_settings.sculpt.brush.texture_slot.angle'),
                            ("color_path", 'tool_settings.sculpt.brush.cursor_color_add'),
                            ("fill_color_path", ''),
                            ("fill_color_override_path", ''),
                            ("fill_color_override_test_path", ''),
                            ("zoom_path", ''),
                            ("image_id", 'tool_settings.sculpt.brush'),
                            ("secondary_tex", False),
                        ],
                    },
                ),
                (
                    "wm.radial_control",
                    {"type": 'F', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("data_path_primary", 'tool_settings.sculpt.brush.strength'),
                            (
                                "data_path_secondary",
                                'tool_settings.unified_paint_settings.strength',
                            ),
                            (
                                "use_secondary",
                                'tool_settings.unified_paint_settings.use_unified_strength',
                            ),
                            ("rotation_path", 'tool_settings.sculpt.brush.texture_slot.angle'),
                            ("color_path", 'tool_settings.sculpt.brush.cursor_color_add'),
                            ("fill_color_path", ''),
                            ("fill_color_override_path", ''),
                            ("fill_color_override_test_path", ''),
                            ("zoom_path", ''),
                            ("image_id", 'tool_settings.sculpt.brush'),
                            ("secondary_tex", False),
                        ],
                    },
                ),
                (
                    "wm.radial_control",
                    {"type": 'F', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("data_path_primary", 'tool_settings.sculpt.brush.texture_slot.angle'),
                            ("data_path_secondary", ''),
                            ("use_secondary", ''),
                            ("rotation_path", 'tool_settings.sculpt.brush.texture_slot.angle'),
                            ("color_path", 'tool_settings.sculpt.brush.cursor_color_add'),
                            ("fill_color_path", ''),
                            ("fill_color_override_path", ''),
                            ("fill_color_override_test_path", ''),
                            ("zoom_path", ''),
                            ("image_id", 'tool_settings.sculpt.brush'),
                            ("secondary_tex", False),
                        ],
                    },
                ),
                (
                    "brush.stencil_control",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("mode", 'TRANSLATION'),
                        ],
                    },
                ),
                (
                    "brush.stencil_control",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("mode", 'SCALE'),
                        ],
                    },
                ),
                (
                    "brush.stencil_control",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'ROTATION'),
                        ],
                    },
                ),
                (
                    "brush.stencil_control",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("mode", 'TRANSLATION'),
                            ("texmode", 'SECONDARY'),
                        ],
                    },
                ),
                (
                    "brush.stencil_control",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'SCALE'),
                            ("texmode", 'SECONDARY'),
                        ],
                    },
                ),
                (
                    "brush.stencil_control",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
                    {
                        "properties": [
                            ("mode", 'ROTATION'),
                            ("texmode", 'SECONDARY'),
                        ],
                    },
                ),
                (
                    "paint.brush_select",
                    {"type": 'X', "value": 'PRESS'},
                    {
                        "properties": [
                            ("sculpt_tool", 'DRAW'),
                        ],
                    },
                ),
                (
                    "paint.brush_select",
                    {"type": 'S', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("sculpt_tool", 'SMOOTH'),
                        ],
                    },
                ),
                (
                    "paint.brush_select",
                    {"type": 'P', "value": 'PRESS'},
                    {
                        "properties": [
                            ("sculpt_tool", 'PINCH'),
                        ],
                    },
                ),
                (
                    "paint.brush_select",
                    {"type": 'I', "value": 'PRESS'},
                    {
                        "properties": [
                            ("sculpt_tool", 'INFLATE'),
                        ],
                    },
                ),
                (
                    "paint.brush_select",
                    {"type": 'G', "value": 'PRESS'},
                    {
                        "properties": [
                            ("sculpt_tool", 'GRAB'),
                        ],
                    },
                ),
                (
                    "paint.brush_select",
                    {"type": 'L', "value": 'PRESS'},
                    {
                        "properties": [
                            ("sculpt_tool", 'LAYER'),
                        ],
                    },
                ),
                (
                    "paint.brush_select",
                    {"type": 'T', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("sculpt_tool", 'FLATTEN'),
                        ],
                    },
                ),
                (
                    "paint.brush_select",
                    {"type": 'C', "value": 'PRESS'},
                    {
                        "properties": [
                            ("sculpt_tool", 'CLAY'),
                        ],
                    },
                ),
                (
                    "paint.brush_select",
                    {"type": 'C', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("sculpt_tool", 'CREASE'),
                        ],
                    },
                ),
                (
                    "paint.brush_select",
                    {"type": 'K', "value": 'PRESS'},
                    {
                        "properties": [
                            ("sculpt_tool", 'SNAKE_HOOK'),
                        ],
                    },
                ),
                (
                    "paint.brush_select",
                    {"type": 'M', "value": 'PRESS'},
                    {
                        "properties": [
                            ("sculpt_tool", 'MASK'),
                            ("toggle", True),
                            ("create_missing", True),
                        ],
                    },
                ),
                (
                    "wm.context_menu_enum",
                    {"type": 'E', "value": 'CLICK'},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.sculpt.brush.stroke_method'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'S', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.sculpt.brush.use_smooth_stroke'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'R', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_angle_control'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'A', "value": 'CLICK'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_sculpt_mask_edit_pie'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'A', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_sculpt_automasking_pie'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'W', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_sculpt_face_sets_edit_pie'),
                        ],
                    },
                ),
                (
                    "wm.call_panel",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PT_sculpt_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_panel",
                    {"type": 'APP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PT_sculpt_context_menu'),
                        ],
                    },
                ),
            ],
        },
    ),
    (
        "Text Generic",
        {"space_type": 'TEXT_EDITOR', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "wm.context_toggle",
                    {"type": 'T', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("data_path", 'space_data.show_region_ui'),
                        ],
                    },
                ),
                ("text.start_find", {"type": 'F', "value": 'PRESS', "ctrl": True}, None),
                ("text.jump", {"type": 'J', "value": 'PRESS', "ctrl": True}, None),
                ("text.find_set_selected", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
                ("text.replace", {"type": 'H', "value": 'PRESS', "ctrl": True}, None),
            ],
        },
    ),
    (
        "UV Editor",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {
            "items": [
                ("pie.q_key_shift", {"type": 'Q', "value": 'CLICK', "shift": True}, None),
                ("pie.q_key", {"type": 'Q', "value": 'CLICK'}, None),
                (
                    "uv.uv_face_join",
                    {"type": 'V', "value": 'PRESS', "shift": True, "alt": True},
                    None,
                ),
                ("uv.uv_face_rip", {"type": 'V', "value": 'PRESS', "alt": True}, None),
                ("uv.uv_squares_by_shape", {"type": 'E', "value": 'PRESS', "alt": True}, None),
                (
                    "wm.call_menu",
                    {"type": 'TAB', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'IMAGE_MT_uvs_select_mode'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'ONE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'VERT'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'TWO', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'EDGE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'THREE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'FACE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'ONE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("use_extend", True),
                            ("type", 'VERT'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'TWO', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("use_extend", True),
                            ("type", 'EDGE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'THREE', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("use_extend", True),
                            ("type", 'FACE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'ONE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("use_expand", True),
                            ("type", 'VERT'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'TWO', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("use_expand", True),
                            ("type", 'EDGE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'THREE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("use_expand", True),
                            ("type", 'FACE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'ONE', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("use_extend", True),
                            ("use_expand", True),
                            ("type", 'VERT'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'TWO', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("use_extend", True),
                            ("use_expand", True),
                            ("type", 'EDGE'),
                        ],
                    },
                ),
                (
                    "mesh.select_mode",
                    {"type": 'THREE', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("use_extend", True),
                            ("use_expand", True),
                            ("type", 'FACE'),
                        ],
                    },
                ),
                ("mesh.select_mode", {"type": 'FOUR', "value": 'PRESS'}, None),
                (
                    "uv.select_mode",
                    {"type": 'ONE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'VERTEX'),
                        ],
                    },
                ),
                (
                    "uv.select_mode",
                    {"type": 'TWO', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'EDGE'),
                        ],
                    },
                ),
                (
                    "uv.select_mode",
                    {"type": 'THREE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'FACE'),
                        ],
                    },
                ),
                (
                    "uv.select_mode",
                    {"type": 'FOUR', "value": 'PRESS'},
                    {
                        "properties": [
                            ("type", 'ISLAND'),
                        ],
                    },
                ),
                (
                    "uv.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK'},
                    {
                        "properties": [
                            ("deselect_all", True),
                        ],
                    },
                ),
                (
                    "uv.select",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True},
                    {
                        "properties": [
                            ("toggle", True),
                        ],
                    },
                ),
                ("uv.mark_seam", {"type": 'E', "value": 'PRESS', "ctrl": True}, None),
                ("uv.select_loop", {"type": 'LEFTMOUSE', "value": 'CLICK', "alt": True}, None),
                (
                    "uv.select_loop",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "alt": True},
                    {
                        "properties": [
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "uv.select_edge_ring",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "uv.select_edge_ring",
                    {
                        "type": 'LEFTMOUSE',
                        "value": 'CLICK',
                        "shift": True,
                        "ctrl": True,
                        "alt": True,
                    },
                    {
                        "properties": [
                            ("extend", True),
                        ],
                    },
                ),
                (
                    "uv.shortest_path_pick",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True},
                    {
                        "properties": [
                            ("use_fill", False),
                        ],
                    },
                ),
                (
                    "uv.shortest_path_pick",
                    {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("use_fill", True),
                        ],
                    },
                ),
                ("uv.select_split", {"type": 'Y', "value": 'PRESS'}, None),
                (
                    "uv.select_box",
                    {"type": 'B', "value": 'PRESS'},
                    {
                        "properties": [
                            ("pinned", False),
                        ],
                    },
                ),
                (
                    "uv.select_box",
                    {"type": 'B', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("pinned", True),
                        ],
                    },
                ),
                ("uv.select_circle", {"type": 'C', "value": 'PRESS'}, None),
                (
                    "uv.select_lasso",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'ADD'),
                        ],
                    },
                ),
                (
                    "uv.select_lasso",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("mode", 'SUB'),
                        ],
                    },
                ),
                ("uv.select_linked", {"type": 'L', "value": 'PRESS', "ctrl": True}, None),
                (
                    "uv.select_linked_pick",
                    {"type": 'L', "value": 'PRESS'},
                    {
                        "properties": [
                            ("extend", True),
                            ("deselect", False),
                        ],
                    },
                ),
                (
                    "uv.select_linked_pick",
                    {"type": 'L', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("deselect", True),
                        ],
                    },
                ),
                (
                    "uv.select_more",
                    {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    None,
                ),
                (
                    "uv.select_less",
                    {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True, "repeat": True},
                    None,
                ),
                ("uv.select_similar", {"type": 'G', "value": 'PRESS', "shift": True}, None),
                (
                    "uv.select_all",
                    {"type": 'A', "value": 'PRESS'},
                    {
                        "properties": [
                            ("action", 'SELECT'),
                        ],
                    },
                ),
                (
                    "uv.select_all",
                    {"type": 'A', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                (
                    "uv.select_all",
                    {"type": 'I', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("action", 'INVERT'),
                        ],
                    },
                ),
                (
                    "uv.select_all",
                    {"type": 'A', "value": 'DOUBLE_CLICK'},
                    {
                        "properties": [
                            ("action", 'DESELECT'),
                        ],
                    },
                ),
                ("uv.reveal", {"type": 'H', "value": 'PRESS', "alt": True}, None),
                (
                    "uv.hide",
                    {"type": 'H', "value": 'PRESS'},
                    {
                        "properties": [
                            ("unselected", False),
                        ],
                    },
                ),
                (
                    "uv.hide",
                    {"type": 'H', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("unselected", True),
                        ],
                    },
                ),
                ("uv.select_pinned", {"type": 'P', "value": 'PRESS', "shift": True}, None),
                (
                    "wm.call_menu",
                    {"type": 'M', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'IMAGE_MT_uvs_merge'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'M', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("name", 'IMAGE_MT_uvs_split'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'W', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'IMAGE_MT_uvs_align'),
                        ],
                    },
                ),
                ("uv.stitch", {"type": 'V', "value": 'PRESS', "alt": True}, None),
                ("uv.rip_move", {"type": 'V', "value": 'PRESS'}, None),
                (
                    "uv.pin",
                    {"type": 'P', "value": 'PRESS'},
                    {
                        "properties": [
                            ("clear", False),
                        ],
                    },
                ),
                (
                    "uv.pin",
                    {"type": 'P', "value": 'PRESS', "alt": True},
                    {
                        "properties": [
                            ("clear", True),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'U', "value": 'CLICK'},
                    {
                        "properties": [
                            ("name", 'IMAGE_MT_uvs_unwrap'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'S', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'IMAGE_MT_uvs_snap_pie'),
                        ],
                    },
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'O', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_MT_proportional_editing_falloff_pie'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'O', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.use_proportional_edit'),
                        ],
                    },
                ),
                ("transform.translate", {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'}, None),
                ("transform.translate", {"type": 'G', "value": 'PRESS'}, None),
                ("transform.rotate", {"type": 'R', "value": 'CLICK'}, None),
                ("transform.resize", {"type": 'S', "value": 'CLICK'}, None),
                (
                    "transform.shear",
                    {"type": 'S', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
                    None,
                ),
                ("transform.mirror", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
                (
                    "wm.context_toggle",
                    {"type": 'TAB', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.use_snap_uv'),
                        ],
                    },
                ),
                (
                    "wm.context_menu_enum",
                    {"type": 'TAB', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("data_path", 'tool_settings.snap_uv_element'),
                        ],
                    },
                ),
                (
                    "wm.context_toggle",
                    {"type": 'ACCENT_GRAVE', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("data_path", 'space_data.show_gizmo'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'RIGHTMOUSE', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'IMAGE_MT_uvs_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'APP', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'IMAGE_MT_uvs_context_menu'),
                        ],
                    },
                ),
                ("uv.cursor_set", {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True}, None),
                (
                    "transform.translate",
                    {"type": 'RIGHTMOUSE', "value": 'CLICK_DRAG', "shift": True},
                    {
                        "properties": [
                            ("cursor_transform", True),
                            ("release_confirm", True),
                        ],
                    },
                ),
                (
                    "wm.tool_set_by_id",
                    {"type": 'W', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'builtin.select_box'),
                            ("cycle", True),
                        ],
                    },
                ),
            ],
        },
    ),
    (
        "Window",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {
            "items": [
                (
                    "pie.ranslate_tooltips",
                    {"type": 'T', "value": 'CLICK', "shift": True, "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "pie.translate_interface",
                    {"type": 'T', "value": 'CLICK', "shift": True, "alt": True},
                    None,
                ),
                (
                    "wm.call_menu_pie",
                    {"type": 'S', "value": 'CLICK_DRAG', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'VIEW3D_PIE_MT_Bottom_S_ctrl'),
                        ],
                    },
                ),
                ("atomic.invoke_pie_menu_ui", {"type": 'F5', "value": 'PRESS', "alt": True}, None),
                (
                    "wm.call_menu",
                    {"type": 'F', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("name", 'THREEDI_MT_Main_Menu'),
                        ],
                    },
                ),
                (
                    "wm.save_reload",
                    {"type": 'W', "value": 'PRESS', "shift": True, "ctrl": True},
                    None,
                ),
                ("scene.refresh", {"type": 'F5', "value": 'PRESS', "alt": True}, None),
                (
                    "pie.ranslate_tooltips",
                    {"type": 'T', "value": 'CLICK', "shift": True, "ctrl": True, "alt": True},
                    None,
                ),
                (
                    "pie.translate_interface",
                    {"type": 'T', "value": 'CLICK', "shift": True, "alt": True},
                    None,
                ),
                (
                    "wm.call_menu",
                    {"type": 'N', "value": 'PRESS', "ctrl": True},
                    {
                        "properties": [
                            ("name", 'TOPBAR_MT_file_new'),
                        ],
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'O', "value": 'PRESS', "shift": True, "ctrl": True},
                    {
                        "properties": [
                            ("name", 'TOPBAR_MT_file_open_recent'),
                        ],
                    },
                ),
                ("wm.open_mainfile", {"type": 'O', "value": 'PRESS', "ctrl": True}, None),
                ("wm.save_mainfile", {"type": 'S', "value": 'CLICK', "ctrl": True}, None),
                (
                    "wm.save_as_mainfile",
                    {"type": 'S', "value": 'CLICK', "shift": True, "ctrl": True},
                    None,
                ),
                (
                    "wm.quit_blender",
                    {"type": 'Q', "value": 'CLICK', "ctrl": True},
                    {
                        "active": False,
                    },
                ),
                (
                    "wm.call_menu",
                    {"type": 'Q', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'SCREEN_MT_user_menu'),
                        ],
                        "active": False,
                    },
                ),
                (
                    "screen.space_type_set_or_cycle",
                    {"type": 'F1', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("space_type", 'FILE_BROWSER'),
                        ],
                    },
                ),
                (
                    "screen.space_type_set_or_cycle",
                    {"type": 'F2', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("space_type", 'CLIP_EDITOR'),
                        ],
                    },
                ),
                (
                    "screen.space_type_set_or_cycle",
                    {"type": 'F3', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("space_type", 'NODE_EDITOR'),
                        ],
                    },
                ),
                (
                    "screen.space_type_set_or_cycle",
                    {"type": 'F4', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("space_type", 'CONSOLE'),
                        ],
                    },
                ),
                (
                    "screen.space_type_set_or_cycle",
                    {"type": 'F5', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("space_type", 'VIEW_3D'),
                        ],
                    },
                ),
                (
                    "screen.space_type_set_or_cycle",
                    {"type": 'F6', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("space_type", 'GRAPH_EDITOR'),
                        ],
                    },
                ),
                (
                    "screen.space_type_set_or_cycle",
                    {"type": 'F7', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("space_type", 'PROPERTIES'),
                        ],
                    },
                ),
                (
                    "screen.space_type_set_or_cycle",
                    {"type": 'F8', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("space_type", 'SEQUENCE_EDITOR'),
                        ],
                    },
                ),
                (
                    "screen.space_type_set_or_cycle",
                    {"type": 'F9', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("space_type", 'OUTLINER'),
                        ],
                    },
                ),
                (
                    "screen.space_type_set_or_cycle",
                    {"type": 'F10', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("space_type", 'IMAGE_EDITOR'),
                        ],
                    },
                ),
                (
                    "screen.space_type_set_or_cycle",
                    {"type": 'F11', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("space_type", 'TEXT_EDITOR'),
                        ],
                    },
                ),
                (
                    "screen.space_type_set_or_cycle",
                    {"type": 'F12', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("space_type", 'DOPESHEET_EDITOR'),
                        ],
                    },
                ),
                (
                    "wm.call_panel",
                    {"type": 'NDOF_BUTTON_MENU', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'USERPREF_PT_ndof_settings'),
                        ],
                    },
                ),
                (
                    "wm.context_scale_float",
                    {"type": 'NDOF_BUTTON_PLUS', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'preferences.inputs.ndof_sensitivity'),
                            ("value", 1.1),
                        ],
                    },
                ),
                (
                    "wm.context_scale_float",
                    {"type": 'NDOF_BUTTON_MINUS', "value": 'PRESS'},
                    {
                        "properties": [
                            ("data_path", 'preferences.inputs.ndof_sensitivity'),
                            ("value", 0.90909094),
                        ],
                    },
                ),
                (
                    "wm.context_scale_float",
                    {"type": 'NDOF_BUTTON_PLUS', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("data_path", 'preferences.inputs.ndof_sensitivity'),
                            ("value", 1.5),
                        ],
                    },
                ),
                (
                    "wm.context_scale_float",
                    {"type": 'NDOF_BUTTON_MINUS', "value": 'PRESS', "shift": True},
                    {
                        "properties": [
                            ("data_path", 'preferences.inputs.ndof_sensitivity'),
                            ("value", 0.6666667),
                        ],
                    },
                ),
                (
                    "info.reports_display_update",
                    {"type": 'TIMER_REPORT', "value": 'ANY', "any": True},
                    None,
                ),
                ("wm.doc_view_manual_ui_context", {"type": 'F1', "value": 'PRESS'}, None),
                (
                    "wm.call_panel",
                    {"type": 'F2', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'TOPBAR_PT_name'),
                            ("keep_open", False),
                        ],
                    },
                ),
                ("wm.batch_rename", {"type": 'F2', "value": 'PRESS', "ctrl": True}, None),
                ("wm.search_menu", {"type": 'SPACE', "value": 'DOUBLE_CLICK'}, None),
                (
                    "wm.call_menu",
                    {"type": 'F4', "value": 'PRESS'},
                    {
                        "properties": [
                            ("name", 'TOPBAR_MT_file_context_menu'),
                        ],
                    },
                ),
                (
                    "wm.toolbar_fallback_pie",
                    {"type": 'W', "value": 'PRESS', "alt": True},
                    {
                        "active": False,
                    },
                ),
                (
                    "wm.toolbar",
                    {"type": 'SPACE', "value": 'PRESS', "shift": True},
                    {
                        "active": False,
                    },
                ),
                ("取消", {"type": 'ACCENT_GRAVE', "value": 'PRESS', "repeat": True}, None),
            ],
        },
    ),
]


if __name__ == "__main__":
    # Only add keywords that are supported.
    from bpy.app import version as blender_version

    keywords = {}
    if blender_version >= (2, 92, 0):
        keywords["keyconfig_version"] = keyconfig_version
    import os
    from bl_keymap_utils.io import keyconfig_import_from_data

    keyconfig_import_from_data(
        os.path.splitext(os.path.basename(__file__))[0],
        keyconfig_data,
        **keywords,
    )
