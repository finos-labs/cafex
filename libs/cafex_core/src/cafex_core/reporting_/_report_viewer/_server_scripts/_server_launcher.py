import json
import os
import subprocess
import time
import webbrowser
from pathlib import Path

import psutil
from cafex_core.logging.logger_ import CoreLogger

logger = CoreLogger(name=__name__).get_logger()


def _get_server_info(directory: Path) -> dict:
    """Get server information if it exists.

    Args:
        directory (Path): Directory to check for server info

    Returns:
        dict: Server information or empty dict if not found
    """
    info_file = directory / ".server_info"
    try:
        if info_file.exists():
            with open(info_file) as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not read server info: {e}")
    return {}


def stop_server(directory: Path) -> None:
    """Stop any running server for the given directory.

    Args:
        directory (Path): Directory whose server should be stopped
    """
    try:
        info = _get_server_info(directory)
        port = info.get("port")

        if not port:
            return

        for proc in psutil.process_iter(attrs=["pid", "name"]):
            try:
                connections = proc.connections(kind="inet")  # Only check network connections
                for conn in connections:
                    if conn.laddr.port == port:
                        logger.info(f"Stopping server (PID: {proc.pid}) running on port {port}")
                        proc.terminate()  # Gracefully terminate first
                        proc.wait(timeout=2)  # Wait for 2 seconds
                        if proc.is_running():
                            proc.kill()  # Force kill if still running
                        time.sleep(0.5)  # Give time to shut down
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue  # Skip processes we can't access

        # Clean up server info file
        info_file = directory / ".server_info"
        if info_file.exists():
            info_file.unlink()

    except Exception as e:
        logger.warning(f"Error stopping server: {e}")


def launch_server_and_browser(script_file: Path, port: int) -> None:
    """Launches the server and opens the browser.

    Args:
        script_file (Path): Path to the server script to execute
        port (int): Port number the server will use

    Raises:
        Exception: If server launch fails
    """
    try:
        if os.name == "nt":  # Windows
            os.startfile(script_file)
        else:  # Unix
            subprocess.Popen(["xterm", "-e", f"bash {script_file}"])

        # Give the server a moment to start
        time.sleep(1)

        # Open browser
        url = f"http://localhost:{port}/report.html"
        webbrowser.open(url)

    except Exception as e:
        logger.error(f"Error launching server: {e}")
        raise
