from mock import MagicMock, patch, call
from pytest import fixture, raises

from schemas.rules import RulesSchema
from schemas.transactions import TransactionSchema
from tasks.task_categorize_transactions import CategorizeTransactionsTask


class TestTaskCategorizeTransactions:

    # ---- Test Fixtures ------------------------------

    @fixture
    def args(self):
        # research if there is a better way to do this
        class Args:
            def __init__(self):
                self.task_type = "categorize_transactions"

        return Args()

    @fixture
    def db_mock(self):
        select_data = [
            self.db_select_trans(),
            self.db_select_rules_base(),
            self.db_select_rules_custom(),
        ]
        db_mock = MagicMock()
        db_mock.select = MagicMock(side_effect=select_data)
        return db_mock

    @fixture
    def fs_mock(self):
        fs_mock = MagicMock()
        return fs_mock

    @fixture
    def config_mock(self):
        config_mock = MagicMock()
        config_mock.database.columns.transactions = [
            "institution",
            "account",
            "tran_id",
            "tran_type",
            "amount",
            "narrative",
            "date_posted",
            "date_processed",
            "primary_rule_id",
            "supp_rule_ids",
        ]
        config_mock.database.columns.base_rules = [
            "id",
            "type",
            "operation",
            "value",
            "description",
            "confidence",
            "category_id",
        ]
        return config_mock

    @fixture
    def cat_eng_mock(self):
        cat_eng_mock = MagicMock()
        return cat_eng_mock

    @fixture
    def task(self, args, db_mock, config_mock, fs_mock):
        with patch("tasks.task_base.Database", return_value=db_mock):
            with patch("tasks.task_base.Configuration", return_value=config_mock):
                with patch("tasks.task_base.FileSystem", return_value=fs_mock):
                    task = CategorizeTransactionsTask(args)
                    return task

    # ---- Test Data Objects --------------------------------

    @staticmethod
    def db_select_trans():
        return [
            (
                "my_bank",
                "my_account",
                "0001",
                "DEBIT",
                12.34,
                "mamamia pizza",
                "20191130000000",
                "20191130000000",
                None,
                None,
            ),
            (
                "my_bank",
                "my_account",
                "0002",
                "DEBIT",
                56.78,
                "xbox_games",
                "20191130000000",
                "20191130000000",
                None,
                None,
            ),
        ]

    @staticmethod
    def db_select_rules_base():
        return [
            ("rb01", "base", "contains", "pizza", "pizza rule", 90, "cb01"),
            ("rb02", "base", "contains", "playstation", "video games", 70, "cb02"),
        ]

    @staticmethod
    def db_select_rules_custom():
        return [("rc01", "base", "starts_with", "xbox", "xbox rule", 95, "cb02")]

    @staticmethod
    def loaded_trans():
        tran_dicts = [
            {
                "institution": "my_bank",
                "account": "my_account",
                "tran_id": "0001",
                "tran_type": "DEBIT",
                "amount": 12.34,
                "narrative": "mamamia pizza",
                "date_posted": "20191130000000",
                "date_processed": "20191130000000",
                "primary_rule_id": None,
                "supp_rule_ids": None,
            },
            {
                "institution": "my_bank",
                "account": "my_account",
                "tran_id": "0002",
                "tran_type": "DEBIT",
                "amount": 56.78,
                "narrative": "xbox_games",
                "date_posted": "20191130000000",
                "date_processed": "20191130000000",
                "primary_rule_id": None,
                "supp_rule_ids": None,
            },
        ]
        loaded_trans = []
        for tran in tran_dicts:
            loaded_trans.append(TransactionSchema().load(tran))
        return loaded_trans

    @staticmethod
    def categorized_trans():
        tran_dicts = [
            {
                "institution": "my_bank",
                "account": "my_account",
                "tran_id": "0001",
                "tran_type": "DEBIT",
                "amount": 12.34,
                "narrative": "mamamia pizza",
                "date_posted": "20191130000000",
                "date_processed": "20191130000000",
                "primary_rule_id": "rb01",
                "supp_rule_ids": None,
            },
            {
                "institution": "my_bank",
                "account": "my_account",
                "tran_id": "0002",
                "tran_type": "DEBIT",
                "amount": 56.78,
                "narrative": "xbox_games",
                "date_posted": "20191130000000",
                "date_processed": "20191130000000",
                "primary_rule_id": "rc01",
                "supp_rule_ids": None,
            },
        ]
        loaded_trans = []
        for tran in tran_dicts:
            loaded_trans.append(TransactionSchema().load(tran))
        return loaded_trans

    # ---- Tests --------------------------------------------

    def test_when_init_the_correct_object_returned(self, args):
        task = CategorizeTransactionsTask(args)
        assert isinstance(task, CategorizeTransactionsTask)
        assert hasattr(task, "_args")
        assert hasattr(task, "_config")
        assert hasattr(task, "_db")
        assert hasattr(task, "_fs")
        assert hasattr(task, "_logger")

    def test_when_repr_then_correct_str_returned(self, task):
        assert (
            task.__repr__()
            == "PyFynance.Tasks.CategorizeTransactionsTask(task_type=categorize_transactions)"
        )

    def test_when_before_task_then_correct_methods_called(self, task, db_mock):
        task.before_task()
        db_mock.assert_has_calls(
            [
                call.start_db("transactions"),
                call.start_db("rules_base"),
                call.start_db("rules_custom"),
            ]
        )

    @patch(
        "tasks.task_categorize_transactions.CategorizeTransactionsTask.post_categorisations_to_db"
    )
    @patch(
        "tasks.task_categorize_transactions.CategorizeTransactionsTask.categorize_transactions"
    )
    @patch(
        "tasks.task_categorize_transactions.CategorizeTransactionsTask.load_transactions"
    )
    def test_when_do_task_then_correct_methods_called(
        self, lt_patch, ct_patch, pc_patch, task
    ):
        task.do_task()
        assert lt_patch.call_count == 1
        assert ct_patch.call_count == 1
        assert pc_patch.call_count == 1

    def test_when_do_task_and_error_then_catch_error(self, task):
        with patch(
            "tasks.task_categorize_transactions.CategorizeTransactionsTask.load_transactions"
        ) as lt_patch:
            lt_patch.side_effect = Exception()
            with raises(Exception) as raised_error:
                task.do_task()
        assert raised_error.typename == "TaskCategorizeTransactionsError"
        assert (
            raised_error.value.args[0]
            == "An error occurred during the do_task step of 'PyFynance.Tasks."
            "CategorizeTransactionsTask(task_type=categorize_transactions)'.  "
        )

    def test_when_load_transactions_that_correct_transactions_loaded(
        self, task, db_mock
    ):
        task.load_transactions()
        db_mock.select.assert_called_once_with("transactions", "transactions")
        for task_tran, test_tran in zip(task._transactions, self.loaded_trans()):
            assert task_tran.__dict__ == test_tran.__dict__

    def test_when_categorize_transactions_then_rules_loaded_correctly(
        self, cat_eng_mock, db_mock, task
    ):
        db_mock.select = MagicMock(
            side_effect=[self.db_select_rules_base(), self.db_select_rules_custom()]
        )
        with patch(
            "tasks.task_categorize_transactions.CategorizationEngine",
            return_value=cat_eng_mock,
        ):
            task.categorize_transactions()
        db_mock.select.assert_has_calls(
            [call("rules_base", "base_rules"), call("rules_custom", "custom_rules")],
            any_order=True,
        )

    def test_when_categorize_transactions_then_cet_engine_called_correctly(
        self, cat_eng_mock, db_mock, task
    ):
        db_mock.select = MagicMock(
            side_effect=[self.db_select_rules_base(), self.db_select_rules_custom()]
        )
        transactions = self.loaded_trans()
        task._transactions = transactions
        with patch(
            "tasks.task_categorize_transactions.CategorizationEngine",
            return_value=cat_eng_mock,
        ):
            task.categorize_transactions()
        cat_eng_mock.categorize_transactions.assert_called_once_with(transactions)

    def test_when_post_categorisations_to_db_then_db_updated_correctly(
        self, task, db_mock
    ):
        transactions = self.categorized_trans()
        task._transactions = transactions
        task.post_categorisations_to_db()
        db_mock.update.assert_has_calls(
            [
                call(
                    "transactions",
                    "transactions",
                    {"primary_rule_id": "rb01", "supp_rule_ids": None},
                    {
                        "institution": "my_bank",
                        "account": "my_account",
                        "tran_id": "0001",
                    },
                ),
                call(
                    "transactions",
                    "transactions",
                    {"primary_rule_id": "rc01", "supp_rule_ids": None},
                    {
                        "institution": "my_bank",
                        "account": "my_account",
                        "tran_id": "0002",
                    },
                ),
            ]
        )

    def test_when_after_task_and_passed_then_tran_db_commits(self, task, db_mock):
        passed = True
        task.after_task(passed)
        db_mock.stop_db.assert_has_calls(
            [
                call("rules_base", commit=False),
                call("rules_custom", commit=False),
                call("transactions", commit=True),
            ]
        )

    def test_when_after_task_and_not_passed_then_tran_db_does_not_commit(
        self, task, db_mock
    ):
        passed = False
        task.after_task(passed)
        db_mock.stop_db.assert_has_calls(
            [
                call("rules_base", commit=False),
                call("rules_custom", commit=False),
                call("transactions", commit=False),
            ]
        )
