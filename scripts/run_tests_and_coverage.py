import os
import sys
import shutil
import subprocess


def run_tests_and_coverage(toxinidir, package_name, fail_on_test_error=True):
    """
    Runs tests, generates coverage report, and cleans up old HTML reports for the specified package.

    Args:
        toxinidir: The root directory of the tox project.
        package_name: The name of the package to run tests and coverage for.
        fail_on_test_error: Whether to raise an exception if the test command fails (default: True).
    """

    # Clean up existing HTML report directory
    html_report_dir = os.path.join(toxinidir, "coverage", "html_reports", package_name)
    if os.path.exists(html_report_dir):
        shutil.rmtree(html_report_dir)
        print(f"Deleted existing HTML report directory for {package_name}.")

    # Run tests and generate coverage data
    test_command = ['pytest', '--cov=' + package_name, './tests/',
                    f'--html={toxinidir}/unit_test_reports/{package_name}_report.html']
    subprocess.run(test_command, check=fail_on_test_error)

    # Generate HTML coverage report
    coverage_command = ['coverage', 'html', '-d', html_report_dir]
    subprocess.run(coverage_command, check=fail_on_test_error)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python run_tests_and_coverage.py <toxinidir> <package_name> <fail_on_test_error>")
        sys.exit(1)

    _toxinidir = sys.argv[1]
    _package_name = sys.argv[2]
    _fail_on_test_error = sys.argv[3].lower() == 'true'  # Convert string to boolean
    run_tests_and_coverage(_toxinidir, _package_name, _fail_on_test_error)
