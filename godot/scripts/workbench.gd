extends Node3D

const MANIFEST_PATH := "res://assets/freecad/manifest.json"
const ASSET_ROOT := "res://assets/freecad/"
const SNAP_STEP := 0.025
const PALETTE := [
	Color("4d9be6"), Color("36c9a5"), Color("f0a23b"), Color("8f6bd6"),
	Color("e95c64"), Color("55b965"), Color("728099"), Color("e678b2")
]

@onready var camera: Camera3D = $Camera3D
@onready var objects: Node3D = $Objects
@onready var grid_holder: Node3D = $GeneratedGrid
@onready var shape_buttons: GridContainer = $Interface/Sidebar/Content/ShapeButtons
@onready var selected_label: Label = $Interface/Sidebar/Content/SelectedPanel/SelectedContent/SelectedLabel
@onready var dimensions_label: Label = $Interface/Sidebar/Content/SelectedPanel/SelectedContent/DimensionsLabel
@onready var status_label: Label = $Interface/Sidebar/Content/Status

var entries: Array = []
var items: Dictionary = {}
var original_transforms: Dictionary = {}
var original_colours: Dictionary = {}
var colour_steps: Dictionary = {}
var selected_id := ""
var grab_active := false
var grab_start := Vector3.ZERO
var orbiting := false
var camera_target := Vector3(0.06, 0.035, 0.0)
var camera_yaw := 0.72
var camera_pitch := 0.62
var camera_distance := 0.62


func _ready() -> void:
	_build_grid()
	_connect_controls()
	_load_shapes()
	_update_camera()
	if not entries.is_empty():
		_select_shape(entries[0]["id"])
	status_label.text = "Ready. Choose an object, then use the buttons or keyboard."


func get_loaded_shape_count() -> int:
	return items.size()


func _connect_controls() -> void:
	$Interface/Sidebar/Content/ActionButtons/MoveButton.pressed.connect(_begin_grab)
	$Interface/Sidebar/Content/ActionButtons/RotateButton.pressed.connect(_rotate_selected)
	$Interface/Sidebar/Content/ActionButtons/BiggerButton.pressed.connect(_scale_selected.bind(1.1))
	$Interface/Sidebar/Content/ActionButtons/SmallerButton.pressed.connect(_scale_selected.bind(1.0 / 1.1))
	$Interface/Sidebar/Content/ActionButtons/ColourButton.pressed.connect(_change_colour)
	$Interface/Sidebar/Content/ActionButtons/ResetButton.pressed.connect(_reset_all)


func _load_shapes() -> void:
	var file := FileAccess.open(MANIFEST_PATH, FileAccess.READ)
	if file == null:
		status_label.text = "Could not read the FreeCAD shape list. Rebuild the library first."
		return
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	if not parsed is Dictionary or not parsed.has("shapes"):
		status_label.text = "The shape list is invalid. Rebuild the library."
		return
	entries = parsed["shapes"]
	for index in entries.size():
		var entry: Dictionary = entries[index]
		var mesh_resource: Resource = load(ASSET_ROOT + entry["file"])
		if mesh_resource == null:
			push_error("Could not load " + entry["file"])
			continue
		var item := MeshInstance3D.new()
		item.name = entry["id"]
		item.mesh = mesh_resource
		item.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		var material := StandardMaterial3D.new()
		var source_colour := Color(
			float(entry["color"][0]), float(entry["color"][1]), float(entry["color"][2]), 1.0
		)
		material.albedo_color = source_colour
		material.roughness = 0.66
		material.metallic = 0.08
		item.material_override = material
		var column := index % 4
		var row := index / 4
		item.position = Vector3(-0.15 + column * 0.14, 0.0, -0.08 + row * 0.18)
		objects.add_child(item)
		items[entry["id"]] = item
		original_transforms[entry["id"]] = item.transform
		original_colours[entry["id"]] = source_colour
		colour_steps[entry["id"]] = index % PALETTE.size()

		var button := Button.new()
		button.text = entry["label"]
		button.custom_minimum_size = Vector2(130, 38)
		button.tooltip_text = entry["dimensions"]
		button.pressed.connect(_select_shape.bind(entry["id"]))
		shape_buttons.add_child(button)


func _entry_for(shape_id: String) -> Dictionary:
	for entry in entries:
		if entry["id"] == shape_id:
			return entry
	return {}


func _select_shape(shape_id: String) -> void:
	if not items.has(shape_id):
		return
	if grab_active:
		_cancel_grab()
	for id in items:
		var material: StandardMaterial3D = items[id].material_override
		material.emission_enabled = false
	selected_id = shape_id
	var selected: MeshInstance3D = items[selected_id]
	var selected_material: StandardMaterial3D = selected.material_override
	selected_material.emission_enabled = true
	selected_material.emission = selected_material.albedo_color * 0.22
	selected_material.emission_energy_multiplier = 0.7
	var entry := _entry_for(selected_id)
	selected_label.text = entry["label"]
	dimensions_label.text = entry["category"] + "\n" + entry["dimensions"]
	status_label.text = "Selected " + entry["label"] + ". Press G to move it."


func _selected() -> MeshInstance3D:
	if selected_id.is_empty() or not items.has(selected_id):
		return null
	return items[selected_id]


