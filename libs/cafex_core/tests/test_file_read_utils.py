import unittest
import pytest
import zipfile
import os
import pandas as pd
import csv
from cafex_core.utils.file_reader_utils import FileReaderUtil
from docx import Document


file_reader_util = FileReaderUtil()

class MyTestCase(unittest.TestCase):
    def test_read_pdf_file(self):
        pdf_file_path = 'path/to/file.pdf'
        expected_first_word = "word"
        pdf_content = file_reader_util.read_pdf_file(pdf_file_path)
        first_word = pdf_content[0].split()[0] if pdf_content and len(pdf_content[0].split()) > 0 else None
        assert first_word == expected_first_word, f"Expected '{expected_first_word}', but got '{first_word}'"

    def test_read_pdf_file_invalid_path(self):
        invalid_pdf_file_path = 'path/to/invalidfile.pdf'
        with pytest.raises(Exception) as e:
            file_reader_util.read_pdf_file(invalid_pdf_file_path)
        assert "An error occurred while reading the PDF file" in str(e.value)

    def test_read_excel_file(self):
        excel_file_path = 'path/to/valid.xlsx'
        expected_first_value = 789
        sheet_content = file_reader_util.read_excel(excel_file_path,sheet_reference=0)
        first_value = sheet_content[1][1] if sheet_content and len(sheet_content) > 1 else None
        assert first_value == expected_first_value, f"Expected '{expected_first_value}', but got '{first_value}'"

    def test_read_excel_valid_file_and_sheet_name(self):
        excel_file_path = 'path/to/valid.xlsx'
        expected_values = [[123, 456], [678, 789]]
        values = file_reader_util.read_excel(excel_file_path)
        assert values == expected_values, f"Expected {expected_values}, but got {values}"

    def test_read_excel_file_invalid_path(self):
        invalid_excel_file_path = 'path/to/invalid.xlsx'
        with pytest.raises(Exception) as e:
            file_reader_util.read_excel(invalid_excel_file_path,sheet_reference="Sheet2")
        assert "An error occurred while reading the Excel file" in str(e.value)
        print(e)

    def test_read_word_file(self):
        word_file_path = 'path/to/valid.docx'
        expected_content = ["Hi", "CAFÉ"]
        word_content = file_reader_util.read_word_file(word_file_path)
        assert word_content == expected_content, f"Expected {expected_content}, but got {word_content}"

    def test_read_word_file_invalid_path(self):
        invalid_word_file_path = 'path/to/invalid.docx'
        with pytest.raises(Exception) as e:
            file_reader_util.read_word_file(invalid_word_file_path)
        assert "An error occurred while reading the Word file" in str(e.value)

    def test_read_csv_file_valid(self):
        csv_file_path = 'path/to/valid.csv'
        expected_headers = ['Customer ID', 'Age', 'Gender']
        expected_data = [
            ['1', '55', 'Male'],
            ['2', '19', 'Male'],
            ['3', '50', 'Male']
        ]
        content = file_reader_util.read_csv_file(csv_file_path)
        assert len(content) > 3, "The CSV file does not contain enough rows."
        actual_headers = content[0][:3]
        assert actual_headers == expected_headers, f"Expected headers {expected_headers}, but got {actual_headers}"
        for i in range(3):
            assert content[i + 1][:3] == expected_data[
                i], f"Expected data {expected_data[i]}, but got {content[i + 1][:3]}"

    def test_read_csv_file_invalid_path(self):
        invalid_csv_file_path = 'path/to/invalidfile.csv'
        with pytest.raises(Exception) as e:
            file_reader_util.read_csv_file(invalid_csv_file_path)
        assert "An error occurred while reading the CSV file" in str(e.value)

    def test_extract_7z_file(self):
        zip_file_path = 'path/to/valid.7z'
        target_dir = 'path/to/target'
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        extracted_file_path = file_reader_util.extract_7z_file(zip_file_path, target_dir)
        extracted_files = os.listdir(target_dir)
        assert len(extracted_files) > 0, "Expected some files to be extracted, but none were found."

    def test_extract_7z_file_invalid_path(self):
        invalid_zip_file_path = 'path/to/invalidfile.7z'
        target_dir = 'path/to/target'
        with pytest.raises(Exception) as e:
            file_reader_util.extract_7z_file(invalid_zip_file_path, target_dir)
        assert "The provided file is not supported" in str(e.value)

    def test_unzip_zip_file(self):
        zip_file_path ='path/to/valid.zip'
        target_dir = 'path/to/target'
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        file_reader_util.unzip_zip_file(zip_file_path, target_dir)
        extracted_files = os.listdir(target_dir)
        assert len(extracted_files) > 0, "Expected some files to be extracted, but none were found."

    def test_unzip_zip_file_invalid_path(self):
        invalid_zip_file_path = 'path/to/invalidfile.zip'
        target_dir = 'path/to/target'
        with pytest.raises(Exception) as e:
            file_reader_util.unzip_zip_file(invalid_zip_file_path, target_dir)
        assert "The provided file is not supported" in str(e.value)

    def test_read_txt_file_valid(self):
        txt_file_path = 'path/to/valid.txt'
        expected_content = "Hi Hello"
        content = file_reader_util.read_txt_file(txt_file_path)
        assert content == expected_content, f"Expected content '{expected_content}', but got '{content}'"

    def test_read_txt_file_invalid_path(self):
        invalid_txt_file_path = 'path/to/invalid.txt'
        with pytest.raises(Exception) as e:
            file_reader_util.read_txt_file(invalid_txt_file_path)
        assert "An error occurred while reading the text file" in str(e.value)

    def test_write_txt_file_valid(self):
        txt_file_path = 'path/to/valid.txt'
        content = "This is a test content for the text file."
        file_reader_util.write_txt_file(txt_file_path, content)
        assert os.path.exists(txt_file_path), f"Expected file '{txt_file_path}' does not exist."
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            written_content = f.read()
            assert written_content == content, f"Expected content '{content}', but got '{written_content}'."

    def test_write_txt_file_invalid_path(self):
        invalid_txt_file_path = 'path/to/invalid.txt'
        content = "This content will not be written due to an invalid path."
        with pytest.raises(Exception) as e:
            file_reader_util.write_txt_file(invalid_txt_file_path, content)
        assert "An error occurred while writing to the text file" in str(e.value)


    def test_write_excel_file_valid(self):
        excel_file_path = 'path/to/valid.xlsx'
        data = [
            ['Customer ID', 'Age', 'Gender'],
            ['1', '55', 'Male'],
            ['2', '19', 'Male'],
            ['3', '50', 'Male']
        ]
        file_reader_util.write_excel_file(excel_file_path, data)
        assert os.path.exists(excel_file_path), f"Expected Excel file '{excel_file_path}' does not exist."
        df = pd.read_excel(excel_file_path)
        expected_df = pd.DataFrame(data)
        pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)

    def test_write_excel_file_invalid_path(self):
        invalid_excel_file_path = 'path/to/invalid.xlsx'
        data = [
            ['Customer ID', 'Age', 'Gender'],
            ['1', '55', 'Male']
        ]
        with pytest.raises(Exception) as e:
            file_reader_util.write_excel_file(invalid_excel_file_path, data)
        assert "An error occurred while writing to the Excel file" in str(e.value)

    def test_write_word_file_valid(self):
        word_file_path = 'path/to/valid.docx'
        content = [
            "This is the first paragraph.",
            "This is the second paragraph.",
            "This is the third paragraph."
        ]
        file_reader_util.write_word_file(word_file_path, content)
        assert os.path.exists(word_file_path), f"Expected Word file '{word_file_path}' does not exist."
        doc = Document(word_file_path)
        written_content = [para.text for para in doc.paragraphs]
        assert written_content == content, f"Expected content {content}, but got {written_content}."

    def test_write_word_file_invalid_path(self):
        invalid_word_file_path = 'path/to/invalid.doc'
        content = [
            "This content will not be written due to an invalid path."
        ]
        with pytest.raises(Exception) as e:
            file_reader_util.write_word_file(invalid_word_file_path, content)
        assert "An error occurred while writing to the Word file" in str(e.value)

    def test_write_csv_file_valid(self):
        csv_file_path = 'path/to/valid.csv'
        data = [
            ['Customer ID', 'Age', 'Gender'],
            ['1', '55', 'Male'],
            ['2', '19', 'Male'],
            ['3', '50', 'Male']
        ]
        file_reader_util.write_csv_file(csv_file_path, data)
        assert os.path.exists(csv_file_path), f"Expected CSV file '{csv_file_path}' does not exist."
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            written_content = list(reader)
        assert written_content == data, f"Expected content {data}, but got {written_content}."

    def test_write_csv_file_invalid_path(self):
        invalid_csv_file_path = 'path/to/invalid.csv'
        data = [
            ['Customer ID', 'Age', 'Gender'],
            ['1', '55', 'Male']
        ]
        with pytest.raises(Exception) as e:
            file_reader_util.write_csv_file(invalid_csv_file_path, data)
        assert "An error occurred while writing to the CSV file" in str(e.value)

    def test_delete_file_valid(self):
        test_file_path = 'path/to/valid.txt'
        # with open(test_file_path, 'w') as f:
        #     f.write("This is a test file.")
        assert os.path.exists(test_file_path), "Test file does not exist before deletion."
        file_reader_util.delete_file(test_file_path)
        assert not os.path.exists(test_file_path), "Test file still exists after deletion."

    def test_delete_file_invalid_path(self):
        invalid_file_path = 'path/to/invalidfile.txt'
        with pytest.raises(Exception) as e:
            file_reader_util.delete_file(invalid_file_path)
        assert f"The file '{invalid_file_path}' does not exist." in str(e.value)



if __name__ == '__main__':
    unittest.main()
