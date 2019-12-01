import logging
import os

from core.config import Configuration
from core.exceptions import TaskError


class PyFynance:
    """
    The PyFynance application class is the main orchestrator for task execution within PyFyanance.

    The public run interface will begin and manage a run of PyFynance and will build and execute the task type
    specified in the class argument variable
    """

    def __init__(self, args):
        self._args = args
        self._config = Configuration()
        self._logger = self._configure_logger(
            self._config.paths.logs_path,
            self._config.version,
            self._args.task_type,
            self._args.runtime,
        )

    def run(self):
        """
        This method is the main runner method for the PyFynance Application. This method controls the flow of
        executing tasks within PyFynance.

        :return: exit_code: Int: returns 0 if the task that was run finished successfully or 1 of the task failed
        """
        self._logger.info("Started PyFynance Application Run")
        passed = True

        try:
            passed = self._execute_tasks()
            if passed:
                self._logger.info(
                    f"PyFynance application ran successfully!  task_type = '{self._args.task_type}'"
                )
            else:
                self._logger.info(
                    f"PyFynance application failed to run successfully :(  task_type = '{self._args.task_type}'"
                )
        except Exception as e:
            passed = False
            self._logger.exception(
                f"PyFynance experienced a fatal exception while running task of task_type '{self._args.task_type}'.  "
                f"exception = '{e}'"
            )
            raise TaskError(e)
        finally:
            exit_code = 0 if passed else 1

        self._logger.info("Finished PyFynance Application Run")
        return exit_code

    def _execute_tasks(self):
        """
        this method is responsible for selecting and triggering the correct task class based on the task_type selected

        :return: task_passed: Boolean: returns True of the task that was executed passed, False if the task
        encountered an error
        """

        task_class_name = self._resolve_task_class()
        task_class_object = self._new_instance(task_class_name)
        task = task_class_object(self._args)
        task_passed = task.execute()
        return task_passed

    def _resolve_task_class(self):
        """
        This private method will resolve the task class based on the task_type within the args object

        :return: PyFynance Task Class: returns the appropriate task class based on the task type on the self._args
        object
        """

        return {
            self._config.tasks.load_transactions: "tasks.task_load_transactions.LoadTransactionsTask",
            self._config.tasks.categorize_transactions: "tasks.task_categorize_transactions.CategorizeTransactionsTask",
        }[self._args.task_type]

    @staticmethod
    def _configure_logger(log_path, version, task_type, runtime):
        """
        this private method will set the logging configuration for each run of PyFynance

        :param log_path: The path to write logfiles out to
        :param version: The version number of PyFynance
        :param task_type: The PyFynance task type
        :param runtime: The timestamp of when PyFynance started in YYYYMMDDHHMMSS format
        :return: returns a configured python logger object
        """

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s %(name)-35s %(levelname)-8s %(message)s"
        )

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        log_datetime = runtime.strftime("%Y%m%d%H%M%S")
        log_folder = os.sep.join([log_path, str(version)])
        log_filename = f"{log_path}{os.sep}{version}{os.sep}PyFynance_{task_type}_{log_datetime}.log"
        # delayed import for python path addition
        from services.file_system import FileSystem

        fs = FileSystem()
        fs.create_directory(log_folder)

        fh = logging.FileHandler(log_filename, "w")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        logger.info("Logging Service Initalised")
        logger.info(f"PyFynance Version = {version}")
        logger.info(f"PyFynance Task Type = {task_type}")

        return logger

    @staticmethod
    def _new_instance(task_class):
        """
        this private method will create a new instance of the specified fully-qualified class name

        :param task_class: String
        :return: PyFynance Task Instance: returns an instanciated instance of the PyFynance task class provided
        """

        namespace = task_class.split(".")
        module_name = ".".join(namespace[:-1])
        module = __import__(module_name)
        for component in namespace[1:]:
            module = getattr(module, component)
        return module
