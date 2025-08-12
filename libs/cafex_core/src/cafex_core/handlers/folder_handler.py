import os
import shutil
from datetime import datetime
from pathlib import Path

from ..reporting_._report_viewer import stop_server


class FolderHandler:
    """A class that handles file and folder operations."""

    @staticmethod
    def delete_files_in_folder(folder_path):
        """Delete all files in the specified folder.

        Args:
            folder_path (str): The path of the folder containing the files to be deleted.

        Returns:
            None

        Raises:
            None
        """
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"File '{file_path}' deleted successfully.")
                    elif os.path.isdir(file_path):  # Optional: Delete subfolders
                        shutil.rmtree(file_path)
                except OSError as e:
                    print(f"Error deleting '{file_path}': {e}")

    @staticmethod
    def create_folder(root_dir, folder_name):
        """Create a folder in the specified root directory.

        Args:
            root_dir (str): The root directory where the folder will be created.
            folder_name (str): The name of the folder to be created.

        Returns:
            None

        Raises:
            None
        """
        folder_path = os.path.join(root_dir, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    @staticmethod
    def delete_folder(folder_path):
        """Delete the specified folder and all its contents.

        Args:
            folder_path (str): The path of the folder to be deleted.

        Returns:
            None

        Raises:
            None
        """
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
            except Exception as e:
                print(f"Error deleting folder '{folder_path}': {e}")

    @staticmethod
    def reorganize_result_folders(conf_cwd, current_execution_uuid):
        """Reorganize result folders by moving existing results to a history
        folder, sorting them, and keeping only the 10 most recent, excluding
        the current execution.

        Args:
            conf_cwd (str): The root directory of the project.
            current_execution_uuid (str): The UUID of the current execution.

        Returns:
            None
        """
        result_dir = os.path.join(conf_cwd, "result")
        history_dir = os.path.join(result_dir, "history")

        # Create history folder if it doesn't exist
        os.makedirs(history_dir, exist_ok=True)

        # Get all subdirectories in the result folder, excluding the current execution and history
        subdirs = [
            d
            for d in os.listdir(result_dir)
            if os.path.isdir(os.path.join(result_dir, d))
            and d != "history"
            and d != current_execution_uuid
        ]

        # Rename and move subdirectories to history folder
        for subdir in subdirs:
            src_path = os.path.join(result_dir, subdir)
            creation_time = datetime.fromtimestamp(os.path.getctime(src_path))

            stop_server(Path(src_path))

            # Check if the folder name already starts with a timestamp
            if not subdir[:15].replace("_", "").isdigit():
                new_name = f"{creation_time.strftime('%Y%m%d_%H%M%S')}_{subdir}"
            else:
                new_name = subdir

            dst_path = os.path.join(history_dir, new_name)
            shutil.move(src_path, dst_path)

        # Sort history folders by creation date (newest first)
        history_subdirs = [
            d for d in os.listdir(history_dir) if os.path.isdir(os.path.join(history_dir, d))
        ]
        sorted_history_subdirs = sorted(
            history_subdirs,
            key=lambda x: os.path.getctime(os.path.join(history_dir, x)),
            reverse=True,
        )

        # Keep only the 10 most recent history folders
        for old_dir in sorted_history_subdirs[10:]:
            shutil.rmtree(os.path.join(history_dir, old_dir))
