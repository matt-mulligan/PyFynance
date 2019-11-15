import logging
from abc import ABCMeta, abstractmethod

from core.config import Configuration
from core.exceptions import TaskError
from services.database import Database
from services.file_system import FileSystem
from services.ofx_parser import OFXParser


class BaseTask:

    __metaclass__ = ABCMeta  # Abstract Base Class

    def __init__(self, args):
        self._args = args
        self._logger = logging.getLogger(__name__)
        self._config = Configuration()
        self._ofx_parser = OFXParser(self._config)
        self._db = Database()
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
    def after_task(self):  # pragma: no cover
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
            "Beginning task execution for task type '{}'".format(
                self.__class__.__name__
            )
        )
        passed = True

        try:
            self.before_task()
            self.do_task()
        except Exception as e:
            passed = False
            self._logger.exception(
                "PyFynance encountered an error while running task.  {}".format(e)
            )
            raise TaskError(e)
        finally:
            self.after_task()
            status = "Success" if passed else "Failure"
            self._logger.info(
                "Finished task execution for task type '{}' with status '{}'".format(
                    self.__class__.__name__, status
                )
            )
        return passed

    def get_args_repr(self):
        """
        This public method will return a string representation of the self._args variable

        :return: String representation of the objects args attribute
        """

        repr_string = ""
        for key, value in self._args.__dict__.items():
            repr_string += "{}={}, ".format(key, value)
        return repr_string[:-2]
