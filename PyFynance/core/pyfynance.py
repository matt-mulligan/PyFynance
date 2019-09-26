"""
This is module level documentation, outside of the class at the top of the file

"""

import logging
import os

from core.config import Configuration
from core.exceptions import TaskError


class PyFynance:
    """
    PyFynance application class. Controls the flow of the application
    """

    def __init__(self, args):
        self._args = args
        self._config = Configuration()
        self._logger = self._configure_logger(self._config.paths.logs_path, self._config.version,
                                              self._args.task_type, self._args.runtime)

    def run(self):
        """
        This method is the main runner method for the PyFynance Application. this method controls the flow of
        executing tasks within PyFynance
        """
        self._logger.info("Started PyFynance Application Run")
        passed = True

        try:
            passed = self._execute_tasks()
            if passed:
                self._logger.info("PyFynance application ran successfully!  task_type = '{}'".
                                  format(self._args.task_type))
            else:
                self._logger.info("PyFynance application failed to run successfully :(  task_type = '{}'".
                                  format(self._args.task_type))
        except Exception as e:
            passed = False
            self._logger.exception("PyFynance experienced a fatal exception while running task of task_type '{}'.  "
                                   "exception = '{}'".format(self._args.task_type, e))
            raise TaskError(e)
        finally:
            exit_code = 0 if passed else 1

        self._logger.info("Finished PyFynance Application Run")
        return exit_code

    def _execute_tasks(self):
        """
        this method is responsible for selecting and triggering the correct task class based on the task_type selected

        :return:
        """

        task_class_name = self._resolve_task_class()
        task_class_object = self._new_instance(task_class_name)
        task = task_class_object(self._args)
        task_passed = task.execute()
        return task_passed

    def _resolve_task_class(self):
        """
        this method will resolve the task class based on the task_type within the args object
        :return:
        """

        return {
            "load_transactions": "tasks.task_load_transactions.LoadTransactionsTask"
        }[self._args.task_type]

    @staticmethod
    def _configure_logger(log_path, version, task_type, runtime):
        """
        this method will set the logging configuration for each run of PyFynance

        :param log_path: The path to write logfiles out to
        :param version: The version number of PyFynance
        :param task_type: The PyFynance task type
        :return: returns a configured python logger object
        """

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s %(name)-35s %(levelname)-8s %(message)s")

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        log_datetime = runtime.strftime("%Y%m%d%H%M%S")
        log_filename = "{log_path}{sep}{version}{sep}PyFynance_{task_type}_{timestamp}.log".format(log_path=log_path,
                                                                                                   sep=os.sep,
                                                                                                   version=str(version),
                                                                                                   task_type=task_type,
                                                                                                   timestamp=log_datetime)
        # delayed import for python path addition
        from core.helpers import makedirs
        makedirs(log_filename)

        fh = logging.FileHandler(log_filename, "w")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        logger.info("Logging Service Initalised")
        logger.info("PyFynance Version = {}".format(version))
        logger.info("PyFynance Task Type = {}".format(task_type))

        return logger

    @staticmethod
    def _new_instance(task_class):
        """
        this method will create a new instance of the specified fully-qualified class name
        :param task_class:
        :return:
        """

        namespace = task_class.split(".")
        module_name = ".".join(namespace[:-1])
        module = __import__(module_name)
        for component in namespace[1:]:
            module = getattr(module, component)
        return module
