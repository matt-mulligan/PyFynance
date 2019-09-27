"""
PyFynance task structure implements abstract base classes to ensure consistency in task design.
all tasks in PyFynance must be child classes that implement tasks/base_task.
The purpose of this is to ensure that all tasks remain consistent, and that all tasks implement the require abstract
methods needed for the runner (core/PyFynance) to properly trigger and manage each task.

|

The abstract methods required to be implemented by each task are:

|

* before_task
    Any setup steps required to run your task. e.g. starting the database services

* do_task
    the actual business logic of your task

* after_task
    any cleanup / validation required by the task
"""