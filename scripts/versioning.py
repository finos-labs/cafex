import os
import argparse
import json
import re


def get_version(package):
    with open(os.path.join("libs", package, "version.txt")) as f:
        return f.read().strip()


def increment_version(package, part):
    major, minor, patch = map(int, get_version(package).split("."))
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def update_package_version(package_name, new_version):
    package_dir = os.path.join("libs", package_name)

    # Determine the correct base directory for file operations
    if os.getcwd().endswith(package_name) and "libs" in os.getcwd():  # Running from within the package directory
        base_dir = os.path.join("..", "..")  # Go up two levels
    else:
        base_dir = "."  # Running from project root

    with open(os.path.join(base_dir, package_dir, "version.txt"), "w") as f:
        f.write(new_version)

    init_file = os.path.join(base_dir, package_dir, "src", package_name, "__init__.py")
    with open(init_file, "r+") as f:
        content = f.read()
        # Use regex to find and replace the version, regardless of the existing value
        version_pattern = r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]'
        updated_content = re.sub(version_pattern, f'__version__ = "{new_version}"', content, count=1)

        f.seek(0)
        f.write(updated_content)
        f.truncate()
    print(f"Version for {package_name} updated to: {new_version}")


def handle_version_argument(args):
    for package, new_version in args.version.items():
        update_package_version(package, new_version)


def handle_bump_argument(args):
    for package, bump_type in args.bump.items():
        new_version = increment_version(package, bump_type)
        update_package_version(package, new_version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Version management script")
    parser.add_argument("--version", type=str)
    parser.add_argument("--bump", type=str)
    args = parser.parse_args()

    if args.version:
        args.version = json.loads(args.version)
        handle_version_argument(args)
    elif args.bump:
        bump_list = args.bump.split()
        bump_dict = {}
        for i in range(0, len(bump_list), 2):
            bump_dict[bump_list[i]] = bump_list[i + 1]
        args.bump = bump_dict
        handle_bump_argument(args)
