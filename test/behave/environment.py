import glob
import os
import shutil
import sqlite3

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
    search_path = os.sep.join(
        [config.paths.logs_path, str(config.version), logname_regex]
    )
    logs = glob.glob(search_path)
    logs.sort(reverse=True)

    with open(logs[0]) as logfile:
        return logfile.read()


def get_db_cursor(db_name, state_folder):
    """
    This public function will open a connection to a pyfynance database and return the cursor object so that evaluation
    actions can be performed on the database.

    :param db_name: the name of the PyFynance database to be opened ["transactions"]
    :param state_folder: the state folder to open the database from ["current" | "backup"]
    :return: sqlite3 cursor object for the database
    """

    config = Configuration()
    db_regex = os.sep.join(
        [config.paths.db_path, state_folder, "{}*db".format(db_name)]
    )
    db_path = glob.glob(db_regex)[0]
    db_connection = sqlite3.connect(db_path)
    return db_connection.cursor()
