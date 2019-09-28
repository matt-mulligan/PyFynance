import glob
import os
import shutil

from core.config import Configuration


def find_all_files(search_path):
    """
    this public function will search the specified path and return all files that match
    :param search_path: a full path that can be searched using glob
    :return: a list of matching files
    """

    return glob.glob(search_path)


def delete_file(filepath):
    """
    This public function will delete the file path passed to it

    :param filepath: the full path to the file
    :return: None
    """

    os.remove(filepath)


def copy_file(source_path, dest_path):
    """
    This public function will copy the file from the source path to the destination path

    :param source_path: the source path to get the file from
    :param dest_path: the destination path to copy the file to
    :return: None
    """

    shutil.copyfile(source_path, dest_path)


def read_log_file(task_type):
    """
    This public function will read the contents of the latest PyFynance file of the correct type

    :param task_type: the PyFYance task type that has been run
    :return:
    """

    config = Configuration()
    logname_regex = "PyFynance_{}_*.log".format(task_type)
    search_path = os.sep.join([config.paths.log_path, config.version, logname_regex])
    logs = glob.glob(search_path)
    logpath = logs.sort(reverse=True)[0]

    with open(logpath) as logfile:
        return logfile.readlines()
