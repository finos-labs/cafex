import json
import time
from typing import Any, Callable, Dict, List, Optional, Union

import websocket

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.exceptions import CoreExceptions

from .api_exceptions import APIExceptions

try:
    import thread
except ImportError:
    import _thread as thread


class WebSocketHandler:
    """
    Handles WebSocket connections, sending messages, and receiving responses.

    This class provides methods for:
    * Establishing WebSocket connections.
    * Sending single and multiple messages.
    * Handling message receiving, errors, connection opening, and closing.
    """

    def __init__(self):
        self.multi_message_wait_time = 1
        self._ws = None
        self.arr_multi_response = []
        self.list_messages = ""
        self.logger = CoreLogger(name=__name__).get_logger()
        self.__exceptions_generic = CoreExceptions()
        self.__exceptions_services = APIExceptions()

    def set_socket_connection(self, socket_url: str) -> Optional[websocket.WebSocket]:
        """
        Establishes a WebSocket connection to the specified URL.

        This method creates a WebSocket connection using the `create_connection`
        function from the `websocket` library.

        Args:
            socket_url: The URL of the WebSocket server.

        Returns:
            A WebSocket object representing the established connection, or None if connection fails.

        Examples:
            >>> handler = WebSocketHandler()
            >>> ws = handler.set_socket_connection("ws://echo.websocket.org")
            >>> # Use the WebSocket connection
            >>> ws.send("Hello WebSocket!")
            >>> response = ws.recv()
        """
        try:
            if not socket_url:
                self.__exceptions_services.raise_null_value(
                    "socket_url cannot be empty or None", fail_test=False
                )
                return None

            self._ws = websocket.create_connection(socket_url)
            return self._ws
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error establishing WebSocket connection: {str(e)}", fail_test=False
            )
            return None

    def send_socket_message(self, socket_url: str, message: str) -> Optional[str]:
        """
        Sends a single message to the WebSocket server and returns the response.

        Args:
            socket_url: The URL of the WebSocket server.
            message: The message to be sent.

        Returns:
            The response received from the WebSocket server, or None if operation fails.

        Examples:
            >>> handler = WebSocketHandler()
            >>> ws_response = handler.send_socket_message('ws://echo.websocket.org', 'Hello World')
            >>> print(ws_response)
            'Hello World'
        """
        try:
            if not socket_url:
                self.__exceptions_services.raise_null_value(
                    "socket_url cannot be empty or None", fail_test=False
                )
                return None

            if not message:
                self.__exceptions_services.raise_null_value(
                    "pstr_message cannot be empty or None", fail_test=False
                )
                return None

            if self._ws is None:
                self._ws = self.set_socket_connection(socket_url)
                if self._ws is None:
                    return None

            self._ws.send(message)
            response = self._ws.recv()
            return response
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error while sending message to the WebSocket server: {str(e)}", fail_test=False
            )
            return None

    def send_multi_socket_message(
        self,
        socket_url: str,
        messages: List[Dict],
        wait_time: int = 1,
        on_message: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_open: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        ssl_options: Optional[dict] = None,
    ) -> bool:
        """
        Sends multiple messages to the WebSocket server and captures the response until an exit
        criteria is met. This method allows overwriting the default behavior of WebSocket's
        on_message, on_error, on_open, and on_close methods.

        Args:
            socket_url: The URL of the WebSocket server.
            messages: A list of messages to be sent.
            wait_time: The time (in seconds) to wait between sending messages. Defaults to 1.
            on_message: A custom on_message callback function.
            on_error: A custom on_error callback function.
            on_open: A custom on_open callback function.
            on_close: A custom on_close callback function.
            ssl_options: SSL options for the WebSocket connection.

        Returns:
            True if successful, False otherwise

        Examples:
            >>> handler = WebSocketHandler()
            >>> # Define messages
            >>> messages_ws = [{"type": "subscribe", "channel": "channel1"},
            ...            {"type": "message", "content": "Hello WebSocket!"}]
            >>>
            >>> # Using default callbacks
            >>> success = handler.send_multi_socket_message("ws://example.com", messages_ws)
            >>>
            >>> # Using custom callbacks
            >>> def custom_on_message(ws, message):
            ...     print(f"Received: {message}")
            >>>
            >>> success_cus = handler.send_multi_socket_message(
            ...     "ws://example.com",
            ...     messages_ws,
            ...     on_message=custom_on_message
            ... )
            >>>
            >>> # Access the responses
            >>> for response in handler.arr_multi_response:
            ...     print(response)

        Note:
            When user wants to create custom implementation of
            on_message/on_error/on_open/on_close, make sure to leverage
            WebSocketHandler's class variables 'arr_multi_response' and 'list_messages'
        """
        try:
            if not socket_url:
                self.__exceptions_services.raise_null_value(
                    "socket_url cannot be empty or None", fail_test=False
                )
                return False

            if not messages:
                self.__exceptions_services.raise_null_value(
                    "messages cannot be empty or None", fail_test=False
                )
                return False

            # Use default callbacks if not provided
            on_message = on_message or self.__on_message
            on_error = on_error or self.__on_error
            on_open = on_open or self.__on_open
            on_close = on_close or self.__on_close

            websocket.enableTrace(True)
            self.list_messages = messages
            self.arr_multi_response = []
            self.multi_message_wait_time = wait_time
            self._ws = websocket.WebSocketApp(
                socket_url,
                on_message=on_message,
                on_error=on_error,
                on_open=on_open,
                on_close=on_close,
            )

            self._ws.on_open = self.__on_open
            self._ws.run_forever(sslopt=ssl_options)
            return True
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error while sending multiple messages to WebSocket server: {str(e)}",
                fail_test=False,
            )
            return False

    def __on_message(self, _ws: websocket.WebSocket, message: str) -> None:
        """
        Default on_message callback for WebSocket connection.

        Args:
            _ws: The WebSocket connection.
            message: The received message.
        """
        try:
            self.logger.info("***ON_MESSAGE***")
            self.logger.info(message)
            self.arr_multi_response.append(message)
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in on_message handler: {str(e)}", fail_test=False
            )

    def __on_error(self, _ws: websocket.WebSocket, error: Union[str, Exception]) -> None:
        """
        Default on_error callback for WebSocket connection.

        Args:
            _ws: The WebSocket connection.
            error: The error that occurred.
        """
        try:
            self.logger.exception("***ON_ERROR***")
            self.logger.exception(error)
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in on_error handler: {str(e)}", fail_test=False
            )

    def __on_close(
        self,
        _ws: websocket.WebSocket,
        _close_status_code: Optional[int] = None,
        _close_msg: Optional[str] = None,
    ) -> None:
        """
        Default on_close callback for WebSocket connection.

        Args:
            _ws: The WebSocket connection.
            _close_status_code: The WebSocket close status code.
            _close_msg: The WebSocket close message.
        """
        try:
            self.logger.warning("***ON_CLOSE***")
            self.logger.warning(self.arr_multi_response)
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in on_close handler: {str(e)}", fail_test=False
            )

    def __on_open(self, *_args: Any) -> None:
        """
        Default on_open callback for WebSocket connection.

        Args:
            *_args: Variable length argument list.
        """

        try:

            def run(*_args) -> None:
                """Thread function to send messages one by one."""
                try:
                    for message in self.list_messages:
                        self._ws.send(json.dumps(message))
                        time.sleep(self.multi_message_wait_time)
                    self._ws.close()
                except Exception as ex:
                    self.__exceptions_generic.raise_generic_exception(
                        f"Error in WebSocket thread: {str(ex)}", fail_test=False
                    )

            thread.start_new_thread(run, ())
            self.logger.info("WebSocket connection opened")
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in on_open handler: {str(e)}", fail_test=False
            )
