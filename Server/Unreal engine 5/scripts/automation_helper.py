import unreal

@unreal.uclass()
class AutomationLibrary(unreal.Object):
    @unreal.ufunction(static=True, meta=dict(Category="Utilities|Automation"))
    def press_import_all_button():
        unreal.log("Attempting to press 'Import All' button")

        slate_app = unreal.SlateApplication.get()
        windows = slate_app.get_all_visible_windows()

        for window in windows:
            title = window.get_title().to_string()
            unreal.log(f"Found window with title: {title}")
            if title == "FBX Import Options":
                # Find and press the "Import All" button
                for widget in window.get_all_widgets():
                    if widget.get_type() == "SButton" and widget.get_tool_tip_text().to_string() == "Import All":
                        unreal.log("Found 'Import All' button. Pressing it.")
                        widget.click()
                        return
        unreal.log_warning("FBX Import Options window or 'Import All' button not found.")
