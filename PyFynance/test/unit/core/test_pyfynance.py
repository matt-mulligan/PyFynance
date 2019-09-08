from mock import MagicMock, patch
from pytest import fixture, raises

from core.exceptions import TaskError
from core.pyfynance import PyFynance


@fixture
def args_load_transactions():
    args = MagicMock()
    args.task_type = "load_transactions"
    return args


def test_when_init_the_pyfynance_object_returned(args_load_transactions):
    app = PyFynance(args_load_transactions)

    assert hasattr(app, "_config")
    assert hasattr(app, "_args")
    assert hasattr(app, "_logger")

    assert app._args.task_type == "load_transactions"


@patch("tasks.task_load_transactions.LoadTransactionsTask.execute", return_value=True)
def test_when_run_and_task_is_successful_then_exit_code_zero(execute_mock, args_load_transactions):
    app = PyFynance(args_load_transactions)
    exit_code = app.run()
    assert exit_code == 0


@patch("tasks.task_load_transactions.LoadTransactionsTask.execute", return_value=False)
def test_when_run_and_task_is_unsuccessful_then_exit_code_one(execute_mock, args_load_transactions):
    app = PyFynance(args_load_transactions)
    exit_code = app.run()
    assert exit_code == 1


@patch("core.pyfynance.PyFynance._execute_tasks", side_effect=[Exception("thrown_error_message")])
def test_when_run_and_error_then_error_raised(execute_mock, args_load_transactions):
    app = PyFynance(args_load_transactions)
    with raises(TaskError):
        app.run()
