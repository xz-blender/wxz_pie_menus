# SPDX-License-Identifier: GPL-3.0-or-later
"""A reversible edit over a snapshot of the selected mesh elements."""
from dataclasses import dataclass

import bmesh


def selection_domain(select_mode):
    # Vertex selection takes precedence in mixed modes.
    return "POINT" if select_mode[0] else "EDGE"


def attribute_name(kind, domain):
    if kind not in {"crease", "bevel_weight"} or domain not in {"POINT", "EDGE"}:
        raise ValueError("不支持的属性或网格域")
    return f"{kind}_{'vert' if domain == 'POINT' else 'edge'}"


@dataclass
class MeshSnapshot:
    mesh: object
    bm: object
    indices: list
    originals: list
    existed: bool
    targets: tuple = ()


class WeightEdit:
    def __init__(self, context, kind):
        self.domain = selection_domain(context.tool_settings.mesh_select_mode)
        self.name = attribute_name(kind, self.domain)
        self.snapshots = []
        self.changed = False
        self._last_value = None
        seen = set()
        for obj in context.objects_in_mode_unique_data:
            if obj.type != "MESH" or obj.data.as_pointer() in seen:
                continue
            mesh = obj.data
            seen.add(mesh.as_pointer())
            bm = bmesh.from_edit_mesh(mesh)
            sequence = bm.verts if self.domain == "POINT" else bm.edges
            layer = sequence.layers.float.get(self.name)
            indices = []
            values = []
            if layer is None:
                indices = [index for index, element in enumerate(sequence) if element.select and not element.hide]
                values = [0.0] * len(indices)
            else:
                for index, element in enumerate(sequence):
                    if element.select and not element.hide:
                        indices.append(index)
                        values.append(element[layer])
            if not indices:
                continue
            attribute = mesh.attributes.get(self.name)
            if attribute and (attribute.domain != self.domain or attribute.data_type != "FLOAT"):
                raise ValueError(f"{obj.name}: {self.name} 已存在，但不是正确域的浮点属性")
            # Creating the first custom-data layer can invalidate BMVert/BMEdge
            # wrappers. Keep stable indices; this modal tool never edits topology.
            self.snapshots.append(MeshSnapshot(mesh, bm, indices, values, layer is not None))
        if not self.snapshots:
            raise ValueError("请先选择顶点或边")
        self.count = sum(len(snapshot.indices) for snapshot in self.snapshots)
        self.initial_value = sum(sum(snapshot.originals) for snapshot in self.snapshots) / self.count

    def valid(self):
        try:
            return all(snapshot.mesh.is_editmode and snapshot.bm.is_valid for snapshot in self.snapshots)
        except ReferenceError:
            return False

    def _elements(self, snapshot):
        sequence = snapshot.bm.verts if self.domain == "POINT" else snapshot.bm.edges
        sequence.ensure_lookup_table()
        return sequence

    @staticmethod
    def _update(snapshot):
        bmesh.update_edit_mesh(snapshot.mesh, loop_triangles=False, destructive=False)

    def apply(self, value):
        if not self.valid():
            raise RuntimeError("网格已离开编辑模式")
        value = max(0.0, min(1.0, value))
        if value == self._last_value:
            return False
        # Mark before writing so partially completed updates can also be restored.
        self.changed = True
        for snapshot in self.snapshots:
            layers = self._elements(snapshot).layers.float
            layer = layers.get(self.name)
            if layer is None:
                layer = layers.new(self.name)
            # Bind only after layer creation. Adding custom data may invalidate
            # all element wrappers; refresh them if that happens between writes.
            if not snapshot.targets or not snapshot.targets[0].is_valid:
                elements = self._elements(snapshot)
                snapshot.targets = tuple(elements[index] for index in snapshot.indices)
            for element in snapshot.targets:
                element[layer] = value
            self._update(snapshot)
        self._last_value = value
        return True

    def restore(self):
        if not self.changed:
            return
        for snapshot in self.snapshots:
            try:
                if not snapshot.mesh.is_editmode or not snapshot.bm.is_valid:
                    continue
                elements = self._elements(snapshot)
                layers = elements.layers.float
                layer = layers.get(self.name)
                if layer is None:
                    continue
                if snapshot.existed:
                    for index, value in zip(snapshot.indices, snapshot.originals):
                        elements[index][layer] = value
                else:
                    layers.remove(layer)
                self._update(snapshot)
            except ReferenceError:
                continue
        self.changed = False
        self._last_value = None
        for snapshot in self.snapshots:
            snapshot.targets = ()
