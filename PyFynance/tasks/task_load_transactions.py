import os
import shutil

from core.exceptions import TaskError
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
        self._load_transactions_from_file()
        self._filter_transactions()
        self._write_transactions_to_db()
        self._logger.info("Finished do_task method of task '{}'.".format(self))

    def after_task(self):
        """
        this do task manages all of the teardown tasks that this task performs after its action is done
        :return:
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

        :return: None
        """

        transactions_input_path = os.sep.join([self._config.paths.input_path, "banking_transactions"])
        files_to_parse = find_all_files(transactions_input_path, ["*.ofx", "*.qfx"])
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
        This private method will move the already ingested file from the input location into the ingested folder

        :param ingested_file: String: path to the ingested file
        :return: None
        """

        dest_filename = "{}_{}".format(ingested_file.split(os.sep)[-1], self._args.runtime.strftime("%Y%m%d%H%M%S"))
        dest_path = os.sep.join([self._config.paths.input_path, "banking_transactions", "ingested", dest_filename])
        shutil.move(ingested_file, dest_path)

    def _filter_transactions(self):
        """
        This private method will filter down the list of transactions to only the ones that have not already been
        ingested.
        This is achieved by deriving the composite key for all of the loaded transactions and checking to see if that
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
        This private method will build and return the correct value for the narrative field in a transaction.
        It will also throw an error if there is no suitable narrative field found.

        :param transaction: Object: a transaction object defined in PyFynance.schemas.ofx_banking_transaction.py
        :return: String: the correct memo value for the transaction
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
            raise TaskError("Transaction does not have a memo or name attribute.  The transaction has the following "
                            "attributes '{}'".format(transaction.__dict__.keys()))
