import os

from mock import patch, call, MagicMock, mock_open
from pytest import fixture, raises

from core.exceptions import FileSystemError
from services.file_system import FileSystem


@fixture
def fs():
    return FileSystem()


@patch("shutil.move", return_value=MagicMock())
def test_when_move_file_and_valid_paths_then_correct_call_made(shutil_mock, fs):
    with patch.object(fs, "path_exists", return_value=True):
        with patch.object(fs, "is_directory", return_value=True):
            os.sep.join(["C:", "source", "path", "file"])
            fs.move_file(os.sep.join(["C:", "source", "path", "file"]), os.sep.join(["C:", "dest", "path", "file"]))
    shutil_mock.assert_has_calls(
        [call(os.sep.join(["C:", "source", "path", "file"]), os.sep.join(["C:", "dest", "path", "file"]))]
    )


@patch("shutil.move", return_value=MagicMock())
def test_when_move_file_and_bad_input_then_error_raised(shutil_mock, fs):
    with patch.object(fs, "path_exists", return_value=False):
        with patch.object(fs, "is_directory", return_value=True):
            with raises(FileSystemError) as raised_error:
                fs.move_file(os.sep.join(["C:", "source", "path", "file"]), os.sep.join(["C:", "dest", "path", "file"]))
    assert not shutil_mock.called
    assert (
        raised_error.value.args[0]
        == "Source Path '{}' does not exist.".format(os.sep.join(["C:", "source", "path", "file"]))
    )


@patch("shutil.move", return_value=MagicMock())
def test_when_move_file_and_output_folder_dosent_exist_then_error_raised(
    shutil_mock, fs
):
    with patch.object(fs, "path_exists", return_value=True):
        with patch.object(fs, "is_directory", return_value=False):
            with raises(FileSystemError) as raised_error:
                fs.move_file(os.sep.join(["C:", "source", "path", "file"]), os.sep.join(["C:", "dest", "path", "file"]))
    assert not shutil_mock.called
    assert (
        "destination path '{}' either isnt a directory or dosent exist".format(os.sep.join(["C:", "dest", "path"]))
        in raised_error.value.args[0]
    )


@patch("shutil.copyfile", return_value=MagicMock())
def test_when_copy_file_and_valid_paths_then_correct_call_made(shutil_mock, fs):
    with patch.object(fs, "path_exists", return_value=True):
        with patch.object(fs, "is_directory", return_value=True):
            fs.copy_file(os.sep.join(["C:", "source", "path", "file"]), os.sep.join(["C:", "dest", "path", "file"]))
    shutil_mock.assert_has_calls(
        [call(os.sep.join(["C:", "source", "path", "file"]), os.sep.join(["C:", "dest", "path", "file"]))]
    )


@patch("shutil.copyfile", return_value=MagicMock())
def test_when_copy_file_and_bad_input_then_error_raised(shutil_mock, fs):
    with patch.object(fs, "path_exists", return_value=False):
        with patch.object(fs, "is_directory", return_value=True):
            with raises(FileSystemError) as raised_error:
                fs.copy_file(os.sep.join(["C:", "source", "path", "file"]), os.sep.join(["C:", "dest", "path", "file"]))
    assert not shutil_mock.called
    assert (
        raised_error.value.args[0]
        == "Source Path '{}' does not exist.".format(os.sep.join(["C:", "source", "path", "file"]))
    )


@patch("shutil.copyfile", return_value=MagicMock())
def test_when_copy_file_and_output_folder_dosent_exist_then_error_raised(
    shutil_mock, fs
):
    with patch.object(fs, "path_exists", return_value=True):
        with patch.object(fs, "is_directory", return_value=False):
            with raises(FileSystemError) as raised_error:
                fs.copy_file(os.sep.join(["C:", "source", "path", "file"]), os.sep.join(["C:", "dest", "path", "file"]))
    assert not shutil_mock.called
    assert (
        "destination path '{}' either isnt a directory or dosent exist".format(os.sep.join(["C:", "dest", "path"]))
        in raised_error.value.args[0]
    )


