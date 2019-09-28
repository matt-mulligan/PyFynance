import os
import subprocess

from behave import *
from core.config import Configuration
from test.behave.environment import find_all_files, delete_file, copy_file, read_log_file


@given("PyFynance task type is '{task_type}'")
def step_impl(context, task_type):
    """
    THis behave step implementation will set the pyfynance task type value on the context object for later reference
    :type context: behave.runner.Context
    """

    context.task_type = task_type


@given("no '{db_type}' databases are present in the '{state_folder}' folder")
def step_impl(context, db_type, state_folder):
    """
    This behave step implementation will delete all of the databases type specified from the state folder specified to
    clean up the test environment before a test is run

    :param db_type: represents the DB type that needs to be removed
    :param state_folder: represents the state folder to remove the db from. must be either ["current", "backup"]
    :type context: behave.runner.Context
    """

    config = Configuration()
    db_name = "{}*".format(db_type)
    path = os.sep.join([config.paths.db_path, state_folder, db_name])
    files = find_all_files(path)
    for filepath in files:
        delete_file(filepath)


@step("no files are present in input '{input_type}' folder")
def step_impl(context, input_type):
    """
    THis behave step implementation will delete all files for the spcified input folder to clean up the test
    environment before a test is run

    :param input_type: represents the input folder to delete files from
    :type context: behave.runner.Context
    """

    config = Configuration()
    input_path = os.sep.join([config.paths.input_path, input_type, "*"])
    files = find_all_files(input_path)
    for filepath in files:
        delete_file(filepath)


@step("file resource '{filename}' is placed in the input '{input_type}' folder")
def step_impl(context, filename, input_type):
    """
    This behave step implementation will place the required test resource file in the spcified input folder as part
    of the test setup phase

    :param filename: the name of the resource to load from the test/resources folder
    :param input_type: represents the input folder to place the file resource in
    :type context: behave.runner.Context
    """

    config = Configuration()
    context.input_filename = filename
    source_path = os.sep.join([config.paths.test_path, "resources", context.feature, filename])
    dest_path = os.sep.join([config.paths.input_path, input_type, filename])
    copy_file(source_path, dest_path)


@when("I run PyFynance with the arguments '{cmd_line_args}'")
def step_impl(context, cmd_line_args):
    """
    :type context: behave.runner.Context
    """

    cmd = "pipenv run python -m PyFynance {}".format(cmd_line_args)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None, shell=True)
    process.communicate()
    context.return_code = process.returncode
    context.log = read_log_file(context.task_type)


@then("PyFynance exits with code '{expected_rc}'")
def step_impl(context, expected_rc):
    """
    This behave step implementation will assert that the return code from PyFynance matches the expected return
    for the test

    :param expected_rc: the tests expected return code
    :type context: behave.runner.Context
    """

    assert str(context.return_code) == str(expected_rc)


@step("input file has been moved to '{result_folder}' folder")
def step_impl(context, result_folder):
    """
    

    :type context: behave.runner.Context
    """
    raise NotImplementedError(u'STEP: And input file has been moved to \'ingested\' folder')