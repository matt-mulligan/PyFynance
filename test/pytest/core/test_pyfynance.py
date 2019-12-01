import datetime

from mock import MagicMock, patch
from pytest import fixture, raises

from core.exceptions import TaskError
from core.pyfynance import PyFynance


class TestPyFynance:

    # ---- Test Fixtures ------------------------------

    @fixture
    def args_load_transactions(self):
        args = MagicMock()
        args.task_type = "load_transactions"
        args.runtime = datetime.datetime(2015, 2, 14, 10, 11, 12)
        return args

    # ---- Test Data Objects --------------------------

    # ---- Test Methods ------------------------------

    def test_when_init_the_pyfynance_object_returned(self, args_load_transactions):
        app = PyFynance(args_load_transactions)

        assert isinstance(app, PyFynance)
        assert hasattr(app, "_config")
        assert hasattr(app, "_args")
        assert hasattr(app, "_logger")
        assert app._args.task_type == "load_transactions"

    @patch(
        "tasks.task_load_transactions.LoadTransactionsTask.execute", return_value=True
    )
    def test_when_run_and_task_is_successful_then_exit_code_zero(
        self, execute_mock, args_load_transactions
    ):
        app = PyFynance(args_load_transactions)
        exit_code = app.run()
        assert exit_code == 0

    @patch(
        "tasks.task_load_transactions.LoadTransactionsTask.execute", return_value=False
    )
    def test_when_run_and_task_is_unsuccessful_then_exit_code_one(
        self, execute_mock, args_load_transactions
    ):
        app = PyFynance(args_load_transactions)
        exit_code = app.run()
        assert exit_code == 1

    @patch(
        "core.pyfynance.PyFynance._execute_tasks",
        side_effect=[Exception("thrown_error_message")],
    )
    def test_when_run_and_error_then_error_raised(
        self, execute_mock, args_load_transactions
    ):
        app = PyFynance(args_load_transactions)
        with raises(TaskError) as e:
            app.run()
