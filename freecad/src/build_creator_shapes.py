"""Build the reusable FreeCAD shapes and Godot-ready meshes.

The plain-text dimensions file is the design source. The generated FCStd,
STEP, STL, OBJ and JSON files are outputs and can always be rebuilt.
"""

import json
import re
import sys
import traceback
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import FreeCAD as App
import Mesh
import Part


SRC = Path(__file__).resolve().parent
FREECAD_DIR = SRC.parent
ROOT = FREECAD_DIR.parent
CAD_DIR = FREECAD_DIR / "cad"
EXPORT_DIR = FREECAD_DIR / "exports"
GODOT_ASSET_DIR = ROOT / "godot" / "assets" / "freecad"
DIMENSIONS_PATH = FREECAD_DIR / "dimensions.txt"
FCSTD_PATH = CAD_DIR / "creator-shapes.FCStd"
GUI_TEMPLATE_DIR = SRC / "gui-template"


COLORS = {
    "RoundedBox": (0.22, 0.56, 0.91),
    "Tube": (0.18, 0.72, 0.64),
    "Ring": (0.96, 0.63, 0.22),
    "Tray": (0.54, 0.40, 0.82),
    "Bracket": (0.91, 0.35, 0.38),
    "Handle": (0.30, 0.72, 0.34),
    "Pin": (0.38, 0.45, 0.55),
    "HoleGauge": (0.92, 0.48, 0.72),
}


def load_dimensions(path):
    values = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if "=" not in line:
            raise ValueError(f"Line {line_number} needs name = number")
        name, text = (part.strip() for part in line.split("=", 1))
        if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ValueError(f"Invalid dimension name on line {line_number}: {name}")
        values[name] = float(text)
    return values


def need(values, *names):
    missing = [name for name in names if name not in values]
    if missing:
        raise ValueError("Missing dimensions: " + ", ".join(missing))


def rounded_box(length, width, height, radius, origin=None):
    origin = origin or App.Vector(0, 0, 0)
    if min(length, width, height) <= 0:
        raise ValueError("Rounded-box dimensions must be positive")
    radius = min(radius, length / 2.0, width / 2.0)
    if radius <= 0:
        return Part.makeBox(length, width, height, origin)
    x, y, z = origin.x, origin.y, origin.z
    shape = Part.makeBox(length - 2 * radius, width, height, App.Vector(x + radius, y, z))
    shape = shape.fuse(
        Part.makeBox(length, width - 2 * radius, height, App.Vector(x, y + radius, z))
    )
    for cx in (x + radius, x + length - radius):
        for cy in (y + radius, y + width - radius):
            shape = shape.fuse(Part.makeCylinder(radius, height, App.Vector(cx, cy, z)))
    return shape.removeSplitter()


def tube_shape(outer_diameter, inner_diameter, length):
    if not 0 < inner_diameter < outer_diameter:
        raise ValueError("Tube inner diameter must be between zero and outer diameter")
    outer = Part.makeCylinder(
        outer_diameter / 2.0, length, App.Vector(0, 0, outer_diameter / 2.0), App.Vector(1, 0, 0)
    )
    inner = Part.makeCylinder(
        inner_diameter / 2.0, length, App.Vector(0, 0, outer_diameter / 2.0), App.Vector(1, 0, 0)
    )
    return outer.cut(inner)


def ring_shape(outer_diameter, inner_diameter, height):
    if not 0 < inner_diameter < outer_diameter:
        raise ValueError("Ring inner diameter must be between zero and outer diameter")
    return Part.makeCylinder(outer_diameter / 2.0, height).cut(
        Part.makeCylinder(inner_diameter / 2.0, height)
    )


def tray_shape(length, width, height, wall, floor, radius):
    if wall * 2 >= min(length, width) or floor >= height:
        raise ValueError("Tray wall/floor dimensions leave no usable interior")
    outer = rounded_box(length, width, height, radius)
    inner_radius = max(0.5, radius - wall)
    inner = rounded_box(
        length - 2 * wall,
        width - 2 * wall,
        height - floor + 1.0,
        inner_radius,
        App.Vector(wall, wall, floor),
    )
    return outer.cut(inner)


def bracket_shape(length, depth, height, thickness):
    if thickness >= min(length, height):
        raise ValueError("Bracket thickness is too large")
    base = Part.makeBox(length, depth, thickness)
    upright = Part.makeBox(thickness, depth, height)
    return base.fuse(upright).removeSplitter()


