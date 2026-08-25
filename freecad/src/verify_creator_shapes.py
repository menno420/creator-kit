"""Verify the Creator Kit's native model and every generated exchange file."""

import json
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
CAD = FREECAD_DIR / "cad" / "creator-shapes.FCStd"
EXPORTS = FREECAD_DIR / "exports"
GODOT_ASSETS = ROOT / "godot" / "assets" / "freecad"
EXPECTED = ("RoundedBox", "Tube", "Ring", "Tray", "Bracket", "Handle", "Pin", "HoleGauge")


def verify():
    doc = App.openDocument(str(CAD))
    for shape_id in EXPECTED:
        feature = doc.getObject(shape_id)
        if feature is None or feature.TypeId != "Part::Feature":
            raise RuntimeError(f"Missing independently movable Part::Feature: {shape_id}")
        if feature.Shape.isNull() or not feature.Shape.isValid() or len(feature.Shape.Solids) != 1:
            raise RuntimeError(f"{shape_id} is not one valid solid")
        if "press G" not in feature.HowToMove:
            raise RuntimeError(f"{shape_id} is missing its direct-move instruction")

    manifest = json.loads((GODOT_ASSETS / "manifest.json").read_text(encoding="utf-8"))
    if len(manifest.get("shapes", [])) != len(EXPECTED):
        raise RuntimeError("Godot manifest does not list all eight shapes")

    facet_total = 0
    for entry in manifest["shapes"]:
        shape_id = entry["id"]
        if shape_id not in EXPECTED:
            raise RuntimeError(f"Unexpected manifest shape: {shape_id}")
        stem = Path(entry["file"]).stem
        step_path = EXPORTS / f"{stem}.step"
        stl_path = EXPORTS / f"{stem}.stl"
        obj_path = GODOT_ASSETS / entry["file"]
        step_shape = Part.Shape()
        step_shape.read(str(step_path))
        if step_shape.isNull() or not step_shape.isValid() or len(step_shape.Solids) != 1:
            raise RuntimeError(f"Invalid STEP export: {step_path.name}")
        mesh = Mesh.Mesh(str(stl_path))
        if mesh.CountFacets <= 0:
            raise RuntimeError(f"Empty STL export: {stl_path.name}")
        facet_total += mesh.CountFacets
        text = obj_path.read_text(encoding="utf-8")
        if text.count("\nv ") < 4 or text.count("\nf ") < 4:
            raise RuntimeError(f"Empty Godot OBJ export: {obj_path.name}")
        if any(value <= 0 for value in entry["bounds_mm"]):
            raise RuntimeError(f"Invalid bounds for {shape_id}")

    showcase_step = Part.Shape()
    showcase_step.read(str(EXPORTS / "creator-shapes-showcase.step"))
    if showcase_step.isNull() or not showcase_step.isValid() or len(showcase_step.Solids) != 8:
        raise RuntimeError("Showcase STEP does not contain eight solids")
    showcase_mesh = Mesh.Mesh(str(EXPORTS / "creator-shapes-showcase.stl"))
    if showcase_mesh.CountFacets != facet_total:
        raise RuntimeError("Showcase STL facet total differs from individual shapes")

    with zipfile.ZipFile(CAD, "r") as archive:
        if "GuiDocument.xml" not in archive.namelist():
            raise RuntimeError("FreeCAD visual state is missing")
        gui_root = ET.fromstring(archive.read("GuiDocument.xml"))
    visible = set()
    for view_provider in gui_root.findall(".//ViewProvider"):
        shape_id = view_provider.get("name")
        for prop in view_provider.findall(".//Property"):
            value = prop.find("Bool")
            if (
                shape_id in EXPECTED
                and prop.get("name") == "Visibility"
                and value is not None
                and value.get("value") == "true"
            ):
                visible.add(shape_id)
    if visible != set(EXPECTED):
        raise RuntimeError("Not every FreeCAD shape opens visible")

    print("CREATOR_KIT_FREECAD_VERIFY_OK")
    print(f"Native_parts={len(EXPECTED)}")
    print(f"STEP_solids={len(showcase_step.Solids)}")
    print(f"STL_facets={showcase_mesh.CountFacets}")
    print(f"Godot_assets={len(manifest['shapes'])}")
    print(f"FreeCAD_visible_parts={len(visible)}")
    App.closeDocument(doc.Name)


try:
    verify()
except Exception:
    traceback.print_exc()
    print("CREATOR_KIT_FREECAD_VERIFY_FAILED")
    sys.exit(1)
