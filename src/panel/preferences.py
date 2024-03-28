import bpy

from ..lib import pkginfo

if "_LOADED" in locals():
    import importlib

    for mod in (pkginfo,):  # list all imports here
        importlib.reload(mod)
_LOADED = True

package_name = pkginfo.package_name()


class PreferencesPanel(bpy.types.AddonPreferences):
    bl_idname = package_name

    def draw(self, context) -> None:
        layout = self.layout
        layout.label(text=f"Blender {bpy.app.version_string} is older than 4.1.x. The addon is loaded!",
                     icon="OUTLINER_OB_LIGHT")


REGISTER_CLASSES = [PreferencesPanel]
