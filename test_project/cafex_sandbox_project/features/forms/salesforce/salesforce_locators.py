class SalesforceLocators:
    username_field = 'xpath=//input[@id="username"]'
    password_field = 'xpath=//input[@id="password"]'
    login_field = 'xpath=//input[@id="Login"]'
    error_field = 'xpath=//div[@id="error"]'
    search_field = 'xpath=//button[normalize-space()="Search..."]'
    leads_header="xpath=//p[@class='slds-page-header__name-meta']"
    new_lead_button = "xpath=//button[normalize-space()='New']"
    new_lead_page_header = "xpath=//h2[normalize-space()='New Lead']"
    new_lead_save_button = "xpath=//button[normalize-space()='Save']"
    default_lead_validation = "xpath=//h2[normalize-space()='We hit a snag.']"
    lead_data= "xpath=//label[span[text()='<<<replace_text>>>']]/following-sibling::input"
    lead_dropdown="xpath=//lightning-button-menu[@class='menu-button-item slds-dropdown_actions slds-dropdown-trigger slds-dropdown-trigger_click']//lightning-primitive-icon[@variant='bare']//*[name()='svg']"
    lead_dropdown_option="xpath=//span[normalize-space()='<<<replace_text>>>']"
    convert_button = "xpath=//button[normalize-space()='Convert']"
    convert_lead_header = "xpath=(//h1[normalize-space()='Convert Lead'])[1]"
    lead_convertion_validation = "xpath=/h2[normalize-space()='Your lead has been converted']"
    go_to_leads_button = "xpath=//button[normalize-space()='Go to Leads']"
    stage_xpath = "xpath=//td[@data-label='Stage']//button[@data-action-edit='true']"
    stage_dropdown_path="xpath=//div[contains(@class, 'dropdown-trigger')]"
    stage_select_closed_won="xpath=//span[text()='Closed Won']"


    # Locators for clone of opportunity
    opportunity_tab_field = "xpath=//a[@title='Opportunities']"
    opportunity_header = "xpath=//h1[normalize-space()='Opportunities']"
    first_opportunity_link = "xpath=//a[@title='<<<replace_text>>>']"
    clone_button = "xpath=//button[@name='Clone']"
    clone_page_header = "xpath=//span[normalize-space()='Opportunity Information']"
    opportunity_name_field = "xpath=//input[@name='Name']"
    save_opportunity_button = "xpath=//button[@name='SaveEdit']"
    details_bar = "xpath=(//a[@id='detailTab__item'])[2]"
    details_bar_validation = "xpath=//span[normalize-space()='Opportunity Owner']"
    new_opportunity_name_field = "xpath=(//span[@class='test-id__field-value slds-form-element__static slds-grow word-break-ie11'])[3]"

    #adding new note to opportunity locators
    note_button = "xpath=//button[@class='slds-button slds-button_neutral'][normalize-space()='New Note']"
    note_dialog_header = "xpath=//h2[normalize-space()='New Note']"
    note_title_field = "xpath=//label[span[text()='Title']]/following-sibling::input"
    note_body_field = "xpath=//label[span[text()='Body']]/following-sibling::textarea"
    save_note_button = "xpath=(//button[@class='slds-button slds-button_brand cuf-publisherShareButton undefined uiButton'])[1]"
    new_note_link = "xpath=//div[@class='slds-size_12-of-12 slds-grid slds-nowrap']"
    new_note_title_validation = "xpath=//span[@title='<<<replace_text>>>']"



