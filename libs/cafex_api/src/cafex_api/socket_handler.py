import json
import time
from typing import Any, Callable, Dict, List, Optional, Union

import websocket
from cafex_core.logging.logger_ import CoreLogger

try:
    import thread
except ImportError:
    import _thread as thread


class WebSocketHandler:
    """Handles WebSocket connections, sending messages, and receiving
    responses.

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

    def set_socket_connection(self, socket_url: str) -> websocket.WebSocket:
        """Establishes a WebSocket connection to the specified URL.

        This method creates a WebSocket connection using the `create_connection`
        function from the `websocket` library.

        Args:
            socket_url: The URL of the WebSocket server.

        Returns:
            A WebSocket object representing the established connection.

        Raises:
            ValueError: If the `socket_url` is empty or `None`.
            Exception: If an error occurs while establishing the WebSocket connection.
        """
        if not socket_url:
            raise ValueError("socket_url cannot be empty or None")
        try:
            self._ws = websocket.create_connection(socket_url)
            return self._ws
        except Exception as e:
            self.logger.exception("Error establishing WebSocket connection: %s", e)
            raise e

    def send_socket_message(self, socket_url: str, message: str) -> str:
        """Sends a single message to the WebSocket server and returns the
        response.

        Args:
            socket_url (str): The URL of the WebSocket server.
            message (str): The message to be sent.

        Returns:
            str: The response received from the WebSocket server.

        Raises:
            ValueError: If the `socket_url` or `message` is empty or `None`.
            Exception: If an error occurs while sending the message.

        Examples:
            send_socket_message('ws://example.com/json','abcd')
        """
        if not socket_url:
            raise ValueError("socket_url cannot be empty or None")
        if not message:
            raise ValueError("pstr_message cannot be empty or None")

        try:
            if self._ws is None:
                self._ws = self.set_socket_connection(socket_url)
            self._ws.send(message)
            response = self._ws.recv()
            return response
        except Exception as e:
            self.logger.exception("Error while sending message to the WebSocket server: %s", e)
            raise e

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
    ) -> None:
        """Sends multiple messages to the WebSocket server and captures the
        response until an exit criteria is met. This method allows overwriting
        the default behavior of WebSocket's on_message, on_error, on_open, and
        on_close methods.

        Args:
            socket_url (str): The URL of the WebSocket server.
            messages (List[Dict]): A list of messages to be sent.
            on_message (Optional[Callable], optional): A custom on_message callback function.
            on_error (Optional[Callable], optional): A custom on_error callback function.
            on_open (Optional[Callable], optional): A custom on_open callback function.
            on_close (Optional[Callable], optional): A custom on_close callback function.
            wait_time (int, optional): The time (in seconds) to wait between sending messages.
                                       Defaults to 1.
            ssl_options (Optional[Dict], optional): SSL options for the WebSocket connection.
                                                    Defaults to None.

        Returns:
            None: This method doesn't return anything. But to fetch the response of multi socket
            message,use the WebSocketHandler class variable 'arr_multi_response'

        Raises:
            ValueError: If the `socket_url` is empty or `None`.
            Exception: If an error occurs while sending the messages

        Examples:
            # Using default callbacks
            handler.send_multi_socket_message(socket_url, messages)

            # Using custom callbacks
            handler.send_multi_socket_message(socket_url, messages,
                                              on_message=custom_on_message, ...)

            # Bypass SSL verification
            ssl_opt = {"cert_reqs": ssl.CERT_NONE}
            handler.send_multi_socket_message(socket_url, messages, ssl_opt=ssl_opt)

        Note:
            When user wants to create custom implementation of
            on_message/on_error/on_open/on_close, make sure to leverage
            WebSocketHandler's class variables 'arr_multi_response' and 'list_messages'
        """
        if not socket_url:
            raise ValueError("socket_url cannot be empty or None")

        try:
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
        except Exception as e:
            self.logger.exception(
                "Error while sending multiple messages to WebSocket server: %s", e
            )
            raise e

    def __on_message(self, _ws: websocket.WebSocket, message: str) -> None:
        try:
            self.logger.info("***ON_MESSAGE***")
            self.logger.info(message)
            self.arr_multi_response.append(message)
        except Exception as e:
            raise e

    def __on_error(self, _ws: websocket.WebSocket, error: Union[str, Exception]):
        try:
            self.logger.exception("***ON_ERROR***")
            self.logger.exception(error)
        except Exception as e:
            raise e

    def __on_close(
        self,
        _ws: websocket.WebSocket,
        _close_status_code: Optional[int] = None,
        _close_msg: Optional[str] = None,
    ) -> None:
        try:
            self.logger.warning("***ON_CLOSE***")
            self.logger.warning(self.arr_multi_response)
        except Exception as e:
            raise e

    def __on_open(self, *_args: Any) -> None:
        try:

            def run(*_args) -> None:
                try:
                    for message in self.list_messages:
                        self._ws.send(json.dumps(message))
                        time.sleep(self.multi_message_wait_time)
                    self._ws.close()
                except Exception as ex:
                    self.logger.exception("Error in run: %s", ex)

            thread.start_new_thread(run, ())
            self.logger.info("WebSocket connection opened")
        except Exception as e:
            raise e
