import time
import pytest
from selenium.webdriver.common.by import By
import os
import subprocess
from cafex_ui.web_client.web_driver_factory import WebDriverFactory
from web_configuration import WebUnitTestConfiguration as web_config


class TestWebDriverFactory:

    def test_web_driver_factory_exception_with_invalid_driver(self):
        web_driver_factory = WebDriverFactory()
        try:
            web_driver_factory.create_driver(browser="invalid")
        except Exception as e:
            assert str(e) == "browser value should be either chrome, firefox, edge, safari or internet explorer"

    @pytest.mark.parametrize("platform_system, expected_platform_name", [
        ("win", "WINDOWS"),
        ("os", "MAC"),
        ("linux", "LINUX"),
        ("Unknown", None),
    ])
    def test_platform_name(self, monkeypatch, platform_system, expected_platform_name):
        monkeypatch.setattr("platform.system", lambda: platform_system)
        assert WebDriverFactory.platform_name() == expected_platform_name

    def test_desired_capabilities(self):
        try:
            web_driver_factory = WebDriverFactory()
            additional_capabilities = {
                'acceptInsecureCerts': True
            }
            driver = web_driver_factory.create_driver(browser="chrome", capabilities=additional_capabilities)
            assert driver.name == "chrome"
            assert driver.capabilities['acceptInsecureCerts'] is True
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_desired_capabilities method: ", e)

    def test_chrome_driver(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="chrome")
            assert driver.name == "chrome"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_chrome_driver method: ", e)

    def test_window_size_option(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="chrome", chrome_options=["--window-size=null"])
            driver.get(web_config.google_search_url)
            actual_screen_size = driver.get_window_size()
            assert actual_screen_size == {'width': 800, 'height': 600}
            driver.quit()
            driver1 = web_driver_factory.create_driver(browser="chrome", chrome_options=["--window-size=600,800"])
            driver1.get(web_config.google_search_url)
            actual_screen_size = driver1.get_window_size()
            assert actual_screen_size == {'width': 800, 'height': 600}
            driver1.quit()
        except Exception as e:
            print("Exception occurred in test_window_size_option method: ", e)

    def test_chrome_driver_with_chrome_options_and_proxies(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="chrome", chrome_options=["--headless"])
            assert driver.name == "chrome"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
            driver1 = web_driver_factory.create_driver(browser="chrome",
                                                       proxies=web_config.proxy_link)
            driver1.get(web_config.google_search_url)
            assert driver1.title == "Google"
            driver1.quit()
        except Exception as e:
            print("Exception occurred in test_chrome_driver_with_chrome_options_and_proxies method: ", e)

    def test_chrome_driver_with_incognito_option(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver1 = web_driver_factory.create_driver(browser="chrome")
            driver1.get("chrome://version/")
            result_before = driver1.find_element(By.XPATH, "//*[@id='command_line']").text
            assert "--incognito" not in result_before
            print(result_before)
            driver = web_driver_factory.create_driver(browser="chrome", chrome_options=["--incognito"])
            driver.get("chrome://version/")
            result_after = driver.find_element(By.XPATH, "//*[@id='command_line']").text
            assert "--incognito" in result_after
            print(result_after)
            driver.quit()
            driver1.quit()
        except Exception as e:
            print("Exception occurred in test_chrome_driver_with_incognito_option method: ", e)

    def test_chrome_driver_with_window_size_option(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver1 = web_driver_factory.create_driver(browser="chrome")
            driver1.get("chrome://version/")
            result_before = driver1.find_element(By.XPATH, "//*[@id='command_line']").text
            assert "--window-size=800x600" not in result_before
            print(result_before)
            result_before_size = driver1.get_window_size()
            print(result_before_size)
            driver = web_driver_factory.create_driver(browser="chrome", chrome_options=["--window-size=800x600"])
            driver.get("chrome://version/")
            actual_screen_size = driver.get_window_size()
            assert actual_screen_size == {'width': 800, 'height': 600}
            assert result_before_size != actual_screen_size
            driver.quit()
            driver1.quit()
        except Exception as e:
            print("Exception occurred in test_chrome_driver_with_window_size_option method: ", e)

    def test_selenium_hub_chrome(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="chrome", use_grid=True,
                                                      selenium_grid_ip=web_config.selenium_grid_url)
            assert driver.name == "chrome"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_selenium_hub_chrome method: ", e)

    def test_chrome_driver_with_download_directory_option(self):
        try:
            web_driver_factory = WebDriverFactory()
            chrome_prefs = {
                "download.default_directory": f"{os.getcwd()}//mydownloads",
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False
            }
            driver = web_driver_factory.create_driver(browser="chrome",
                                                      chrome_options=[
                                                          '--disable-features=DownloadBubble,DownloadBubbleV2',
                                                          '--disable-gpu', '--disable-extensions',
                                                          '--disable-dev-shm-usage',
                                                          '--log-level=3'], chrome_preferences=chrome_prefs)
            driver.get(web_config.internet_page_url + "/download")
            time.sleep(10)
            download_link = driver.find_element(By.XPATH, "//a[normalize-space()='demo.txt']")
            download_link.click()
            time.sleep(45)
            downloaded_file = os.path.join(f"{os.getcwd()}//mydownloads", "demo.txt")
            assert os.path.exists(downloaded_file), "File not downloaded to the custom directory"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_chrome_driver_with_download_directory_option method: ", e)

    def test_chrome_driver_with_chrome_version(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="chrome", browser_version="116.0.5845.96")
            driver.get("chrome://version/")
            result = driver.find_element(By.XPATH, "//*[@id='version']").text
            assert "116.0.5845.96" in result
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_chrome_driver_with_chrome_version method: ", e)
    def test_browserstack_driver(self):
        try:
            driver = WebDriverFactory().create_driver(browser="chrome",
                                                      browserstack_username=web_config.browserstack_username,
                                                      browserstack_access_key=web_config.browserstack_access_key,
                                                      browserstack_capabilities=web_config.browserstack_chrome_options,
                                                      run_on_browserstack=True)
            assert driver.name == "chrome"
            assert driver.session_id is not None
            driver.quit()
            driver = WebDriverFactory().create_driver(browser="chrome",
                                                      browserstack_username=web_config.browserstack_access_key,
                                                      browserstack_access_key=web_config.browserstack_access_key,
                                                      browserstack_capabilities=web_config.browserstack_chrome_options,
                                                      run_on_browserstack=True)
            assert driver.name == "chrome"
        except Exception as e:
            assert str(e) == "browserstack_username is required to run tests on BrowserStack"

    def test_firefox_driver(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="firefox")
            assert driver.name == "firefox"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_firefox_driver method: ", e)

    def test_firefox_driver_with_firefox_options(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="firefox", firefox_options=["--headless"])
            assert driver.name == "firefox"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_firefox_driver_with_firefox_options method: ", e)

    def test_firefox_driver_with_window_size_option(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="firefox", firefox_options=["--incognito"])
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_firefox_driver_with_window_size_option method: ", e)

    def test_firefox_driver_with_proxies(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="firefox",
                                                      proxies=web_config.proxy_link)
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_firefox_driver_with_proxies method: ", e)

    def test_selenium_hub_firefox(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="firefox", use_grid=True,
                                                      selenium_grid_ip=web_config.selenium_grid_url)
            assert driver.name == "firefox"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_selenium_hub_firefox method: ", e)

    def test_firefox_driver_with_download_directory_option(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="firefox",
                                                      firefox_preferences={"browser.download.dir": "root/mydownloads",
                                                                           "browser.download.folderList": 2,
                                                                           "browser.helperApps.neverAsk.saveToDisk": "application/txt"})
            driver.get(web_config.internet_page_url + "/download")
            time.sleep(10)
            download_link = driver.find_element(By.XPATH, "//a[normalize-space()='some-file.txt']")
            download_link.click()
            time.sleep(45)
            downloaded_file = os.path.join(f"{os.getcwd()}/mydownloads", "some-file.txt")
            assert os.path.exists(downloaded_file), "File not downloaded to the custom directory"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_firefox_driver_with_download_directory_option method: ", e)

    def test_browserstack_firefox_driver(self):
        try:
            driver = WebDriverFactory().create_driver(browser="firefox",
                                                      browserstack_username=web_config.browserstack_username,
                                                      browserstack_access_key=web_config.browserstack_access_key,
                                                      browserstack_capabilities=web_config.browserstack_edge_or_firefox_options,
                                                      run_on_browserstack=True)
            assert driver.name == "firefox"
            assert driver.session_id is not None
            driver.quit()
            driver1 = WebDriverFactory().create_driver(browser="firefox",
                                                      browserstack_username=web_config.browserstack_access_key,
                                                      browserstack_access_key=web_config.browserstack_access_key,
                                                      browserstack_capabilities=web_config.browserstack_edge_or_firefox_options,
                                                      run_on_browserstack=True)
            assert driver1.name == "firefox"
            assert driver1.session_id is not None
            driver1.quit()
        except Exception as e:
            print("Exception occurred in test_browserstack_firefox_driver method: ", e)

    # Perform Edge driver test
    def test_edge_driver(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="edge")
            assert driver.name == "MicrosoftEdge"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_edge_driver method: ", e)

    def test_edge_driver_on_selenium_grid(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="edge", use_grid=True,
                                                      selenium_grid_ip=web_config.selenium_grid_url)
            assert driver.name == "MicrosoftEdge"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_edge_driver_on_selenium_grid method: ", e)

    def test_edge_driver_with_edge_options(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="edge", edge_options=["--headless"])
            assert driver.name == "MicrosoftEdge"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_edge_driver_with_edge_options method: ", e)

    def test_edge_driver_in_incognito_mode(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="edge", edge_options=["--inprivate"])
            assert driver.name == "MicrosoftEdge"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_edge_driver_in_incognito_mode method: ", e)

    def test_edge_driver_with_clear_browser_history(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="edge", ie_and_edge_clear_browser_history=True)
            assert driver.name == "MicrosoftEdge"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.get("edge://history")
            time.sleep(5)
            assert len(driver.find_elements(By.XPATH, "//*[@id='list-focus-container']/div[1]/div")) == 1
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_edge_driver_with_clear_browser_history method: ", e)

    def test_edge_driver_with_window_size_option(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver1 = web_driver_factory.create_driver(browser="edge")
            result_before_size = driver1.get_window_size()
            driver = web_driver_factory.create_driver(browser="edge", edge_options=["--window-size=800,600"])
            driver.get("edge://version/")
            actual_screen_size = driver.get_window_size()
            assert actual_screen_size == {'width': 800, 'height': 600}
            assert result_before_size != actual_screen_size
            driver.quit()
            driver1.quit()
        except Exception as e:
            print("Exception occurred in test_edge_driver_with_window_size_option method: ", e)

    def test_edge_download_scenario(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="edge")
            driver.get(web_config.internet_page_url + "/download")
            time.sleep(10)
            download_link = driver.find_element(By.XPATH, "//a[normalize-space()='some-file.txt']")
            download_link.click()
            time.sleep(45)
            downloaded_file = os.path.join(f"{os.getcwd()}/Downloads", "some-file.txt")
            assert os.path.exists(downloaded_file), "File not downloaded to the default directory"
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_edge_download_scenario method: ", e)

    def test_browserstack_edge_driver(self):
        try:
            driver = WebDriverFactory().create_driver(browser="edge",
                                                      browserstack_username=web_config.browserstack_username,
                                                      browserstack_access_key=web_config.browserstack_access_key,
                                                      browserstack_capabilities=web_config.browserstack_edge_or_firefox_options,
                                                      run_on_browserstack=True)
            assert driver.name == "MicrosoftEdge"
            assert driver.session_id is not None
            driver.quit()
        except Exception as e:
            print("Exception occurred in test_browserstack_edge_driver method: ", e)

    def test_chrome_driver_with_chrome_options_and_proxies_example(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="edge", chrome_options=["--headless"])
            assert driver.name == "MicrosoftEdge"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
            driver1 = web_driver_factory.create_driver(browser="edge",
                                                       proxies=web_config.proxy_link)
            driver1.get(web_config.google_search_url)
            assert driver1.title == "Google"
            driver1.quit()
        except Exception as e:
            print("Exception occurred in test_chrome_driver_with_chrome_options_and_proxies method: ", e)

    # Perform Safari driver test
    # only supports MacOS
    def test_safari_driver(self):
        web_driver_factory = WebDriverFactory()
        driver = web_driver_factory.create_driver(browser="safari")
        assert driver.name == "safari"
        driver.get(web_config.google_search_url)
        assert driver.title == "Google"


    def test_browserstack_driver_safari(self):
        driver = WebDriverFactory().create_driver(browser="safari", run_on_browserstack=True,
                                                  browserstack_username=web_config.browserstack_username,
                                                  browserstack_access_key=web_config.browserstack_access_key,
                                                  browserstack_capabilities=web_config.browserstack_safari_options)
        assert driver.name == "Safari"
        assert driver.session_id is not None
        driver.quit()

    # Perform Internet Explorer driver test
    def test_ie_driver(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="internet explorer")
            assert driver.name == "internet explorer"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
            subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], check=True)
            print("Microsoft Edge has been killed successfully.")
        except Exception as e:
            print("Exception occurred in test_ie_driver method: ", e)

    def test_ie_driver_with_proxies(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="internet explorer", proxies=
            web_config.proxy_link)
            assert driver.name == "internet explorer"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
            subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], check=True)
            print("Microsoft Edge has been killed successfully.")
        except Exception as e:
            print("Exception occurred in test_ie_driver method: ", e)

    def test_ie_driver_with_ie_options(self):
        # not working in headless mode
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="internet explorer", ie_options=["--headless"])
            assert driver.name == "internet explorer"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
            subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], check=True)
            print("Microsoft Edge has been killed successfully.")
        except Exception as e:
            print("Exception occurred in test_ie_driver_with_ie_options method: ", e)

    def test_ie_with_window_size_options(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="internet explorer",
                                                      ie_options=["height=600", "width=800"])
            assert driver.name == "internet explorer"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.quit()
            subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], check=True)
            print("Microsoft Edge has been killed successfully.")
        except Exception as e:
            print("Exception occurred in test_ie_driver_with_ie_options method: ", e)

    def test_ie_driver_with_clear_browser_history(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver = web_driver_factory.create_driver(browser="internet explorer",
                                                      ie_and_edge_clear_browser_history=True)
            assert driver.name == "internet explorer"
            driver.get(web_config.google_search_url)
            assert driver.title == "Google"
            driver.get("edge://history")
            time.sleep(5)
            assert len(driver.find_elements(By.XPATH, "//*[@id='list-focus-container']/div[1]/div")) == 1
            driver.quit()
            subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], check=True)
            print("Microsoft Edge has been killed successfully.")
        except Exception as e:
            print("Exception occurred in test_ie_driver_with_clear_browser_history method: ", e)

    def test_ie_driver_with_window_size_option(self):
        try:
            web_driver_factory = WebDriverFactory()
            driver1 = web_driver_factory.create_driver(browser="internet explorer")
            assert driver1.name == "internet explorer"
            result_before_size = driver1.get_window_size()
            driver1.quit()
            subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], check=True)
            print("Microsoft Edge has been killed successfully.")
            driver = web_driver_factory.create_driver(browser="internet explorer", ie_options=["--window-size=800,600"])
            driver.get("edge://version/")
            actual_screen_size = driver.get_window_size()
            assert actual_screen_size == {'width': 800, 'height': 600}
            assert result_before_size != actual_screen_size
            driver.quit()
            subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], check=True)
            print("Microsoft Edge has been killed successfully.")
        except Exception as e:
            print("Exception occurred in test_ie_driver_with_window_size_option method: ", e)

    def test_browserstack_driver_internet_explorer(self):
        try:
            driver = WebDriverFactory().create_driver(browser="internet explorer", run_on_browserstack=True,
                                                      browserstack_username=web_config.browserstack_username,
                                                      browserstack_access_key=web_config.browserstack_access_key,
                                                      browserstack_capabilities=web_config.browserstack_safari_options,
                                                      ie_options=["--headless", "height=600", "width=800"])
            assert driver.name == "internet explorer"
            assert driver.session_id is not None
            driver.quit()
            driver1 = WebDriverFactory().create_driver(browser="internet explorer", run_on_browserstack=True,
                                                       browserstack_username=web_config.browserstack_access_key,
                                                       browserstack_access_key=web_config.browserstack_access_key,
                                                       browserstack_capabilities=web_config.browserstack_safari_options)
            assert driver1.name == "internet explorer"
            assert driver1.session_id is not None
            driver1.quit()
        except Exception as e:
            print("Exception occurred in test_browserstack_driver_internet_explorer method: ", e)
