import os
import platform
import signal

import psutil

if platform.system().upper() == "WINDOWS":
    from pywinauto.application import Application
    from pywinauto.base_wrapper import BaseWrapper

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.exceptions import CoreExceptions
from cafex_core.singletons_.session_ import SessionStore
from cafex_desktop.desktop_client.desktop_client_exceptions import (
    DesktopClientExceptions,
)


class WindowActions:
    def __init__(self, phandler: Application = None):
        self.app = phandler or SessionStore().storage.get("handler")
        self.window = None
        self.__exceptions_generic = CoreExceptions()
        self.__exceptions_desktop_client = DesktopClientExceptions()
        self.logger = CoreLogger(name=__name__).get_logger()

    def get_window_object(
        self,
        title: str = None,
        title_regex: str = None,
        class_name: str = None,
        control_type: str = None,
        auto_id: str = None,
        best_match: str = None,
        timeout: int = 60,
        wait_for_exists: bool = True,
    ) -> BaseWrapper:
        """
        Retrieve a window object based on the specified parameters.

        This method attempts to locate a window in the application using the provided parameters.
        If the `wait_for_exists` flag is set to True, it waits for the window to exist within the
        specified timeout period. If the window is found, it sets focus and maximizes the window.
        If the window is not found, an exception is raised.

        Args:
            title (str, optional): The exact title of the window to locate. Defaults to None.
            title_regex (str, optional): A regular expression to match the window title. Defaults to None.
            class_name (str, optional): The class name of the window to locate. Defaults to None.
            control_type (str, optional): The control type of the window to locate. Defaults to None.
            auto_id (str, optional): The automation ID of the window to locate. Defaults to None.
            best_match (str, optional): A string to find the best matching window title. Defaults to None.
            timeout (int, optional): The maximum time (in seconds) to wait for the window to exist. Defaults to 60.
            wait_for_exists (bool, optional): Whether to wait for the window to exist before proceeding. Defaults to True.

        Returns:
            object: The located window object if found.

        Raises:
            Exception: If the window cannot be located or any other error occurs during the process.

        Examples:
            1. Locate a window with an exact title:
                >>> actions = WindowActions(self.app)
                >>> window = actions.get_window_object(title="My Application")

            2. Locate a window using a regular expression for the title:
                >>> window = actions.get_window_object(title_regex=".*Application.*")

            3. Locate a window with a specific class name and control type:
                >>> window = actions.get_window_object(class_name="WindowClass", control_type="Window")

            4. Locate a window and wait for it to exist:
                >>> window = actions.get_window_object(title="My Application", wait_for_exists=True)

        Notes:
            - If multiple parameters are provided, they are combined to narrow down the search.
            - If `wait_for_exists` is True and the window does not exist within the timeout, an exception is raised.
            - The method sets focus and maximizes the window if it is successfully located.
        """
        if self.app is None:
            self.__exceptions_generic.raise_generic_exception(
                message="Application is not connected. Ensure the application is launched or connected before calling get_window_object.",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )
        try:
            self.window = self.app.window(
                title=title,
                title_re=title_regex,
                class_name=class_name,
                control_type=control_type,
                auto_id=auto_id,
                best_match=best_match,
            )

            if wait_for_exists:
                if self.window.exists(timeout=timeout):
                    self.window.set_focus()
                    self.window.maximize()
                else:
                    self.__exceptions_desktop_client.raise_window_not_found(
                        insert_report=True,
                        trim_log=True,
                        log_local=True,
                        fail_test=True,
                    )
            return self.window
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message="Unable to get Window object" + str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def connect_to_app(
        self,
        process_id: int = None,
        path: str = None,
        title: str = None,
        title_re: str = None,
        class_name: str = None,
        control_type: str = None,
        auto_id: str = None,
        best_match: str = None,
        handle: object = None,
        timeout: int = 60,
        backend: str = "uia",
    ):
        """
        Connect to an already running application based on the provided parameters.

        Args:
            process_id (int, optional): Process ID of the target application. Defaults to None.
            path (str, optional): Path used to launch the target application. Defaults to None.
            title (str, optional): Elements with this text. Defaults to None.
            title_re (str, optional): Elements whose text matches this regular expression. Defaults to None.
            class_name (str, optional): Elements with this window class. Defaults to None.
            control_type (str, optional): Elements with this control type. Defaults to None.
            auto_id (str, optional): Elements with this automation ID. Defaults to None.
            best_match (str, optional): Elements with a title similar to this. Defaults to None.
            handle (object, optional): Window handle of the target application. Defaults to None.
            timeout (int, optional): Timeout to connect to the application. Defaults to 60 seconds.
            backend (str, optional): Backend to use for connection (e.g., "uia"). Defaults to "uia".

        Returns:
            Application: The connected application object.

        Raises:
            Exception: If the application cannot be connected or any other error occurs.
        """
        try:
            if process_id:
                self.app = Application(backend=backend).connect(process=process_id)
            elif handle:
                self.app = Application(backend=backend).connect(handle=handle)
            elif path:
                self.app = Application(backend=backend).connect(path=path)
            elif any([title, title_re, class_name, control_type, auto_id, best_match]):
                self.app = Application(backend=backend).connect(
                    title=title,
                    title_re=title_re,
                    class_name=class_name,
                    control_type=control_type,
                    auto_id=auto_id,
                    best_match=best_match,
                    timeout=timeout,
                )
            else:
                self.__exceptions_desktop_client.raise_invalid_parameters(
                    insert_report=True,
                    trim_log=True,
                    log_local=True,
                    fail_test=True,
                )

            return self.app

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message="Unable to connect with specified application: " + str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def close(
        self, handler: BaseWrapper, is_alert: bool = False, button_caption: str = "Yes", **kwargs
    ):
        """
        Close the specified window and handle any confirmation pop-ups if required.

        This method attempts to close the given window object. If a confirmation pop-up appears,
        it handles the pop-up by interacting with the specified button.

        Args:
            handler (object): The window object to be closed.
            is_alert (bool, optional): Set to True if a confirmation pop-up appears on closing the window. Defaults to False.
            button_caption (str, optional): The name or title of the button to interact with in the pop-up. Defaults to "Yes".
            **kwargs: Additional parameters to locate elements in the confirmation pop-up (e.g., class_name, title, auto_id, control_type).

        Returns:
            None

        Raises:
            Exception: If the window cannot be closed or any other error occurs.

        Examples:
            1. Close a window without handling a pop-up:
                >>> actions = WindowActions(self.app)
                >>> actions.close(self.window)

            2. Close a window and handle a confirmation pop-up:
                >>> actions.close(self.window, is_alert=True, button_caption="Yes", class_name="MessageOverlayView")

        Notes:
            - If `is_alert` is True, the method will attempt to handle the confirmation pop-up.
            - Additional parameters in `kwargs` can be used to locate elements in the pop-up.
        """
        try:
            handler.close()

            if is_alert:
                self.window_handler_alert(handler, button_caption, **kwargs)
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message="Unable to close the window: " + str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def launch(
        self,
        cmdline_appname: str,
        work_dir: str = None,
        timeout: int = None,
        backend: str = "uia",
        wait_for_idle: bool = False,
    ) -> Application:
        """
        Launch an application based on the provided parameters.

        This method starts an application using the specified command-line argument and optional parameters.

        Args:
            cmdline_appname (str): Command-line argument of the application to be launched.
            work_dir (str, optional): Working directory for the application. Defaults to None.
            timeout (int, optional): Timeout for launching the application. Defaults to None.
            backend (str, optional): Backend to use for the application (e.g., "uia"). Defaults to "uia".
            wait_for_idle (bool, optional): Whether to wait for the application to become idle after launching. Defaults to False.

        Returns:
            Application: The launched application object.

        Raises:
            Exception: If the application cannot be launched or any other error occurs.

        Examples:
            1. Launch an application using a batch file:
                >>> actions = WindowActions(self.app)
                >>> app = actions.launch("ctstest.bat")

            2. Launch an application with a specific working directory:
                >>> app = actions.launch("setup.exe", work_dir="C:\\ApplicationName")

            3. Launch an application with a timeout and wait for it to become idle:
                >>> app = actions.launch("app.exe", timeout=30, wait_for_idle=True)

        Notes:
            - The `backend` parameter specifies the automation backend to use (default is "uia").
            - If `wait_for_idle` is True, the method waits for the application to become idle after launching.
        """
        try:
            self.app = Application(backend=backend).start(
                cmdline_appname,
                timeout=timeout,
                wait_for_idle=wait_for_idle,
                work_dir=work_dir,
            )
            return self.app

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message="Unable to launch application: " + str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def quit_application(self, process_name: str = None, process_id: int = None):
        """
        Exit the application based on the provided parameters.

        This method allows the user to terminate an application by specifying either the process name or process ID.
        If no parameters are provided, it attempts to close the application object set in the class.

        Args:
            process_name (str, optional): Name of the process to close/quit the application. Defaults to None.
            process_id (int, optional): Process ID of the application to terminate. Defaults to None.

        Returns:
            None

        Raises:
            Exception: If the application cannot be terminated or invalid parameters are provided.

        Examples:
            1. Quit an application by process name:
                >>> actions = WindowActions(self.app)
                >>> actions.quit_application(process_name="SNL.NextGenes.Loader.exe")

            2. Quit an application by process ID:
                >>> actions.quit_application(process_id=1234)

            3. Quit the application object set in the class:
                >>> actions.quit_application()

        Notes:
            - If `process_name` is provided, the method attempts to terminate all processes matching the name.
            - If `process_id` is provided, the method terminates the process with the specified ID.
            - If neither `process_name` nor `process_id` is provided, the method attempts to terminate the application object.
        """
        try:
            if self.app is not None:
                self.app.kill()
            elif process_id is not None:
                os.kill(process_id, signal.SIGTERM)
            elif process_name is not None:
                process_found = False
                for proc in psutil.process_iter():
                    try:
                        # Check if the process name matches
                        if process_name.lower() in proc.name().lower():
                            proc.kill()
                            process_found = True
                    except Exception as e:
                        self.logger.exception(
                            "Error occurred while killing the process: %s", str(e)
                        )
                if not process_found:
                    self.logger.info("Incorrect process name provided")
                    self.__exceptions_desktop_client.raise_invalid_parameters(
                        insert_report=True,
                        trim_log=True,
                        log_local=True,
                        fail_test=True,
                    )
            else:
                self.__exceptions_desktop_client.raise_invalid_parameters(
                    insert_report=True,
                    trim_log=True,
                    log_local=True,
                    fail_test=True,
                )
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message=f"Unable to quit application: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def refresh_window_objects(self, window_title: str) -> None:
        """
        Refresh the window controls based on the specified window title.

        This method connects to the application using the provided window title (supports regular expressions),
        refreshes the window controls, and sets focus on the top window. If the window is not found, a custom
        exception is raised.

        Args:
            window_title (str): The title of the window to refresh. This can be a regular expression to match
                                the window title.

        Returns:
            None

        Raises:
            Exception: If the window cannot be found or an error occurs during the refresh process.

        Examples:
            1. Refresh the app and window controls using an exact title:
                >>> actions = WindowActions(self.app)
                >>> actions.refresh_window_objects("Mines")

            2. Refresh the app and window controls using a title pattern:
                >>> actions.refresh_window_objects(".*Mines.*")

        Notes:
            - This method matches the window title using a regular expression.
            - Ensure the application is running and the window title is correct.
            - If the window is not found, a `raise_window_not_found` exception is triggered.
        """
        try:
            # Connect to the application using the provided window title
            app = self.connect_to_app(title_re=window_title, control_type="Window")
            if app is not None:
                # Set the application and window objects
                self.app = app
                self.window = self.app.top_window()
                self.window.set_focus()
            else:
                # Raise a custom exception if the window is not found
                self.__exceptions_desktop_client.raise_window_not_found(
                    insert_report=True,
                    trim_log=True,
                    log_local=True,
                    fail_test=True,
                )
        except Exception as e:
            # Handle any unexpected errors and raise a generic exception
            error_message = "Error occurred while refreshing window objects for title %s: %s" % (
                window_title,
                str(e),
            )
            self.__exceptions_generic.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def launch_form(
        self,
        cmdline_appname: str,
        form_name: str,
        work_dir: str = None,
        timeout: int = None,
        backend: str = "uia",
        wait_for_idle: bool = False,
    ) -> None:
        """
        Launch an application and open a specific form.

        This method starts an application using the provided command-line argument and optional parameters.
        It then connects to the application and maximizes the specified form window.

        Args:
            cmdline_appname (str): Command-line argument of the application to launch.
            form_name (str): Name of the form to open.
            work_dir (str, optional): Working directory for the application. Defaults to None.
            timeout (int, optional): Timeout for launching the application. Defaults to None.
            backend (str, optional): Backend to use for the application. Defaults to "uia".
            wait_for_idle (bool, optional): Whether to wait for the application to become idle. Defaults to False.

        Raises:
            Exception: If the application or form cannot be launched.

        Examples:
            Launch an application and open a form:
                >>> actions = WindowActions(self.app)
                >>> actions.launch_form("app_path", "FormName", work_dir="C:/App", timeout=30)
        """
        try:
            # Start the application
            self.app = Application(backend=backend).start(
                cmdline_appname,
                timeout=timeout,
                wait_for_idle=wait_for_idle,
                work_dir=work_dir,
            )
            # Connect to the application and maximize the form window
            self.app = self.connect_to_app(title=form_name, control_type="Window", timeout=300)
            self.app.window(title=form_name, control_type="Window").maximize()
        except Exception as e:
            error_message = "Unable to launch application %s or form %s: %s" % (
                cmdline_appname,
                form_name,
                str(e),
            )
            self.__exceptions_generic.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def window_switch(self, base_window_title: str, target_window_title: str) -> None:
        """
        Switch focus between two windows based on their titles.

        This method connects to the application, sets focus on the base window, and then switches
        focus to the target window. It also highlights both windows for debugging purposes.

        Args:
            base_window_title (str): The title of the current window to focus on initially.
            target_window_title (str): The title of the target window to switch focus to.

        Returns:
            None

        Raises:
            Exception: If an error occurs while switching windows.

        Examples:
            Switch focus between two windows:
                >>> actions = WindowActions(self.app)
                >>> actions.window_switch("Mines", "QuickGet")

        Notes:
            - Ensure the `basewindow_title` and `targetwindow_title` match the window titles exactly or use regular expressions.
            - The method highlights the windows for debugging purposes before switching focus.
            - If the specified windows are not found, an exception is raised.
        """
        try:
            # Connect to the application and focus on the base window
            app = Application(backend="uia").connect(title_re=base_window_title)
            base_window = app.window(title_re=base_window_title).set_focus()
            base_window.draw_outline()

            # Switch focus to the target window
            target_window = app.window(title_re=target_window_title)
            target_window.draw_outline()
            target_window.set_focus()

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error occurred while switching windows: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def window_handler_alert(
        self,
        window_handle: BaseWrapper,
        button_caption: str,
        auto_id: str = None,
        title: str = None,
        class_name: str = None,
        control_type: str = None,
    ) -> None:
        """
        Handle alert messages by interacting with a specified button.

        This method locates an alert window and clicks the specified button within it.
        It uses the provided parameters to identify the alert and the button to interact with.

        Args:
            window_handle (BaseWrapper): The current window object containing the alert.
            button_caption (str): The caption of the button to be clicked within the alert.
            auto_id (str, optional): The automation ID of the alert. Defaults to None.
            title (str, optional): The title of the alert. Defaults to None.
            class_name (str, optional): The class name of the alert. Defaults to None.
            control_type (str, optional): The control type of the alert. Defaults to None.

        Returns:
            None

        Raises:
            Exception: If an error occurs while handling the alert.

        Examples:
            Handle an alert with a specific button:
                >>> actions = WindowActions(self.app)
                >>> actions.window_handler_alert(window_handle, "OK", control_type="Window")

            Handle an alert with additional parameters:
                >>> actions.window_handler_alert(
                ...     window_handle,
                ...     "Yes",
                ...     auto_id="alert123",
                ...     title="Confirmation",
                ...     class_name="AlertWindow",
                ...     control_type="Window"
                ... )

        Notes:
            - Ensure the `window_handle` is a valid object representing the current window.
            - Use the `get_window_object` method to retrieve the window handle before calling this method.
            - The method highlights the alert and button for debugging purposes.
        """
        try:
            # Highlight the window for debugging
            window_handle.draw_outline()

            # Locate the alert window
            alert = window_handle.child_window(
                class_name=class_name, control_type=control_type, auto_id=auto_id, title=title
            )
            alert.draw_outline()

            # Locate and click the button within the alert
            button = alert.child_window(title=button_caption, control_type="Button")
            button.click_input()

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error occurred while handling alert: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def get_window_title(self, pobject_window: BaseWrapper) -> str:
        """
        Fetch the window title of a given window/dialog.

        Args:
            pobject_window (BaseWrapper): The window/dialog object whose title needs to be fetched.

        Returns:
            str: The title of the window/dialog.

        Examples:
            >>> actions = WindowActions(self.app)
            >>> app_window = self.app.window(title_re="app.*", control_type="Window")
            >>> title = actions.get_window_title(app_window)

        Raises:
            Exception: If unable to fetch the window title.
        """
        try:
            str_title_value = pobject_window.window_text()
            return str_title_value
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message=f"Unable to find window title: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def get_child_window(
        self,
        parent_window: BaseWrapper,
        title: str = None,
        class_name: str = None,
        control_type: str = None,
        auto_id: str = None,
        **kwargs,
    ) -> BaseWrapper:
        """
        Get a child window of the specified parent window.

        Args:
            parent_window (BaseWrapper): The parent window object.
            title (str, optional): The title of the child window. Defaults to None.
            class_name (str, optional): The class name of the child window. Defaults to None.
            control_type (str, optional): The control type of the child window. Defaults to None.
            auto_id (str, optional): The automation ID of the child window. Defaults to None.
            **kwargs: Additional parameters to locate the child window.

        Returns:
            BaseWrapper: The child window object.

        Raises:
            Exception: If unable to find the child window.
        """
        try:
            child_window = parent_window.child_window(
                title=title,
                class_name=class_name,
                control_type=control_type,
                auto_id=auto_id,
                **kwargs,
            )
            return child_window
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message=f"Unable to find child window: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )
