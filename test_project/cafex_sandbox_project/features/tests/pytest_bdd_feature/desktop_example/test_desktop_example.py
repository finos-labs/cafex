from pytest_bdd import given, when, then, parsers, scenario
from test_project.cafex_sandbox_project.features.forms.desktop_methods.desktop_methods import NotepadUtils

notepad = NotepadUtils()


@scenario("desktop_example.feature", "Replace text and save the file")
def test_notepad_functionality():
    pass


@given("the user opens Notepad")
def step_when_open_notepad():
    print("Opening Notepad")
    assert notepad.is_notepad_launched(), "Notepad application is not accessible"


@when(parsers.parse('the user types "{text}"'))
def step_when_type_text(text):
    print(f"Typing text: {text}")
    notepad.type_text_to_notepad(text)


@when(parsers.parse('the user replaces the word "{find_text}" with "{replace_text}"'))
def step_when_replace_text(find_text, replace_text):
    print(f"Replacing '{find_text}' with '{replace_text}'")
    notepad.replace_text(find_text, replace_text)


@when(parsers.parse('the user saves the file as "{file_name}"'))
def step_when_save_file(file_name):
    print(f"Saving file as '{file_name}'")
    notepad.save_file(file_name)


@then(parsers.parse('the file "{file_name}" should be saved successfully'))
def step_then_file_saved(file_name):
    print(f"File '{file_name}' should be saved successfully")
    assert notepad.validate_file(file_name)
