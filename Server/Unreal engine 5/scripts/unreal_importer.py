import unreal

@unreal.uclass()
class ImporterHelper(unreal.Object):
    @unreal.ufunction(static=True, meta=dict(Category="Utilities|Importer"))
    def import_fbx(save_path, file_name):
        unreal.log("Starting import process...")

        # Create the import task
        import_task = unreal.AssetImportTask()
        import_task.filename = save_path
        import_task.destination_path = "/Game/Imported"
        import_task.destination_name = file_name.split('.')[0]
        import_task.automated = True
        import_task.save = True
        import_task.replace_existing = True
        import_task.suppress_import_dialog = True

        # Create and configure the FBX import options
        options = unreal.FbxImportUI()
        options.automated_import_should_detect_type = True
        options.import_materials = False
        options.import_textures = False
        options.import_as_skeletal = False
        options.static_mesh_import_data = unreal.FbxStaticMeshImportData()
        options.static_mesh_import_data.combine_meshes = True
        options.static_mesh_import_data.auto_generate_collision = True

        import_task.options = options

        # Perform the import
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])
        unreal.log(f"FBX file {file_name} imported successfully")

        # Refresh the asset registry to make the new asset visible in the Content Browser
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        asset_registry.scan_paths_synchronous(['/Game/Imported'])
        imported_asset = unreal.load_asset(f'/Game/Imported/{file_name.split(".")[0]}')
        if imported_asset:
            unreal.EditorAssetLibrary.sync_browser_to_objects([imported_asset])
        else:
            unreal.log_warning(f"Failed to load the imported asset: /Game/Imported/{file_name.split(".")[0]}')

        unreal.log("Import process completed.")
