from typing import Callable
import bpy
from .lib import addon
from .operator import mark_sharps as mark_sharps_operator
from .menu import mark_sharps as mark_sharps_menu
from .panel import preferences as preferences_panel, wrong_version_prefs_panel

if "_LOADED" in locals():
    import importlib

    for mod in (addon, mark_sharps_operator, mark_sharps_menu, preferences_panel, wrong_version_prefs_panel):
        importlib.reload(mod)

_LOADED = True

package_name = __package__

# Supports 3.x or 4.0 only, nothing past 4.0
is_supported_blender_version = bpy.app.version[0] <= 3 or (bpy.app.version[0] == 4 and bpy.app.version[1] == 0)

bl_info = {
    "name": "Mark Sharps",
    "description": "Mark sharp edges created by the \"Auto Smooth\" option",
    "author": "FLEB (a.k.a. SuperFLEB)",
    "version": (0, 1, 1),
    "blender": (3, 6, 0),
    "location": "View3D > Object",
    "warning": "For use in Blender 3.x/4.0 only. It will not be loaded in newer versions.",
    "doc_url": "https://github.com/SuperFLEB/blender_mark_sharps",
    "tracker_url": "https://github.com/SuperFLEB/blender_mark_sharps/issues",
    "support": "COMMUNITY",
    "category": "Mesh",
}

# This can be used to register menus (MT) or header items (HT)
menus: list[tuple[str, Callable]] = [
    ("VIEW3D_MT_editor_menus", addon.menuitem(mark_sharps_menu.mark_sharps_MT_MarkSharps)),
    ("VIEW3D_MT_object_context_menu", addon.menuitem(mark_sharps_operator.mesh_OT_mark_sharps_selected))
]

registerable_modules = [
    mark_sharps_operator,
    mark_sharps_menu,
    preferences_panel,
]


def register() -> None:
    if not is_supported_blender_version:
        print("Mark Sharps: This Blender version is too new for this addon. Skipping registration except prefs panel.")
        addon.register_classes([wrong_version_prefs_panel])
        return
    addon.warn_unregisterable(registerable_modules)
    addon.register_classes(registerable_modules)
    addon.register_menus(menus)


def unregister() -> None:
    if not is_supported_blender_version:
        print("Mark Sharps: This Blender version is too new for this addon, so only the prefs panel was registered. ",
              "Unregistering prefs panel.")
        addon.unregister_classes([wrong_version_prefs_panel])
        return
    addon.unregister_menus(menus)
    addon.unregister_classes(registerable_modules)


if __name__ == "__main__":
    register()
