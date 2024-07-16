

import bpy
#import bmesh
import blf


from mathutils import Matrix, Vector, Quaternion
from mathutils import bvhtree
from bpy_extras import view3d_utils
import gpu
from gpu_extras.batch import batch_for_shader
import math

if bpy.app.version < (3, 5, 0):
    import bgl


import pprint

if bpy.app.version < (3, 5, 0):
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
else:
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')



shader2d = gpu.shader.from_builtin('2D_UNIFORM_COLOR')

handle3d = None
handle3dtext = None
handle3drect = None

lines = []
lines2 = []
txtall = []
rects = []
textpos = []
data = []


def addline(p1, p2):
    global lines
    lines.append(p1)
    lines.append(p2)


def addline2(p1, p2):
    global lines2
    lines2.append(p1)
    lines2.append(p2)    


def get_screen_pos(loc):
    region = bpy.context.region
    region3D = bpy.context.space_data.region_3d
    pos = view3d_utils.location_3d_to_region_2d(region, region3D, loc)
    return pos    


def addtext(loc, txt):
    global textpos
    pos = get_screen_pos(loc)
    textpos.append((str(txt), pos.x, pos.y, 20))


def ShowMessageBox(messages = "", title = "", icon = 'BLENDER'):
    def draw(self, context):
        for s in messages:
            self.layout.label(text=s)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


def draw_3d(self, context):
    global lines
    global lines2
    draw_line(lines, (1, 0.3, 0.3, 1), True, True, 1)
    draw_line(lines2, (0.3, 1, 0.3, 1), True, True, 1)


def draw_text_callback(self, context):
    global txtall
    global textpos
    left = 100
    sp = 20 * 1.7
    top = len(txtall) * sp + 50
    off = 0
    for p in txtall:
        off += sp
        draw_text( [left, top - off], p)    

    for p in textpos:        
        #draw_text( [left, top - off], p)    
        draw_text_adv(p)    



def draw_text_adv(pam):
    # sc = bpy.context.preferences.view.ui_scale  
    sc = bpy.context.preferences.system.ui_scale 
    text, x, y, size = pam
    font_id = 0
    # draw some text
    blf.color(font_id, 1,1,1,1)
    blf.position(font_id, x, y, 0)
    blf.size(font_id, math.floor(size * sc), 72)
    blf.draw(font_id, text)


def draw_text(pos, text):
    # sc = bpy.context.preferences.view.ui_scale 
    sc = bpy.context.preferences.system.ui_scale 
    if pos == None:
        return
    font_id = 0
    # draw some text
    blf.color(font_id, 1, 1, 1, 1)
    blf.position(font_id, pos[0], pos[1], 0)
    blf.size(font_id, math.floor(16 * sc), 72)
    blf.draw(font_id, text)


    
def draw_line(points, color, blend=False, smooth=False, width=1):
    if bpy.app.version < (3, 5, 0):
        draw_line_gl(points, color, blend=blend, smooth=smooth, width=width)
        return
    # draw_line_gl(points, color, blend=blend, smooth=smooth, width=width)
    # return

    global shader
    gpu.state.blend_set('ALPHA')
    # gpu.state.line_width_set(width)    
    #bgl.glEnable(bgl.GL_LINE_SMOOTH)
    
    #bgl.glLineWidth(width)
    shader.bind()
    shader.uniform_float("viewportSize", gpu.state.viewport_get()[2:])
    shader.uniform_float("color", color)
    shader.uniform_float("lineWidth", width)
    batch = batch_for_shader(shader, 'LINES', {"pos": points})
    batch.draw(shader)

    gpu.state.blend_set("NONE")

    #bgl.glDisable(bgl.GL_BLEND)
    #bgl.glDisable(bgl.GL_LINE_SMOOTH)
    #bgl.glLineWidth(1)    




def draw_line_gl(points, color, blend=False, smooth=False, width=1):
    global shader

    if len(points) == 0:
        return

    if blend:
        bgl.glEnable(bgl.GL_BLEND)
    else:
        bgl.glDisable(bgl.GL_BLEND)

    if smooth:
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
    else:
        bgl.glDisable(bgl.GL_LINE_SMOOTH)
    
    bgl.glLineWidth(width)

    shader.bind()
    shader.uniform_float("color", color)
    batch = batch_for_shader(shader, 'LINES', {"pos": points})
    batch.draw(shader)

    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_LINE_SMOOTH)
    bgl.glLineWidth(1)    





def draw_rect_callback(self, context):
    global rects
    #vertices = ((100, 100), (300, 100), (100, 200), (300, 200))
    vertices = rects
    indices = ((0, 1, 2), (2, 1, 3))

    shader2d.bind()
    shader2d.uniform_float("color", (0, 0, 0, 0.3))
    batch = batch_for_shader(shader2d, 'TRIS', {"pos": vertices}, indices=indices)
    batch.draw(shader)


def draw_handle_add(arg):
    global handle3d
    print('add draw')
    handle3d = bpy.types.SpaceView3D.draw_handler_add(
        draw_3d, arg, 'WINDOW', 'POST_VIEW')

def text_handle_add(arg):
    global handle3dtext
    print('add text')
    handle3dtext = bpy.types.SpaceView3D.draw_handler_add(
        draw_text_callback, arg, 'WINDOW', 'POST_PIXEL')

def rect_handle_add(arg):
    global handle3drect
    print('add rect')
    handle3drect = bpy.types.SpaceView3D.draw_handler_add(
        draw_rect_callback, arg, 'WINDOW', 'POST_PIXEL')


def draw_handle_remove():    
    global handle3d
    if handle3d != None:
        print('remove draw')
        bpy.types.SpaceView3D.draw_handler_remove(
            handle3d, 'WINDOW')   
    global handle3dtext
    if handle3dtext != None:
        print('remove text')
        bpy.types.SpaceView3D.draw_handler_remove(
            handle3dtext, 'WINDOW')   
    global handle3drect
    if handle3drect != None:
        print('remove rect')
        bpy.types.SpaceView3D.draw_handler_remove(
            handle3drect, 'WINDOW')   
          