import logging
from abc import ABCMeta, abstractmethod

from core.config import Configuration
from core.exceptions import TaskError
from services.qif_parsser import QIFParser


class BaseTask:

    __metaclass__ = ABCMeta  # Abstract Base Class

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._config = Configuration()
        self._qif_parser = QIFParser(self._config)

    @abstractmethod
    def before_task(self):  # pragma: no cover
        """
        this is the abstract method "before_task" and must be implemented by the child classes
        :return:
        """

        pass

    @abstractmethod
    def do_task(self):  # pragma: no cover
        """
        this is the abstract method "do_task" and must be implemented by the child classes
        :return:
        """

        pass

    @abstractmethod
    def after_task(self):  # pragma: no cover
        """
        this is the abstract method "after_task" and must be implemented by the child classes
        :return:
        """

        pass

    def execute(self):
        """
        this method will run the tasks before, do and after task methods in sequence and track results
        :return:
        """

        self._logger.info("Beginning task execution for task type '{}'".format(self.__class__.__name__))
        passed = True

        try:
            self.before_task()
            self.do_task()
            self.after_task()
        except Exception as e:
            passed = False
            self._logger.exception("PyFynance encountered an error while running task.  {}".format(e))
            raise TaskError(e)
        finally:
            status = "Success" if passed else "Failure"
            self._logger.info("Finished task execution for task type '{}' with status '{}'".
                              format(self.__class__.__name__, status))
        return passed
