from mock import patch, call
from core.helpers import *


@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=False)
@patch("os.makedirs")
@patch("os.path.dirname")
def test_when_makedirs_with_dir_path_and_not_exists_then_makedirs(os_dirname_mock, os_makedirs_mock,
                                                                  os_exists_mock, os_isdir_mock):
    calls_makedirs = [call("path_to_directory")]
    calls_dirname = []
    makedirs("path_to_directory")
    os_makedirs_mock.assert_has_calls(calls_makedirs)
    os_dirname_mock.assert_has_calls(calls_dirname)


@patch("os.path.isdir", return_value=False)
@patch("os.path.exists", return_value=False)
@patch("os.makedirs")
@patch("os.path.dirname", return_value="path_to_directory")
def test_when_makedirs_with_file_path_and_not_exists_then_makedirs(os_dirname_mock, os_makedirs_mock,
                                                                  os_exists_mock, os_isdir_mock):
    calls_makedirs = [call("path_to_directory")]
    calls_dirname = [call("path_to_file")]
    makedirs("path_to_file")
    os_makedirs_mock.assert_has_calls(calls_makedirs)
    os_dirname_mock.assert_has_calls(calls_dirname)

@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("os.path.dirname", return_value="path_to_directory")
def test_when_makedirs_with_dir_path_and_not_exists_then_not_makedirs(os_dirname_mock, os_makedirs_mock,
                                                                      os_exists_mock, os_isdir_mock):
    calls_makedirs = []
    calls_dirname = []
    makedirs("path_to_directory")
    os_makedirs_mock.assert_has_calls(calls_makedirs)
    os_dirname_mock.assert_has_calls(calls_dirname)

@patch("os.path.isdir", return_value=False)
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("os.path.dirname", return_value="path_to_directory")
def test_when_makedirs_with_file_path_and_not_exists_then_not_makedirs(os_dirname_mock, os_makedirs_mock,
                                                                       os_exists_mock, os_isdir_mock):
    calls_makedirs = []
    calls_dirname = [call("path_to_file")]
    makedirs("path_to_file")
    os_makedirs_mock.assert_has_calls(calls_makedirs)
    os_dirname_mock.assert_has_calls(calls_dirname)


@patch("glob.glob")
def test_when_find_all_files_and_full_path_and_recursive_then_full_path_files_returned(glob_mock):
    glob_return_value = ["C:\\fake\\path\\to\\search\\file1_pattern.csv",
                         "C:\\fake\\path\\to\\search\\recursive\\file2_pattern.csv"]
    glob_mock.return_value = glob_return_value
    file_paths = find_all_files("C:\\fake\\path\\to\\search", ["*pattern.csv"], recursive=True, full_path=True)

    glob_mock.assert_has_calls([call("C:\\fake\\path\\to\\search\\*pattern.csv", recursive=True)])
    assert file_paths == glob_return_value


@patch("glob.glob")
def test_when_find_all_files_and_not_full_path_and_not_recursive_then_full_path_files_returned(glob_mock):
    glob_return_value = ["C:\\fake\\path\\to\\search\\file1_pattern.csv",
                         "C:\\fake\\path\\to\\search\\recursive\\file2_pattern.csv"]
    glob_mock.return_value = glob_return_value
    file_paths = find_all_files("C:\\fake\\path\\to\\search", ["*pattern.csv"], recursive=False, full_path=False)

    glob_mock.assert_has_calls([call("C:\\fake\\path\\to\\search\\*pattern.csv", recursive=False)])
    assert file_paths ==["file1_pattern.csv", "file2_pattern.csv"]