@patch("os.remove", return_value=MagicMock())
def test_when_delete_file_and_file_exists_then_correct_call_made(os_mock, fs):
    with patch.object(fs, "path_exists", return_value=True):
        fs.delete_file(os.sep.join(["C:", "files", "to", "delete"]))
    os_mock.assert_has_calls([call(os.sep.join(["C:", "files", "to", "delete"]))])


@patch("os.remove", return_value=MagicMock())
def test_when_delete_file_and_file_dosent_exist_then_no_call_made(os_mock, fs):
    with patch.object(fs, "path_exists", return_value=False):
        fs.delete_file(os.sep.join(["C:", "files", "to", "delete"]))
    assert not os_mock.called


@patch("shutil.move", return_value=MagicMock())
def test_when_rename_file_and_file_exists_then_correct_call_made(shutil_mock, fs):
    with patch.object(fs, "path_exists", return_value=True):
        fs.rename_file(os.sep.join(["C:", "source", "path", "old_file"]), "new_file")
    shutil_mock.assert_has_calls(
        [call(os.sep.join(["C:", "source", "path", "old_file"]), os.sep.join(["C:", "source", "path", "new_file"]))]
    )


@patch("shutil.move", return_value=MagicMock())
def test_when_rename_file_and_file_does_not_exist_then_correct_call_made(
    shutil_mock, fs
):
    with patch.object(fs, "path_exists", return_value=False):
        with raises(FileSystemError) as raised_error:
            fs.rename_file(os.sep.join(["C:", "source", "path", "old_file"]), "new_file")
    assert not shutil_mock.called
    assert (
        raised_error.value.args[0]
        == "File Path '{}' does not exist.".format(os.sep.join(["C:", "source", "path", "old_file"]))
    )


@patch("os.path.isdir", return_value=MagicMock())
def test_when_is_directory_then_correct_call_made(os_mock, fs):

    fs.is_directory(os.sep.join(["C:", "path", "to", "folder"]))
    os_mock.assert_has_calls([call(os.sep.join(["C:", "path", "to", "folder"]))])


@patch("os.path.isfile", return_value=MagicMock())
def test_when_is_file_then_correct_call_made(os_mock, fs):
    fs.is_file(os.sep.join(["C:", "path", "to", "file"]))
    os_mock.assert_has_calls([call(os.sep.join(["C:", "path", "to", "file"]))])


@patch("os.path.exists", return_value=MagicMock())
def test_when_path_exists_then_correct_call_made(os_mock, fs):
    fs.path_exists(os.sep.join(["C:", "an", "actual", "path"]))
    os_mock.assert_has_calls([call(os.sep.join(["C:", "an", "actual", "path"]))])


@patch("os.path.exists", return_value=True)
@patch("os.makedirs", return_value=MagicMock())
def test_when_create_directory_and_exists_then_correct_calls_made(
    makedirs_mock, exists_mock, fs
):
    fs.create_directory(os.sep.join(["C:", "an", "actual", "path"]))
    exists_mock.assert_has_calls([call(os.sep.join(["C:", "an", "actual", "path"]))])
    assert not makedirs_mock.called


@patch("os.path.exists", return_value=False)
@patch("os.makedirs", return_value=MagicMock())
def test_when_create_directory_and_not_exists_then_correct_calls_made(
    makedirs_mock, exists_mock, fs
):
    fs.create_directory(os.sep.join(["C:", "an", "actual", "path"]))
    exists_mock.assert_has_calls([call(os.sep.join(["C:", "an", "actual", "path"]))])
    makedirs_mock.assert_has_calls([call(os.sep.join(["C:", "an", "actual", "path"]))])


