import unittest
import pytest
from cafex_core.reporting_.step_decorator import step
from test_project.cafex_sandbox_project.features.forms.desktop_methods.desktop_methods import NotepadUtils

notepad = NotepadUtils()


class TestNotepadFunctionality(unittest.TestCase):
    """Unit tests for Notepad functionality: Replace text and save the file."""

    @pytest.mark.ui_desktop_client
    def test_notepad_functionality(self):
        """Test Notepad functionality: Replace text and save the file."""

        @step("Given the user opens Notepad")
        def step_given_open_notepad():
            print("Opening Notepad")
            self.assertTrue(notepad.is_notepad_launched(), "Notepad application is not accessible")

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
            self.assertTrue(notepad.validate_file(file_name))

        # Execute the steps
        step_given_open_notepad()
        step_when_type_text("Hello, World!")
        step_when_replace_text("World", "Python")
        step_when_save_file("example.txt")
        step_then_file_saved("example.txt")


if __name__ == '__main__':
    unittest.main()
