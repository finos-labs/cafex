import argparse
import inspect

from .mobile_client import MobileClientActionsClass, MobileDriverClass
from .web_client import Keyboard_Mouse_Class, WebDriverClass


class CafeXWeb(Keyboard_Mouse_Class, WebDriverClass):
    pass


class CafeXMobile(MobileClientActionsClass, MobileDriverClass):
    pass


def list_methods():
    methods = inspect.getmembers(CafeXWeb, predicate=inspect.isfunction)
    for name, method in methods:
        print(f"{name}: {method.__doc__}")


def main():
    parser = argparse.ArgumentParser(description="CafeXWeb CLI")
    parser.add_argument(
        "--list-methods", action="store_true", help="Show all methods of CafeXWeb class"
    )
    args = parser.parse_args()

    if args.list_methods:
        list_methods()


__version__ = "0.0.43"
