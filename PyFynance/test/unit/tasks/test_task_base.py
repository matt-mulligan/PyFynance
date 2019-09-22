import datetime

from mock import patch, MagicMock
from pytest import raises, fixture

from core.exceptions import TaskError
from tasks.task_base import BaseTask


@fixture
def args():
    args = MagicMock()
    args.task_type = "load_transactions"
    args.runtime = datetime.datetime(2015, 2, 14, 10, 11, 12)
    return args


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
