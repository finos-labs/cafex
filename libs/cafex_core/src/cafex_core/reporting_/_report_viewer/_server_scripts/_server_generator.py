import json
import os
from pathlib import Path

from cafex_core.logging.logger_ import CoreLogger

logger = CoreLogger(name=__name__).get_logger()


def _save_server_info(directory: Path, port: int) -> None:
    """Save server information to a file.

    Args:
        directory (Path): Directory where to save the server info
        port (int): Port number being used by the server
    """
    info_file = directory / ".server_info"
    try:
        with open(info_file, "w") as f:
            json.dump({"port": port}, f)
    except Exception as e:
        logger.warning(f"Could not save server info: {e}")


def create_server_script(directory: Path, port: int) -> Path:
    """Creates a script to start the server.

    Args:
        directory (Path): Directory to serve
        port (int): Port number to use

    Returns:
        Path: Path to the created server script

    Raises:
        Exception: If script creation fails
    """
    try:
        # Save server info
        _save_server_info(directory, port)

        if os.name == "nt":  # Windows
            script_content = f"""@echo off
echo Starting server...
cd /d "{directory}"
echo.
echo Server running at http://localhost:{port}
echo.
echo To stop the server, close this window
echo.
python -m http.server {port} --bind localhost --directory "{directory}"
del /f .server_info
"""
            script_file = directory / "start_report_server.bat"
        else:  # Unix
            script_content = f"""#!/bin/bash
echo "Starting server..."
cd "{directory}"
echo "Server running at http://localhost:{port}"
echo ""
echo "To stop the server, press Ctrl+C"
python3 -m http.server {port} --bind localhost --directory "{directory}"
rm -f .server_info
"""
            script_file = directory / "start_report_server.sh"

        with open(script_file, "w", newline="\n") as f:
            f.write(script_content)

        if not os.name == "nt":
            os.chmod(script_file, 0o755)  # Make executable on Unix

        return script_file

    except Exception as e:
        logger.error(f"Error creating server script: {e}")
        raise
