import bpy
import gpu
from gpu_extras.batch import batch_for_shader


def get_builtin_shader_name(name, prefix="3D"):
    if bpy.app.version >= (4, 0, 0):
        return name
    else:
        return f"{prefix}_{name}"


def draw_focus_HUD(context, color=(1, 1, 1), alpha=1, width=2):
    if context.space_data.overlay.show_overlays:
        region = context.region
        view = context.space_data

        if view.local_view:

            coords = [
                (width, width),
                (region.width - width, width),
                (region.width - width, region.height - width),
                (width, region.height - width),
            ]
            indices = [(0, 1), (1, 2), (2, 3), (3, 0)]

            shader = gpu.shader.from_builtin(get_builtin_shader_name("UNIFORM_COLOR", "2D"))
            shader.bind()
            shader.uniform_float("color", (*color, alpha / 4))

            gpu.state.depth_test_set("NONE")
            gpu.state.blend_set("ALPHA" if (alpha / 4) < 1 else "NONE")
            gpu.state.line_width_set(width)

            batch = batch_for_shader(shader, "LINES", {"pos": coords}, indices=indices)
            batch.draw(shader)


def manage_focus_HUD():
    global focusHUD
    focusHUD = None

    scene = getattr(bpy.context, "scene", None)

    if scene:
        if focusHUD and "RNA_HANDLE_REMOVED" in str(focusHUD):
            focusHUD = None

        focusHUD = bpy.types.SpaceView3D.draw_handler_add(
            draw_focus_HUD, (bpy.context, (1, 1, 1), 1, 2), "WINDOW", "POST_PIXEL"
        )


def delay_execution(func, delay=0):
    if bpy.app.timers.is_registered(func):
        bpy.app.timers.unregister(func)

    bpy.app.timers.register(func, first_interval=delay)
