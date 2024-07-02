

import bpy

from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, FloatProperty, EnumProperty, FloatVectorProperty


class BendFacePreferences(AddonPreferences):
    bl_idname = __package__

    bool_con: BoolProperty(
        name="Continuous Mode",
        description="Stay inside the tool until pressing Q or Esc key",
        default=True
    )   

    def draw(self, context):
        layout = self.layout        
        row = layout.row()
        row.prop(self, "bool_con")    


def get_pref():
    pe = {'bool_con' : True, 
        }

    try:
        addons = bpy.context.preferences.addons
        if __package__ in addons:
            this_addon = addons[__package__]            
            if hasattr(this_addon, 'preferences'):
                pre = this_addon.preferences                
                pe['bool_con'] = pre.bool_con
                return pe

    except:
        print('pref error')
        pass
    return pe
