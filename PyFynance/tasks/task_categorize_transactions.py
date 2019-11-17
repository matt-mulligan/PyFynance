from core.exceptions import TaskCategorizeTransactionsError
from tasks.task_base import BaseTask


class CategorizeTransactionsTask(BaseTask):
    """
    The Categorize Transactions task is responsible loading transactions from the transactions database, categorising
    them according to the rules within the rules database then writing the
    results back to the transactions DB.

    ChangeLog:
        - original implementation of this task added to PyFynance in Release 1.1
    """

    def __init__(self, args):
        super(CategorizeTransactionsTask, self).__init__(args)
        self._task_state = "OK"

    def __repr__(self):
        return f"PyFynance.Tasks.CategorizeTransactionsTask({self._args})"

    def before_task(self):
        """
        This public before task manages all setup activities required by this task to perform its action

        :return: None
        """

        self._logger.info(f"Beginning before_task method of task '{self}'.")
        self._db.start_db("transactions")
        self._db.start_db("rules")
        self._logger.info(f"Finished before_task method of task '{self}'.")

    def do_task(self):
        """
        This public do task manages all of the actions this task runs

        :return: None
        """

        try:
            self._logger.info(f"Beginning do_task method of task '{self}'.")
            self._logger.info(f"Finished do_task method of task '{self}'.")
        except Exception as error_msg:
            self._task_state = "FAILED"
            raise TaskCategorizeTransactionsError(
                f"An error occurred during the do_task step of the '{self}'.  {error_msg}"
            )

    def after_task(self):
        """
        this public after task manages all of the teardown tasks that this task performs after its action is done

        :return: None
        """

        self._logger.info(f"Beginning after_task method of task '{self}'.")
        if self._task_state == "FAILED":
            pass
        else:
            pass
        self._logger.info(f"Finished after_task method of task '{self}'.")
