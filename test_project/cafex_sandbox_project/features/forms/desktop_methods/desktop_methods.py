import os

from cafex_core.reporting_.reporting import Reporting
from cafex_core.utils.config_utils import ConfigUtils
from cafex_desktop import CafeXDesktop
import time


class NotepadUtils:
    def __init__(self):
        self.config_utils = ConfigUtils()
        self.reporting = Reporting()
        self.notepad_window = None
        self.app = None

    def is_notepad_launched(self) -> bool:
        try:
            self.app = CafeXDesktop().app
            if not self.app:
                raise AssertionError("Notepad application is not accessible")
            self.reporting.insert_step("Notepad launched", "Notepad launched", "True")
            return True
        except Exception as e:
            self.reporting.insert_step("Notepad not launched", "Notepad not launched", "False")
            raise AssertionError("Notepad is not installed or not accessible") from e

    def type_text_to_notepad(self, text):
        if not self.is_notepad_launched():
            raise AssertionError("Notepad application is not accessible")
        self.notepad_window = CafeXDesktop().app.UntitledNotepad
        self.notepad_window.wait("ready", timeout=10)
        CafeXDesktop().type(self.notepad_window.Edit, text)
        time.sleep(1)
        self.reporting.insert_step("Text typed", "Text typed", "True")

    def replace_text(self, find_text, replace_text):
        CafeXDesktop().select_menu_item(self.notepad_window, "Edit -> Replace")
        replace_dialog = CafeXDesktop().get_window_object(title_regex="Replace", wait_for_exists=False)
        replace_dialog.wait("ready", timeout=10)

        # Clear the "Find what" field and type new text
        find_what_field = CafeXDesktop().get_child_window(replace_dialog, class_name="Edit", found_index=0)
        find_what_field.set_text("")  # Clear the field
        CafeXDesktop().type(find_what_field, find_text)  # Type new text

        # Clear the "Replace with" field and type new text
        replace_with_field = CafeXDesktop().get_child_window(replace_dialog, class_name="Edit", found_index=1)
        replace_with_field.set_text("")  # Clear the field
        CafeXDesktop().type(replace_with_field, replace_text)  # Type new text
        time.sleep(1)

        replace_all_button = CafeXDesktop().get_child_window(replace_dialog, title="Replace &All", class_name="Button")
        if replace_all_button.exists(timeout=20) and replace_all_button.is_enabled():
            replace_all_button.click()
            time.sleep(1)
        else:
            raise AssertionError("Replace &All button is not available or not enabled")
        cancel_button = CafeXDesktop().get_child_window(replace_dialog, title="Cancel", class_name="Button")
        if cancel_button.exists(timeout=10) and cancel_button.is_enabled():
            cancel_button.click()
            time.sleep(1)
        else:
            raise AssertionError("Cancel button is not available or not enabled")
        self.reporting.insert_step("Text replaced", "Text replaced", "True")

    def save_file(self, file_name):
        file_path = os.path.join(self.config_utils.fetch_testdata_path(), file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        self.notepad_window.type_keys("^s")
        time.sleep(1)
        save_as_dialog = CafeXDesktop().get_window_object(title_regex="Save As")
        save_as_dialog.wait("ready", timeout=10)
        file_path = os.path.join(self.config_utils.fetch_testdata_path(), file_name)
        file_name_field = CafeXDesktop().get_child_window(save_as_dialog, class_name="Edit", found_index=0)
        file_name_field.set_text("")
        CafeXDesktop().type(file_name_field, file_path)
        time.sleep(5)
        save_as_dialog.Save.click()
        time.sleep(10)
        self.reporting.insert_step("File saved", "File saved", "True")

    def validate_file(self, file_name):
        file_path = os.path.join(self.config_utils.fetch_testdata_path(), file_name)
        if os.path.exists(file_path):
            self.reporting.insert_step("File exists", "File exists", "True")
            print(f"File '{file_name}' exists at '{file_path}'")
            return True
        else:
            self.reporting.insert_step("File does not exist", "File does not exist", "False")
            return False
