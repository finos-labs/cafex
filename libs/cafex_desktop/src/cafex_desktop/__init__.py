import argparse
import inspect

from .desktop_client import DesktopClientActionsClass


class CafeXDesktop(DesktopClientActionsClass):
    pass


def list_methods():
    methods = inspect.getmembers(CafeXDesktop, predicate=inspect.isfunction)
    for name, method in methods:
        print(f"{name}: {method.__doc__}")


def main():
    parser = argparse.ArgumentParser(description="CafeXDesktop CLI")
    parser.add_argument(
        "--list-methods", action="store_true", help="Show all methods of CafeXDesktop class"
    )
    args = parser.parse_args()

    if args.list_methods:
        list_methods()


__version__ = "0.0.44"
