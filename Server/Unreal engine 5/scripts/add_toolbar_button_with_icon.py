import unreal

def server_on():
    import sys
    import importlib

    sys.path.append('C:/Users/loved/Documents/Unreal Projects/Python_TestV1/Content/scripts')
    import unreal_server
    importlib.reload(unreal_server)
    unreal_server.start_server()  # To start the server

def server_off():
    import sys
    import importlib

    sys.path.append('C:/Users/loved/Documents/Unreal Projects/Python_TestV1/Content/scripts')
    import unreal_server
    importlib.reload(unreal_server)
    unreal_server.stop_server()  # To stop the server

def create_toolbar_button():
    tool_menus = unreal.ToolMenus.get()
    tools_menu = tool_menus.find_menu("LevelEditor.MainMenu.Tools")

    if tools_menu:
        # Add the Prometheus menu entry
        prometheus_entry = unreal.ToolMenuEntry(
            name="MyPrometheusMainMenu",
            type=unreal.MultiBlockType.MENU_ENTRY,
            insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST)
        )
        prometheus_entry.set_label("Prometheus")

        # Add the Prometheus menu entry
        tools_menu.add_menu_entry("Tools", prometheus_entry)

        # Create submenu entries
        server_on_entry = unreal.ToolMenuEntry(
            name="MyPrometheusSubMenuServerOn",
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        server_on_entry.set_label("Server On")
        server_on_entry.set_string_command(
            type=unreal.ToolMenuStringCommandType.PYTHON,
            custom_type="",
            string="import add_toolbar_button_with_icon; add_toolbar_button_with_icon.server_on()"
        )

        server_off_entry = unreal.ToolMenuEntry(
            name="MyPrometheusSubMenuServerOff",
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        server_off_entry.set_label("Server Off")
        server_off_entry.set_string_command(
            type=unreal.ToolMenuStringCommandType.PYTHON,
            custom_type="",
            string="import add_toolbar_button_with_icon; add_toolbar_button_with_icon.server_off()"
        )

        # Extend the Prometheus menu to add submenu entries
        prometheus_menu = tool_menus.extend_menu("LevelEditor.MainMenu.Tools")
        if prometheus_menu:
            prometheus_menu.add_sub_menu(
                owner="LevelEditor.MainMenu.Tools",
                section_name="Tools",
                name="Prometheus",
                label="Prometheus"
            )
            prometheus_submenu = tool_menus.find_menu("LevelEditor.MainMenu.Tools.Prometheus")
            if (prometheus_submenu):
                prometheus_submenu.add_menu_entry("PrometheusSubmenuSection", server_on_entry)
                prometheus_submenu.add_menu_entry("PrometheusSubmenuSection", server_off_entry)
                unreal.log("Prometheus menu with Server On/Off added successfully")
            else:
                unreal.log_warning("Prometheus submenu not found")
        else:
            unreal.log_warning("Failed to extend Tools menu")

    else:
        unreal.log_warning("LevelEditor.MainMenu.Tools menu not found")

    # Refresh the UI
    tool_menus.refresh_all_widgets()

if __name__ == "__main__":
    create_toolbar_button()
