import glob
import os
import sqlite3
import subprocess

from behave import *
from core.config import Configuration
from test.behave.environment import (
    find_all_files,
    delete_file,
    copy_file,
    read_log_file,
    get_db_cursor,
)


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


@step("no '{input_type}' input files are present in the '{state_folder}' folder")
def step_impl(context, input_type, state_folder):
    """
    THis behave step implementation will delete all files for the spcified input folder to clean up the test
    environment before a test is run

    :param input_type: represents the input folder to delete files from
    :type context: behave.runner.Context
    """

    config = Configuration()
    input_path = os.sep.join([config.paths.input_path, input_type, state_folder, "*"])
    files = find_all_files(input_path)
    for filepath in files:
        delete_file(filepath)


@step(
    "file resource '{filename}' is placed in input folder '{input_type}' within '{state_folder}'"
)
def step_impl(context, filename, input_type, state_folder):
    """
    This behave step implementation will place the required test resource file in the spcified input folder as part
    of the test setup phase

    :param filename: the name of the resource to load from the test/resources folder
    :param input_type: represents the input folder to place the file resource in
    :type context: behave.runner.Context
    """

    config = Configuration()
    source_path = os.sep.join(
        [
            config.paths.test_path,
            "resources",
            context.feature.name,
            "input_files",
            filename,
        ]
    )
    dest_path = os.sep.join(
        [config.paths.input_path, input_type, state_folder, filename]
    )
    copy_file(source_path, dest_path)


@step(
    "db resource '{resource_name}' is placed in '{state_folder}' folder as '{db_type}' database named '{db_name}'"
)
def step_impl(context, resource_name, state_folder, db_type, db_name):
    config = Configuration()
    source_path = os.sep.join(
        [
            config.paths.test_path,
            "resources",
            context.feature.name,
            "database_files",
            db_type,
            resource_name,
        ]
    )
    dest_path = os.sep.join(
        [config.paths.resources_path, "databases", state_folder, db_name]
    )
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


@step(
    "input file '{input_filename}' has been moved to '{input_folder}' folder within '{state_folder}'"
)
def step_impl(context, input_filename, input_folder, state_folder):
    """

    :param input_folder: the folder to look for the log file in
    :type context: behave.runner.Context
    """

    config = Configuration()
    path = os.sep.join(
        [
            config.paths.input_path,
            input_folder,
            state_folder,
            "{}*".format(input_filename),
        ]
    )
    assert len(glob.glob(path)) > 0


@step("database '{db_name}' exists in the '{state_folder}' folder")
def step_impl(context, db_name, state_folder):
    """
    :type context: behave.runner.Context
    """
    config = Configuration()
    path = os.sep.join([config.paths.db_path, state_folder, "{}*db".format(db_name)])
    db_files = glob.glob(path)

    assert len(db_files) > 0
    assert os.path.isfile(db_files[0])


@step(
    "rowcount for table '{table_name}' in database '{db_name}' in folder '{state_folder}' is {exp_rowcount}"
)
def step_impl(context, table_name, db_name, state_folder, exp_rowcount):
    db_cursor = get_db_cursor(db_name, state_folder)
    sql = "SELECT count(*) FROM {table};".format(table=table_name)
    result = db_cursor.execute(sql).fetchall()
    db_cursor.close()

    assert str(result[0][0]) == str(exp_rowcount)


@step(
    "select column '{sel_col}' for table '{table_name}' in database '{db_name}' in folder '{state_folder}' returns "
    "'{exp_data}' when ordered by column '{order_col}'"
)
def step_impl(context, sel_col, table_name, db_name, state_folder, exp_data, order_col):
    db_cursor = get_db_cursor(db_name, state_folder)
    sql = "SELECT {sel_col} FROM {table} ORDER BY {order_col};".format(
        sel_col=sel_col, table=table_name, order_col=order_col
    )
    result = db_cursor.execute(sql).fetchall()
    db_cursor.close()

    assert str(result) == exp_data


@step("message '{exp_message}' can be found in the PyFynance log")
def step_impl(context, exp_message):
    assert exp_message in context.log
