from time import time

import bpy
import rna_keymap_ui
from bl_ui.space_statusbar import STATUSBAR_HT_header as statusbar
from mathutils import Vector

from ...utils import get_prefs

icons = None


def get_icon(name):
    global icons

    if not icons:
        from . import icons

    return icons[name].icon_id


def get_mouse_pos(self, context, event, hud=True, hud_offset=(20, 20)):

    self.mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))

    if hud:
        scale = context.preferences.system.ui_scale * get_prefs().modal_hud_scale

        self.HUD_x = self.mouse_pos.x + hud_offset[0] * scale
        self.HUD_y = self.mouse_pos.y + hud_offset[1] * scale


def draw_keymap_items(kc, name, keylist, layout):
    drawn = []

    idx = 0

    for item in keylist:
        keymap = item.get("keymap")
        isdrawn = False

        if keymap:
            km = kc.keymaps.get(keymap)

            kmi = None
            if km:
                idname = item.get("idname")

                for kmitem in km.keymap_items:
                    if kmitem.idname == idname:
                        properties = item.get("properties")

                        if properties:
                            if all([getattr(kmitem.properties, name, None) == value for name, value in properties]):
                                kmi = kmitem
                                break

                        else:
                            kmi = kmitem
                            break

            if kmi:
                if idx == 0:
                    box = layout.box()

                if len(keylist) == 1:
                    label = name.title().replace("_", " ")

                else:
                    if idx == 0:
                        box.label(text=name.title().replace("_", " "))

                    label = item.get("label")

                row = box.split(factor=0.15)
                row.label(text=label)

                rna_keymap_ui.draw_kmi(["ADDON", "USER", "DEFAULT"], kc, km, kmi, row, 0)

                infos = item.get("info", [])
                for text in infos:
                    row = box.split(factor=0.15)
                    row.separator()
                    row.label(text=text, icon="INFO")

                isdrawn = True
                idx += 1

        drawn.append(isdrawn)
    return drawn


def get_keymap_item(name, idname, key=None, alt=False, ctrl=False, shift=False, properties=[], iterate=False):

    def return_found_item():
        found = (
            True
            if key is None
            else all([kmi.type == key and kmi.alt is alt and kmi.ctrl is ctrl and kmi.shift is shift])
        )

        if found:
            if properties:
                if all([getattr(kmi.properties, name, False) == prop for name, prop in properties]):
                    return kmi
            else:
                return kmi

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user

    km = kc.keymaps.get(name)

    if bpy.app.version >= (3, 0, 0):
        alt = int(alt)
        ctrl = int(ctrl)
        shift = int(shift)

    if km:

        if iterate:
            kmis = [kmi for kmi in km.keymap_items if kmi.idname == idname]

            for kmi in kmis:
                r = return_found_item()

                if r:
                    return r

        else:
            kmi = km.keymap_items.get(idname)

            if kmi:
                return return_found_item()


def init_status(self, context, title="", func=None):
    self.bar_orig = statusbar.draw

    if func:
        statusbar.draw = func
    else:
        statusbar.draw = draw_basic_status(self, context, title)


def draw_basic_status(self, context, title):
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.label(text=title)

        row.label(text="", icon="MOUSE_LMB")
        row.label(text="Finish")

        if context.window_manager.keyconfigs.active.name.startswith("blender"):
            row.label(text="", icon="MOUSE_MMB")
            row.label(text="Viewport")

        row.label(text="", icon="MOUSE_RMB")
        row.label(text="Cancel")

    return draw


def finish_status(self):
    statusbar.draw = self.bar_orig


def navigation_passthrough(event, alt=True, wheel=False):
    if alt and wheel:
        return (
            event.type in {"MIDDLEMOUSE"}
            or event.type.startswith("NDOF")
            or (event.alt and event.type in {"LEFTMOUSE", "RIGHTMOUSE"} and event.value == "PRESS")
            or event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}
        )
    elif alt:
        return (
            event.type in {"MIDDLEMOUSE"}
            or event.type.startswith("NDOF")
            or (event.alt and event.type in {"LEFTMOUSE", "RIGHTMOUSE"} and event.value == "PRESS")
        )
    elif wheel:
        return (
            event.type in {"MIDDLEMOUSE"}
            or event.type.startswith("NDOF")
            or event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}
        )
    else:
        return event.type in {"MIDDLEMOUSE"} or event.type.startswith("NDOF")


def init_timer_modal(self, debug=False):

    self.start = time()

    self.countdown = self.time * get_prefs().modal_hud_timeout

    if debug:
        print(f"initiating timer with a countdown of {self.time}s ({self.time * get_prefs().modal_hud_timeout}s)")


def set_countdown(self, debug=False):

    self.countdown = self.time * get_prefs().modal_hud_timeout - (time() - self.start)

    if debug:
        print("countdown:", self.countdown)


def get_timer_progress(self, debug=False):

    progress = self.countdown / (self.time * get_prefs().modal_hud_timeout)

    if debug:
        print("progress:", progress)

    return progress


def ignore_events(event, none=True, timer=True, timer_report=True):
    ignore = ["INBETWEEN_MOUSEMOVE", "WINDOW_DEACTIVATE"]

    if none:
        ignore.append("NONE")

    if timer:
        ignore.extend(["TIMER", "TIMER1", "TIMER2", "TIMER3"])

    if timer_report:
        ignore.append("TIMER_REPORT")

    return event.type in ignore


def force_ui_update(context, active=None):

    if context.mode == "OBJECT":
        if active:
            active.select_set(True)

        else:
            visible = context.visible_objects

            if visible:
                visible[0].select_set(visible[0].select_get())

    elif context.mode == "EDIT_MESH":
        context.active_object.select_set(True)
