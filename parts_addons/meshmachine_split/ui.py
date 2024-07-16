import blf
import bpy
import rna_keymap_ui
from bl_ui.space_statusbar import STATUSBAR_HT_header as statusbar
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_location_3d
from mathutils import Vector

from .utils import *
from .vars import *


def draw_init(self):
    self.font_id = 1
    self.offset = 0


def draw_title(self, title, subtitle=None, subtitleoffset=125, HUDcolor=None, HUDalpha=0.5, shadow=True):
    if not HUDcolor:
        HUDcolor = get_prefs().modal_hud_color
    shadow = (0, 0, 0)

    scale = bpy.context.preferences.system.ui_scale * get_prefs().modal_hud_scale

    if shadow:
        blf.color(self.font_id, *shadow, HUDalpha * 0.7)
        blf.position(self.font_id, self.HUD_x - 7 + 1, self.HUD_y - 1, 0)
        blf.size(self.font_id, int(20 * scale))
        blf.draw(self.font_id, "• " + title)

    blf.color(self.font_id, *HUDcolor, HUDalpha)
    blf.position(self.font_id, self.HUD_x - 7, self.HUD_y, 0)
    blf.size(self.font_id, int(20 * scale))
    blf.draw(self.font_id, f"» {title}")

    if subtitle:
        if shadow:
            blf.color(self.font_id, *shadow, HUDalpha / 2 * 0.7)
            blf.position(self.font_id, self.HUD_x - 7 + int(subtitleoffset * scale), self.HUD_y, 0)
            blf.size(self.font_id, int(15 * scale))
            blf.draw(self.font_id, subtitle)

        blf.color(self.font_id, *HUDcolor, HUDalpha / 2)
        blf.position(self.font_id, self.HUD_x - 7 + int(subtitleoffset * scale), self.HUD_y, 0)
        blf.size(self.font_id, int(15 * scale))
        blf.draw(self.font_id, subtitle)


