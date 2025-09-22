import json
import socket
from pathlib import Path
from typing import Any, Dict

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore

from ._report_viewer import create_server_script, launch_server_and_browser

logger = CoreLogger(name=__name__).get_logger()
session_store = SessionStore()


class ReportGenerator:
    """Generates a self-contained HTML test report."""

    REQUIRED_FILES = ["index.html", "styles.css", "app.js"]

    @staticmethod
    def _find_free_port(start_port: int = 8000) -> int:
        """Find an available port starting from start_port."""
        for port in range(start_port, start_port + 100):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(("localhost", port))
                if result != 0:  # Port is available
                    return port
        raise RuntimeError("No available ports found")

    @staticmethod
    def _validate_paths(result_dir: Path, viewer_source: Path) -> None:
        """Validates all required paths and files exist."""
        if not result_dir.exists():
            raise FileNotFoundError(f"Result directory does not exist: {result_dir}")

        for file_name in ReportGenerator.REQUIRED_FILES:
            if not (viewer_source / file_name).exists():
                raise FileNotFoundError(f"Missing required file: {file_name}")

        result_file = result_dir / "result.json"
        if not result_file.exists():
            raise FileNotFoundError(f"Missing result.json file: {result_file}")

    @staticmethod
    def _read_file(file_path: Path) -> str:
        """Reads file content with utf-8 encoding."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _create_html_report(
        html_template: str, css_content: str, js_content: str, result_data: Dict[str, Any]
    ) -> str:
        """Creates the self-contained HTML report content."""
        return html_template.replace(
            "<!-- STYLE_PLACEHOLDER -->", f"<style>\n{css_content}\n</style>"
        ).replace(
            "<!-- SCRIPT_PLACEHOLDER -->",
            f"<script>\nconst reportData = {json.dumps(result_data, indent=2)};\n{js_content}\n</script>",
        )

    @staticmethod
    def _write_report(content: str, output_file: Path) -> None:
        """Writes the report file."""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def _get_log_files(result_dir: Path) -> list:
        """Get all log files from the logs directory."""
        logs_dir = result_dir / "logs"
        if not logs_dir.exists():
            return []

        log_files = []
        for log_file in logs_dir.glob("*.log"):
            try:
                with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                    log_files.append(
                        {
                            "name": log_file.name,
                            "content": f.read(),
                            "timestamp": log_file.name.split("_")[1].split(".")[
                                0
                            ],  # Extract timestamp from filename
                        }
                    )
            except Exception as e:
                logger.warning("Error reading log file %s: %s", log_file, e)
                continue

        # Sort by timestamp descending
        return sorted(log_files, key=lambda x: x["timestamp"], reverse=True)

    @staticmethod
    def prepare_report_viewer(result_dir: str | Path) -> bool:
        """Creates a self-contained HTML report file, generates a server script, and launches both
        server and browser.
        """
        try:
            logger.info("Starting report generation process...")
            result_dir = Path(result_dir)
            output_file = result_dir / "report.html"
            viewer_source = Path(__file__).parent / "_report_viewer"

            # Validate paths
            ReportGenerator._validate_paths(result_dir, viewer_source)

            # Read all required files
            file_contents = {}
            for file_name in ReportGenerator.REQUIRED_FILES:
                file_contents[file_name] = ReportGenerator._read_file(viewer_source / file_name)

            # Read result data
            with open(result_dir / "result.json", "r", encoding="utf-8") as f:
                result_data = json.load(f)

            logger.info("Report generated successfully : %s", output_file)

            # Get log files and add to result data
            log_files = ReportGenerator._get_log_files(result_dir)
            result_data["logs"] = log_files

            # Create HTML report
            complete_html = ReportGenerator._create_html_report(
                file_contents["index.html"],
                file_contents["styles.css"],
                file_contents["app.js"],
                result_data,
            )

            # Write report file
            ReportGenerator._write_report(complete_html, output_file)

            # Launch server and open browser
            if session_store.base_config.get("auto_launch_report", True):
                # Find available port and create server script
                port = ReportGenerator._find_free_port()
                script_file = create_server_script(result_dir, port)

                launch_server_and_browser(script_file, port)

                logger.info("\nReport server started!")
                logger.info("Report URL: http://localhost:%s/report.html", port)
                logger.info("\nNote: Close the server window when done viewing the report.")

            return True

        except Exception as e:
            logger.exception("Unexpected error during report generation: %s", e)
            return False
