import platform

import psutil

if platform.system().upper() == "WINDOWS":
    from pywinauto import Application

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.exceptions import CoreExceptions
from cafex_desktop.desktop_client.desktop_client_exceptions import (
    DesktopClientExceptions,
)


class DesktopApplicationHandler:
    """This class provides methods to launch and connect to desktop client applications."""

    def __init__(self, desktop_client_config=None):
        self.desktop_client_config = desktop_client_config
        self.__exceptions_generic = CoreExceptions()
        self.__exceptions_desktop_client = DesktopClientExceptions()
        self.logger = CoreLogger(name=__name__).get_logger()

    def get_handler(self, application_name: str = None, app_path: str = None) -> Application:
        """
        Retrieve and launch the appropriate application handler.

        This method determines which application to launch based on the provided `application_name` or the
        configuration. It supports launching predefined applications like Excel and Notepad, or a custom
        application specified in the configuration.

        Args:
            app_path(str): The path to the application to launch. If not provided, the method will use the
                                    `app_path` value from the configuration.
            application_name (str): The name of the application to launch. If not provided, the method will
                                    use the `application` value from the configuration.

        Returns:
            None: The method launches the application and does not return any value.

        Raises:
            Exception: If an error occurs while launching the application.

        Examples:
            1. Launch Excel:
                >>> handler = DesktopApplicationHandler()
                >>> handler.get_handler("excel")

            2. Launch Notepad:
                >>> handler.get_handler("notepad")

            3. Launch a custom application:
                >>> handler.get_handler("custom_app")

        Notes:
            - If `application_name` is not provided, the method will fall back to the `application_name` value
              from the configuration.
            - For Excel and Notepad, specific methods (`launch_excel` and `launch_notepad`) are used.
            - For other applications, the `launch` method is used with the application path from the configuration.
        """
        try:
            application_name = application_name or self.desktop_client_config.get(
                "application_name"
            )
            app_path = app_path or self.desktop_client_config.get("app_path")
            if app_path:
                return self.launch(app_path)
            elif application_name:
                return self.launch_application(application_name)
            else:
                raise ValueError("Both application_name and app_path are None.")
        except Exception as e:
            self.logger.error("Error occurred while launching the application: %s", str(e))
            self.__exceptions_generic.raise_generic_exception(
                message="Error occurred while launching the application: " + str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def launch_application(
        self,
        application_name: str,
        connect_to_open_app: bool = False,
        process_name: str = None,
        app_path: str = None,
    ) -> Application:
        """
        Launch the Excel application.

        This method launches the Excel application or connects to an already running instance based on the
        `connect_to_open_app` parameter. If `connect_to_open_app` is False, it terminates any existing Excel
        processes before launching a new instance.

        Args:
            application_name(str):  The name of the application to launch (e.g., "excel", "notepad").
            connect_to_open_app (bool): Whether to connect to an already running application.
            process_name (str): The name of the application process to terminate if `connect_to_open_app` is False.
            app_path (str): The path to the application executable.

        Returns:
            object: The application object representing the launched or connected Excel instance.

        Raises:
            Exception: If an error occurs while killing processes, launching, or connecting to the application.

        Examples:
            1. Launch a new Excel instance:
                >>> handler = DesktopApplicationHandler()
                >>> handler.launch_application(application_name= "excel",connect_to_open_app=False, process_name="excel.exe",
                app_path="C:/Program Files/Microsoft Office/root/Office16/EXCEL.EXE")

            2. Connect to an already running Excel instance:
                >>> handler.launch_application(application_name= "excel",connect_to_open_app=True, process_name="excel.exe", app_path="")
            3. Launch a new Notepad instance:
                >>> handler.launch_application(application_name= "notepad",connect_to_open_app=False, process_name="notepad.exe",
                 app_path="C:/Windows/System32/notepad.exe")
            4. Connect to an already running Notepad instance:
                >>> handler.launch_application(application_name= "notepad",connect_to_open_app=True, process_name="notepad.exe", app_path="")

        Notes:
            - If `connect_to_open_app` is False, all existing Excel processes with the specified `process_name`
              will be terminated before launching a new instance.
            - If `connect_to_open_app` is True, the method attempts to connect to an already running Excel instance.
        """
        try:
            connect_to_open_app = connect_to_open_app or self.desktop_client_config.get(
                "connect_to_open_app"
            )
            process_name = process_name or self.desktop_client_config.get("process_name")
            app_path = app_path or self.desktop_client_config.get("app_path")
            if not connect_to_open_app:
                # Kill existing running Excel application
                for proc in psutil.process_iter():
                    try:
                        # Get process name & pid from process object
                        if proc.name().lower() == process_name.lower():
                            proc.kill()
                    except Exception as e:
                        raise Exception(
                            f"Error occurred while killing the process '{process_name}': {e}"
                        )

                # Launch Excel application
                app = self.launch(application_name)
                # app = self.connect_to_app(title_re=application_name, control_type="Window", timeout=300)
                # app.window(title_re=application_name, control_type="Window").maximize()
                return app

            else:
                # Connect to an already running Excel application
                app = self.connect_to_app(
                    title_re=application_name, control_type="Window", timeout=60
                )
                app.window(title_re=application_name, control_type="Window").maximize()
                return app

        except Exception as e:
            error_message = f"Error occurred while launching or connecting to Excel: {e}"
            self.__exceptions_generic.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )
            raise e

    def launch(
        self,
        cmdline_appname: str,
        work_dir: str = None,
        timeout: int = None,
        backend: str = None,
        wait_for_idle: bool = False,
    ) -> Application:
        """
        Launch an application based on the provided parameters.

        This method starts an application using the specified command-line argument and optional parameters.

        Args:
            cmdline_appname (str): Command-line argument of the application to launch.
            work_dir (str, optional): Working directory for the application. Defaults to None.
            timeout (int, optional): Timeout for launching the application. Defaults to None.
            backend (str, optional): Backend to use for the application. Defaults to "uia".
            wait_for_idle (bool, optional): Whether to wait for the application to become idle. Defaults to False.

        Returns:
            Application: The launched application object.

        Raises:
            Exception: If an error occurs while launching the application.

        Examples:
            1. Launch an application with default parameters:
                >>> handler = DesktopApplicationHandler()
                >>> handler.launch("ctstest.bat")

            2. Launch an application with a specific working directory:
                >>> handler.launch("setup.exe", work_dir="C:/App", timeout=30, backend="win32", wait_for_idle=True)

        Notes:
            - Ensure the `cmdline_appname` is a valid executable or script.
            - The `backend` parameter determines the automation backend (e.g., "uia" or "win32").
        """
        try:
            # Start the application with the provided parameters
            if backend is None:
                self.app = Application().start(
                    cmdline_appname,
                    timeout=timeout,
                    wait_for_idle=wait_for_idle,
                    work_dir=work_dir,
                )
                return self.app
            self.app = Application(backend=backend).start(
                cmdline_appname,
                timeout=timeout,
                wait_for_idle=wait_for_idle,
                work_dir=work_dir,
            )
            return self.app
        except Exception as e:
            error_message = f"Unable to connect with specified application: {e}"
            self.__exceptions_generic.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )
            raise e

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
        backend: str = "uia",
        timeout: int = 60,
    ) -> Application:
        """
        Connect to an already running application based on the provided parameters.

        This method connects to an existing application using various criteria such as process ID, path,
        title, or other attributes.

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
            backend (str, optional): Backend to use for the application. Defaults to "uia".
            timeout (int, optional): Timeout for connecting to the application. Defaults to 60 seconds.

        Returns:
            Application: The connected application object.

        Raises:
            Exception: If unable to connect to the application.

        Examples:
            1. Connect using process ID:
                >>> handler = DesktopApplicationHandler()
                >>> handler.connect_to_app(process_id=16052)

            2. Connect using path:
                >>> handler.connect_to_app(path="C:/Data/CTSTest/SNL.NextGenes.Loader.exe")

            3. Connect using title and control type:
                >>> handler.connect_to_app(title="Financials", control_type="Window")

        Notes:
            - At least one parameter must be provided to connect to an already running application.
            - The `backend` parameter determines the automation backend (e.g., "uia" or "win32").
        """
        try:
            # Ensure at least one parameter is provided
            if not any(
                [
                    process_id,
                    path,
                    title,
                    title_re,
                    class_name,
                    control_type,
                    auto_id,
                    best_match,
                    handle,
                ]
            ):
                raise ValueError(
                    "At least one parameter must be provided to connect to an application."
                )

            app = None

            # Connect using process ID
            if process_id is not None:
                app = Application(backend=backend).connect(process=process_id, timeout=timeout)

            # Connect using window handle
            elif handle is not None:
                app = Application(backend=backend).connect(handle=handle)

            # Connect using executable path
            elif path is not None:
                app = Application(backend=backend).connect(path=path, timeout=timeout)

            # Connect using window attributes
            elif any([title, title_re, class_name, control_type, auto_id, best_match]):
                app = Application(backend=backend).connect(
                    title=title,
                    title_re=title_re,
                    class_name=class_name,
                    control_type=control_type,
                    auto_id=auto_id,
                    best_match=best_match,
                    timeout=timeout,
                )
            if app is None:
                raise RuntimeError(
                    "Failed to connect to the application. No valid connection criteria matched."
                )

            return app

        except Exception as e:
            error_message = (
                f"Failed to connect to the application. Parameters: "
                f"process_id={process_id}, path={path}, title={title}, title_re={title_re}, "
                f"class_name={class_name}, control_type={control_type}, auto_id={auto_id}, "
                f"best_match={best_match}, handle={handle}, backend={backend}, timeout={timeout}. "
                f"Error: {e}"
            )
            self.__exceptions_generic.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )
            raise e
