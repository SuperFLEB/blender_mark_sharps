from math import pi
from typing import Set
import bpy
from ..lib import mark_sharps as mark_sharps_lib, object as object_lib
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, FloatProperty

if "_LOADED" in locals():
    import importlib

    for mod in (mark_sharps_lib, object_lib,):  # list all imports here
        importlib.reload(mod)
_LOADED = True


class MarkSharpsBaseOperator(Operator):
    retain: EnumProperty(
        items=[
            ("CLEAR_ALL", "Clear Existing Sharp/Smooth", "Clear existing Sharp and Smooth edges"),
            ("RETAIN_SHARP", "Keep Edges Marked Sharp", "Keep existing Sharp marked edges"),
            ("RETAIN_SMOOTH", "Keep Edges Marked Smooth", "Keep existing Smooth marked edges"),
        ],
        name="Retain Strategy",
        default="CLEAR_ALL"
    )
    include_single_edges: BoolProperty(default=True, name="Include Single Edges")
    crank_auto_smooth: BoolProperty(default=False, name="Set Auto-smooth to 180°")
    override_angle: BoolProperty(default=False, name="Override Angle")
    override_angle_value: FloatProperty(default=pi/6, subtype="ANGLE",  min=0.0, max=pi, name="Angle")

    def _mark_mesh(self, mesh):
        mark_sharps_lib.mark_auto_smooth(
            mesh,
            angle=self.override_angle_value if self.override_angle else None,
            retain=mark_sharps_lib.RetainStrategy[self.retain],
            include_single_edges=self.include_single_edges,
            crank_auto_smooth=self.crank_auto_smooth
        )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "retain", text="")
        layout.prop(self, "include_single_edges")
        layout.prop(self, "crank_auto_smooth")
        layout.label(text="Override Auto-Smooth Angle:")
        row = layout.row()
        row.prop(self, "override_angle", text="")
        subrow = row.row(align=True)
        subrow.enabled = self.override_angle
        subrow.prop(self, "override_angle_value", text="")

class mesh_OT_mark_sharps_file(MarkSharpsBaseOperator):
    """Mark sharp edges created by the "Auto Smooth" option for all meshes in the file"""
    bl_idname = "mesh.mark_sharps_file"
    bl_label = "Mark Sharps in File"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context) -> Set[str]:
        for mesh in bpy.data.meshes:
            self._mark_mesh(mesh)
        return {'FINISHED'}


class mesh_OT_mark_sharps_selected(MarkSharpsBaseOperator):
    """Mark sharp edges created by the "Auto Smooth" option for the selected mesh object"""
    bl_idname = "mesh.mark_sharps_selected"
    bl_label = "Mark Sharps on Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    include_children: BoolProperty(default=True, name="Include Collection Contents/Instanced Children", description="Include instanced children and Collection Instance contents")

    @classmethod
    def poll(cls, context) -> bool:
        if len(bpy.context.selected_objects) == 0:
            cls.poll_message_set("No objects selected")
            return False
        if object_lib.may_have_meshes(bpy.context.selected_objects):
            return True
        cls.poll_message_set("No selected objects contain mesh data")
        return False

    def draw(self, context) -> None:
        layout = self.layout
        layout.prop(self, "include_children")
        layout.separator()
        super().draw(context)

    def execute(self, context) -> Set[str]:
        if self.include_children:
            meshes = object_lib.get_meshes_multiple(bpy.context.selected_objects)
        else:
            meshes = object_lib.get_meshes_shallow(bpy.context.selected_objects)

        for mesh in meshes:
            self._mark_mesh(mesh)
        return {'FINISHED'}


REGISTER_CLASSES = [mesh_OT_mark_sharps_file, mesh_OT_mark_sharps_selected]
