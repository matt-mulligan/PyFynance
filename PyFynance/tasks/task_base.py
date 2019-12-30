import logging
from abc import ABCMeta, abstractmethod

from core.config import Configuration
from core.exceptions import TaskError
from services.file_system import FileSystem
from services.database.client import SqliteClient
from services.database.service import Database


class BaseTask:

    __metaclass__ = ABCMeta  # Abstract Base Class

    def __init__(self, args):
        self._args = args
        self._logger = logging.getLogger(__name__)
        self._config = Configuration()
        self._db = Database(SqliteClient(), Configuration())
        self._fs = FileSystem()

    @abstractmethod
    def before_task(self):  # pragma: no cover
        """
        this abstract method manages the execution of all pre-task activities required.

        :return: None
        """

        pass

    @abstractmethod
    def do_task(self):  # pragma: no cover
        """
        this abstract method manages the execution of the task steps

        :return: None
        """

        pass

    @abstractmethod
    def after_task(self, passed):  # pragma: no cover
        """
        this abstract method manages the execution of all post-task activities required.

        :return: None
        """

        pass

    def execute(self):
        """
        This public orchestrates the calling and exception handling of the task abstract methods
        :return: Boolean representing if the task execution was successful or not
        """

        self._logger.info(
            f"Beginning task execution for task type '{self.__class__.__name__}'"
        )
        passed = True

        try:
            self.before_task()
            self.do_task()
        except Exception as e:
            passed = False
            self._logger.exception(
                f"PyFynance encountered an error while running task.  {e}"
            )
            raise TaskError(e)
        finally:
            self.after_task(passed)
            status = "Success" if passed else "Failure"
            self._logger.info(
                f"Finished task execution for task type '{self.__class__.__name__}' with status '{status}'"
            )
        return passed

    def get_args_repr(self):
        """
        This public method will return a string representation of the self._args variable

        :return: String representation of the objects args attribute
        """

        repr_string = ""
        for key, value in self._args.__dict__.items():
            repr_string += f"{key}={value}, "
        return repr_string[:-2]
