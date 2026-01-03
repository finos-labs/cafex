from pytest_bdd import given, when, then, parsers, scenario
from test_project.cafex_sandbox_project.features.forms.salesforce.salesforce_utils import Salesforce

salesforce_utils = Salesforce()

@scenario('salesforce.feature', 'Create and convert a lead, then update opportunity stage')
def test_salesforce_lead_conversion():
    print("Create and convert a lead, then update opportunity stage")

@scenario('salesforce.feature', 'Clone an opportunity and validate details')
def test_clone_opportunity():
    print("Clone an opportunity and validate details")

@scenario('salesforce.feature',"Add a note to an opportunity and validate the title")
def test_add_note_to_opportunity():
    print("Add a note to an opportunity and validate the title")

@given(parsers.parse('user log into Salesforce with credentials:\n{table}'),converters={'table': str})
def login_with_credentials(table):
    print("user log into Salesforce with credentials")
    salesforce_utils.salesforce_login(table)

@given(parsers.parse('user navigates to leads tab'))
def go_to_app():
    print("user navigates to leads tab")
    salesforce_utils.navigate_to_leads_tab()

@given(parsers.parse('user create a lead with default data'))
def create_lead_default():
    print("Creating a lead with default data")
    salesforce_utils.create_lead_with_default_data()

@given(parsers.parse('user create a lead with following data:\n{data}'),converters={'data': str})
def create_lead_with_data(data):
    print("Creating a lead with the following data")
    salesforce_utils.create_lead_with_data(data)

@given('user will open new created lead and will convert the lead')
def convert_lead():
    print("user will open new created lead and will convert the lead")
    salesforce_utils.convert_lead()

@then(parsers.parse('user go to "Opportunity" app'))
def go_to_opportunity_app():
    salesforce_utils.go_to_opportunity_page()

@when(parsers.parse('user set the {stage} as {value} for the created opportunity'))
def set_field_values(stage,value):
    print("Setting field values")
    assert salesforce_utils.set_stage_as_closed_won(stage,value)

@then(parsers.parse('user should see the opportunity stage updated to {expected_stage}'))
def verify_field_values(expected_stage):
    print("Verifying field values")
    assert salesforce_utils.validate_stage_value(expected_stage)

@given('the user is on the Opportunity page')
def user_on_opportunity_page():
    print("User is on the Opportunity page")
    assert salesforce_utils.go_to_opportunity_page()

@when(parsers.cfparse('the user selects an {name} opportunity'))
def select_opportunity(name):
    print("Select the first opportunity")
    assert salesforce_utils.select_opportunity(name)

@when('clicks the Clone button')
def click_clone_button():
    print("Click the Clone button")
    assert salesforce_utils.click_clone_button()

@when('appends the opportunity name with clone text')
def append_clone_text_to_name():
    print("Append clone text to opportunity name")
    assert salesforce_utils.append_opportunity_name_with_clone_text()

@when('clicks the Save button')
def click_save_button():
    print("Click the Save button")
    assert salesforce_utils.click_save_button()

@when('opens the newly cloned opportunity')
def open_cloned_opportunity():
    print("Open the newly cloned opportunity")
    assert salesforce_utils.open_cloned_opportunity()

@then('the opportunity details should be validated')
def validate_opportunity_details():
    print("Validate the opportunity details")
    assert salesforce_utils.validate_cloned_opportunity_details()

@when('clicks the Note button')
def click_note_button():
    salesforce_utils.click_note_button()

@when(parsers.parse('enters a new title {title} and body content {body}'))
def enter_note_title_and_body(title,body):
    salesforce_utils.enter_note_title_and_body(title,body)

@when('clicks the Save button')
def click_save_button():
    salesforce_utils.click_save_button()

@when('opens the newly created note')
def open_new_note():
    salesforce_utils.open_new_note()

@then(parsers.parse('the note title should be validated as {expected_title}'))
def validate_note_title(expected_title):
    assert salesforce_utils.validate_note_title(expected_title)

