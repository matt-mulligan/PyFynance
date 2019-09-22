import os

from tasks.task_base import BaseTask
from core.helpers import find_all_files


class LoadTransactionsTask(BaseTask):
    """
    This task manages the ingestion of transactions into the PyFynance database
    """

    def __init__(self, args):
        super(LoadTransactionsTask, self).__init__(args)
        self._transactions = []

    def __repr__(self):
        return "PyFynance.Tasks.LoadTransactionsTask({})".format(self._get_args_repr())

    def before_task(self):
        """
        this before task manages all setup activities required by this task to perform its action
        :return:
        """

        self._logger.info("Beginning before_task method of task '{}'.".format(self))
        self._db.start_db("transactions")
        self._logger.info("Finished before_task method of task '{}'.".format(self))

    def do_task(self):
        """
        this do task manages all of the actions this task runs
        :return:
        """

        self._logger.info("Beginning do_task method of task '{}'.".format(self))
        # get file paths to parse
        transactions_input_path = "{}{}{}".format(self._config.paths.input_path, os.sep, "banking_transactions")
        files_to_parse = find_all_files(transactions_input_path, ["*.ofx", "*.qfx"])

        # parse transaction file to python objects
        for file_path in files_to_parse:
            self._transactions.extend(self._ofx_parser.parse("banking_transactions", file_path,))

        # get transactions from transactions DB
        # determine which transactions are new
        # categorise new transactions
        # write back new transactions to DB
        self._logger.info("Finished do_task method of task '{}'.".format(self))

    def after_task(self):
        """
        this do task manages all of the teardown tasks that this task performs after its action is done
        :return:
        """

        self._logger.info("Beginning after_task method of task '{}'.".format(self))
        self._db.stop_db("transactions")
        self._logger.info("Finished after_task method of task '{}'.".format(self))
