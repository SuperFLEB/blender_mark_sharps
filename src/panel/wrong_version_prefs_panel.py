import bpy

from ..lib import pkginfo

if "_LOADED" in locals():
    import importlib

    importlib.reload(pkginfo)
_LOADED = True

package_name = pkginfo.package_name()


class WrongVersionPrefsPanel(bpy.types.AddonPreferences):
    bl_idname = package_name

    def draw(self, context) -> None:
        layout = self.layout
        layout.label(text="This addon is not compatible with Blender 4.1 or later. The addon has not been loaded.",
                     icon="ERROR")


REGISTER_CLASSES = [WrongVersionPrefsPanel]
