from typing import Iterable
from bpy.types import Mesh, Object


def may_have_meshes(objs: Iterable[Object]) -> bool:
    """Returns whether the object is of the type that may be instance meshes. Will return a false positive (True) in
    cases such as a Collection Instance of only non-mesh objects, e.g. lights, but it should be good enough to use in a
    poll method."""

    for obj in objs:
        if isinstance(obj.data, Mesh):
            return True
        if obj.instance_type != "NONE":
            return True
    return False


def get_meshes(obj: Object, found: set[Mesh] = None) -> set[Mesh]:
    """Get a set of meshes in the given object, as well as its instanced children and collection contents. Does not
    return meshes from children of a parent-child relationship if they are not instanced."""

    if found is None:
        found = set()

    if obj.instance_type == "NONE":
        pass
    elif obj.instance_type == "COLLECTION":
        for coll_obj in obj.instance_collection.objects:
            get_meshes(coll_obj, found)
    else:
        for inst_obj in obj.children:
            get_meshes(inst_obj, found)

    if isinstance(obj.data, Mesh):
        found.add(obj.data)

    return found


def get_meshes_multiple(objs: Iterable[Object], found: set[Mesh] = None) -> set[Mesh]:
    """Get a set of meshes in the given objects, as well as their instanced children and collection contents. Does not
    return meshes from children of a parent-child relationship if they are not instanced."""
    if found is None:
        found = set()
    for obj in objs:
        get_meshes(obj, found)
    return found


def get_meshes_shallow(objs: Iterable[Object], found: set[Mesh] = None) -> set[Mesh]:
    """Get a set of meshes from the given objects, not traversing into instanced children or collections"""
    return {obj.data for obj in objs if isinstance(obj.data, Mesh)} | (found or set())

