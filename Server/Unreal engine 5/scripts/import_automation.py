import unreal

class ImportAutomationLibrary:

    @staticmethod
    def import_fbx_automated(file_path: str):
        unreal.log("Starting automated FBX import process...")

        destination_path = "/Game/Imported"
        task = unreal.AssetImportTask()
        task.filename = file_path
        task.destination_path = destination_path
        task.destination_name = None
        task.automated = True
        task.save = True
        task.replace_existing = True

        options = unreal.FbxImportUI()
        options.automated_import_should_detect_type = True
        options.import_materials = True  # Allow import of materials
        options.import_textures = True   # Allow import of textures
        options.import_as_skeletal = False
        options.static_mesh_import_data = unreal.FbxStaticMeshImportData()
        options.static_mesh_import_data.combine_meshes = True
        options.static_mesh_import_data.auto_generate_collision = True

        task.options = options

        try:
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
            unreal.log("Import task executed successfully.")
        except Exception as e:
            unreal.log_error(f"Error executing import task: {e}")

        try:
            asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
            asset_registry.scan_paths_synchronous([destination_path])
            unreal.log("Asset registry scan completed.")

            imported_asset = unreal.load_asset(f'{destination_path}/{unreal.Paths.get_base_filename(file_path)}')
            if imported_asset:
                unreal.EditorAssetLibrary.sync_browser_to_objects([imported_asset])
                unreal.log(f"FBX file {file_path} imported successfully")
            else:
                unreal.log_warning(f"Failed to load the imported asset: {destination_path}/{unreal.Paths.get_base_filename(file_path)}")
        except Exception as e:
            unreal.log_error(f"Error during post-import steps: {e}")

        unreal.log("Automated FBX import process completed.")

    @staticmethod
    def import_texture_automated(file_path: str):
        unreal.log("Starting automated texture import process...")

        destination_path = "/Game/Imported"
        task = unreal.AssetImportTask()
        task.filename = file_path
        task.destination_path = destination_path
        task.destination_name = None
        task.automated = True
        task.save = True
        task.replace_existing = True

        options = unreal.TextureFactory()
        task.options = options

        try:
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
            unreal.log("Texture import task executed successfully.")
        except Exception as e:
            unreal.log_error(f"Error executing texture import task: {e}")

        unreal.log("Automated texture import process completed.")
