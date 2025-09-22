from pywinauto import application
import time
import os
import pytest

from cafex_core.utils.config_utils import ConfigUtils
from cafex_core.reporting_.step_decorator import step
from test_project.cafex_sandbox_project.features.forms.desktop_methods.desktop_methods import NotepadUtils

notepad = NotepadUtils()


@pytest.mark.ui_desktop_client
def test_notepad_functionality():
    """Test Notepad functionality: Replace text and save the file."""

    @step("Given the user opens Notepad")
    def step_given_open_notepad():
        print("Opening Notepad")
        assert notepad.is_notepad_launched(), "Notepad application is not accessible"

    @step('When the user types "{text}"')
    def step_when_type_text(text):
        print(f"Typing text: {text}")
        notepad.type_text_to_notepad(text)

    @step('When the user replaces the word "{find_text}" with "{replace_text}"')
    def step_when_replace_text(find_text, replace_text):
        print(f"Replacing '{find_text}' with '{replace_text}'")
        notepad.replace_text(find_text, replace_text)

    @step('When the user saves the file as "{file_name}"')
    def step_when_save_file(file_name):
        print(f"Saving file as '{file_name}'")
        notepad.save_file(file_name)

    @step('Then the file "{file_name}" should be saved successfully')
    def step_then_file_saved(file_name):
        print(f"File '{file_name}' should be saved successfully")
        assert notepad.validate_file(file_name)

    # Execute the steps
    step_given_open_notepad()
    step_when_type_text("Hello, World!")
    step_when_replace_text("World", "Python")
    step_when_save_file("example.txt")
    step_then_file_saved("example.txt")


def test_automate_notepad_operations():
    try:
        # Start Notepad
        app = application.Application().start("notepad.exe")
        time.sleep(2)  # Wait for Notepad to open

        # Connect to the Notepad window
        notepad_window = app.UntitledNotepad
        notepad_window.wait("ready", timeout=10)

        # Type some text
        notepad_window.Edit.type_keys("This is a test.\nLet's replace some text.", with_spaces=True)
        time.sleep(1)
        # Open the Replace dialog (Ctrl+H)
        notepad_window.menu_select("Edit -> Replace")
        replace_dialog = app.window(title_re="Replace")
        replace_dialog.wait("ready", timeout=10)

        # Clear the "Find what" field and type new text
        find_what_field = replace_dialog.child_window(class_name="Edit", found_index=0)
        find_what_field.set_text("")  # Clear the field
        find_what_field.type_keys("test", with_spaces=True)  # Type new text

        # Clear the "Replace with" field and type new text
        replace_with_field = replace_dialog.child_window(class_name="Edit", found_index=1)
        replace_with_field.set_text("")  # Clear the field
        replace_with_field.type_keys("example", with_spaces=True)  # Type new text
        time.sleep(1)

        # Perform the replace operation
        replace_all_button = replace_dialog.child_window(title="Replace &All", class_name="Button")

        # Verify if the button exists and is enabled
        if replace_all_button.exists(timeout=20) and replace_all_button.is_enabled():
            replace_all_button.click()
            time.sleep(1)
        else:
            print("Replace &All button is not available or not enabled.")

        # Locate the "Cancel" button in the dialog
        cancel_button = replace_dialog.child_window(title="Cancel", class_name="Button")

        # Verify if the button exists and is enabled
        if cancel_button.exists(timeout=10) and cancel_button.is_enabled():
            cancel_button.click()  # Click the button to close the dialog
            time.sleep(1)
        else:
            print("Cancel button is not available or not enabled.")
        file_path = os.path.join(ConfigUtils().fetch_testdata_path(), "sample.txt")
        if os.path.exists(file_path):
            os.remove(file_path)
        # Open Save As dialog (Ctrl+S or File -> Save As)
        notepad_window.type_keys("^s")  # Ctrl+S
        time.sleep(1)  # Wait for the dialog to appear

        # Connect to the Save As dialog
        save_as_dialog = app.SaveAs

        # Print the control identifiers to debug the structure
        save_as_dialog.print_control_identifiers()

        # Set the file name in the edit box (update the control name/class based on the debug output)
        file_name_field = save_as_dialog.child_window(class_name="Edit", found_index=0)  # Adjust if needed
        file_name_field.type_keys(file_path)

        # Click the Save button
        save_as_dialog.Save.click()

        # Optional: Close Notepad
        notepad_window.close()

        print(f"File saved successfully at: {file_path}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise
