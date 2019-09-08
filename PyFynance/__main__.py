import argparse
import datetime
import logging
import os
import sys


def main():  # pragma: no cover
    """
    bootstrap method for PyFynance App
    :return:
    """

    configure_libraries()
    args = parse_arguments(sys.argv[1:])
    from pyfynance import PyFynance
    app = PyFynance(args)
    exit_code = app.run()
    sys.exit(exit_code)


def configure_libraries():
    """
    THis method will append the code root of PyFynance to the python path so that all import statements work
    :return:
    """
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_arg_parser():  # pragma: no cover
    """
    this method will create an argument parser object
    :return:
    """

    parser = argparse.ArgumentParser(description="PyFynance Argument parser")
    parser.add_argument("--task_type", metavar="task_type", help="task_type", choices=["load_transactions"],
                        required=True)
    return parser


def parse_arguments(cmd_line_args):  # pragma: no cover
    """
    this method will setup and load the arguments using the Arg Parser class
    :return:
    """
    arg_parser = create_arg_parser()
    return arg_parser.parse_args(cmd_line_args)


if __name__ == "__main__":  # pragma: no cover
    main()