@patch("shutil.copytree", return_value=MagicMock())
def test_when_copy_directory_and_input_good_then_correct_call_made(shutil_mock, fs):
    with patch.object(fs, "path_exists", return_value=True):
        fs.copy_directory(os.sep.join(["C:", "source", "path", "file"]), os.sep.join(["C:", "dest", "path", "file"]))
    shutil_mock.assert_has_calls(
        [call(os.sep.join(["C:", "source", "path", "file"]), os.sep.join(["C:", "dest", "path", "file"]))]
    )


@patch("shutil.copytree", return_value=MagicMock())
def test_when_copy_directory_and_input_bad_then_correct_call_made(shutil_mock, fs):
    with patch.object(fs, "path_exists", return_value=False):
        with raises(FileSystemError) as raised_error:
            fs.copy_directory(os.sep.join(["C:", "source", "path", "file"]), os.sep.join(["C:", "dest", "path", "file"]))
    assert not shutil_mock.called
    assert (
        raised_error.value.args[0]
        == "Source Path '{}' does not exist.".format(os.sep.join(["C:", "source", "path", "file"]))
    )


@patch("shutil.rmtree", return_value=MagicMock())
def test_when_delete_directory_and_dir_exists_then_correct_call_made(shutil_mock, fs):
    with patch.object(fs, "path_exists", return_value=True):
        fs.delete_directory(os.sep.join(["C:", "directory", "to", "delete"]))
    shutil_mock.assert_has_calls([call(os.sep.join(["C:", "directory", "to", "delete"]))])


@patch("shutil.rmtree", return_value=MagicMock())
def test_when_delete_directory_and_dir_does_not_exist_then_no_shutil_call(
    shutil_mock, fs
):
    with patch.object(fs, "path_exists", return_value=False):
        fs.delete_directory(os.sep.join(["C:", "directory", "to", "delete"]))
    assert not shutil_mock.called


@patch("shutil.move", return_value=MagicMock())
def test_when_move_directory_and_correct_input_then_correct_call_made(shutil_mock, fs):
    with patch.object(fs, "path_exists", return_value=True):
        fs.move_directory(os.sep.join(["C:", "source", "path", "dir"]), os.sep.join(["C:", "dest", "path", "dir"]))
    shutil_mock.assert_has_calls([call(os.sep.join(["C:", "source", "path", "dir"]), os.sep.join(["C:", "dest", "path", "dir"]))])


@patch("shutil.move", return_value=MagicMock())
def test_when_move_directory_and_incorrect_input_then_raise_error(shutil_mock, fs):
    with patch.object(fs, "path_exists", return_value=False):
        with raises(FileSystemError) as raised_error:
            fs.move_directory(os.sep.join(["C:", "source", "path", "dir"]), os.sep.join(["C:", "dest", "path", "dir"]))
    assert not shutil_mock.called
    assert (
        raised_error.value.args[0]
        == "Source path '{}' does not exist.".format(os.sep.join(["C:", "source", "path", "dir"]))
    )


@patch("shutil.move", return_value=MagicMock())
def test_when_rename_directory_then_correct_call_made(shutil_mock, fs):
    with patch.object(fs, "path_exists", return_value=True):
        fs.rename_directory(os.sep.join(["C:", "source", "path", "old_dir"]), "new_dir")
    shutil_mock.assert_has_calls(
        [call(os.sep.join(["C:", "source", "path", "old_dir"]), os.sep.join(["C:", "source", "path", "new_dir"]))]
    )


@patch("shutil.move", return_value=MagicMock())
def test_when_rename_directory_and_wrong_input_then_raise_error(shutil_mock, fs):
    with patch.object(fs, "path_exists", return_value=False):
        with raises(FileSystemError) as raised_error:
            fs.rename_directory(os.sep.join(["C:", "source", "path", "old_dir"]), "new_dir")
    assert not shutil_mock.called
    assert (
        raised_error.value.args[0]
        == "Source path '{}' does not exist.".format(os.sep.join(["C:", "source", "path", "old_dir"]))
    )
