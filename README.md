# Mark Sharps

https://github.com/SuperFLEB/blender_mark_sharps

Blender 4.1 and later removes the "Auto Smooth" feature, replacing it with either the "Smooth By Angle" modifier or
the "Shade Smooth By Angle" function that marks edges Sharp by angle. This can present a problem when importing older
models that used the Auto Smooth from previous Blender versions, because the automatically-set sharp edges are not
imported and any "Auto Smooth" objects are shaded entirely smooth (save for manually-Sharp-marked edges).

This addon functions as a converter or full-file processor, to "apply" the Auto Smooth setting to all affected meshes--
applying "Mark Sharp" and "Clear Sharp" accordingly-- so the result will look the same when importing into Blender 4.1.

This addon is meant to be run in Blender 3.x, and it is only meant for use in Blender 3.x and 4.0, as Blender 4.1 and
later lacks the Auto Smooth feature entirely, but has the "Shade Smooth By Angle" operation that does the same thing
this does. This addon will not operate in Blender versions 4.1 or later.

## Features

* **Mark Sharps on File** - Apply auto-smoothing to all meshes in the file.
* **Mark Sharps on Selected Objects** - Apply auto-smoothing to the mesh(es) associated with the selected object.
  * Includes the recursive contents of Collection Instances and instanced children (only instanced children, not all
    children)
  * ⚠️ Keep in mind that this works on the Mesh level, not the Object level. If other objects or scenes use the same
    meshes, they will be similarly updated in all instances.

## To install

Either install the ZIP file from the release, clone this repository and use the
build_release.py script to build a ZIP file that you can install into Blender.

## To use

Menu items are in two places in the 3D view in Object mode:

1. In a "Mark Sharps" menu at the top of the pane.
2. In a "Mark Sharps on Selected Objects" item in the Right-click/W context menu