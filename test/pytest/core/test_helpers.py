from mock import patch, call
from core.helpers import *


@patch("glob.glob")
def test_when_find_all_files_and_full_path_and_recursive_then_full_path_files_returned(
    glob_mock
):
    glob_return_value = [
        os.sep.join(["C:", "fake", "path", "to", "search", "file1_pattern.csv"]),
        os.sep.join(["C:", "fake", "path", "to", "search", "recursive", "file2_pattern.csv"])
    ]
    glob_mock.return_value = glob_return_value
    file_paths = find_all_files(
        os.sep.join(["C:", "fake", "path", "to", "search"]), ["*pattern.csv"], recursive=True, full_path=True
    )

    glob_mock.assert_has_calls(
        [call(os.sep.join(["C:", "fake", "path", "to", "search", "*pattern.csv"]), recursive=True)]
    )
    assert file_paths == glob_return_value


@patch("glob.glob")
def test_when_find_all_files_and_not_full_path_and_not_recursive_then_full_path_files_returned(
    glob_mock
):
    glob_return_value = [
        os.sep.join(["C:", "fake", "path", "to", "search", "file1_pattern.csv"]),
        os.sep.join(["C:", "fake", "path", "to", "search", "recursive", "file2_pattern.csv"])
    ]
    glob_mock.return_value = glob_return_value
    file_paths = find_all_files(
        os.sep.join(["C:", "fake", "path", "to", "search"]), ["*pattern.csv"], recursive=False, full_path=False
    )

    glob_mock.assert_has_calls(
        [call(os.sep.join(["C:", "fake", "path", "to", "search", "*pattern.csv"]), recursive=False)]
    )
    assert file_paths == ["file1_pattern.csv", "file2_pattern.csv"]
