import datetime
import os
from decimal import Decimal

from mock import MagicMock, patch, call
from pytest import fixture, raises

from core.exceptions import TaskLoadTransactionsError
from tasks.task_categorize_transactions import CategorizeTransactionsTask


@fixture
def args():
    # research if there is a better way to do this
    class Args:
        def __init__(self):
            self.task_type = "categorize_transactions"

    return Args()


@fixture
def task(args):
    with patch(
        "os.path.abspath",
        MagicMock(
            return_value=os.sep.join(
                ["BASE", "REPO", "PATH", "PyFynance", "core", "config.py"]
            )
        ),
    ):
        return CategorizeTransactionsTask(args)


def test_when_init_the_correct_object_returned(args):
    task = CategorizeTransactionsTask(args)
    assert isinstance(task, CategorizeTransactionsTask)
    assert hasattr(task, "_args")
    assert hasattr(task, "_config")
    assert hasattr(task, "_db")
    assert hasattr(task, "_logger")


def test_when_repr_then_correct_str_returned(task):
    assert (
        task.__repr__()
        == "PyFynance.Tasks.CategorizeTransactionsTask(task_type=categorize_transactions)"
    )


def test_when_before_task_then_correct_methods_called(task):
    with patch.object(task, "_db", return_value=MagicMock()) as db_mock:
        task.before_task()
    db_mock.assert_has_calls([call.start_db("transactions"), call.start_db("rules")])
