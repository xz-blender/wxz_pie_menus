import collections
import os
import subprocess
import sys
import tempfile
import typing

import bpy

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (4, 1, 0),
    "location": "View3D",
    "category": "3D View",
}


MODULE_CLASSES: typing.List[typing.Type] = []


class DatablockMemoryUsage:
    @staticmethod
    def get_attribute_datatype_size(datatype: str) -> int:
        if datatype == "FLOAT":
            return 4
        elif datatype == "INT":
            return 4
        elif datatype == "FLOAT_VECTOR":
            return 3 * 4
        elif datatype == "FLOAT_COLOR":
            return 4 * 4  # RGBA
        elif datatype == "STRING":
            # TODO: we just make something up here...
            return 16
        elif datatype == "BOOLEAN":
            return 1
        elif datatype == "FLOAT2":
            return 2 * 4
        else:
            # TODO: warn?
            return 0

    @staticmethod
    def get_attribute_domain_multiplier(datablock: bpy.types.Mesh, domain: str) -> int:
        if domain == "POINT":
            return len(datablock.vertices)
        elif domain == "EDGE":
            return len(datablock.edges)
        elif domain == "FACE":
            return len(datablock.polygons)
        elif domain == "CORNER":
            # TODO: no idea
            return 0
        elif domain == "CURVE":
            # TODO: no idea
            return 0
        elif domain == "INSTANCE":
            # TODO: no idea
            return 0
        # origin:
        # else:
        #     telemetry.log_warning(f"{domain} not supported in memory estimation")
        # new:
        else:
            return 0

    def __init__(self, datablock: bpy.types.ID):
        self.bytes = 0
        if hasattr(datablock, "name_full"):
            self.title = f"{type(datablock).__name__}:{datablock.name_full}"
        else:
            self.title = f"{type(datablock).__name__}:{datablock.name}"

        if isinstance(datablock, bpy.types.Mesh):
            # vertex position, 3x float32
            self.bytes += len(datablock.vertices) * 3 * 4

            if datablock.has_custom_normals:
                # custom normal, 3x float32
                self.bytes += len(datablock.vertices) * 3 * 4

            # each attribute has to be treated separately
            for attribute in datablock.attributes:
                self.bytes += self.get_attribute_datatype_size(
                    attribute.data_type
                ) * self.get_attribute_domain_multiplier(datablock, attribute.domain)

            # each edge indexes into two vertices, each index is int32, plus crease and bevel floats
            self.bytes += len(datablock.edges) * 4 * 4
            # edge index, vertex index
            # TODO: normals? does blender store tangent, bitangent or is this calculated on the fly?
            self.bytes += len(datablock.loops) * 2 * 4
            for polygon in datablock.polygons:
                # loop_start, loop_total indices
                self.bytes += 2 * 4
                # vertex indices
                self.bytes += len(polygon.vertices) * 4

            for uv_layer in datablock.uv_layers:
                # we assume 2x float32
                self.bytes += len(datablock.vertices) * 2 * 4

            for vertex_color in datablock.vertex_colors:
                # we assume 3x int8
                self.bytes += len(datablock.vertices) * 3 * 1

            # TODO: This model is super simplified

        elif isinstance(datablock, bpy.types.Image):
            width, height = datablock.size
            bits_per_pixel = datablock.depth
            self.bytes += (width * height * bits_per_pixel) // 8

        assert self.bytes >= 0, f"The {datablock.name} datablock cannot use negative memory"

    def __repr__(self) -> str:
        return f"{self.bytes} B"


