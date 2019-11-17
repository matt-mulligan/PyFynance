from mock import patch, call
from pytest import raises

from core.helpers import *


@patch("glob.glob")
def test_when_find_all_files_and_full_path_and_recursive_then_full_path_files_returned(
    glob_mock
):
    glob_return_value = [
        os.sep.join(["C:", "fake", "path", "to", "search", "file1_pattern.csv"]),
        os.sep.join(
            ["C:", "fake", "path", "to", "search", "recursive", "file2_pattern.csv"]
        ),
    ]
    glob_mock.return_value = glob_return_value
    file_paths = find_all_files(
        os.sep.join(["C:", "fake", "path", "to", "search"]),
        ["*pattern.csv"],
        recursive=True,
        full_path=True,
    )

    glob_mock.assert_has_calls(
        [
            call(
                os.sep.join(["C:", "fake", "path", "to", "search", "*pattern.csv"]),
                recursive=True,
            )
        ]
    )
    assert file_paths == glob_return_value


@patch("glob.glob")
def test_when_find_all_files_and_not_full_path_and_not_recursive_then_full_path_files_returned(
    glob_mock
):
    glob_return_value = [
        os.sep.join(["C:", "fake", "path", "to", "search", "file1_pattern.csv"]),
        os.sep.join(
            ["C:", "fake", "path", "to", "search", "recursive", "file2_pattern.csv"]
        ),
    ]
    glob_mock.return_value = glob_return_value
    file_paths = find_all_files(
        os.sep.join(["C:", "fake", "path", "to", "search"]),
        ["*pattern.csv"],
        recursive=False,
        full_path=False,
    )

    glob_mock.assert_has_calls(
        [
            call(
                os.sep.join(["C:", "fake", "path", "to", "search", "*pattern.csv"]),
                recursive=False,
            )
        ]
    )
    assert file_paths == ["file1_pattern.csv", "file2_pattern.csv"]


def test_when_convert_tuple_to_dict_then_dict_returned():
    data_tuple = ("Matt Mulligan", 26)
    keys_list = ["name", "age"]
    ret_val = convert_tuple_to_dict(data_tuple, keys_list)
    assert ret_val == {"name": "Matt Mulligan", "age": 26}


def test_when_convert_tuple_to_dict_and_mismatch_arguments_length_then_error_raised():
    data_tuple = ("Matt Mulligan", 26)
    keys_list = ["name", "age", "fav_colour"]
    with raises(AttributeError) as raised_error:
        convert_tuple_to_dict(data_tuple, keys_list)
    assert (
        raised_error.value.args[0]
        == "Length of data_tuple (2) and keys_list (3) do not match. "
        "Both parameters must be the same length to convert them to a dictionary"
    )


def test_when_convert_tuple_to_dict_and_data_tuple_not_tuple_then_error_raised():
    data_tuple = {"Matt Mulligan", 26}
    keys_list = ["name", "age"]
    with raises(AttributeError) as raised_error:
        convert_tuple_to_dict(data_tuple, keys_list)
    assert (
        raised_error.value.args[0]
        == "Data type of argument 'data_tuple' is <class 'set'>. Expected type is tuple."
    )


def test_when_convert_tuple_to_dict_and_key_list_not_list_then_error_raised():
    data_tuple = ("Matt Mulligan", 26)
    keys_list = ("name", "age")
    with raises(AttributeError) as raised_error:
        convert_tuple_to_dict(data_tuple, keys_list)
    assert (
        raised_error.value.args[0]
        == "Data type of argument 'keys_list' is <class 'tuple'>. Expected type is list."
    )
