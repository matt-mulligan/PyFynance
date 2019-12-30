from core.exceptions import (
    TaskCategorizeTransactionsError,
    TaskAnalyseTransactionsError,
)
from core.helpers import convert_tuple_to_dict, load_objects_from_db
from schemas.rules import RulesSchema
from schemas.transactions import TransactionSchema
from tasks.task_base import BaseTask


class AnalyseTransactionsTask(BaseTask):
    """
    The Analyse Transactions task is responsible loading categorised transactions from the PyFynance database and
    analysing the spending habits by category.
    Analysis provided in tabular and graphical formats.

    ChangeLog:
        - original implementation of this task added to PyFynance in Release 1.1
    """

    def __init__(self, args):
        super(AnalyseTransactionsTask, self).__init__(args)
        self._transactions = None
        self._rule_mappings = None

    def __repr__(self):
        return f"PyFynance.Tasks.AnalyseTransactionsTask({self.get_args_repr()})"

    def before_task(self):
        """
        This public before task manages all setup activities required by this task to perform its action

        :return: None
        """

        self._logger.info(f"Beginning before_task method of task '{self}'.")
        self._db.start_db("transactions")
        self._db.start_db("rules_base")
        self._db.start_db("rules_custom")
        self._logger.info(f"Finished before_task method of task '{self}'.")

    def do_task(self):
        """
        This public do task manages all of the actions this task runs

        :return: None
        """

        try:
            self._logger.info(f"Beginning do_task method of task '{self}'.")
            self.load_transactions()
            self.load_category_information()
            self.summerise_aggregate_data()
            self.create_table_analysis()
            self.create_graph_analysis()
            self._logger.info(f"Finished do_task method of task '{self}'.")
        except Exception as error_msg:
            raise TaskAnalyseTransactionsError(
                f"An error occurred during the do_task step of '{self}'.  {error_msg}"
            )

    def after_task(self, passed):
        """
        this public after task manages all of the teardown tasks that this task performs after its action is done

        :return: None
        """

        self._logger.info(f"Beginning after_task method of task '{self}'.")
        self._db.stop_db("rules_base", commit=False)
        self._db.stop_db("rules_custom", commit=False)
        self._db.stop_db("transactions", commit=False)
        self._logger.info(f"Finished after_task method of task '{self}'.")

    def load_transactions(self):
        """
        This method deals with loading the transactions from the database into a transactions object on this class
        :return: None
        """

        self._transactions = []
        transactions_tuples = self._db.select("transactions", "transactions")
        for transaction_tuple in transactions_tuples:
            transaction_dict = convert_tuple_to_dict(
                transaction_tuple, self._config.database.columns["transactions"]
            )
            self._transactions.append(TransactionSchema().load(transaction_dict))

    def load_category_information(self):
        """
        This method deals with loading the transactions from the database into a transactions object on this class
        :return: None
        """

        self._rule_mappings = []

        rules = load_objects_from_db(self._config, self._db, "base_rules")
        rules.extend(load_objects_from_db(self._config, self._db, "custom_rules"))

        categories = load_objects_from_db(self._config, self._db, "base_categories")
        categories.extend(
            load_objects_from_db(self._config, self._db, "custom_categories")
        )

        for rule in rules:
            for category in categories:
                if category.id == rule.category_id:
                    rule.primary_category = category.primary_category
                    rule.secondary_category = category.secondary_category
            self._rule_mappings.append(rule)
