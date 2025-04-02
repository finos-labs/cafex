import time

import pandas as pd
import requests
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.config_utils import ConfigUtils
from cafex_ui.web_client.web_client_actions.element_interactions import (
    ElementInteractions,
)
from cafex_ui.web_client.web_client_actions.webdriver_interactions import (
    WebDriverInteractions,
)


class UtilityMethods:
    """This class contains methods to perform various operations on a browser
    and its elements."""

    def __init__(
            self,
            web_driver: WebDriver = None,
            default_explicit_wait: int = None,
            default_implicit_wait: int = None,
    ):
        """Initializes WebClientActions with a driver and optional explicit
        wait.

        Args:
            web_driver: The selenium webdriver instance.
                            if not provided, it will be picked from Session Store
            default_explicit_wait: The default explicit wait time (in seconds).
                                   If not provided, it will be retrieved from ConfigUtils.
        """
        self.default_explicit_wait = default_explicit_wait or ConfigUtils().get_explicit_wait()
        self.default_implicit_wait = default_implicit_wait or ConfigUtils().get_implicit_wait()
        self.driver = web_driver or SessionStore().storage.get("driver")
        self.logger = CoreLogger(name=__name__).get_logger()
        self.navigate_methods = WebDriverInteractions(
            web_driver=self.driver,
            default_explicit_wait=self.default_explicit_wait,
            default_implicit_wait=self.default_implicit_wait,
        )
        self.element_interactions = ElementInteractions(
            web_driver=self.driver,
            default_explicit_wait=self.default_explicit_wait,
            default_implicit_wait=self.default_implicit_wait,
        )

    def get_webtable_data_into_dataframe(self, pstr_row_locator: str, **kwargs) -> pd.DataFrame:
        """Fetch all the data from a web table into a DataFrame format. If a
        header locator is provided, column names will be header names.
        Otherwise, column names will be integers starting from 0.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_webtable_data_into_dataframe('xpath=//*[@id="leftcontainer"]/table/tbody/tr')
            >> CafeXWeb().get_webtable_data_into_dataframe('xpath=//*[@id="rightcontainer"]/table/tbody/tr',
            pstr_header_locator='xpath=//*[@id="leftcontainer"]/table/thead/tr/th')

        Args:
            pstr_row_locator: Web Table tr xpath.
            **kwargs: Additional keyword arguments:
                - pstr_header_locator: Table Header locator.
                - df_row: Row information.
                - df_column: Column information.

        Returns:
            A DataFrame containing the web table data.
        """
        try:
            if kwargs.get("pstr_header_locator") is not None:
                pstr_header_locator = kwargs.get("pstr_header_locator")
                if len(self.element_interactions.get_web_elements(pstr_header_locator)) > 1:
                    lst_row_data = self.get_webtable_all_data_into_list(pstr_row_locator)
                    lst_header_names = self.webtable_header_into_list(pstr_header_locator)
                    df_table_data = pd.DataFrame(lst_row_data, columns=lst_header_names)
                else:
                    raise Exception("Header count is zero, kindly provide correct header locator")
            else:
                lst_row_data = self.get_webtable_all_data_into_list(pstr_row_locator)
                df_table_data = pd.DataFrame(lst_row_data)

            if kwargs.get("df_row") is None and kwargs.get("df_column") is None:
                return df_table_data
            else:
                df_table_data = self.fetch_data_from_dataframe(
                    kwargs.get("df_row"), kwargs.get("df_column"), df_table_data
                )
                return df_table_data
        except Exception as e:
            self.logger.exception(
                "Exception in get_webtable_data_into_dataframe method. Exception Details: ",
                exc_info=e,
            )
            raise e

    def fetch_data_from_dataframe(self, row_no: str, col_no: str, pdf_webtable_df):
        """Fetch data from the web table DataFrame based on the user input for
        row and column numbers.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().fetch_data_from_dataframe(1, 2, df_webtable)

        Args:
            row_no: Row information.
            col_no: Column information.
            pdf_webtable_df: DataFrame containing the web table data.

        Returns:
            A DataFrame containing the fetched data.
        """
        try:
            str_row_string1, str_row_string2 = self.__format_row_and_column(row_no)
            str_col_string1, str_col_string2 = self.__format_row_and_column(col_no)
            if isinstance(col_no, int) and isinstance(
                    row_no, int
            ):  # Fetch data by row & column numbers
                df_webtable_data = pdf_webtable_df.iloc[row_no, col_no]
            elif (
                    type(row_no) is int and type(col_no) is str
            ):  # Fetch all the columns and specific rows
                df_webtable_data = pdf_webtable_df.head(row_no)
            elif isinstance(col_no, list) and isinstance(
                    row_no, list
            ):  # Fetch specific rows and columns
                if isinstance(str_col_string1[0], str):
                    df_webtable_data = pdf_webtable_df.loc[row_no, col_no]
                else:
                    df_webtable_data = pdf_webtable_df.iloc[row_no, col_no]
            else:
                if row_no == "all":
                    if str_col_string2 is None:
                        if isinstance(str_col_string1[0], str):
                            df_webtable_data = pdf_webtable_df.loc[:, str_col_string1]
                        else:
                            df_webtable_data = pdf_webtable_df.iloc[:, str_col_string1]
                    else:
                        if isinstance(str_col_string1, str):
                            df_webtable_data = pdf_webtable_df.loc[
                                               :, str_col_string1:str_col_string2
                                               ]
                        else:
                            df_webtable_data = pdf_webtable_df.iloc[
                                               :, str_col_string1:str_col_string2
                                               ]
                elif col_no == "all":
                    if str_row_string2 is None:
                        df_webtable_data = pdf_webtable_df.iloc[str_row_string1, :]
                    else:
                        df_webtable_data = pdf_webtable_df.iloc[str_row_string1:str_row_string2, :]
                elif str_row_string2 is None:
                    df_webtable_data = pdf_webtable_df.iloc[
                                       str_row_string1, str_col_string1:str_col_string2
                                       ]
                elif str_col_string2 is None:
                    if isinstance(str_col_string1[0], str):
                        df_webtable_data = pdf_webtable_df.loc[
                                           str_row_string1:str_row_string2, str_col_string1
                                           ]
                    else:
                        df_webtable_data = pdf_webtable_df.iloc[
                                           str_row_string1:str_row_string2, str_col_string1
                                           ]
                else:
                    if isinstance(str_col_string1, str):
                        df_webtable_data = pdf_webtable_df.loc[
                                           str_row_string1:str_row_string2, str_col_string1:str_col_string2
                                           ]
                    else:
                        df_webtable_data = pdf_webtable_df.iloc[
                                           str_row_string1:str_row_string2, str_col_string1:str_col_string2
                                           ]
            return df_webtable_data
        except Exception as e:
            self.logger.exception(
                "Exception in fetch_data_from_dataframe method. Exception Details: ", exc_info=e
            )
            raise e

    def __format_row_and_column(self, pstr_row_col):
        """Format the row or column passed by the user to suit the DataFrame
        format.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().format_row_and_column("1:5")
            >> CafeXWeb().format_row_and_column(["1", "2", "3"])

        Args:
            pstr_row_col: Row or column string.

        Returns:
            A tuple containing formatted row and column strings.
        """
        try:
            if isinstance(pstr_row_col, list):
                return pstr_row_col, None  # if it is list then return the string as it is
            elif pstr_row_col == "all":
                return None, None
            if ":" in str(pstr_row_col):
                if type(eval(pstr_row_col.split(":")[0])) is int:
                    return eval(pstr_row_col.split(":")[0]), eval(pstr_row_col.split(":")[1])
            else:
                return None, None
        except (ValueError, SyntaxError, NameError):
            return pstr_row_col.split(":")[0], pstr_row_col.split(":")[1]
        except Exception as e:
            self.logger.exception(
                "Exception in format_row_and_column method. Exception Details: ", exc_info=e
            )
            raise e

    def webtable_header_into_list(self, pstr_header_locator: str) -> list:
        """Read the headers from a web table and return them as a list.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().webtable_header_into_list("xpath=/html/body/table/tbody/tr/th")

        Args:
            pstr_header_locator: The locator for the table headers.

        Returns:
            A list containing the header names.
        """
        try:
            lst_header_data = []
            for int_header_cnt in range(
                    len(self.element_interactions.get_web_elements(pstr_header_locator))
            ):
                str_header_full_locator = f"{pstr_header_locator}[{int_header_cnt + 1}]"
                str_header_data = self.element_interactions.get_web_element(
                    str_header_full_locator
                ).text
                lst_header_data.append(str_header_data)
            return lst_header_data
        except Exception as e:
            self.logger.exception(
                "Exception in webtable_header_into_list method. Exception Details: ", exc_info=e
            )
            raise e

    def wait_until_file_download(
            self,
            current_execution_browser: str,
            explicit_wait: int,
            frequency_poll_time: int,
            parent_window_handle: int = 0,
    ):
        """Wait until a file gets downloaded.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().wait_until_file_download("chrome", 120, 1)

        Args:
            current_execution_browser: The browser in which the file is getting downloaded.
            explicit_wait: The time (in seconds) to wait for the file to be downloaded.
            frequency_poll_time: The frequency (in seconds) to check the download status of the file.
            parent_window_handle: The parent window handle (default is 0).

        Returns:
            None
        """
        try:
            current_execution_browser = (
                    current_execution_browser or ConfigUtils().fetch_current_browser()
            )
            explicit_wait = explicit_wait or self.default_explicit_wait
            if current_execution_browser.lower() == "chrome":
                paths = WebDriverWait(
                    current_execution_browser, explicit_wait, frequency_poll_time
                ).until(lambda driver: self.__check_download_status())
                if paths is not None:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[parent_window_handle])
        except Exception as e:
            self.logger.exception(
                "Exception in wait_until_file_download method. Exception Details: ", exc_info=e
            )
            raise e

    def __check_download_status(self) -> list:
        """
        Check the download status in the Chrome browser. It opens a new tab with the 'chrome://downloads/' URL if not
        already open and retrieves the download status.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().__check_download_status()

        Returns:
            A list of file URLs that have been downloaded.
        """
        try:
            if not self.driver.current_url.startswith("chrome://downloads"):
                self.driver.execute_script("window.open('');")
                get_handles = self.driver.window_handles
                self.driver.switch_to.window(self.driver.window_handles[len(get_handles) - 1])
                self.driver.get("chrome://downloads/")
            return self.driver.execute_script(
                """
                var items = document.querySelector('downloads-manager')
                    .shadowRoot.getElementById('downloadsList').items;
                if (items.every(e => e.state == "COMPLETE" || e.state == 2))
                    return items.map(e => e.fileUrl || e.file_url);
                """
            )
        except Exception as e:
            self.logger.exception(f"Error in the __check_download_status method. Error: {str(e)}")
            raise e

    def check_stale_element_exception(self, locator: str) -> bool:
        """Check for stale element exception and attempt to click the element
        up to three times.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().check_stale_element_exception("xpath=//*[@id='element']")

        Args:
            locator: The locator of the element.

        Returns:
            A boolean indicating whether the element was successfully clicked.
        """
        try:
            done_stale_element_check = False
            attempts = 0
            while attempts < 3:
                try:
                    self.element_interactions.get_web_element(locator).click()
                    done_stale_element_check = True
                    break
                except StaleElementReferenceException:
                    pass
                attempts += 1
            return done_stale_element_check
        except Exception as e:
            self.logger.exception(
                f"Error in the check_stale_element_exception method. Error: {str(e)}"
            )
            return False

    def scroll(self, scroll_type: str, **kwargs):
        """Scroll on web pages based on the specified scroll type.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().scroll("height", value=50)
            >> CafeXWeb().scroll("bottom")
            >> CafeXWeb().scroll("infinite", scroll_pause_time=1)
            >> CafeXWeb().scroll("web_element", locator="xpath=.//[id='password']")
            >> CafeXWeb().scroll("web_element", element=web_element)

        Args:
            scroll_type: The type of scroll. One of the following values - height, bottom, infinite, web_element.
            value (optional): The length of scroll (required for height scroll type).
            scroll_pause_time (optional): Time to wait (in seconds) before scrolling to the end of the page (required for infinite scroll type).
            element (optional): The web element to scroll to (required for web_element scroll type).
            locator (optional): The locator of the web element to scroll to (required for web_element scroll type).

        Returns:
            None
        """
        try:
            if scroll_type == "height":
                if "value" in kwargs:
                    self.element_interactions.execute_javascript(
                        "window.scrollTo(0, arguments[0])", kwargs.get("value")
                    )
                else:
                    raise Exception("Height to be scrolled not given")
            elif scroll_type == "bottom":
                self.element_interactions.execute_javascript(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
            elif scroll_type == "infinite":
                count = 0
                scroll_pause_time = kwargs.get("scroll_pause_time", 1)
                last_height = self.element_interactions.execute_javascript(
                    "return document.body.scrollHeight"
                )
                while count < 20:
                    count += 1
                    self.element_interactions.execute_javascript(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    time.sleep(scroll_pause_time)
                    new_height = self.element_interactions.execute_javascript(
                        "return document.body.scrollHeight"
                    )
                    if new_height == last_height:
                        break
                    last_height = new_height
            elif scroll_type == "web_element":
                if "element" in kwargs:
                    self.element_interactions.execute_javascript(
                        "arguments[0].scrollIntoView(true);", kwargs.get("element")
                    )
                elif "locator" in kwargs:
                    web_element = self.element_interactions.get_web_element(kwargs.get("locator"))
                    self.element_interactions.execute_javascript(
                        "arguments[0].scrollIntoView(true);", web_element
                    )
                else:
                    raise Exception("Element or locator not passed where driver needs to scroll")
            else:
                raise Exception(
                    "Incorrect Scroll type, the scroll type can be height/bottom/infinite/web_element"
                )
        except Exception as e:
            self.logger.exception(f"Exception in scroll method. Exception Details: {repr(e)}")
            raise e

    def search_broken_links(self) -> int:
        """Fetch the total links on the web page and identify how many links
        are working fine and which are broken.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().search_broken_links()

        Returns:
            An integer representing the number of broken links on the page.
        """
        try:
            total_links = 0
            broken_links = 0
            anchor_links = self.driver.find_elements(By.CSS_SELECTOR, "a")
            images = self.driver.find_elements(By.CSS_SELECTOR, "img")
            links = anchor_links + images
            self.logger.info("The total number of links on the page are: %d", len(links))
            for link in links:
                flag = "href"
                temp_variable = link.get_attribute("href")
                if temp_variable is None:
                    flag = "src"
                    temp_variable = link.get_attribute("src")
                try:
                    if "https" in temp_variable:
                        r = requests.head(link.get_attribute(flag), verify=False)
                        if r.status_code in [400, 403, 404, 408, 409, 500, 501, 502, 503, 504]:
                            broken_links += 1
                            self.logger.info("Broken link: %s", link.get_attribute(flag))
                except Exception as e:
                    self.logger.exception(e)
                total_links += 1
            self.logger.info(
                "Final Value: %d out of %d are broken on this URL: %s",
                broken_links,
                total_links,
                self.driver.current_url,
            )
            return broken_links
        except Exception as e:
            self.logger.exception(
                "Exception in search_broken_links method. Exception Details: %s", str(e)
            )
            raise e

    def get_browser_logs(self, log_type: str = None) -> list:
        """Get console logs from the Chrome browser. Captures errors like
        '404', '500', etc.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_browser_logs()
            >> CafeXWeb().get_browser_logs("info")
            >> CafeXWeb().get_browser_logs("warning")

        Args:
            log_type: The type of logs to capture. Can be 'info', 'warning', or 'severe'. Defaults to 'severe'.

        Returns:
            A list of error logs.
        """
        try:
            log_errors = []
            if "chrome" in str(self.driver):
                logs = self.driver.get_log("browser")
                if log_type is not None:
                    log_type = str(log_type).upper()
                    if log_type == "INFO":
                        for entry in logs:
                            if entry["level"] == "INFO":
                                log_errors.append(entry["message"])
                    elif log_type == "WARNING":
                        for entry in logs:
                            if entry["level"] == "WARNING":
                                log_errors.append(entry["message"])
                else:
                    for entry in logs:
                        if entry["level"] == "SEVERE":
                            log_errors.append(entry["message"])
            else:
                self.logger.info("get_browser_logs method works only for chrome")
            return log_errors
        except Exception as e:
            self.logger.exception(
                "Exception in get_browser_logs method. Exception Details: ", exc_info=e
            )
            raise e

    def get_webtable_all_data_into_list(
            self, pstr_row_locator: str, **kwargs
    ) -> tuple[int, int] | list[list[str]]:
        """Fetch all the data from a web table into a list. If a text to search
        is provided, it will return the row and column positions of the text.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_webtable_all_data_into_list("xpath=/html/body/table/tbody/tr")
            >> CafeXWeb().get_webtable_all_data_into_list("xpath=/html/body/table/tbody/tr",
            pstr_text_to_search="Sample Text")

        Args:
            pstr_row_locator: The locator for the table rows.
            **kwargs: Additional keyword arguments:
                - pstr_text_to_search: Text to be searched in the web table.

        Returns:
            A list containing the web table data or the row and column positions of the searched text.
        """
        try:
            int_no_txt_found = -1
            lst_webtable_final_data = []
            if len(self.element_interactions.get_web_elements(pstr_row_locator)) > 0:
                for row_counter in range(
                        len(self.element_interactions.get_web_elements(pstr_row_locator))
                ):
                    str_col_locator = f"{pstr_row_locator}[{row_counter + 1}]/td"
                    int_col_cnt = len(self.element_interactions.get_web_elements(str_col_locator))
                    lst_webtable_data = []
                    for col_counter in range(int_col_cnt):
                        str_row_col_data_locator = (
                            f"{pstr_row_locator}[{row_counter + 1}]/td[{col_counter + 1}]"
                        )
                        if kwargs.get("pstr_text_to_search") is None:
                            str_webtable_data = self.element_interactions.get_web_element(
                                str_row_col_data_locator
                            ).text
                            lst_webtable_data.append(str_webtable_data)
                            int_no_txt_found = 1
                        else:
                            str_webtable_data = self.element_interactions.get_web_element(
                                str_row_col_data_locator
                            ).text
                            if str(kwargs.get("pstr_text_to_search")) in str(str_webtable_data):
                                return (row_counter + 1), (col_counter + 1)
                    lst_webtable_final_data.append(lst_webtable_data)
                if int_no_txt_found == -1:
                    raise Exception(
                        "pstr_text_to_search not found, kindly provide correct search string"
                    )
                return lst_webtable_final_data
        except Exception as e:
            self.logger.exception(
                "Exception in get_webtable_all_data_into_list method. Exception Details: ",
                exc_info=e,
            )
            raise e