def draw_prop(
    self,
    name,
    value,
    offset=0,
    decimal=2,
    active=True,
    HUDcolor=None,
    prop_offset=120,
    hint="",
    hint_offset=200,
    shadow=True,
):
    if not HUDcolor:
        HUDcolor = get_prefs().modal_hud_color
    shadow = (0, 0, 0)

    if active:
        alpha = 1
    else:
        alpha = 0.4

    scale = bpy.context.preferences.system.ui_scale * get_prefs().modal_hud_scale

    offset = self.offset + int(offset * scale)
    self.offset = offset

    if shadow:
        blf.color(self.font_id, *shadow, alpha * 0.7)
        blf.position(self.font_id, self.HUD_x + int(20 * scale) + 1, self.HUD_y - int(20 * scale) - offset - 1, 0)
        blf.size(self.font_id, int(11 * scale))
        blf.draw(self.font_id, name)

    blf.color(self.font_id, *HUDcolor, alpha)
    blf.position(self.font_id, self.HUD_x + int(20 * scale), self.HUD_y - int(20 * scale) - offset, 0)
    blf.size(self.font_id, int(11 * scale))
    blf.draw(self.font_id, name)

    if type(value) is str:
        if shadow:
            blf.color(self.font_id, *shadow, alpha * 0.7)
            blf.position(
                self.font_id, self.HUD_x + int(prop_offset * scale) + 1, self.HUD_y - int(20 * scale) - offset - 1, 0
            )
            blf.size(self.font_id, int(14 * scale))
            blf.draw(self.font_id, value)

        blf.color(self.font_id, *HUDcolor, alpha)
        blf.position(self.font_id, self.HUD_x + int(prop_offset * scale), self.HUD_y - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(14 * scale))

        blf.draw(self.font_id, value)

    elif type(value) is bool:
        if shadow:
            blf.color(self.font_id, *shadow, alpha * 0.7)
            blf.position(
                self.font_id, self.HUD_x + int(prop_offset * scale) + 1, self.HUD_y - int(20 * scale) - offset - 1, 0
            )
            blf.size(self.font_id, int(14 * scale))
            blf.draw(self.font_id, str(value))

        if value:
            blf.color(self.font_id, 0.5, 1, 0.5, alpha)
        else:
            blf.color(self.font_id, 1, 0.3, 0.3, alpha)

        blf.position(self.font_id, self.HUD_x + int(prop_offset * scale), self.HUD_y - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(14 * scale))
        blf.draw(self.font_id, str(value))

    elif type(value) is int:
        if shadow:
            blf.color(self.font_id, *shadow, alpha * 0.7)
            blf.position(
                self.font_id, self.HUD_x + int(prop_offset * scale) + 1, self.HUD_y - int(20 * scale) - offset - 1, 0
            )
            blf.size(self.font_id, int(20 * scale))
            blf.draw(self.font_id, "%d" % (value))

        blf.color(self.font_id, *HUDcolor, alpha)
        blf.position(self.font_id, self.HUD_x + int(prop_offset * scale), self.HUD_y - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(20 * scale))
        blf.draw(self.font_id, "%d" % (value))

    elif type(value) is float:
        if shadow:
            blf.color(self.font_id, *shadow, alpha * 0.7)
            blf.position(
                self.font_id, self.HUD_x + int(prop_offset * scale) + 1, self.HUD_y - int(20 * scale) - offset - 1, 0
            )
            blf.size(self.font_id, int(16 * scale))
            blf.draw(self.font_id, "%.*f" % (decimal, value))

        blf.color(self.font_id, *HUDcolor, alpha)
        blf.position(self.font_id, self.HUD_x + int(prop_offset * scale), self.HUD_y - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(16 * scale))
        blf.draw(self.font_id, "%.*f" % (decimal, value))

    if get_prefs().modal_hud_hints and hint:
        if shadow:
            blf.color(self.font_id, *shadow, 0.6 * 0.7)
            blf.position(
                self.font_id, self.HUD_x + int(hint_offset * scale) + 1, self.HUD_y - int(20 * scale) - offset - 1, 0
            )
            blf.size(self.font_id, int(11 * scale))
            blf.draw(self.font_id, "%s" % (hint))

        blf.color(self.font_id, *HUDcolor, 0.6)
        blf.position(self.font_id, self.HUD_x + int(hint_offset * scale), self.HUD_y - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(11 * scale))
        blf.draw(self.font_id, "%s" % (hint))


def draw_text(self, text, size, offset=0, offsetx=0, HUDcolor=None, HUDalpha=0.5, shadow=True):
    if not HUDcolor:
        HUDcolor = get_prefs().modal_hud_color
    shadow = (0, 0, 0)

    scale = bpy.context.preferences.system.ui_scale * get_prefs().modal_hud_scale

    offset = self.offset + int(offset * scale)
    self.offset = offset

    if shadow:
        blf.color(self.font_id, *shadow, HUDalpha * 0.7)
        blf.position(
            self.font_id, self.HUD_x + int(20 * scale) + offsetx + 1, self.HUD_y - int(20 * scale) - offset - 1, 0
        )
        blf.size(self.font_id, int(size * scale))
        blf.draw(self.font_id, text)

    blf.color(self.font_id, *HUDcolor, HUDalpha)
    blf.position(self.font_id, self.HUD_x + int(20 * scale) + offsetx, self.HUD_y - int(20 * scale) - offset, 0)
    blf.size(self.font_id, int(size * scale))
    blf.draw(self.font_id, text)


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

                label = item.get("label", None)

                if not label:
                    label = name.title().replace("_", " ")

                if len(keylist) > 1:
                    if idx == 0:
                        box.label(text=name.title().replace("_", " "))

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


