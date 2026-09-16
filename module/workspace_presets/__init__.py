from pathlib import Path

import bpy
from bpy.types import Operator

PRESET_DIRECTORY = Path(__file__).resolve().parents[2] / "assets" / "blends" / "workspace"
BASE_PRESET = PRESET_DIRECTORY / "workspace_base.blend"
CUSTOM_PRESET = PRESET_DIRECTORY / "workspace_custom.blend"

WORKSPACE_NAMES = (
    "0-LIB",
    "1-MOD",
    "2-GN",
    "3-MAT",
    "4-UV",
    "5-MOTION",
    "6-RENDER",
    "7-COMPO",
    "8-SETTING",
)


class PIE_WorkspaceSwapOperator(Operator):
    """Swap workspaces with this operator"""

    bl_idname = "pie.workspaceswapper"
    bl_label = "Swap Workspace"
    bl_options = {"REGISTER", "UNDO"}

    target_workspace: bpy.props.StringProperty(name="Target Workspace")  # type: ignore
    default_workspace: bpy.props.StringProperty(name="Default Workspcae", default="Layout")  # type: ignore

    def execute(self, context):
        t_name = self.target_workspace
        d_spaces = bpy.data.workspaces

        path = str(BASE_PRESET)

        if context.workspace.name == t_name:
            self.report({"INFO"}, "已经为该工作空间！")
            return {"CANCELLED"}

        if t_name in d_spaces:
            context.window.workspace = d_spaces[t_name]
            self.report({"INFO"}, f'已切换工作空间:"{t_name}"')
            return {"FINISHED"}

        if t_name not in d_spaces:
            bpy.ops.workspace.append_activate(idname=t_name, filepath=path)
            context.window.workspace = d_spaces[t_name]
            self.report({"INFO"}, f'已添加工作空间:"{t_name}"')

            return {"FINISHED"}


class PIE_Workspace_Import_Online_Operator(Operator):
    """Import missing custom workspaces into the current file."""

    bl_idname = "pie.workspace_online_batch_import"
    bl_label = "Import Workspaces"
    bl_options = {"REGISTER", "UNDO"}

    target_workspace: bpy.props.StringProperty(name="Target Workspace")  # type: ignore

    def execute(self, context):
        d_spaces = bpy.data.workspaces
        added = 0
        for name in WORKSPACE_NAMES:
            if name in d_spaces:
                continue
            bpy.ops.workspace.append_activate(idname=name, filepath=str(CUSTOM_PRESET))
            context.window.workspace = d_spaces[name]
            added += 1
        self.report({"INFO"}, f"已添加 {added} 个工作空间")
        return {"FINISHED"}