def handle_shape(length, depth, grip_height, rise, post_width, radius):
    if post_width * 2 >= length or rise <= 0:
        raise ValueError("Handle posts leave no grip span")
    grip = rounded_box(
        length, depth, grip_height, radius, App.Vector(0, 0, rise)
    )
    left = rounded_box(
        post_width, depth, rise + 1.0, min(radius, post_width / 2.0)
    )
    right = rounded_box(
        post_width,
        depth,
        rise + 1.0,
        min(radius, post_width / 2.0),
        App.Vector(length - post_width, 0, 0),
    )
    return grip.fuse(left).fuse(right).removeSplitter()


def pin_shape(diameter, length, head_diameter, head_height):
    if head_diameter <= diameter or min(diameter, length, head_height) <= 0:
        raise ValueError("Pin needs a positive shaft and a wider head")
    shaft = Part.makeCylinder(diameter / 2.0, length)
    head = Part.makeCylinder(head_diameter / 2.0, head_height, App.Vector(0, 0, length))
    return shaft.fuse(head).removeSplitter()


def hole_gauge_shape(length, width, height, radius, holes):
    plate = rounded_box(length, width, height, radius)
    spacing = length / (len(holes) + 1)
    result = plate
    for index, diameter in enumerate(holes, 1):
        if diameter <= 0 or diameter >= width - 2:
            raise ValueError(f"Gauge hole {diameter} mm does not fit the plate")
        cutter = Part.makeCylinder(
            diameter / 2.0,
            height + 2.0,
            App.Vector(spacing * index, width / 2.0, -1.0),
        )
        result = result.cut(cutter)
    return result


def shape_specs(d):
    required = (
        "rounded_box_length", "rounded_box_width", "rounded_box_height", "rounded_box_radius",
        "tube_outer_diameter", "tube_inner_diameter", "tube_length",
        "ring_outer_diameter", "ring_inner_diameter", "ring_height",
        "tray_length", "tray_width", "tray_height", "tray_wall", "tray_floor", "tray_radius",
        "bracket_length", "bracket_depth", "bracket_height", "bracket_thickness",
        "handle_length", "handle_depth", "handle_grip_height", "handle_rise",
        "handle_post_width", "handle_radius", "pin_diameter", "pin_length",
        "pin_head_diameter", "pin_head_height", "gauge_length", "gauge_width",
        "gauge_height", "gauge_radius", "gauge_hole_1", "gauge_hole_2",
        "gauge_hole_3", "gauge_hole_4",
    )
    need(d, *required)
    return [
        {
            "id": "RoundedBox", "label": "Rounded Box", "category": "Container",
            "shape": rounded_box(d["rounded_box_length"], d["rounded_box_width"], d["rounded_box_height"], d["rounded_box_radius"]),
            "dimensions": f'{d["rounded_box_length"]:g} x {d["rounded_box_width"]:g} x {d["rounded_box_height"]:g} mm',
            "stage": (0, 0, 0),
        },
        {
            "id": "Tube", "label": "Tube", "category": "Connector",
            "shape": tube_shape(d["tube_outer_diameter"], d["tube_inner_diameter"], d["tube_length"]),
            "dimensions": f'OD {d["tube_outer_diameter"]:g}, ID {d["tube_inner_diameter"]:g}, L {d["tube_length"]:g} mm',
            "stage": (100, 0, 0),
        },
        {
            "id": "Ring", "label": "Ring / Collar", "category": "Connector",
            "shape": ring_shape(d["ring_outer_diameter"], d["ring_inner_diameter"], d["ring_height"]),
            "dimensions": f'OD {d["ring_outer_diameter"]:g}, ID {d["ring_inner_diameter"]:g}, H {d["ring_height"]:g} mm',
            "stage": (190, 20, 0),
        },
        {
            "id": "Tray", "label": "Open Tray", "category": "Container",
            "shape": tray_shape(d["tray_length"], d["tray_width"], d["tray_height"], d["tray_wall"], d["tray_floor"], d["tray_radius"]),
            "dimensions": f'{d["tray_length"]:g} x {d["tray_width"]:g} x {d["tray_height"]:g} mm; wall {d["tray_wall"]:g}',
            "stage": (270, 0, 0),
        },
        {
            "id": "Bracket", "label": "L-Bracket", "category": "Support",
            "shape": bracket_shape(d["bracket_length"], d["bracket_depth"], d["bracket_height"], d["bracket_thickness"]),
            "dimensions": f'{d["bracket_length"]:g} x {d["bracket_depth"]:g} x {d["bracket_height"]:g} mm; {d["bracket_thickness"]:g} thick',
            "stage": (0, 100, 0),
        },
        {
            "id": "Handle", "label": "Raised Handle", "category": "Grip",
            "shape": handle_shape(d["handle_length"], d["handle_depth"], d["handle_grip_height"], d["handle_rise"], d["handle_post_width"], d["handle_radius"]),
            "dimensions": f'{d["handle_length"]:g} x {d["handle_depth"]:g}; rise {d["handle_rise"]:g} mm',
            "stage": (100, 100, 0),
        },
        {
            "id": "Pin", "label": "Headed Pin", "category": "Connector",
            "shape": pin_shape(d["pin_diameter"], d["pin_length"], d["pin_head_diameter"], d["pin_head_height"]),
            "dimensions": f'shaft {d["pin_diameter"]:g} x {d["pin_length"]:g} mm; head {d["pin_head_diameter"]:g}',
            "stage": (210, 105, 0),
        },
        {
            "id": "HoleGauge", "label": "Hole-Size Gauge", "category": "Test piece",
            "shape": hole_gauge_shape(d["gauge_length"], d["gauge_width"], d["gauge_height"], d["gauge_radius"], [d[f"gauge_hole_{i}"] for i in range(1, 5)]),
            "dimensions": 'holes ' + ', '.join(f'{d[f"gauge_hole_{i}"]:g}' for i in range(1, 5)) + ' mm',
            "stage": (280, 105, 0),
        },
    ]