def wrap_cursor(self, context, event):

    if event.mouse_region_x <= 0:
        context.window.cursor_warp(context.region.width + self.region_offset_x - 10, event.mouse_y)

    if (
        event.mouse_region_x >= context.region.width - 1
    ):  # the -1 is required for full screen, where the max region width is never passed
        context.window.cursor_warp(self.region_offset_x + 10, event.mouse_y)

    if event.mouse_region_y <= 0:
        context.window.cursor_warp(event.mouse_x, context.region.height + self.region_offset_y - 10)

    if event.mouse_region_y >= context.region.height - 1:
        context.window.cursor_warp(event.mouse_x, self.region_offset_y + 100)


def finish_status(self):
    statusbar.draw = self.bar_orig


def get_zoom_factor(context, depth_location, scale=10, ignore_obj_scale=False, debug=False):
    center = Vector((context.region.width / 2, context.region.height / 2))
    offset = center + Vector((scale, 0))

    center_3d = region_2d_to_location_3d(context.region, context.region_data, center, depth_location)
    offset_3d = region_2d_to_location_3d(context.region, context.region_data, offset, depth_location)

    zoom_factor = (center_3d - offset_3d).length

    if context.active_object and not ignore_obj_scale:
        mx = context.active_object.matrix_world.to_3x3()

        zoom_vector = mx.inverted_safe() @ Vector((zoom_factor, 0, 0))
        zoom_factor = zoom_vector.length

    if debug:
        from .draw import draw_point

        draw_point(depth_location, color=yellow, modal=False)
        draw_point(center_3d, color=green, modal=False)
        draw_point(offset_3d, color=red, modal=False)

        print("zoom factor:", zoom_factor)
    return zoom_factor


def init_cursor(self, event, offsetx=0, offsety=20):
    self.last_mouse_x = event.mouse_x
    self.last_mouse_y = event.mouse_y

    self.region_offset_x = event.mouse_x - event.mouse_region_x
    self.region_offset_y = event.mouse_y - event.mouse_region_y

    self.HUD_x = event.mouse_x - self.region_offset_x + offsetx
    self.HUD_y = event.mouse_y - self.region_offset_y + offsety


def init_status(self, context, title="", func=None):
    self.bar_orig = statusbar.draw

    if func:
        statusbar.draw = func
    else:
        statusbar.draw = draw_basic_status(self, context, title)


def popup_message(message, title="Info", icon="INFO", terminal=True):
    def draw_message(self, context):
        if isinstance(message, list):
            for m in message:
                self.layout.label(text=m)
        else:
            self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw_message, title=title, icon=icon)

    if terminal:
        if icon == "FILE_TICK":
            icon = "ENABLE"
        elif icon == "CANCEL":
            icon = "DISABLE"
        print(icon, title)
        print(" • ", message)


def get_zoom_factor(context, depth_location, scale=10, ignore_obj_scale=False):
    center = Vector((context.region.width / 2, context.region.height / 2))
    offset = center + Vector((scale, 0))

    center_3d = region_2d_to_location_3d(context.region, context.region_data, center, depth_location)
    offset_3d = region_2d_to_location_3d(context.region, context.region_data, offset, depth_location)

    zoom_factor = (center_3d - offset_3d).length

    if context.active_object and not ignore_obj_scale:
        mx = context.active_object.matrix_world.to_3x3()

        zoom_vector = mx.inverted_safe() @ Vector((zoom_factor, 0, 0))
        zoom_factor = zoom_vector.length
    return zoom_factor


def get_flick_direction(self, context):
    origin_2d = location_3d_to_region_2d(
        context.region,
        context.region_data,
        self.init_mouse_3d,
        default=Vector((context.region.width / 2, context.region.height / 2)),
    )
    axes_2d = {}

    for direction, axis in self.axes.items():

        axis_2d = location_3d_to_region_2d(
            context.region, context.region_data, self.init_mouse_3d + axis, default=origin_2d
        )
        if (axis_2d - origin_2d).length:
            axes_2d[direction] = (axis_2d - origin_2d).normalized()

    return min([(d, abs(self.flick_vector.xy.angle_signed(a))) for d, a in axes_2d.items()], key=lambda x: x[1])[0]
