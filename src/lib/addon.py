import bpy
from bpy.types import Operator, Menu
from typing import Callable, Type
from types import ModuleType

from hashlib import md5

"""
This library contains helper functions useful in setup and management of Blender addons.
It is required by the __init__.py, so don't remove it unless you fix dependencies.
"""

def _collate_registerable(registerable_modules: list[ModuleType], attribute: str) -> list[Type] | list[Callable]:
    # Classes grouped by module
    mod_items = [getattr(mod, attribute) for mod in registerable_modules if hasattr(mod, attribute)]
    # Flatten (comprehension) and deduplicate (list(dict.fromkeys()))
    return list(dict.fromkeys([c for mc in mod_items for c in mc]))

class SimpleMenu(Menu):
    # If the menu item needs its own operator context, use a tuple of (OperatorClass, "context")
    items: list[Operator | Menu | str | None | tuple[Operator, str]] = []

    @staticmethod
    def _verify_tuple(item: tuple[Operator, str] | tuple[Operator, str, str]) -> bool:
        if len(item) < 2:
            return False
        if len(item) > 3:
            return False
        if not issubclass(item[0], Operator):
            return False
        if type(item[1]) is not str:
            return False
        if len(item) == 2:
            # Optional name was not given and does not need to be verified
            return True
        if type(item[2]) is not str:
            return False
        return True

    operator_context: str = "INVOKE_REGION_WIN"
    def draw(self, context) -> None:
        self.layout.operator_context = self.operator_context

        for item in self.items:
            layout = self.layout
            layout.operator_context = self.operator_context

            if item is None:
                layout.separator()
                continue
            if type(item) is str:
                layout.label(text=item)
                continue

            item_text = None

            if type(item) is tuple:
                if self._verify_tuple(item):
                    layout = layout.column()
                    layout.operator_context = item[1]
                    if len(item) >= 3:
                        item_text = item[2]
                    item = item[0]
                else:
                    print("(!) Bad tuple in SimpleMenu: ", item)

            if (not hasattr(item, 'can_show')) or item.can_show(context):
                if issubclass(item, bpy.types.Menu):
                    layout.menu(item.bl_idname, text=item_text)
                    continue
                if issubclass(item, bpy.types.Operator):
                    layout.operator(item.bl_idname, text=item_text)
                    continue

            print("(!) Unknown menu item type in SimpleMenu: ", item)




def menuitem(cls: bpy.types.Operator | bpy.types.Menu | Callable, operator_context: str = "EXEC_DEFAULT") -> Callable:
    # Operator
    if issubclass(cls, bpy.types.Operator):
        def operator_fn(self, context):
            self.layout.operator_context = operator_context
            if (not hasattr(cls, 'can_show')) or cls.can_show(context):
                self.layout.operator(cls.bl_idname)

        return operator_fn

    # Submenu
    if issubclass(cls, bpy.types.Menu):
        def submenu_fn(self, context):
            self.layout.menu(cls.bl_idname)
        return submenu_fn

    # Custom draw function
    if callable(cls):
        return cls

    raise Exception(f"Mark Sharps: Unknown menu type for menu {cls}. The developer screwed up.")


def warn_unregisterable(registerable_modules: list[ModuleType]) -> None:
    def can_register(mod: ModuleType) -> bool:
        return hasattr(mod, "REGISTER_CLASSES")
    unregisterable = [mod for mod in registerable_modules if not can_register(mod)]
    if unregisterable:
        print("Mark Sharps: Some modules had nothing to register:")
        print("\n".join([f" - {mod}" for mod in unregisterable]))


def register_classes(registerable_modules: list[ModuleType], register: bool = True) -> None:
    """
    Register or unregister classes specified in modules' REGISTER_CLASSES attributes
    :param registerable_modules: List of modules to register or unregister
    :param register: Whether to register (True) or unregister (False)
    """

    classes = _collate_registerable(registerable_modules, "REGISTER_CLASSES")
    # Reverse order when unregistering
    classes = classes if register else classes[::-1]

    for cls in classes:
        # Always unregister. If we're registering, this ensures clean-up after a prior registration failure.
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            if not register:
                print("(!) Mark Sharps failed to unregister class:", cls)

        if register:
            bpy.utils.register_class(cls)
            if hasattr(cls, 'post_register') and callable(cls.post_register):
                cls.post_register()
            print("Mark Sharps registered class:", cls)
        else:
            if hasattr(cls, 'post_unregister') and callable(cls.post_unregister):
                cls.post_unregister()
            print("Mark Sharps unregistered class:", cls)


def unregister_classes(registerable_modules: list[ModuleType]) -> None:
    """
    Unregister classes specified in modules' REGISTER_CLASSES attributes
    (an alias for register_classes(registerable_modules, False))
    :param registerable_modules:
    :return:
    """
    register_classes(registerable_modules, False)

def register_menus(menus: list[tuple[str, Callable]]):
    for m in menus:
        if not callable(m[1]):
            print(f"(!) Mark Sharps: {m[1]} must be a draw function (callable) to append to menu/panel {m[0]}")
            continue
        getattr(bpy.types, m[0]).append(m[1])


def unregister_menus(menus: list[tuple[str, Callable]]):
    for m in menus[::-1]:
        getattr(bpy.types, m[0]).remove(m[1])