def remember_positions():
    if not FCSTD_PATH.exists():
        return {}
    doc = App.openDocument(str(FCSTD_PATH))
    positions = {}
    for obj in doc.Objects:
        if obj.TypeId == "Part::Feature" and obj.Name in COLORS:
            positions[obj.Name] = (
                (obj.Placement.Base.x, obj.Placement.Base.y, obj.Placement.Base.z),
                tuple(obj.Placement.Rotation.Q),
            )
    App.closeDocument(doc.Name)
    return positions


def _normalise_gui_document(data):
    """Keep the visual state but guarantee that every library shape is shown."""
    root = ET.fromstring(data)
    seen = set()
    for view_provider in root.findall(".//ViewProvider"):
        name = view_provider.get("name")
        if name not in COLORS:
            continue
        for prop in view_provider.findall(".//Property"):
            if prop.get("name") == "Visibility":
                value = prop.find("Bool")
                if value is not None:
                    value.set("value", "true")
                    seen.add(name)
    if seen != set(COLORS):
        missing = sorted(set(COLORS) - seen)
        raise RuntimeError("GUI state is missing view providers: " + ", ".join(missing))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def remember_gui_payload():
    """Preserve FreeCAD's view/camera state across a headless rebuild."""
    payload = {}
    if FCSTD_PATH.exists():
        with zipfile.ZipFile(FCSTD_PATH, "r") as archive:
            names = archive.namelist()
            if "GuiDocument.xml" in names:
                for name in names:
                    if name == "GuiDocument.xml" or (
                        name != "Document.xml"
                        and not name.endswith(".brp")
                        and not name.endswith(".Map.txt")
                    ):
                        payload[name] = archive.read(name)
    if not payload and GUI_TEMPLATE_DIR.exists():
        for path in GUI_TEMPLATE_DIR.iterdir():
            if path.is_file():
                payload[path.name] = path.read_bytes()
    if "GuiDocument.xml" in payload:
        payload["GuiDocument.xml"] = _normalise_gui_document(payload["GuiDocument.xml"])
    return payload


