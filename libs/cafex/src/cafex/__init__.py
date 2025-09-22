import importlib.util


def is_package_installed(package_name):
    """Check if a package is installed."""
    return importlib.util.find_spec(package_name) is not None


if is_package_installed("cafex_ui"):
    from cafex_ui import CafeXWeb, CafeXMobile
else:
    print("Package 'cafex_ui' is not installed.")

if is_package_installed("cafex_api"):
    print("cafex_api package is installed.")
    from cafex_api import CafeXAPI
else:
    print("Package 'cafex_api' is not installed.")

if is_package_installed("cafex_db"):
    from cafex_db import CafeXDB
else:
    print("Package 'cafex_db' is not installed.")

if is_package_installed("cafex_desktop"):
    from cafex_desktop import CafeXDesktop
else:
    print("Package 'cafex_desktop' is not installed.")


__version__ = "0.0.41"

