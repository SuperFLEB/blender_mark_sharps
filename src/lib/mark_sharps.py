import bmesh
from enum import Enum
from math import pi
from bpy.types import Mesh


class RetainStrategy(Enum):
    CLEAR_ALL = 0
    RETAIN_SHARP = 1
    RETAIN_SMOOTH = 2


def mark_auto_smooth(mesh: Mesh, angle: float = None, retain: RetainStrategy = RetainStrategy.CLEAR_ALL,
                     include_single_edges: bool = True, crank_auto_smooth: bool = False) -> None:
    if not mesh.use_auto_smooth:
        return

    if angle is None:
        angle = mesh.auto_smooth_angle

    bm = bmesh.new()
    bm.from_mesh(mesh)
    for edge in bm.edges:
        if retain == RetainStrategy.CLEAR_ALL or \
                (retain == RetainStrategy.RETAIN_SMOOTH and not edge.smooth) or \
                (retain == RetainStrategy.RETAIN_SHARP and edge.smooth):
            edge_angle = edge.calc_face_angle(-1)
            if edge_angle == -1 and include_single_edges:
                edge.smooth = False
                continue
            edge.smooth = True if edge_angle == -1 else (edge_angle <= angle)

    bm.to_mesh(mesh)
    mesh.update()

    if crank_auto_smooth:
        mesh.auto_smooth_angle = pi
