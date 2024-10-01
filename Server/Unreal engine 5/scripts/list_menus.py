import unreal

def check_menus():
    tool_menus = unreal.ToolMenus.get()
    
    menu_paths = [
        "LevelEditor.MainMenu",
        "LevelEditor.MainMenu.File",
        "LevelEditor.MainMenu.Edit",
        "LevelEditor.MainMenu.Window",
        "LevelEditor.LevelEditorToolBar",
        "ContentBrowser.MainMenu"
    ]
    
    for path in menu_paths:
        menu = tool_menus.find_menu(path)
        if menu:
            unreal.log(f"Menu found: {path}")
        else:
            unreal.log_warning(f"Menu not found: {path}")

if __name__ == "__main__":
    check_menus()
