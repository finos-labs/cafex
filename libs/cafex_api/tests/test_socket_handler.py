"""
Test module for the WebSocketHandler class in the CAFEX framework.

This module provides comprehensive test coverage for the WebSocket handling
capabilities in the cafex_api.socket_handler module.
"""

import json
import pytest
import ssl
from unittest.mock import MagicMock, patch, call

from cafex_api.socket_handler import WebSocketHandler


class TestWebSocketHandler:
    """Test suite for WebSocketHandler class."""

    @pytest.fixture
    def socket_handler(self):
        """Fixture to create a WebSocketHandler instance for tests."""
        return WebSocketHandler()

    def test_init(self, socket_handler):
        """Test WebSocketHandler initialization."""
        assert socket_handler is not None
        assert socket_handler.multi_message_wait_time == 1
        assert socket_handler._ws is None
        assert socket_handler.arr_multi_response == []
        assert socket_handler.list_messages == ""
        assert socket_handler.logger is not None

    @patch('websocket.create_connection')
    def test_set_socket_connection(self, mock_create_connection, socket_handler):
        """Test establishing a WebSocket connection."""
        # Setup mock
        mock_ws = MagicMock()
        mock_create_connection.return_value = mock_ws

        # Test valid connection
        socket_url = "ws://example.com/websocket"
        result = socket_handler.set_socket_connection(socket_url)

        # Assertions
        assert result == mock_ws
        assert socket_handler._ws == mock_ws
        mock_create_connection.assert_called_once_with(socket_url)

        # Test empty URL
        with pytest.raises(ValueError):
            socket_handler.set_socket_connection("")

        # Test connection error
        mock_create_connection.side_effect = Exception("Connection error")
        with pytest.raises(Exception) as exc_info:
            socket_handler.set_socket_connection(socket_url)
        assert "Connection error" in str(exc_info.value)

    @patch('websocket.create_connection')
    def test_send_socket_message(self, mock_create_connection, socket_handler):
        """Test sending a single message to the WebSocket server."""
        # Setup mock
        mock_ws = MagicMock()
        mock_ws.recv.return_value = "response data"
        mock_create_connection.return_value = mock_ws

        # Test with new connection
        socket_url = "ws://example.com/websocket"
        message = "Hello WebSocket"
        result = socket_handler.send_socket_message(socket_url, message)

        # Assertions
        assert result == "response data"
        mock_create_connection.assert_called_once_with(socket_url)
        mock_ws.send.assert_called_once_with(message)
        mock_ws.recv.assert_called_once()

        # Test with existing connection
        socket_handler._ws = mock_ws  # Reset mock for existing connection test
        mock_ws.send.reset_mock()
        mock_ws.recv.reset_mock()

        result = socket_handler.send_socket_message(socket_url, "Another message")
        assert result == "response data"
        mock_create_connection.assert_called_once()  # Should not be called again
        mock_ws.send.assert_called_once_with("Another message")
        mock_ws.recv.assert_called_once()

        # Test empty URL
        with pytest.raises(ValueError):
            socket_handler.send_socket_message("", message)

        # Test empty message
        with pytest.raises(ValueError):
            socket_handler.send_socket_message(socket_url, "")

        # Test send error
        mock_ws.send.side_effect = Exception("Send error")
        with pytest.raises(Exception) as exc_info:
            socket_handler.send_socket_message(socket_url, message)
        assert "Send error" in str(exc_info.value)

    @patch('websocket.WebSocketApp')
    @patch('websocket.enableTrace')
    def test_send_multi_socket_message_default_callbacks(self, mock_enable_trace, mock_websocket_app, socket_handler):
        """Test sending multiple messages with default callbacks."""
        # Setup
        socket_url = "ws://example.com/websocket"
        messages = [{"message": "Hello"}, {"message": "World"}]
        mock_ws_app = MagicMock()
        mock_websocket_app.return_value = mock_ws_app

        # Test
        socket_handler.send_multi_socket_message(socket_url, messages)

        # Assertions
        mock_enable_trace.assert_called_once_with(True)
        mock_websocket_app.assert_called_once()
        assert socket_handler.list_messages == messages
        assert socket_handler.arr_multi_response == []
        assert socket_handler.multi_message_wait_time == 1
        mock_ws_app.run_forever.assert_called_once_with(sslopt=None)

    @patch('websocket.WebSocketApp')
    @patch('websocket.enableTrace')
    def test_send_multi_socket_message_custom_callbacks(self, mock_enable_trace, mock_websocket_app, socket_handler):
        """Test sending multiple messages with custom callbacks."""
        # Setup
        socket_url = "ws://example.com/websocket"
        messages = [{"message": "Hello"}, {"message": "World"}]
        mock_ws_app = MagicMock()
        mock_websocket_app.return_value = mock_ws_app

        # Custom callbacks
        on_message = MagicMock()
        on_error = MagicMock()
        on_open = MagicMock()
        on_close = MagicMock()

        # SSL options
        ssl_options = {"cert_reqs": ssl.CERT_NONE}

        # Test
        socket_handler.send_multi_socket_message(
            socket_url,
            messages,
            wait_time=2,
            on_message=on_message,
            on_error=on_error,
            on_open=on_open,
            on_close=on_close,
            ssl_options=ssl_options
        )

        # Assertions
        mock_enable_trace.assert_called_once_with(True)
        mock_websocket_app.assert_called_once_with(
            socket_url,
            on_message=on_message,
            on_error=on_error,
            on_open=on_open,
            on_close=on_close
        )
        assert socket_handler.list_messages == messages
        assert socket_handler.arr_multi_response == []
        assert socket_handler.multi_message_wait_time == 2
        mock_ws_app.run_forever.assert_called_once_with(sslopt=ssl_options)

    @patch('websocket.WebSocketApp')
    @patch('websocket.enableTrace')
    def test_send_multi_socket_message_empty_url(self, mock_enable_trace, mock_websocket_app, socket_handler):
        """Test sending multiple messages with an empty URL."""
        messages = [{"message": "Hello"}, {"message": "World"}]

        with pytest.raises(ValueError):
            socket_handler.send_multi_socket_message("", messages)

        # Ensure WebSocketApp was not created
        mock_websocket_app.assert_not_called()

    @patch('websocket.WebSocketApp')
    @patch('websocket.enableTrace')
    def test_send_multi_socket_message_error(self, mock_enable_trace, mock_websocket_app, socket_handler):
        """Test error handling when sending multiple messages."""
        socket_url = "ws://example.com/websocket"
        messages = [{"message": "Hello"}, {"message": "World"}]

        # Setup error
        mock_websocket_app.side_effect = Exception("WebSocket error")

        # Test
        with pytest.raises(Exception) as exc_info:
            socket_handler.send_multi_socket_message(socket_url, messages)

        # Assertions
        assert "WebSocket error" in str(exc_info.value)
        mock_enable_trace.assert_called_once_with(True)

    def test_on_message(self, socket_handler):
        """Test __on_message method."""
        # Setup
        mock_ws = MagicMock()
        message = "Test message"

        # Test
        socket_handler._WebSocketHandler__on_message(mock_ws, message)

        # Assertions
        assert message in socket_handler.arr_multi_response

    def test_on_error(self, socket_handler):
        """Test __on_error method."""
        # Setup
        mock_ws = MagicMock()
        error = Exception("Test error")

        # Need to patch the logger to avoid actual logging
        with patch.object(socket_handler.logger, 'exception') as mock_logger:
            # Test
            socket_handler._WebSocketHandler__on_error(mock_ws, error)

            # Assertions
            assert mock_logger.call_count == 2
            assert mock_logger.call_args_list[0] == call("***ON_ERROR***")
            assert mock_logger.call_args_list[1] == call(error)

    def test_on_close(self, socket_handler):
        """Test __on_close method."""
        # Setup
        mock_ws = MagicMock()
        socket_handler.arr_multi_response = ["response1", "response2"]

        # Need to patch the logger to avoid actual logging
        with patch.object(socket_handler.logger, 'warning') as mock_logger:
            # Test
            socket_handler._WebSocketHandler__on_close(mock_ws)

            # Assertions
            assert mock_logger.call_count == 2
            assert mock_logger.call_args_list[0] == call("***ON_CLOSE***")
            assert mock_logger.call_args_list[1] == call(["response1", "response2"])

    @patch('_thread.start_new_thread')
    def test_on_open(self, mock_start_thread, socket_handler):
        """Test __on_open method."""
        # Setup
        mock_ws = MagicMock()
        socket_handler._ws = mock_ws
        socket_handler.list_messages = [{"message": "Hello"}, {"message": "World"}]

        # Need to patch the logger to avoid actual logging
        with patch.object(socket_handler.logger, 'info') as mock_logger:
            # Test
            socket_handler._WebSocketHandler__on_open()

            # Assertions
            mock_start_thread.assert_called_once()
            mock_logger.assert_called_once_with("WebSocket connection opened")

    @patch('_thread.start_new_thread')
    def test_run_thread_function(self, mock_start_thread, socket_handler):
        """Test the run function that's passed to the thread."""
        # Setup mocks
        mock_ws = MagicMock()
        socket_handler._ws = mock_ws
        socket_handler.list_messages = [{"message": "Hello"}, {"message": "World"}]
        socket_handler.multi_message_wait_time = 0.01  # Reduce wait time for test

        # Capture the function and arguments passed to start_new_thread
        def capture_thread_func(*args, **kwargs):
            # The first arg is the function to run
            thread_func = args[0]
            # Call it with empty args (same as the original implementation)
            thread_func()
            return MagicMock()

        mock_start_thread.side_effect = capture_thread_func

        # Test
        with patch('time.sleep') as mock_sleep:
            socket_handler._WebSocketHandler__on_open()

        # Assertions
        assert mock_ws.send.call_count == 2
        mock_ws.send.assert_has_calls([
            call(json.dumps({"message": "Hello"})),
            call(json.dumps({"message": "World"}))
        ])
        assert mock_sleep.call_count == 2
        mock_ws.close.assert_called_once()

    @patch('_thread.start_new_thread')
    def test_run_thread_function_error(self, mock_start_thread, socket_handler):
        """Test error handling in the run function."""
        # Setup mocks
        mock_ws = MagicMock()
        mock_ws.send.side_effect = Exception("Send error")
        socket_handler._ws = mock_ws
        socket_handler.list_messages = [{"message": "Hello"}]

        # Need to patch the logger to avoid actual logging
        with patch.object(socket_handler.logger, 'exception') as mock_logger:
            # Capture the function and arguments passed to start_new_thread
            def capture_thread_func(*args, **kwargs):
                # The first arg is the function to run
                thread_func = args[0]
                # Call it with empty args (same as the original implementation)
                thread_func()
                return MagicMock()

            mock_start_thread.side_effect = capture_thread_func

            # Test
            socket_handler._WebSocketHandler__on_open()

            # Assertions
            mock_ws.send.assert_called_once_with(json.dumps({"message": "Hello"}))
            assert mock_logger.call_count == 1
            assert "Send error" in mock_logger.call_args[0][1]