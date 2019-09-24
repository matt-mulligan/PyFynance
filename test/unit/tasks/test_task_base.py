import datetime

from mock import patch
from pytest import raises, fixture

from core.exceptions import TaskError
from tasks.task_base import BaseTask


@fixture
def args():
    # research if there is a better way to do this
    class Args:
        def __init__(self):
            self.task_type = "load_transactions"
            self.runtime = datetime.datetime(2015, 2, 14, 10, 11, 12)
    return Args()


def test_when_init_the_base_task_returned(args):
    task = BaseTask(args)
    assert isinstance(task, BaseTask)
    assert hasattr(task, "_logger")


def test_when_execute_and_successful_then_true_returned(args):
    task = BaseTask(args)
    passed = task.execute()
    assert passed


@patch("tasks.task_base.BaseTask.do_task", side_effect=[TaskError("task_error_message")])
def test_when_execute_and_unsuccessful_then_true_returned(mock_do_task, args):
    task = BaseTask(args)
    with raises(TaskError):
        task.execute()


def test_when_get_args_repr_then_correct_string_returned(args):
    task = BaseTask(args)
    assert task.get_args_repr() == "task_type=load_transactions, runtime=2015-02-14 10:11:12"
