import shutil

import coverage
import os
import sys


def combine_coverage(toxinidir_):
    """Combines coverage data from packages."""
    packages = ["cafex_api", "cafex_ui", "cafex_db", "cafex_core", "cafex_desktop"]
    data_paths = [os.path.join(toxinidir_, "coverage", package) for package in packages]

    # Specify the path for the combined .coverage file
    combined_coverage_file = os.path.join(toxinidir_, "coverage", "combined", ".coverage")
    combined_html_report_dir = os.path.join(toxinidir_, "coverage", "html_reports", "combined")

    if os.path.exists(combined_coverage_file):
        os.remove(combined_coverage_file)
        print(f"Deleted previous combined .coverage file: {combined_coverage_file}")

    if os.path.exists(combined_html_report_dir):
        shutil.rmtree(combined_html_report_dir)
        print(f"Deleted previous combined HTML report directory: {combined_html_report_dir}")

    # Create a Coverage object and configure it
    cov = coverage.Coverage(
        config_file=os.path.join(toxinidir_, "toxtool.toml"),
        data_file=combined_coverage_file  # Set the data_file parameter
    )

    # Filter data_paths to include only existing directories
    existing_data_paths = [path for path in data_paths if os.path.exists(path)]

    # Combine data from existing paths
    if existing_data_paths:
        coverage_files = [os.path.join(path, '.coverage') for path in existing_data_paths if
                          os.path.exists(os.path.join(path, '.coverage'))]
        if coverage_files:
            cov.combine(data_paths=coverage_files, keep=True)
        else:
            print("No coverage files found to combine.")
        cov.save()
        print("Coverage data combined successfully.")
    else:
        print("No coverage data directories found.")

    # Reload the combined data
    cov.load()

    # Generate combined HTML report
    cov.html_report(directory=combined_html_report_dir)
    print("Combined coverage HTML report generated.")


if __name__ == "__main__":
    toxinidir = sys.argv[1]  # Get toxinidir_ from command-line arguments
    combine_coverage(toxinidir)