func _begin_grab() -> void:
	var item := _selected()
	if item == null:
		return
	grab_active = true
	grab_start = item.position
	status_label.text = "MOVE: point on the workbench, then left-click. Escape cancels."


func _confirm_grab() -> void:
	if not grab_active:
		return
	grab_active = false
	status_label.text = "Position set on the 25 mm grid. Press G to move again."


func _cancel_grab() -> void:
	if not grab_active:
		return
	var item := _selected()
	if item != null:
		item.position = grab_start
	grab_active = false
	status_label.text = "Move cancelled."


func _move_to_mouse(mouse_position: Vector2) -> void:
	var item := _selected()
	if item == null:
		return
	var ray_origin := camera.project_ray_origin(mouse_position)
	var ray_direction := camera.project_ray_normal(mouse_position)
	if abs(ray_direction.y) < 0.00001:
		return
	var distance_to_floor := -ray_origin.y / ray_direction.y
	if distance_to_floor <= 0:
		return
	var point := ray_origin + ray_direction * distance_to_floor
	item.position.x = snappedf(point.x, SNAP_STEP)
	item.position.z = snappedf(point.z, SNAP_STEP)


func _rotate_selected() -> void:
	var item := _selected()
	if item == null:
		return
	item.rotate_y(deg_to_rad(15.0))
	status_label.text = "Rotated 15 degrees."


func _scale_selected(factor: float) -> void:
	var item := _selected()
	if item == null:
		return
	var next_scale := clampf(item.scale.x * factor, 0.5, 2.0)
	item.scale = Vector3.ONE * next_scale
	status_label.text = "Scale: " + str(roundf(next_scale * 100.0)) + "%"


func _change_colour() -> void:
	var item := _selected()
	if item == null:
		return
	var next_index: int = (int(colour_steps[selected_id]) + 1) % PALETTE.size()
	colour_steps[selected_id] = next_index
	var material: StandardMaterial3D = item.material_override
	material.albedo_color = PALETTE[next_index]
	material.emission = material.albedo_color * 0.22
	status_label.text = "Colour changed."


func _reset_all() -> void:
	grab_active = false
	for id in items:
		items[id].transform = original_transforms[id]
		var material: StandardMaterial3D = items[id].material_override
		material.albedo_color = original_colours[id]
		colour_steps[id] = entries.find(_entry_for(id)) % PALETTE.size()
	_select_shape(entries[0]["id"])
	status_label.text = "Every object is back in its starting position."


func _build_grid() -> void:
	var mesh := ImmediateMesh.new()
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = Color(0.3, 0.42, 0.58, 0.48)
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mesh.surface_begin(Mesh.PRIMITIVE_LINES, material)
	var x_extent := 0.44
	var z_extent := 0.33
	for index in range(-17, 18):
		var x := index * SNAP_STEP
		mesh.surface_add_vertex(Vector3(x, 0.0005, -z_extent))
		mesh.surface_add_vertex(Vector3(x, 0.0005, z_extent))
	for index in range(-13, 14):
		var z := index * SNAP_STEP
		mesh.surface_add_vertex(Vector3(-x_extent, 0.0005, z))
		mesh.surface_add_vertex(Vector3(x_extent, 0.0005, z))
	mesh.surface_end()
	var grid := MeshInstance3D.new()
	grid.mesh = mesh
	grid_holder.add_child(grid)


func _update_camera() -> void:
	var horizontal := cos(camera_pitch) * camera_distance
	var offset := Vector3(
		sin(camera_yaw) * horizontal,
		sin(camera_pitch) * camera_distance,
		cos(camera_yaw) * horizontal
	)
	camera.position = camera_target + offset
	camera.look_at(camera_target, Vector3.UP)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_G:
				_begin_grab()
			KEY_R:
				_rotate_selected()
			KEY_EQUAL, KEY_KP_ADD:
				_scale_selected(1.1)
			KEY_MINUS, KEY_KP_SUBTRACT:
				_scale_selected(1.0 / 1.1)
			KEY_HOME:
				_reset_all()
			KEY_ESCAPE:
				_cancel_grab()

	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed and grab_active:
			_move_to_mouse(event.position)
			_confirm_grab()
			get_viewport().set_input_as_handled()
		elif event.button_index == MOUSE_BUTTON_RIGHT and event.pressed and grab_active:
			_cancel_grab()
			get_viewport().set_input_as_handled()
		elif event.button_index == MOUSE_BUTTON_MIDDLE:
			orbiting = event.pressed
		elif event.button_index == MOUSE_BUTTON_WHEEL_UP and event.pressed:
			camera_distance = maxf(0.24, camera_distance * 0.9)
			_update_camera()
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN and event.pressed:
			camera_distance = minf(1.4, camera_distance * 1.1)
			_update_camera()

	if event is InputEventMouseMotion:
		if grab_active:
			_move_to_mouse(event.position)
		elif orbiting or (Input.is_key_pressed(KEY_ALT) and event.button_mask & MOUSE_BUTTON_MASK_LEFT):
			camera_yaw -= event.relative.x * 0.008
			camera_pitch = clampf(camera_pitch - event.relative.y * 0.008, 0.18, 1.30)
			_update_camera()
