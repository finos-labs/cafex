import argparse
import inspect

from .mobile_client import MobileClientActionsClass, MobileDriverClass
from .web_client import WebDriverClass, PlaywrightClass


class CafeXWeb(PlaywrightClass,WebDriverClass):
    def __init__(self):
        PlaywrightClass.__init__(self)
        WebDriverClass.__init__(self)

class CafeXMobile(MobileClientActionsClass, MobileDriverClass):
    def __init__(self):
        MobileClientActionsClass.__init__(self)
        MobileDriverClass.__init__(self)


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
