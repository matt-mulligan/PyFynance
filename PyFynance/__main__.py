import argparse
import datetime
import os
import sys


def main():  # pragma: no cover
    """
    bootstrap method for PyFynance App
    :return:
    """

    configure_libraries()
    args = parse_arguments(sys.argv[1:])
    from core.pyfynance import PyFynance

    app = PyFynance(args)
    exit_code = app.run()
    sys.exit(exit_code)


def configure_libraries():
    """
    THis method will append the code root of PyFynance to the python path so that all import statements work
    :return:
    """
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_known_arg_parser():  # pragma: no cover
    """
    this method will create an argument parser object for the arguments we know will be passed to the library
    :return: Agrparse object to parse known arguments
    """

    parser = argparse.ArgumentParser(description="PyFynance Known Arguments parser")
    parser.add_argument(
        "--task_type",
        metavar="task_type",
        help="task_type",
        choices=["load_transactions"],
        required=True,
    )
    return parser


def create_load_tran_parser():
    """
    this method will create an argument parser object for the arguments we know will be passed to the library
    :return: Agrparse object to parse known arguments
    """

    parser = argparse.ArgumentParser(
        description="PyFynance Load Transactions argument parser"
    )
    parser.add_argument(
        "--institution", metavar="institution", help="institution", required=True
    )
    parser.add_argument("--account", metavar="account", help="account", required=True)
    return parser


def parse_arguments(cmd_line_args):  # pragma: no cover
    """
    this method will setup and load the arguments using the Arg Parser class

    :return: python object conatining the arguments parsed from the command line
    """
    known_args_parser = create_known_arg_parser()
    args, remaining_args = known_args_parser.parse_known_args(cmd_line_args)

    if args.task_type == "load_transactions":
        lt_parser = create_load_tran_parser()
        lt_parser.parse_args(remaining_args, namespace=args)

    args.runtime = datetime.datetime.now()

    return args


if __name__ == "__main__":  # pragma: no cover
    main()