class MemoryUsageStatistics:
    def __init__(self):
        self.datablocks: typing.Dict[str, DatablockMemoryUsage] = {}
        self.target_to_dependencies: typing.DefaultDict[str, typing.Set[str]] = collections.defaultdict(set)
        self.dependency_to_targets: typing.DefaultDict[str, typing.Set[str]] = collections.defaultdict(set)

    def debug_print(self):
        print(self.datablocks)
        print(self.target_to_dependencies)
        print(self.dependency_to_targets)

    def write_to_file(self, fp: typing.IO) -> None:
        assert len(self.datablocks) > 0, "Memory usage cannot be calculated with no datablocks"

        sorted_by_usage = sorted(self.datablocks.items(), key=lambda x: x[1].bytes, reverse=True)
        _, max_usage = sorted_by_usage[0]
        total_usage_bytes = sum(usage.bytes for usage in self.datablocks.values())
        max_usage_bytes = max_usage.bytes

        # We want to avoid zero divsion when calculating percentages
        if total_usage_bytes == 0:
            total_usage_bytes = 1
        if max_usage_bytes == 0:
            max_usage_bytes = 1

        # TODO: This should be improved to look better
        # TODO: Missing dependencies visualization, why is a particular mesh even loaded, ...
        print("<html><body>\n", file=fp)
        print(f"<b>total usage:</b> {total_usage_bytes / 1024 / 1024 :.3f} MiB<br>\n", file=fp)
        print("<table>\n", file=fp)
        print("<tr>\n", file=fp)
        print("\t\t<th>datablock</th>\n", file=fp)
        print("\t\t<th>approximate usage</th>\n", file=fp)
        print("\t\t<th>%</th>", file=fp)
        print("\t\t<th></th>\n", file=fp)
        print("\t</tr>\n", file=fp)

        for _, datablock_usage in sorted_by_usage:
            print("\t<tr>\n", file=fp)
            print(f"\t\t<td>{datablock_usage.title}</td>\n", file=fp)
            print(f"\t\t<td>{datablock_usage.bytes / 1024.0 / 1024.0 :.3f} MiB</td>\n", file=fp)
            print(f"\t\t<td>{datablock_usage.bytes * 100 / total_usage_bytes :.2f}%</td>\n", file=fp)
            red_channel = datablock_usage.bytes * 255 // max_usage_bytes
            print(
                f'\t\t<td><div style="background: rgb({red_channel}, {255 - red_channel}, 0); height: 12px; width: {datablock_usage.bytes * 200 // max_usage_bytes}px"></div></td>\n',
                file=fp,
            )
            print("\t</tr>\n", file=fp)
        print("</table>\n", file=fp)
        print("</body></html>\n", file=fp)

    def _datablock_key(self, datablock: bpy.types.ID, scope: str = "") -> str:
        # NodeTrees are owned by materials and between materials NodeTree names can clash, so we
        # assign the scope as part of the datablock_key to make it unique.
        if hasattr(datablock, "name_full"):
            return f"{scope}:{type(datablock).__name__}:{datablock.name_full}"
        else:
            return f"{scope}:{type(datablock).__name__}:{datablock.name}"

    def record_dependency(self, target: bpy.types.ID, dependency: bpy.types.ID) -> None:
        target_key = self._datablock_key(target)
        dependency_key = self._datablock_key(dependency)

        self.target_to_dependencies[target_key].add(dependency_key)
        self.dependency_to_targets[dependency_key].add(target_key)

    def record_datablock(self, datablock: bpy.types.ID, scope: str = "") -> None:
        datablock_key = self._datablock_key(datablock, scope)
        if datablock_key in self.datablocks:
            return  # already recorded

        self.datablocks[datablock_key] = DatablockMemoryUsage(datablock)

        if isinstance(datablock, bpy.types.Scene):
            self._record_scene_dependencies(datablock)
        elif isinstance(datablock, bpy.types.World):
            self._record_world_dependencies(datablock)
        elif isinstance(datablock, bpy.types.Collection):
            self._record_collection_dependencies(datablock)
        elif isinstance(datablock, bpy.types.Object):
            self._record_object_dependencies(datablock)
        elif isinstance(datablock, bpy.types.Camera):
            pass
        elif isinstance(datablock, bpy.types.Light):
            pass
        elif isinstance(datablock, bpy.types.Mesh):
            pass  # meshes don't depend on anything
        elif isinstance(datablock, bpy.types.Curve):
            pass  # meshes don't depend on anything
        elif isinstance(datablock, bpy.types.Material):
            self._record_material_dependencies(datablock)
        elif isinstance(datablock, bpy.types.NodeTree):  # TODO: or only ShaderNodeTree?
            self._record_node_tree_dependencies(datablock, scope)
        elif isinstance(datablock, bpy.types.ShaderNodeTexImage):
            self._record_shader_node_tex_image_dependencies(datablock)
        elif isinstance(datablock, bpy.types.ShaderNodeTexEnvironment):
            self._record_shader_node_tex_environment_dependencies(datablock)
        elif isinstance(datablock, bpy.types.Image):
            pass  # images don't depend on anything
        elif isinstance(datablock, bpy.types.Armature):
            pass  # TODO: Support armatures, armatures are ligthweight
        elif isinstance(datablock, bpy.types.ShaderNodeGroup):
            self._record_shader_node_group_dependencies(datablock)
        else:
            pass

    def _record_scene_dependencies(self, scene: bpy.types.Scene) -> None:
        if scene.world is not None:
            self.record_datablock(scene.world)
            self.record_dependency(scene, scene.world)

        self.record_datablock(scene.collection)
        self.record_dependency(scene, scene.collection)

    def _record_world_dependencies(self, world: bpy.types.World) -> None:
        if world.use_nodes:
            self.record_datablock(world.node_tree, self._datablock_key(world))
            self.record_dependency(world, world.node_tree)

    def _record_collection_dependencies(self, collection: bpy.types.Collection) -> None:
        for obj in collection.objects:
            if obj.hide_render:
                continue  # skip hidden objects

            self.record_datablock(obj)
            self.record_dependency(collection, obj)

        for child_collection in collection.children:
            if child_collection.hide_render:
                continue  # skip hidden collections

            self.record_datablock(child_collection)
            self.record_dependency(collection, child_collection)

    def _record_object_dependencies(self, obj: bpy.types.Object) -> None:
        if obj.data is not None:
            self.record_datablock(obj.data)
            self.record_dependency(obj, obj.data)
        if obj.instance_type == "COLLECTION":
            self.record_datablock(obj.instance_collection)
            self.record_dependency(obj, obj.instance_collection)

        for material_slot in obj.material_slots:
            if material_slot.material is not None:
                self.record_datablock(material_slot.material)
                self.record_dependency(obj, material_slot.material)

        for child_object in obj.children:  # TODO: this takes O(len(bpy.data.objects))!
            self.record_datablock(child_object)
            self.record_dependency(obj, child_object)
            self._record_object_dependencies(child_object)

    def _record_material_dependencies(self, material: bpy.types.Object) -> None:
        if not material.use_nodes:
            return

        if material.node_tree is not None:
            self.record_datablock(material.node_tree, self._datablock_key(material))
            self.record_dependency(material, material.node_tree)

    def _record_node_tree_dependencies(self, node_tree: bpy.types.NodeTree, scope: str = "") -> None:
        for node in node_tree.nodes:
            if isinstance(node, bpy.types.ShaderNodeTexImage):
                self.record_datablock(node, scope)
                self.record_dependency(node_tree, node)
                self._record_shader_node_tex_image_dependencies(node)
            elif isinstance(node, bpy.types.ShaderNodeTexEnvironment):
                self.record_datablock(node, scope)
                self.record_dependency(node_tree, node)
                self._record_shader_node_tex_environment_dependencies(node)
            elif isinstance(node, bpy.types.ShaderNodeGroup):
                self.record_datablock(node, scope)
                self.record_dependency(node_tree, node)
            else:
                # TODO: Tons of nodes we don't support yet
                pass

    def _record_shader_node_tex_image_dependencies(self, node: bpy.types.ShaderNodeTexImage) -> None:
        if node.image is not None:
            self.record_datablock(node.image)
            self.record_dependency(node, node.image)

    def _record_shader_node_tex_environment_dependencies(self, node: bpy.types.ShaderNodeTexEnvironment) -> None:
        if node.image is not None:
            self.record_datablock(node.image)
            self.record_dependency(node, node.image)

    def _record_shader_node_group_dependencies(self, node: bpy.types.ShaderNodeGroup) -> None:
        if node.node_tree is not None:
            self.record_datablock(node.node_tree, scope="bpy.data.node_groups")
            self.record_dependency(node, node.node_tree)


def xdg_open_file(path):
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.call(["open", path])
    else:
        subprocess.call(["xdg-open", path])


class EstimateMemoryUsage(bpy.types.Operator):
    bl_idname = "pie.estimate_memory_usage"
    bl_label = "Estimate Memory Usage (Beta)"
    bl_description = (
        "Goes through datablocks that would have to be loaded for rendering, "
        "estimates how much memory is needed for each one"
    )
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context):
        stats = MemoryUsageStatistics()
        stats.record_datablock(context.scene)

        out_file = tempfile.NamedTemporaryFile(mode="w", prefix="memory_usage_", suffix=".html", delete=False)
        stats.write_to_file(out_file)
        xdg_open_file(out_file.name)

        # print(list(MODULE_CLASSES))
        return {"FINISHED"}


MODULE_CLASSES.append(EstimateMemoryUsage)


def register():
    for cls in MODULE_CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(MODULE_CLASSES):
        bpy.utils.unregister_class(cls)
