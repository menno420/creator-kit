# Menno Creator Kit

A small reusable starting point for physical ideas in **FreeCAD** and spatial
experiments in **Godot**. It is intentionally understandable without coding.

## The 30-second version

### Use the FreeCAD shapes

1. Double-click `freecad\Open FreeCAD Library.cmd`.
2. Select one of the eight named parts in the tree.
3. Press **G**, move the mouse, and click to place it. Shift moves vertically;
   Ctrl snaps to 1 mm; Escape cancels.

### Change a shape

1. Open `freecad\dimensions.txt`.
2. Change a number and save.
3. Close FreeCAD if it is open.
4. Double-click `freecad\Rebuild FreeCAD Library.cmd`.

The rebuild regenerates the editable model, each STEP/STL export and the
correctly scaled meshes used by Godot. Positions you dragged in FreeCAD are
remembered.

### Use the Godot workbench

1. Double-click `godot\Open Creator Workbench.cmd`.
2. Choose an object in the left panel.
3. Use **G** to move, **R** to rotate, `+`/`-` to resize, or the visible buttons.
4. Middle-drag or Alt + left-drag to orbit; use the mouse wheel to zoom.

`godot\Edit Creator Workbench.cmd` opens the same project in Godot's editor
when you want to extend the scene itself.

## What is included

- Rounded box
- Open-ended tube
- Ring / collar
- Open tray
- L-bracket
- Raised handle
- Headed pin
- Hole-size test gauge

All FreeCAD measurements are millimetres. The Godot bridge converts them to
metres, so the objects arrive at real-world scale: **1 Godot unit = 1 metre**.

## Where the truth lives

- `freecad\dimensions.txt` — the measurements you normally edit.
- `freecad\src\` — the repeatable generator and verifier.
- `freecad\cad\creator-shapes.FCStd` — the visual-state master. Keep it: a
  rebuild recreates its geometry while preserving the positions and camera view
  you saved in FreeCAD.
- `freecad\exports\` and `godot\assets\freecad\` — generated outputs; a
  rebuild can recreate them.
- `godot\scenes\workbench.tscn` and `godot\scripts\workbench.gd` — the reusable
  Godot workbench.

Nothing runs in the background. Rebuilding and checking happen only when you
start them.
