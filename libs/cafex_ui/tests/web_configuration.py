class WebUnitTestConfiguration:
    # ------------------------------------ The Internet ------------------------------------
    internet_page_url = "http://the-internet.herokuapp.com/"
    add_or_remove_elements_link = "xpath=//a[normalize-space()='Add/Remove Elements']"
    add_or_remove_elements_header = "xpath=//h3[normalize-space()='Add/Remove Elements']"
    add_element_button = "xpath=//button[normalize-space()='Add Element']"
    add_element_parent = "xpath=//div[@id='elements']"
    add_element_search_locator = "xpath=//div[@id='elements']//button"
    add_element_button_1 = "xpath=//div[@id='elements']//button[1]"
    delete_element_button = "xpath=//button[normalize-space()='Delete']"
    context_menu_link = "xpath=//a[normalize-space()='Context Menu']"
    hotspot = "xpath=//div[@id='hot-spot']"
    drag_and_drop_link = "xpath=//a[normalize-space()='Drag and Drop']"
    drag_and_drop_column_a = "xpath=//div[@id='column-a']"
    drag_and_drop_column_b = "xpath=//div[@id='column-b']"
    horizontal_slider_link = "xpath=//a[normalize-space()='Horizontal Slider']"
    horizontal_slider = "xpath=//input[@type='range']"
    horizontal_slider_range_text = "xpath=//span[@id='range']"
    hovers_link = "xpath=//a[normalize-space()='Hovers']"
    hover_user_1 = "xpath=//div[@class='figure'][1]"
    hover_fig_caption_1 = "xpath=//div[@class='figure'][1]/div[@class='figcaption']"
    key_presses_link = "xpath=//a[normalize-space()='Key Presses']"
    key_presses_input = "xpath=//input[@id='target']"
    form_authentication_link = "xpath=//a[normalize-space()='Form Authentication']"
    form_username = "id=username"
    form_password = "id=password"
    username_xpath = "xpath=//input[@id='username']"
    flash_message = "xpath=//div[@id='flash']"
    form_login_button = "xpath=//button[normalize-space()='Login']"
    scroll_WYSIWYG_Editor_link = "xpath=//a[normalize-space()='WYSIWYG Editor']"
    to_get_all_links = "xpath=//a"
    dynamic_loading_start_button = "xpath=//button[normalize-space()='Start']"
    dynamic_loading_invsibility_element = "xpath=//div[@id='loading']"
    dynamic_loading_header = "xpath=//h4[normalize-space()='Hello World!']"
    dynamic_content_header = "xpath=//h3[normalize-space()='Dynamic Content']"
    flash_messages_locator = "xpath=//div[@id='flash-messages']"
    windows_page_link = "http://the-internet.herokuapp.com/windows"
    windows_click_here_link = "xpath=//a[normalize-space()='Click Here']"
    mutiple_windows_link = "xpath=//a[normalize-space()='Multiple Windows']"
    frames_link = "xpath=//a[normalize-space()='Frames']"
    iframe_link = "xpath=//a[normalize-space()='iFrame']"
    iframe_header_check = "xpath=//h3[normalize-space()='An iFrame containing the TinyMCE WYSIWYG Editor']"
    iframe_body = "xpath=//body[@id='tinymce']"
    javascript_alerts_link = "xpath=//a[normalize-space()='JavaScript Alerts']"
    javascript_alerts_button = "xpath=//button[normalize-space()='Click for JS Alert']"
    javascript_alerts_prompt_button = "xpath=//button[normalize-space()='Click for JS Prompt']"
    javascript_alerts_confirm_button = "xpath=//button[normalize-space()='Click for JS Confirm']"
    javascript_result = "xpath=//p[@id='result']"
    drop_down_link = "xpath=//a[normalize-space()='Dropdown']"
    dropdown_id = "id=dropdown"
    home_page_header = "xpath=//h1[normalize-space()='Welcome to the-internet']"
    elemental_selenium_link = "xpath=//a[normalize-space()='Elemental Selenium']"
    broken_images_link = "http://the-internet.herokuapp.com/broken_images"
    javascript_error_page_link = "http://the-internet.herokuapp.com/javascript_error"

    # ------------------------------------ JQuery UI ------------------------------------
    jquery_droppable_page_url = "https://jqueryui.com/droppable/"
    jquery_draggable_object = "xpath=//div[@id='draggable']"
    jquery_droppable_object = "xpath=//div[@id='droppable']"

    # -----------------------------------------Google Search Page-----------------------------------------
    google_search_url = "https://www.google.com/"
    google_search_textbox = "xpath=//textarea[@id='APjFqb']"
    google_doodles_button = "xpath=//div[@class='FPdoLc lJ9FBc']//input[@name='btnI']"
    google_doodles_page = "https://doodles.google/"
    google_store_xpath = "xpath=//a[normalize-space()='Store']"
    google_about_xpath = "xpath=//a[normalize-space()='About']"

    # ---------------------------------------------w3 schools---------------------------------------------
    w3schools_multiselect_page = "https://www.w3schools.com/tags/tryit.asp?filename=tryhtml_select_multiple"
    dropdown_xpath = "xpath=//select[@name='cars']"
    dropdown_option_1 = "xpath=//select[@id='cars']/option[1]"

    # ---------------------------------------------cosmocode page---------------------------------------------
    cosmocode_page = "https://cosmocode.io/automation-practice-webtable/"
    countries_table_row_locator = "xpath=//*[@id='countries']/tbody/tr"

    # ---------------------------------------------tutorialspoint page---------------------------------------------
    tutorialspoint_page = "https://www.tutorialspoint.com/selenium/practice/webtables.php"
    tutorialspoint_page_row_locator = "xpath=/html/body/main/div/div/div[2]/form/div[2]/table/tbody/tr"
    tutorialspoint_page_headers_locator = "xpath=/html/body/main/div/div/div[2]/form/div[2]/table/thead/tr/th"

    # -------------------------------------------------browsertack_options---------------------------------------------
    browserstack_username = "xxxxxxxxxxxxxxxxxxxxxxxxx"
    browserstack_access_key = "xxxxxxxxxxxxxxxxxxxxxxxxxx"
    browserstack_safari_options = {'projectName': 'Web Automation Demo',
                                   'buildName': 'Web Automation Demo',
                                   'sessionName': 'UI Automation Demo', 'local': False,
                                   'os': 'OS X', 'osVersion': 'Monterey', 'browserVersion': '15.6'}
    browserstack_chrome_options = {'projectName': 'Web Automation Demo',
                                   'buildName': 'Web Automation Demo',
                                   'sessionName': 'UI Automation Demo', 'local': False,
                                   'os': 'Windows', 'osVersion': '10',
                                   'browserVersion': '130.0'}
    browserstack_edge_or_firefox_options = {'projectName': 'Web Automation Demo',
                                 'buildName': 'Web Automation Demo',
                                 'sessionName': 'UI Automation Demo', 'local': False,
                                 'os': 'Windows', 'osVersion': '10',
                                 'browserVersion': 'latest'}

    # --------------selenium_grid_url---------------------------------------------
    selenium_grid_url = "http://localhost:4444"
    proxy_link = "http://example.proxy.com"
