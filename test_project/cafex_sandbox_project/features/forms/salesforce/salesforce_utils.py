import csv
import time
from cafex_core.reporting_.reporting import Reporting
from cafex_core.utils.config_utils import ConfigUtils
from cafex_ui import CafeXWeb
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_project.cafex_sandbox_project.features.forms.salesforce.salesforce_locators import SalesforceLocators

class Salesforce:

    def __init__(self):
        self.config_object = ConfigUtils()
        self.reporting_object = Reporting()
        self.locators = SalesforceLocators()


    def salesforce_login(self,table):
        try:
            base_url = self.config_object.fetch_base_url()
            CafeXWeb().navigate(base_url)
            expected_title = "Login | Salesforce"
            actual_title = CafeXWeb().get_title()
            if actual_title == expected_title:
                self.reporting_object.insert_step(
                    "Validate navigation to Salesforce login page",
                    f"Successfully navigated to '{expected_title}'",
                    "Pass"
                )
            else:
                self.reporting_object.insert_step(
                    "Validate navigation to Salesforce login page",
                    f"Expected: '{expected_title}', Actual: '{actual_title}'",
                    "Fail"
                )
            rows = list(csv.DictReader(table.splitlines(), delimiter='|'))
            for row in rows:
                params = {key.strip(): value.strip() for key, value in row.items()}
                username = params["username"]
                password = params["password"]
                self.login_with_credentials(username, password)
        except Exception as e:
            raise e

    def login_with_credentials(self,username:str,password:str):
        try:
            if not username and not password:
                CafeXWeb().click(self.locators.login_field)
                error_message = CafeXWeb().get_web_element(self.locators.error_field).text
                expected_message = "Error: Please enter your username and password."
                if error_message == expected_message:
                    self.reporting_object.insert_step(
                        "Validate error message for missing username and password",
                        f"Correct error message displayed: '{expected_message}'",
                        "Pass"
                    )
                else:
                    self.reporting_object.insert_step(
                        "Validate error message for missing username and password",
                        f"Expected: '{expected_message}', Actual: '{error_message}'",
                        "Fail"
                    )
            if username and not password:
                CafeXWeb().click(self.locators.login_field)
                error_message = CafeXWeb().get_web_element(self.locators.error_field).text
                if error_message == "Error: Please enter your password.":
                    self.reporting_object.insert_step(
                        "Validate error message for missing password",
                        "Correct error message displayed: 'Error: Please enter your password.'",
                        "Pass"
                    )
                else:
                    self.reporting_object.insert_step(
                        "Validate error message for missing password",
                        f"Expected: 'Error: Please enter your password.', Actual: '{error_message}'",
                        "Fail"
                    )
            if username and password:
                if username == "test_user" and password == "test_pass":
                    username, password = self.config_object.fetch_login_credentials("default_user")
                CafeXWeb().type(self.locators.username_field, username)
                CafeXWeb().type(self.locators.password_field, password)
                CafeXWeb().click(self.locators.login_field, explicit_wait=20)
                time.sleep(10)
                WebDriverWait(CafeXWeb().driver, 30).until(EC.presence_of_element_located((By.ID, "emc")))
                verification_input = CafeXWeb().driver.find_element(By.ID, "emc")
                while True:
                    verification_code = verification_input.get_attribute('value')
                    if len(verification_code) == 6:
                        break
                    time.sleep(1)
                verification_input.send_keys(verification_code)
                CafeXWeb().driver.find_element(By.ID, "save").click()
                if "Salesforce" or "Lightning Experience" in CafeXWeb().get_title(explicit_wait=20):
                    self.reporting_object.insert_step(
                        "Validate navigation to Salesforce home page",
                        "Successfully navigated to 'Home | Salesforce' or 'Lightning Experience'",
                        "Pass"
                    )
                else:
                    actual_title = CafeXWeb().get_title()
                    self.reporting_object.insert_step(
                        "Validate navigation to Salesforce home page",
                        f"Expected: 'Home | Salesforce or Lightning Experience', Actual: '{actual_title}'",
                        "Fail"
                    )
        except Exception as e:
            self.reporting_object.insert_step(
                "Login with credentials",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            raise e

    def navigate_to_leads_tab(self):
        try:
            CafeXWeb().navigate("https://orgfarm-153ddb4ae7-dev-ed.develop.lightning.force.com/lightning/o/Lead/pipelineInspection", explicit_wait=20)
            leads_header = CafeXWeb().get_web_element(self.locators.leads_header, explicit_wait=30).text
            if "Leads" in leads_header:
                self.reporting_object.insert_step(
                    "Navigate to Leads tab and validate header",
                    f"Leads header after navigation: '{leads_header}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Navigate to Leads tab and validate header",
                    f"Unexpected Leads header after navigation: '{leads_header}'",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Navigate to Leads tab and validate header",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            raise e

    def create_lead_with_default_data(self):
        try:
            CafeXWeb().click(self.locators.new_lead_button, explicit_wait=20)
            new_lead_header = CafeXWeb().get_web_element(self.locators.new_lead_page_header, explicit_wait=30).text
            if new_lead_header == "New Lead":
                self.reporting_object.insert_step(
                    "Click New Lead button and validate new lead page is opened",
                    f"New lead page header: '{new_lead_header}'",
                    "Pass"
                )
            else:
                self.reporting_object.insert_step(
                    "Click New Lead button and validate new lead page is opened",
                    f"Unexpected new lead page header: '{new_lead_header}'",
                    "Fail"
                )
            CafeXWeb().click(self.locators.new_lead_save_button, explicit_wait=20)
            default_lead_validation = CafeXWeb().get_web_element(self.locators.default_lead_validation,
                                                                explicit_wait=30).text
            if "hit" in default_lead_validation:
                self.reporting_object.insert_step(
                    "Save new lead with default data and validate",
                    f"Default lead validation message: '{default_lead_validation}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Save new lead with default data and validate",
                    f"Unexpected default lead validation message: '{default_lead_validation}'",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Create lead with default data",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            raise e

    def create_lead_with_data(self,table):
        try:
            rows = list(csv.DictReader(table.splitlines(), delimiter='|'))
            for row in rows:
                params = {key.strip(): value.strip() for key, value in row.items()}
                for field, value in params.items():
                    if not value and not field:
                        locator = self.locators.lead_data.replace('<<<replace_text>>>', field)
                        CafeXWeb().type(locator, value, explicit_wait=20)
                        if CafeXWeb().get_web_element(locator).get_attribute("value") == value:
                            self.reporting_object.insert_step(
                            f"Enter lead data for field '{field}'",
                            f"Successfully entered value '{value}' for field '{field}'",
                            "Pass"
                            )
                        else:
                            self.reporting_object.insert_step(
                            f"Enter lead data for field '{field}'",
                            f"Failed to enter value '{value}' for field '{field}'",
                            "Fail"
                            )
                CafeXWeb().click(self.locators.new_lead_save_button, explicit_wait=20)
        except Exception as e:
            self.reporting_object.insert_step(
                "Create lead with data",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            raise e

    def convert_lead(self):
        try:
            CafeXWeb().click(self.locators.lead_dropdown, explicit_wait=20)
            CafeXWeb().click(self.locators.lead_dropdown_option.replace('<<<replace_text>>>', 'Convert'), explicit_wait=20)
            convert_lead_header = CafeXWeb().get_web_element(self.locators.convert_lead_header, explicit_wait=30).text
            if convert_lead_header == "Convert Lead":
                self.reporting_object.insert_step(
                    "Select Convert option from lead dropdown and validate convert lead page is opened",
                    f"Convert lead page header: '{convert_lead_header}'",
                    "Pass"
                )
            else:
                self.reporting_object.insert_step(
                    "Select Convert option from lead dropdown and validate convert lead page is opened",
                    f"Unexpected convert lead page header: '{convert_lead_header}'",
                    "Fail"
                )
            CafeXWeb().click(self.locators.convert_button, explicit_wait=20)
            lead_convertion_validation = CafeXWeb().get_web_element(self.locators.lead_convertion_validation,
                                                                     explicit_wait=30).text
            if "converted" in lead_convertion_validation:
                self.reporting_object.insert_step(
                    "Convert lead and validate conversion message",
                    f"Lead conversion validation message: '{lead_convertion_validation}'",
                    "Pass"
                )
                CafeXWeb().click(self.locators.go_to_leads_button, explicit_wait=20)
                return True
            else:
                self.reporting_object.insert_step(
                    "Convert lead and validate conversion message",
                    f"Unexpected lead conversion validation message: '{lead_convertion_validation}'",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Convert lead and validate account, contact, and opportunity creation",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            raise e

    def set_stage_as_closed_won(self,stage,value)->bool:
        try:
            self.locators.stage_xpath = self.locators.stage_xpath.replace('<<<replace_text>>>', stage)
            self.locators.stage_select_closed_won = self.locators.stage_select_closed_won.replace('<<<replace_text>>>', value)
            CafeXWeb().click(self.locators.stage_xpath, explicit_wait=20)
            CafeXWeb().click(self.locators.stage_dropdown_path, explicit_wait=20)
            CafeXWeb().click(self.locators.stage_select_closed_won, explicit_wait=20)
            self.reporting_object.insert_step(
                "Set stage as Closed Won",
                "Successfully set stage as Closed Won",
                "Pass"
            )
            return True
        except Exception as e:
            self.reporting_object.insert_step(
                "Set stage as Closed Won",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            raise e

    def validate_stage_value(self,expected_stage)->bool:
        try:
            stage_value_locator = self.locators.stage_xpath.replace('<<<replace_text>>>', 'Stage')
            actual_stage = CafeXWeb().get_web_element(stage_value_locator, explicit_wait=20).text
            if actual_stage == expected_stage:
                self.reporting_object.insert_step(
                    "Validate stage value",
                    f"Expected stage: '{expected_stage}', Actual stage: '{actual_stage}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Validate stage value",
                    f"Expected stage: '{expected_stage}', Actual stage: '{actual_stage}'",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Validate stage value",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            raise e

    def go_to_opportunity_page(self):
        try:
            login_base_url = self.config_object.fetch_base_url()
            CafeXWeb().navigate(login_base_url)
            page_title = CafeXWeb().get_title()
            if CafeXWeb().get_title() == "Login | Salesforce":
                self.reporting_object.insert_step(
                    "Navigate to Salesforce login page and validate title",
                    f"Page title after navigation: '{page_title}'",
                    "Pass"
                )
            else:
                self.reporting_object.insert_step(
                    "Navigate to Salesforce login page and validate title",
                    f"Unexpected page title after navigation: '{page_title}'",
                    "Fail"
                )
            username, password = self.config_object.fetch_login_credentials("default_user")
            self.login_with_credentials(username, password)
            CafeXWeb().navigate(
                "https://orgfarm-153ddb4ae7-dev-ed.develop.lightning.force.com/lightning/o/Opportunity/list")
            time.sleep(5)
            page_header = CafeXWeb().get_web_element(self.locators.opportunity_header, explicit_wait=30).text
            if "Opportunities" in page_header:
                self.reporting_object.insert_step(
                    "Navigate to Opportunity page and validate header",
                    f"Page header after navigation: '{page_header}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Navigate to Opportunity page and validate header",
                    f"Unexpected page header after navigation: '{page_header}'",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Navigate to Opportunity page and validate header",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            raise e

    def select_opportunity(self,opportunity_name:str)->bool:
        try:
            opportunity_locator = self.locators.first_opportunity_link.replace("'<<<replace_text>>>'", opportunity_name)
            CafeXWeb().click(opportunity_locator, explicit_wait=20)
            opportunity_header = CafeXWeb().get_web_element(self.locators.opportunity_header).text
            if opportunity_header:
                self.reporting_object.insert_step(
                    f"Select opportunity '{opportunity_name}' and validate header",
                    f"Opportunity header displayed: '{opportunity_header}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    f"Select opportunity '{opportunity_name}' and validate header",
                    "Opportunity header not found after selection",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                f"Select opportunity '{opportunity_name}' and validate header",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            raise e


    def click_clone_button(self):
        try:
            CafeXWeb().click(self.locators.clone_button, explicit_wait=20)
            clone_page_header = CafeXWeb().get_web_element(self.locators.clone_page_header).text
            if "Opportunity Information" in clone_page_header:
                self.reporting_object.insert_step(
                    "Click clone button and validate clone page is opened",
                    f"Clone page header: '{clone_page_header}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Click clone button and validate clone page is opened",
                    f"Unexpected clone page header: '{clone_page_header}'",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Click clone button and validate clone page is opened",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            raise e


    def append_opportunity_name_with_clone_text(self):
        try:
            original_name = CafeXWeb().get_web_element(self.locators.opportunity_name_field,
                                                       explicit_wait=30).get_attribute("value")
            cloned_name = original_name + "-clone"
            CafeXWeb().type(self.locators.opportunity_name_field, cloned_name, clear=True)
            validate_name = CafeXWeb().get_web_element(
                self.locators.opportunity_name_field, explicit_wait=20
            ).get_attribute("value")
            if validate_name == cloned_name:
                self.reporting_object.insert_step(
                    "Append '-clone' to opportunity name and validate",
                    f"Original name: '{original_name}', updated name: '{validate_name}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Append '-clone' to opportunity name and validate",
                    f"Original name: '{original_name}', updated name: '{validate_name}' (expected: '{cloned_name}')",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Append '-clone' to opportunity name and validate",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            raise e


    def click_save_button(self):
        try:
            CafeXWeb().click(self.locators.save_opportunity_button, explicit_wait=20)
            new_opportunity_header = CafeXWeb().get_web_element(self.locators.opportunity_header, explicit_wait=20).text
            if new_opportunity_header:
                self.reporting_object.insert_step(
                    "Click save button and validate opportunity is saved",
                    f"Opportunity header after save: '{new_opportunity_header}'",
                    "Pass"
                )
            else:
                self.reporting_object.insert_step(
                    "Click save button and validate opportunity is saved",
                    "Opportunity header not found after save",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Click save button and validate opportunity is saved",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            return False



    def open_cloned_opportunity(self):
        try:
            CafeXWeb().click(self.locators.details_bar, explicit_wait=20)
            cloned_opportunity_name = CafeXWeb().get_web_element(self.locators.details_bar_validation,
                                                                 explicit_wait=20).text
            if cloned_opportunity_name:
                self.reporting_object.insert_step(
                    "Open cloned opportunity and validate name is displayed",
                    f"Cloned opportunity name displayed: '{cloned_opportunity_name}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Open cloned opportunity and validate name is displayed",
                    "Cloned opportunity name not found or not displayed",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Open cloned opportunity and validate name is displayed",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            return False


    def validate_cloned_opportunity_details(self):
        try:
            cloned_opportunity_name = CafeXWeb().get_web_element(self.locators.new_opportunity_name_field,
                                                                 explicit_wait=20).text
            if "-clone" in cloned_opportunity_name:
                self.reporting_object.insert_step(
                    "Validate cloned opportunity name contains '-clone'",
                    f"Cloned opportunity name is '{cloned_opportunity_name}' and contains '-clone'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Validate cloned opportunity name contains '-clone'",
                    f"Cloned opportunity name is '{cloned_opportunity_name}' but does not contain '-clone'",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Validate cloned opportunity name contains '-clone'",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            return False


    def click_note_button(self):
        try:
            CafeXWeb().click(self.locators.note_button, explicit_wait=20)
            time.sleep(10)
            note_dialog_header = CafeXWeb().get_web_element(self.locators.note_dialog_header, explicit_wait=30).text
            print(note_dialog_header)
            if note_dialog_header == "New Note":
                self.reporting_object.insert_step(
                    "Click note button and validate note dialog is opened",
                    f"Note dialog header: '{note_dialog_header}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Click note button and validate note dialog is opened",
                    f"Unexpected note dialog header: '{note_dialog_header}'",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Click note button and validate note dialog is opened",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            return False


    def enter_note_title_and_body(self,title,body):
        try:
            title = title.replace('"', "")
            body = body.replace('"', "")
            CafeXWeb().type(self.locators.note_title_field, title, explicit_wait=20)
            CafeXWeb().type(self.locators.note_body_field, body, explicit_wait=20)
            note_title = CafeXWeb().get_web_element(self.locators.note_title_field).get_attribute("value")
            if note_title:
                self.reporting_object.insert_step(
                    "Add note to opportunity and validate title",
                    f"Note title after entry: '{note_title}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Add note to opportunity and validate title",
                    f"Note title not found or empty after entry: '{note_title}'",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Add note to opportunity and validate title",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            return False


    def click_note_save_button(self):
        try:
            button=CafeXWeb().get_web_element(self.locators.save_note_button, explicit_wait=30)
            print(button)
            CafeXWeb().click(self.locators.save_note_button, explicit_wait=30)
            new_note_title = CafeXWeb().get_web_element(self.locators.note_title_field).get_attribute("value")
            print(new_note_title)
            if new_note_title:
                self.reporting_object.insert_step(
                    "Click save button and validate note is saved",
                    f"Note title after save: '{new_note_title}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Click save button and validate note is saved",
                    f"Note title not found or empty after save: '{new_note_title}'",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Click save button and validate note is saved",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            return False


    def open_new_note(self):
        try:
            CafeXWeb().click(self.locators.new_note_link, explicit_wait=20)
            new_note_title = CafeXWeb().get_web_element(self.locators.note_title_field).get_attribute("value")
            if new_note_title:
                self.reporting_object.insert_step(
                    "Open newly created note and validate title",
                    f"Note title after opening: '{new_note_title}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Open newly created note and validate title",
                    f"Note title not found or empty after opening: '{new_note_title}'",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Open newly created note and validate title",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            return False

    def validate_note_title(self, expected_title:str)->bool:
        try:
            expected_title = expected_title.replace('"', "")
            locator=self.locators.new_note_title_validation.replace('<<<replace_text>>>', expected_title)
            new_note_title = CafeXWeb().get_web_element(locator).get_attribute("value")
            if new_note_title == expected_title:
                self.reporting_object.insert_step(
                    "Validate note title matches expected value",
                    f"Expected: '{expected_title}', Actual: '{new_note_title}'",
                    "Pass"
                )
                return True
            else:
                self.reporting_object.insert_step(
                    "Validate note title matches expected value",
                    f"Expected: '{expected_title}', Actual: '{new_note_title}'",
                    "Fail"
                )
                return False
        except Exception as e:
            self.reporting_object.insert_step(
                "Validate note title matches expected value",
                f"Exception occurred: {str(e)}",
                "Fail"
            )
            return False










