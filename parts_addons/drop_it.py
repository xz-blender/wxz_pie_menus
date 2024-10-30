import random
import time

import bpy
import mathutils
import numpy as np

# 记录depsgraph以便于进行射线检测
dgraph = None


class DROPIT_OT_drop_it(bpy.types.Operator):
    """将选中的物体放置到地面或其他表面上"""

    bl_idname = "pie.drop_it"
    bl_label = "置落物体"
    bl_options = {"REGISTER", "UNDO"}

    drop_by: bpy.props.EnumProperty(
        name="放置方式",
        description="选择根据最低顶点或物体原点来放置",
        items=[("lw_vertex", "最低顶点", "根据最低顶点进行放置"), ("origin", "原点", "根据物体原点进行放置")],
    )  # type: ignore

    col_in_sel: bpy.props.BoolProperty(
        name="选择中的碰撞", description="选择中物体的碰撞检测", default=True
    )  # type: ignore

    affect_parenting: bpy.props.BoolProperty(
        name="父子关系设置", description="影响父子连接", default=False
    )  # type: ignore

    affect_only_parents: bpy.props.BoolProperty(
        name="仅影响父物体", description="只影响父物体，保持子物体不变", default=False
    )  # type: ignore

    affect_sel_childs: bpy.props.BoolProperty(
        name="影响选择的子物体", description="影响选择的子物体", default=False
    )  # type: ignore

    bpy.types.WindowManager.surf_align = bpy.props.BoolProperty(
        default=True, name="对齐到表面", description="将物体对齐到碰撞表面的法线"
    )

    rand_zrot: bpy.props.IntProperty(
        name="随机旋转角度", description="在Z轴上随机旋转角度，范围是-Z到+Z", default=0, min=0, max=360, subtype="ANGLE"
    )  # type: ignore

    rand_loc: bpy.props.FloatProperty(
        name="位置随机半径",
        description="在XY平面上为物体位置添加随机半径",
        default=0,
        min=0,
        max=100,
        subtype="DISTANCE",
    )  # type: ignore

    offset_z: bpy.props.FloatProperty(
        name="Z轴偏移位置", description="设置物体在Z轴上的偏移位置", default=0, min=-10, max=10, subtype="DISTANCE"
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and context.mode == "OBJECT" and context.area.type == "VIEW_3D"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        col.label(text="放置方式:")
        row = layout.row()
        row.prop(self, "drop_by")
        row.prop(self, "col_in_sel")

        col = layout.column(align=True)
        col.label(text="随机参数:")
        row = layout.row()
        row.prop(self, "rand_zrot")
        row.prop(self, "rand_loc")
        layout.prop(self, "offset_z")

        layout.column()
        layout.column()
        layout.prop(self, "affect_parenting", icon="LINKED")

        if self.affect_parenting:
            col = layout.column(align=True)
            col.prop(self, "affect_only_parents")
            col.prop(self, "affect_sel_childs")

            if self.affect_only_parents:
                self.affect_sel_childs = False

        wm = context.window_manager
        if wm.surf_align:
            label = "对齐到表面"
            ic = "GIZMO"
        else:
            label = "不对齐"
            ic = "ORIENTATION_VIEW"
        layout.prop(wm, "surf_align", text=label, toggle=True, icon=ic)

    def execute(self, context):
        time_start = time.time()
        objs = context.selected_objects
        view_layer = context.view_layer

        # CHECK RAYCAST APP VERSION
        global dgraph
        dgraph = context.view_layer.depsgraph

        if len(objs) > 1:
            if not self.col_in_sel:
                for obj in objs:
                    obj.hide_set(True)
            else:
                objs_sorted = [(obj, obj.location.z) for obj in objs]
                objs_sorted = sorted(objs_sorted, key=lambda os: os[1])
                objs = [obj[0] for obj in objs_sorted]

        for obj in objs:
            if obj.type == "MESH" or obj.type == "EMPTY":
                if obj.type == "EMPTY" and obj.instance_type == "COLLECTION":
                    self.report({"ERROR"}, f"实例物体 '{obj.name}' 的类型不支持")
                    continue

                parent = None
                children = []
                hidden_objs = []
                obj_rot_z = obj.rotation_euler[2]

                if not self.affect_sel_childs and obj.parent:
                    continue

                if self.affect_only_parents:
                    if obj.children:
                        children = obj.children
                        for child in children:
                            unparent(child)
                    else:
                        continue

                if self.affect_sel_childs:
                    if obj.children:
                        for child in obj.children:
                            if child in objs:
                                children.append(child)
                                unparent(child)

                if obj.parent:
                    parent = obj.parent
                    unparent(obj)

                if context.window_manager.surf_align:
                    obj.rotation_euler = mathutils.Euler()

                if self.rand_loc > 0:
                    x = random.uniform(-self.rand_loc, self.rand_loc)
                    y = random.uniform(-self.rand_loc, self.rand_loc)
                    obj.location.x += x
                    obj.location.y += y

                view_layer.update()

                if self.drop_by == "lw_vertex":
                    # 获取最低顶点
                    lowest_verts = get_lowest_verts(obj)
                    if len(lowest_verts) == 0:
                        self.report({"ERROR"}, f"对象 '{obj.name}' 没有有效的顶点数据")
                        continue
                else:
                    lowest_verts = [obj.location]

                hidden_objs.append(obj)
                obj.hide_set(True)

                if obj.children:
                    for child in obj.children:
                        if not child.hide_get():
                            hidden_objs.append(child)
                            child.hide_set(True)

                hit_info = {}

                for co in lowest_verts:
                    cast = raycast(context, co.copy())
                    if cast is not None:
                        hit_info.update(cast)

                dist = 0
                hitloc_nrm = (0, 0)
                if len(hit_info) == 0:
                    dist = lowest_verts[0][2]
                    hitloc_nrm = (lowest_verts[0], mathutils.Vector((0, 0, 1)))
                else:
                    dist = min(hit_info.keys())
                    hitloc_nrm = hit_info.get(dist)

                obj.location.z -= dist
                view_layer.update()

                if context.window_manager.surf_align:
                    rotate_object(obj, hitloc_nrm[0], hitloc_nrm[1])
                    obj.rotation_euler.rotate_axis("Z", obj_rot_z)

                if self.rand_zrot > 0:
                    obj.rotation_euler.rotate_axis("Z", math.radians(random.randrange(-self.rand_zrot, self.rand_zrot)))

                if self.offset_z != 0:
                    vec = mathutils.Vector((0.0, 0.0, self.offset_z))
                    local_loc = vec @ obj.matrix_world.inverted()
                    obj.location += local_loc

                if parent:
                    set_parent(parent, obj)

                if children:
                    for child in children:
                        set_parent(obj, child)

                if hidden_objs:
                    for o in hidden_objs:
                        o.hide_set(False)
                        o.select_set(True)

                view_layer.update()

        if not self.col_in_sel:
            for obj in objs:
                obj.hide_set(False)
                obj.select_set(True)

        print("放置物体，计算时间: ", str(time.time() - time_start))

        return {"FINISHED"}


def set_parent(parent, child):
    """设置子物体的父物体"""
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def unparent(obj):
    """取消物体的父物体关系"""
    mxw_obj = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_world = mxw_obj


def rotate_object(obj, loc, normal):
    """调整物体旋转以对齐到表面法线"""
    up = mathutils.Vector((0, 0, 1))
    angle = normal.angle(up)
    direction = up.cross(normal)

    R = mathutils.Matrix.Rotation(angle, 4, direction)
    T = mathutils.Matrix.Translation(loc)
    M = T @ R @ T.inverted()

    obj.location = M @ obj.location
    obj.rotation_euler.rotate(M)


def get_lowest_verts(obj):
    """获取物体的最低顶点"""
    if obj.type != "MESH" or obj.data is None:
        return []

    verts = obj.data.vertices
    count = len(verts)
    co = np.zeros(count * 3, dtype=np.float32)
    verts.foreach_get("co", co)
    co.shape = (count, 3)

    mtxw = np.array(obj.matrix_world)
    mtxw2 = mtxw[:3, :3].T
    loc = mtxw[:3, 3]
    co_world = co @ mtxw2 + loc

    co_z_all = co_world[:, 2]
    co_z_min = co_z_all.min()
    co_low_all = co_world[co_z_all == co_z_min]

    count = len(co_low_all)
    if count == 0:
        return []

    x = co_low_all[:, 0]
    y = co_low_all[:, 1]
    x_mean = x.sum() / len(x)
    y_mean = y.sum() / len(y)

    low_center = mathutils.Vector((x_mean, y_mean, co_z_min))
    co_low_all = np.append(co_low_all, [[x_mean, y_mean, co_z_min]], axis=0)

    return co_low_all


def raycast(context, origin):
    """从起点发射射线，并返回碰撞信息"""
    _origin = origin.copy()
    _origin[2] -= 0.0001  # 避免精度问题

    cast = context.scene.ray_cast(dgraph, _origin, (0, 0, -1), distance=1000)

    if not cast[0]:
        return None

    hitloc = cast[1]
    nrm = cast[2]
    dist = origin[2] - hitloc[2]
    return {dist: (hitloc, nrm)}


# 插件类
classes = [
    DROPIT_OT_drop_it,
]


def register():
    """注册插件"""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """卸载插件"""
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
