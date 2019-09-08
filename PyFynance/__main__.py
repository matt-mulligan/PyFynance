import argparse
import datetime
import logging
import os
import sys

from core.config import Configuration
from core.helpers import makedirs


def main():
    args = parse_arguments(sys.argv[1:])
    config = Configuration()
    logger = configure_logger(config.paths.logs_path, config.version, args.task_type)

def configure_logger(log_path, version, task_type):
    """
    this method will set the logging configuration for each run of PyFynance
    :param log_path:
    :param version:
    :param task_type:
    :return:
    """

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(name)-35s %(levelname)-8s %(message)s")

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    log_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    log_filename = "{log_path}{sep}{version}{sep}PyFynance_{task_type}_{timestamp}.log".format(log_path=log_path,
                                                                                               sep=os.sep,
                                                                                               version=str(version),
                                                                                               task_type=task_type,
                                                                                               timestamp=log_datetime)
    makedirs(log_filename)

    fh = logging.FileHandler(log_filename, "w")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info("Logging Service Initalised")
    logger.info("PyFynance Version = {}".format(version))
    logger.info("PyFynance Task Type = {}".format(task_type))

    return logger


def _create_arg_parser():
    """
    this method will create an argument parser object
    :return:
    """

    parser = argparse.ArgumentParser(description="PyFynance Argument parser")
    parser.add_argument("--task_type", metavar="task_type", help="task_type", choices=["load_transactions"])
    return parser


def parse_arguments(cmd_line_args):
    """
    this method will setup and load the arguments using the Arg Parser class
    :return:
    """
    arg_parser = _create_arg_parser()
    return arg_parser.parse_args(cmd_line_args)


if __name__ == "__main__":
    main()
