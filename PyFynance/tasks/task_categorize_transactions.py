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
            self.categorize_transactions()
            self.post_categorisations_to_db()
            self._logger.info(f"Finished do_task method of task '{self}'.")
        except Exception as error_msg:
            raise TaskCategorizeTransactionsError(
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
        if passed:
            self._db.stop_db("transactions", commit=True)
        else:
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

    def categorize_transactions(self):
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

    def post_categorisations_to_db(self):
        """
        this private method is responsible for writing the transactions back to the database
        :return:
        """

        for transaction in self._transactions:
            update_data = {
                "primary_rule_id": transaction.primary_rule_id,
                "supp_rule_ids": transaction.supp_rule_ids,
            }
            primary_keys = {
                "institution": transaction.institution,
                "account": transaction.account,
                "tran_id": transaction.tran_id,
            }
            self._db.update("transactions", "transactions", update_data, primary_keys)

    def _load_rules_from_db(self):
        """
        THis private method manages the loading of rules objects from the database
        :return:
        """

        rules = []
        rules_data = self._db.select("rules_base", "base_rules")
        rules_data.extend(self._db.select("rules_custom", "custom_rules"))
        for rule_obj in rules_data:
            rule_dict = convert_tuple_to_dict(
                rule_obj, self._config.database.columns["base_rules"]
            )
            rules.append(RulesSchema().load(rule_dict))
        return rules
