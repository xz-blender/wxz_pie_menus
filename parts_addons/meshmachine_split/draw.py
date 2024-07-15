import gpu
import bpy
import blf
from mathutils import Vector, Matrix, Quaternion
from gpu_extras.batch import batch_for_shader
from .utils import *

def vert_debug_print(debug, vert, msg, end="\n"):
    if debug:
        if type(debug) is list:
            if vert.index in debug:
                print(msg, end=end)
        else:
            print(msg, end=end)
def update_HUD_location(self, event, offsetx=20, offsety=20):
    self.HUD_x = event.mouse_x - self.region_offset_x + offsetx
    self.HUD_y = event.mouse_y - self.region_offset_y + offsety

def debug_draw_sweeps(self, sweeps, draw_loops=False, draw_handles=False):
    if draw_loops:
        self.loops = []

    if draw_handles:
        self.handles = []

    for sweep in sweeps:
        v1_co = sweep["verts"][0].co
        v2_co = sweep["verts"][1].co

        if draw_loops:
            loops = sweep.get("loops")

            if loops:
                remote1_co = loops[0][1]
                remote2_co = loops[1][1]

                self.loops.extend([v1_co, remote1_co, v2_co, remote2_co])

        if draw_handles:
            handles = sweep.get("handles")

            if handles:
                handle1_co = handles[0]
                handle2_co = handles[1]

                self.handles.extend([v1_co, handle1_co, v2_co, handle2_co])

def draw_stashes_HUD(context, stashes_count, invalid_stashes_count):
    # global machin3tools
    
    # if machin3tools is None:
    #     machin3tools = get_addon('MACHIN3tools')[0]

    region = context.region
    view = context.space_data
    bprefs = context.preferences

    if stashes_count > 0 and len(context.selected_objects) > 0 and view.overlay.show_overlays:
        region_overlap = bprefs.system.use_region_overlap
        header_alpha = bprefs.themes['Default'].view_3d.space.header[3]

        top_header = [r for r in context.area.regions if r.type == 'HEADER' and r.alignment == 'TOP']
        top_tool_header = [r for r in context.area.regions if r.type == 'TOOL_HEADER' and r.alignment == 'TOP']

        scale = context.preferences.system.ui_scale * get_prefs().modal_hud_scale

        offset_y = 5 * scale

        if region_overlap:

            if top_header and header_alpha < 1:
                offset_y += top_header[0].height

            if top_tool_header:
                offset_y += top_tool_header[0].height

        # if machin3tools and context.scene.M3.focus_history:
        #     machin3tools_scale = context.preferences.system.ui_scale * get_addon_prefs('MACHIN3tools').modal_hud_scale

        #     offset_y += 5 * machin3tools_scale + 12 * machin3tools_scale

        color = get_prefs().modal_hud_color
        font = 1
        fontsize = int(12 * scale)

        blf.size(font, fontsize)

        full_text = f"Stashes: {stashes_count}"

        if invalid_stashes_count:
            full_text += f" ({invalid_stashes_count} invalid)"

        offset_x = (blf.dimensions(font, full_text)[0] / 2)

        left_side = (region.width / 2) - offset_x

        title = 'Stashes: '
        dims = blf.dimensions(font, title)
        blf.color(font, *color, 0.5)
        blf.position(font,  left_side, region.height - offset_y - fontsize, 0)
        blf.draw(font, title)

        title = f"{stashes_count}"
        blf.color(font, *color, 1)
        dims2 = blf.dimensions(font, title)
        blf.position(font,  left_side + dims[0], region.height - offset_y - fontsize, 0)
        blf.draw(font, title)

        if invalid_stashes_count:
            title = f" ({invalid_stashes_count} invalid)"
            blf.color(font, *red, 1)
            blf.position(font, left_side + dims[0] + dims2[0], region.height - offset_y - fontsize, 0)
            blf.draw(font, title)

def draw_circle(loc=Vector(), rot=Quaternion(), radius=100, segments='AUTO', width=1, color=(1, 1, 1), alpha=1, xray=True, modal=True, screen=False):
    def draw():
        nonlocal segments

        if segments == 'AUTO':
            segments = max(int(radius), 16)

        else:
            segments = max(segments, 16)

        indices = [(i, i + 1) if i < segments - 1 else (i, 0) for i in range(segments)]

        coords = []

        for i in range(segments):

            theta = 2 * pi * i / segments

            x = loc.x + radius * cos(theta)
            y = loc.y + radius * sin(theta)

            coords.append(Vector((x, y, 0)))

        gpu.state.depth_test_set('NONE' if xray else 'LESS_EQUAL')
        gpu.state.blend_set('ALPHA')

        shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
        shader.uniform_float("color", (*color, alpha))
        shader.uniform_float("lineWidth", width)
        shader.uniform_float("viewportSize", gpu.state.scissor_get()[2:])
        shader.bind()

        batch = batch_for_shader(shader, 'LINES', {"pos": [rot @ co for co in coords]}, indices=indices)
        batch.draw(shader)

    if modal:
        draw()

    elif screen:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_PIXEL')

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')

def draw_label(context, title='', coords=None, offset=0, center=True, size=12, color=(1, 1, 1), alpha=1):
    if not coords:
        region = context.region
        width = region.width / 2
        height = region.height / 2
    else:
        width, height = coords

    scale = context.preferences.system.ui_scale * get_prefs().modal_hud_scale

    font = 1
    fontsize = int(size * scale)

    blf.size(font, fontsize)
    blf.color(font, *color, alpha)

    if center:
        dims = blf.dimensions(font, title)
        blf.position(font, width - (dims[0] / 2), height - (offset * scale), 1)

    else:
        blf.position(font, width, height - (offset * scale), 1)

    blf.draw(font, title)

    return blf.dimensions(font, title)
