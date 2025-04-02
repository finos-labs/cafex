import json
import os


class FileHandler:

    @staticmethod
    def create_json_file(directory, filename, data=None, indent=2):
        """Creates a new JSON file at the specified directory with the given
        filename.

        Args:
            directory (str): The directory where the file will be created.
            filename (str): The name of the file to be created.
            data (list or dict): The data to be written to the file. Can be a list or a dictionary.
            indent (int): The number of spaces to use for indentation. Default is 2.
        """
        filepath = os.path.join(directory, filename)
        if data is None:
            data = {}
        with open(filepath, "w") as file:
            json.dump(data, file, indent=indent)

    @staticmethod
    def delete_file(filepath):
        """Deletes the file at the specified filepath.

        Args:
            filepath (str): The path of the file to be deleted.
        """
        if os.path.exists(filepath):
            os.remove(filepath)
        else:
            print("File does not exist.")

    @staticmethod
    def add_data_to_json_file(filepath, data):
        """Adds data to an existing JSON file.

        Args:
            filepath (str): The path of the JSON file.
            data (dict): The data to be added to the JSON file.
        """
        with open(filepath, "r+") as file:
            json_data = json.load(file)
            json_data.update(data)
            file.seek(0)
            json.dump(json_data, file, indent=4)

    @staticmethod
    def read_data_from_json_file(filepath):
        """Reads data from a JSON file and returns it.

        Args:
            filepath (str): The path of the JSON file.

        Returns:
            dict or list: The data read from the JSON file.
        """

        try:
            with open(filepath, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {filepath}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in file: {filepath}")
