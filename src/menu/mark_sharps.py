import bpy
from ..operator import mark_sharps
from ..lib import addon

if "_LOADED" in locals():
    import importlib

    for mod in (mark_sharps,):  # list all imports here
        importlib.reload(mod)
_LOADED = True


class mark_sharps_MT_MarkSharps(addon.SimpleMenu):
    bl_idname = "mark_sharps_MT_mark_sharps"
    bl_label = "Mark Sharps"
    items = [
        (mark_sharps.mesh_OT_mark_sharps_file, "EXEC_DEFAULT", "All Meshes in File"),
        (mark_sharps.mesh_OT_mark_sharps_selected, "EXEC_DEFAULT", "Selected Object(s)")
    ]

REGISTER_CLASSES = [mark_sharps_MT_MarkSharps]
