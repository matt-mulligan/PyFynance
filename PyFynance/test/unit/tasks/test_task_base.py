from mock import patch
from pytest import raises

from core.exceptions import TaskError
from tasks.task_base import BaseTask


def test_when_init_the_base_task_returned():
    task = BaseTask()
    assert isinstance(task, BaseTask)
    assert hasattr(task, "_logger")


def test_when_execute_and_successful_then_true_returned():
    task = BaseTask()
    passed = task.execute()
    assert passed


@patch("tasks.task_base.BaseTask.do_task", side_effect=[TaskError("task_error_message")])
def test_when_execute_and_unsuccessful_then_true_returned(mock_do_task):
    task = BaseTask()
    with raises(TaskError):
        task.execute()
