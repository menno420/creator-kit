extends SceneTree


func _initialize() -> void:
	call_deferred("_run_verification")


func _fail(message: String) -> void:
	printerr("CREATOR_KIT_GODOT_VERIFY_FAILED: " + message)
	quit(1)


func _run_verification() -> void:
	var manifest_file := FileAccess.open("res://assets/freecad/manifest.json", FileAccess.READ)
	if manifest_file == null:
		_fail("manifest.json is missing")
		return
	var manifest: Variant = JSON.parse_string(manifest_file.get_as_text())
	if not manifest is Dictionary or not manifest.has("shapes"):
		_fail("manifest.json is invalid")
		return
	if manifest["shapes"].size() != 8:
		_fail("expected eight generated shapes")
		return
	for entry in manifest["shapes"]:
		if not ResourceLoader.exists("res://assets/freecad/" + entry["file"]):
			_fail("Godot cannot import " + entry["file"])
			return

	var packed: PackedScene = load("res://scenes/workbench.tscn")
	if packed == null:
		_fail("workbench scene cannot be loaded")
		return
	var workbench := packed.instantiate()
	root.add_child(workbench)
	await process_frame
	await process_frame
	if workbench.get_loaded_shape_count() != 8:
		_fail("workbench did not instantiate all eight meshes")
		return
	if workbench.get_node_or_null("Interface/Sidebar/Content/ActionButtons/MoveButton") == null:
		_fail("workbench controls are missing")
		return
	print("CREATOR_KIT_GODOT_VERIFY_OK")
	print("Imported_shapes=8")
	print("Main_scene=res://scenes/workbench.tscn")
	print("Scale=1_Godot_unit_per_metre")
	quit(0)