def restore_gui_payload(payload):
    if not payload:
        raise RuntimeError(
            "No FreeCAD GUI template exists. Open the generated FCStd once, "
            "show all eight shapes, fit the view and save it."
        )
    with zipfile.ZipFile(FCSTD_PATH, "a", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in payload.items():
            archive.writestr(name, data)


def placement_for(spec, remembered):
    if spec["id"] in remembered:
        base, quat = remembered[spec["id"]]
        return App.Placement(App.Vector(*base), App.Rotation(*quat))
    return App.Placement(App.Vector(*spec["stage"]), App.Rotation())


def add_text_property(obj, name, value):
    obj.addProperty("App::PropertyString", name, "Creator Kit")
    setattr(obj, name, value)


def export_shape(doc, spec, shape):
    stem = re.sub(r"(?<!^)(?=[A-Z])", "-", spec["id"]).lower()
    temp = doc.addObject("Part::Feature", f"Export{spec['id']}")
    temp.Shape = shape
    step_path = EXPORT_DIR / f"{stem}.step"
    Part.export([temp], str(step_path))
    normalize_step(step_path)
    Mesh.export([temp], str(EXPORT_DIR / f"{stem}.stl"))
    doc.removeObject(temp.Name)
    write_obj(shape, GODOT_ASSET_DIR / f"{stem}.obj", spec["label"])
    return stem


def normalize_step(path):
    """Keep FreeCAD's generated STEP text stable and whitespace-clean."""
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text(
        "\n".join(line.rstrip() for line in lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_obj(shape, path, label):
    vertices, triangles = shape.tessellate(0.20)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"# {label} — generated by Menno Creator Kit\n")
        handle.write("# Coordinates are metres; FreeCAD Z-up becomes Godot Y-up.\n")
        handle.write(f"o {re.sub(r'[^A-Za-z0-9_]', '_', label)}\n")
        for point in vertices:
            handle.write(f"v {point.x / 1000.0:.7f} {point.z / 1000.0:.7f} {-point.y / 1000.0:.7f}\n")
        for triangle in triangles:
            handle.write(f"f {triangle[0] + 1} {triangle[1] + 1} {triangle[2] + 1}\n")


def build():
    CAD_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    GODOT_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    sys.dont_write_bytecode = True

    dimensions = load_dimensions(DIMENSIONS_PATH)
    specs = shape_specs(dimensions)
    gui_payload = remember_gui_payload()
    remembered = remember_positions()

    if "CreatorShapes" in App.listDocuments():
        App.closeDocument("CreatorShapes")
    doc = App.newDocument("CreatorShapes", "Menno Creator Kit — FreeCAD Shapes")

    manifest = {"kit": "Menno Creator Kit", "units": "metres", "shapes": []}
    staged_shapes = []
    for spec in specs:
        shape = spec["shape"]
        if shape.isNull() or not shape.isValid() or len(shape.Solids) != 1:
            raise RuntimeError(f"{spec['label']} is not one valid solid")

        # A top-level Part::Feature is deliberate. FreeCAD gives these a
        # visible view provider when a headlessly generated FCStd is opened,
        # and the existing G macro moves the selected feature directly.
        feature = doc.addObject("Part::Feature", spec["id"])
        feature.Label = spec["label"]
        feature.Shape = shape
        feature.Placement = placement_for(spec, remembered)
        add_text_property(feature, "Category", spec["category"])
        add_text_property(feature, "Dimensions", spec["dimensions"])
        add_text_property(feature, "HowToMove", "Select this part, press G, move, click to drop. Shift = vertical; Ctrl = 1 mm snap.")
        try:
            feature.ViewObject.ShapeColor = COLORS[spec["id"]]
            feature.ViewObject.LineColor = (0.12, 0.14, 0.18)
        except AttributeError:
            # FreeCADCmd has no complete GUI view provider. Godot still gets
            # the intended colours from manifest.json.
            pass
        stem = export_shape(doc, spec, shape)
        bounds = shape.BoundBox
        manifest["shapes"].append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "category": spec["category"],
                "dimensions": spec["dimensions"],
                "file": f"{stem}.obj",
                "bounds_mm": [round(bounds.XLength, 3), round(bounds.YLength, 3), round(bounds.ZLength, 3)],
                "color": list(COLORS[spec["id"]]),
            }
        )
        placed = shape.copy()
        placed.Placement = App.Placement(App.Vector(*spec["stage"]), App.Rotation())
        staged_shapes.append(placed)

    showcase = Part.makeCompound(staged_shapes)
    showcase_obj = doc.addObject("Part::Feature", "ShowcaseExport")
    showcase_obj.Label = "Generated showcase export — hidden"
    showcase_obj.Shape = showcase
    try:
        showcase_obj.ViewObject.Visibility = False
    except AttributeError:
        pass
    showcase_step = EXPORT_DIR / "creator-shapes-showcase.step"
    Part.export([showcase_obj], str(showcase_step))
    normalize_step(showcase_step)
    Mesh.export([showcase_obj], str(EXPORT_DIR / "creator-shapes-showcase.stl"))
    doc.removeObject(showcase_obj.Name)

    doc.recompute()
    doc.saveAs(str(FCSTD_PATH))
    restore_gui_payload(gui_payload)
    (GODOT_ASSET_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Built {len(specs)} reusable shapes")
    print(f"FreeCAD library: {FCSTD_PATH}")
    print(f"Godot assets: {GODOT_ASSET_DIR}")
    print("CREATOR_KIT_FREECAD_BUILD_OK")


try:
    build()
except Exception:
    traceback.print_exc()
    print("CREATOR_KIT_FREECAD_BUILD_FAILED")
    sys.exit(1)
