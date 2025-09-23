import subprocess
import argparse
import os
import sys
import shutil

VALID_PACKAGES = ["cafex", "cafex_api", "cafex_core", "cafex_db", "cafex_ui",
                  "cafex_desktop"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build script for packages")
    parser.add_argument("package_name", nargs='?', default=None,
                        help="Name of the package to build (e.g., cafex_api). If not provided, use current directory.")
    parser.add_argument("--version", help="Specify the version directly")
    parser.add_argument("--bump", choices=["major", "minor", "patch"], default=None, help="Increment version part")
    args = parser.parse_args()

    if not args.package_name:
        package_dir = os.getcwd()
        # If package_name isn't provided, try to infer it from the current directory
        args.package_name = os.path.basename(package_dir)
    else:
        package_dir = os.path.join("libs", args.package_name)

    if args.package_name not in VALID_PACKAGES:
        raise ValueError(f"Invalid package name: {args.package_name}. Must be one of: {VALID_PACKAGES}")

    if args.version or args.bump:
        versioning_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts", "versioning.py"))
        # Call versioning.py script
        command = ["python", versioning_script]
        if args.version:  # Add --version argument only if it's not None
            # Update the --version argument to be a JSON string
            command.extend(["--version", f'{{"{args.package_name}": "{args.version}"}}'])
        elif args.bump:  # Add --bump argument only if it's not None
            command.extend(["--bump", f"{args.package_name} {args.bump}"])

        result = subprocess.run(
            command,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise Exception(f"Error updating version: {result.stderr}")
        else:
            print(result.stdout)

    output_dir = os.path.join("..", "..", "dist", args.package_name)

    # Clean the output directory before building
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        print(f"Cleaned output directory: {output_dir}")

    # Build the package
    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", ".", "--outdir", output_dir],
        cwd=package_dir
    )
