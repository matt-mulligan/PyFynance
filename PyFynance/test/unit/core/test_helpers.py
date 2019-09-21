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