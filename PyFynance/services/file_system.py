import logging
import os
import shutil

from core.config import Configuration
from core.exceptions import FileSystemError


class FileSystem:
    """
    The file system service is responsible for all interactions with the host file system within PyFynance and is written
    as a light-weight API over the python standard library to manage these calls.

    This API class implements public methods over the standard file system operations and are paramterised so that they
    can be usable for a wide variety of use cases, while still providing option validation on their calls
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._config = Configuration()

    def move_file(self, source_path, dest_path):
        """
        This public method will move the file from the source path to the destination path. Note that this will
        remove the file from the source destination

        :param source_path: The full filepath (including file name) to the source file
        :type source_path: String
        :param dest_path: The full filepath (including file name) to the destination file
        :type dest_path: String
        :return: None
        """

        if not self.path_exists(source_path):
            raise FileSystemError(f"Source Path '{source_path}' does not exist.")

        if not self.is_directory(self._get_base_path(dest_path)):
            raise FileSystemError(
                f"destination path '{self._get_base_path(dest_path)}' either isnt a directory or dosent exist. "
                "Note that this method requires a destination path to be the full path including the filename, "
                "not just to the destination folder."
            )

        shutil.move(source_path, dest_path)

    def copy_file(self, source_path, dest_path):
        """
        This public static method will copy the file from the source path to the destination path

        :param source_path: The full filepath (including file name) to the source file
        :type source_path: String
        :param dest_path: The full filepath (including file name) to the destination file
        :type dest_path: String
        :return: None
        """

        if not self.path_exists(source_path):
            raise FileSystemError(f"Source Path '{source_path}' does not exist.")

        if not self.is_directory(self._get_base_path(dest_path)):
            raise FileSystemError(
                f"destination path '{self._get_base_path(dest_path)}' either isnt a directory or dosent exist. "
                "Note that this method requires a destination path to be the full path including the filename, "
                "not just to the destination folder."
            )

        shutil.copyfile(source_path, dest_path)

    def delete_file(self, file_path):
        """
        This public static method will delete the file from the source path

        :param file_path: The full filepath (including file name) to the file to delete
        :type file_path: String
        :return: None
        """

        if not self.path_exists(file_path):
            self._logger.info(
                f"File path '{file_path}' does not exist. Skipping deletion"
            )
        else:
            os.remove(file_path)

    def rename_file(self, file_path, new_filename):
        """
        This public static method will rename the file from the file path to the new name provided.

        :param file_path: The full filepath (including file name) to the source file
        :type file_path: String
        :param new_filename: The name to rename the file to
        :type new_filename: String
        :return: None
        """

        if not self.path_exists(file_path):
            raise FileSystemError(f"File Path '{file_path}' does not exist.")

        path_parts = file_path.split(os.sep)
        path_parts.pop(-1)
        path_parts.append(new_filename)
        new_path = os.sep.join(path_parts)
        shutil.move(file_path, new_path)

    @staticmethod
    def is_directory(path_value):
        """
        This public static method will test if the path specified is a directory.

        :param path_value: The full filepath to test
        :type path_value: String
        :return: True if it is a directory, otherwise False
        """

        return os.path.isdir(path_value)

    @staticmethod
    def is_file(path_value):
        """
        This public static method will test if the path specified is a file.

        :param path_value: The full filepath to test
        :type path_value: String
        :return: True if it is a file, otherwise False
        """

        return os.path.isfile(path_value)

    @staticmethod
    def path_exists(path):
        """
        This public static method will test if the path specified exists.

        :param path: The full filepath to test
        :type path: String
        :return: True if the path exists, otherwise False
        """

        return os.path.exists(path)

    @staticmethod
    def create_directory(path_value):
        """
        This private static method will create the directory path if it does not already exist

        :param path_value: The path to try and create
        :return: None
        """

        if not os.path.exists(path_value):
            os.makedirs(path_value)

    def copy_directory(self, source_path, dest_path):
        """
        This public static method will copy the directory from the source path to the destination path

        :param source_path: The full filepath to the source directory
        :type source_path: String
        :param dest_path: The full filepath to the destination directory
        :type dest_path: String
        :return: None
        """

        if not self.path_exists(source_path):
            raise FileSystemError(f"Source Path '{source_path}' does not exist.")

        shutil.copytree(source_path, dest_path)

    def delete_directory(self, path_value):
        """
        This public static method will delete the file from the source path

        :param path_value: The full filepath (including file name) to the file to delete
        :type path_value: String
        :return: None
        """

        if not self.path_exists(path_value):
            self._logger.info(
                f"Directory '{path_value}' does not exist. Skipping deletion"
            )
        else:
            shutil.rmtree(path_value)

    def move_directory(self, source_path, dest_path):
        """
        This public static method will move the folder from the source path to the destination path. Note that this will
        remove the folder from the source destination

        :param source_path: The full filepath (including file name) to the source file
        :type source_path: String
        :param dest_path: The full filepath (including file name) to the destination file
        :type dest_path: String
        :return: None
        """

        if not self.path_exists(source_path):
            raise FileSystemError(f"Source path '{source_path}' does not exist.")

        shutil.move(source_path, dest_path)

    def rename_directory(self, folder_path, new_folder_name):
        """
        This public static method will rename the folder from the path to the new name provided.

        :param folder_path: The full filepath (including file name) to the source file
        :type folder_path: String
        :param new_folder_name: The name to rename the file to
        :type new_folder_name: String
        :return: None
        """

        if not self.path_exists(folder_path):
            raise FileSystemError(f"Source path '{folder_path}' does not exist.")

        path_parts = folder_path.split(os.sep)
        path_parts.pop(-1)
        path_parts.append(new_folder_name)
        new_path = os.sep.join(path_parts)
        shutil.move(folder_path, new_path)

    @staticmethod
    def _get_base_path(path):
        """
        this private method will return the base path of the path that was provided.

        :param path: the path to find the base of.
        :type path: String
        :return: the base path of the provided path
        """

        path_parts = path.split(os.sep)
        path_parts.pop(-1)
        return os.sep.join(path_parts)
