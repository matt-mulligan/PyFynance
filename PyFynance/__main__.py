import argparse
import sys
from core.config import Configuration


def main():
    args = _parse_arguments(sys.argv[1:])
    config = Configuration()


def _create_arg_parser():
    """
    this method will create an argument parser object
    :return:
    """

    parser = argparse.ArgumentParser(description="PyFynance Argument parser")
    parser.add_argument("--task_type", metavar="task_type", help="task_type", choices=["load_transactions"])
    return parser


def _parse_arguments(cmd_line_args):
    """
    this method will setup and load the arguments using the Arg Parser class
    :return:
    """
    arg_parser = _create_arg_parser()
    return arg_parser.parse_args(cmd_line_args)


if __name__ == "__main__":
    main()
