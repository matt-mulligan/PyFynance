import os
import shutil

from core import helpers
from core.exceptions import TaskLoadTransactionsError
from tasks.task_base import BaseTask


class LoadTransactionsTask(BaseTask):
    """
    The Load Transactions task is responsible for loading in financial transactions to PyFynance from OFX/QFX file
    source.

    This task type will load transactions from OFX files, parse the transactions to python dictionaries, serialise the
    values into OFX Banking Transaction objects within python, then write any new transactions to the
    transactions Database.

    This task is triggered in PyFynance by calling the PyFynance module from the command line with the following named
    values:

        * --task_type       load_transactions
        * --institution     The name of the financial institution the transactions are from
        * --account         The name of the account to associate the transactions with

    The load transactions task will load all ofx files it find in the input/banking_transactions folder of this repo.
    Once a file has been loaded using the load_transaction task it will be moved to either:
        * /input/banking_transactions/ingested      if the task was successful
        * /input/banking_transactions/error         if the task failed
    """

    def __init__(self, args):
        super(LoadTransactionsTask, self).__init__(args)
        self._transactions = []

    def __repr__(self):
        return "PyFynance.Tasks.LoadTransactionsTask({})".format(self.get_args_repr())

    def before_task(self):
        """
        This public before task manages all setup activities required by this task to perform its action

        :return: None
        """

        self._logger.info("Beginning before_task method of task '{}'.".format(self))
        self._db.start_db("transactions")
        self._logger.info("Finished before_task method of task '{}'.".format(self))

    def do_task(self):
        """
        This public do task manages all of the actions this task runs

        :return: None
        """

        self._logger.info("Beginning do_task method of task '{}'.".format(self))
        self._load_transactions_from_file()
        self._filter_transactions()
        self._write_transactions_to_db()
        self._logger.info("Finished do_task method of task '{}'.".format(self))

    def after_task(self):
        """
        this public after task manages all of the teardown tasks that this task performs after its action is done

        :return: None
        """

        self._logger.info("Beginning after_task method of task '{}'.".format(self))
        self._db.stop_db("transactions")
        self._logger.info("Finished after_task method of task '{}'.".format(self))

    def _load_transactions_from_file(self):
        """
        This private method controls the flow of loading transactions from files into python objects

        :return: None
        """

        files_to_parse = self._get_files_to_parse()
        for file_path in files_to_parse:
            self._transactions.extend(self._ofx_parser.parse("banking_transactions", file_path))
            self._move_transaction_file_to_ingested_folder(file_path)

    def _get_files_to_parse(self):
        """
        This private method will determine the full file paths to all transaction files that need to be ingested.

        :return: A list of file paths that either end in .ofx or .qfx
        """

        transactions_input_path = os.sep.join([self._config.paths.input_path, "banking_transactions"])
        files_to_parse = helpers.find_all_files(transactions_input_path, ["*.ofx", "*.qfx"])
        if len(files_to_parse) == 0:
            raise TaskLoadTransactionsError("No input ofx/qfx files found in input path '{}'.  Are you sure you "
                                            "placed the file there?".format(transactions_input_path))
        return files_to_parse

    def _write_transactions_to_db(self):
        """
        This private method will handle the writing of new transactions to the transactions database table.

        :return: None
        """

        for transaction in self._transactions:
            data = {
                "institution": self._args.institution,
                "account": self._args.account,
                "tran_id": transaction.fitid,
                "tran_type": transaction.trn_type,
                "amount": transaction.amount,
                "narrative": self._get_narrative_from_transaction(transaction),
                "date_posted": transaction.date_posted.strftime("%Y%m%d%H%M%S")
            }
            self._db.insert("transactions", "transactions", data)

    def _move_transaction_file_to_ingested_folder(self, ingested_file):
        """
        This private method will move the already ingested file from the input folder into the ingested folder

        :param ingested_file: Path to the ingested file
        :type ingested_file: String
        :return: None
        """

        dest_filename = "{}_{}".format(ingested_file.split(os.sep)[-1], self._args.runtime.strftime("%Y%m%d%H%M%S"))
        dest_path = os.sep.join([self._config.paths.input_path, "banking_transactions", "ingested", dest_filename])
        shutil.move(ingested_file, dest_path)

    def _filter_transactions(self):
        """
        This private method will filter down the list of transactions to only the ones that have not already been
        ingested.

        This is achieved by deriving a composite key for all of the loaded transactions and checking to see if that
        key appears already in the tranasactions database table.

        The composite key is INSTITUTION-ACCOUNT-TRANID

        :return: None
        """

        transaction_data = self._get_transactions_from_db()

        composite_keys = []
        for row in transaction_data:
            composite_keys.append("{}-{}-{}".format(row[0], row[1], row[2]))

        new_transactions = []
        for transaction in self._transactions:
            key = "{}-{}-{}".format(self._args.institution, self._args.account, transaction.fitid)
            if key not in composite_keys:
                new_transactions.append(transaction)

        self._transactions = new_transactions

    def _get_transactions_from_db(self):
        """
        This private method will select the required information from the transactions DB table so that the composite
        keys can be produced

        :return: List: all rows of the table that have the required institution and account
        """

        columns = ["institution", "account", "tran_id"]
        where = "institution = \"{institution}\" and account = \"{account}\"".format(institution=self._args.institution,
                                                                                     account=self._args.account)
        return self._db.select("transactions", "transactions", columns=columns, where=where)

    @staticmethod
    def _get_narrative_from_transaction(transaction):
        """
        This private static method will build and return the correct value for the narrative field in a transaction.
        It will also throw an error if there is no suitable narrative field found.

        :param transaction: a transaction object defined in PyFynance.schemas.ofx_banking_transaction.py
        :type transaction: OFX Banking Transaction Object
        :return: String: the correct transaction narrative value
        """

        has_name = hasattr(transaction, "name")
        has_memo = hasattr(transaction, "memo")

        if has_name and has_memo:
            return "{} - {}".format(transaction.name, transaction.memo)
        elif has_memo:
            return transaction.memo
        elif has_name:
            return transaction.name
        else:
            raise TaskLoadTransactionsError("Transaction does not have a memo or name attribute.  The transaction "
                                            "has the following attributes '{}'".format(transaction.__dict__.keys()))
