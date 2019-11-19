from core.exceptions import TaskCategorizeTransactionsError
from core.helpers import convert_tuple_to_dict
from schemas.rules import RulesSchema
from schemas.transactions import TransactionSchema
from services.categorization_engine import CategorizationEngine
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
        self._transactions = None
        self._categorization_engine = None

    def __repr__(self):
        return f"PyFynance.Tasks.CategorizeTransactionsTask({self.get_args_repr()})"

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
            self._load_transactions()
            self._categorise_transactions()
            self._post_categorisations_to_db()
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

    def _load_transactions(self):
        """
        This private method deals with loading the transactions from the database into a transactions object on this class
        :return: None
        """

        self._transactions = []
        transactions_tuples = self._db.select("transactions", "transactions")
        for transaction_tuple in transactions_tuples:
            transaction_dict = convert_tuple_to_dict(
                transaction_tuple, self._config.database.columns.transactions
            )
            self._transactions.append(TransactionSchema().load(transaction_dict))

    def _categorise_transactions(self):
        """
        this private method deals with the orchestration of categorizing transactions using the CategorizationEngine
        service
        :return: None
        """

        rules = self._load_rules_from_db()
        self._categorization_engine = CategorizationEngine(rules, self._config)
        self._transactions = self._categorization_engine.categorize_transactions(
            self._transactions
        )

    def _load_rules_from_db(self):
        """
        THis private method manages the loading of rules objects from the database
        :return:
        """

        rules = []
        rules_data = self._db.select("rules", "base_rules")
        for rule_obj in rules_data:
            rule_dict = convert_tuple_to_dict(
                rule_obj, self._config.database.columns.base_rules
            )
            rules.append(RulesSchema().load(rule_dict))
        return rules
