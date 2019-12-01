======================================
PyFynance Architecture
======================================


Guiding Design Patterns
=======================
PyFynance is built on a Task/Runner architecture where a task represents an end-to-end function of PyFynance that end users will use directly.
The runner is the core/PyFynance module, which controls the flow of execution through all tasks

|

Task Design
===========
PyFynance task structure implements abstract base classes to ensure consistency in task design.

all tasks in PyFyance must be child classes that implement tasks/base_task.

The purpose of this is to ensure that all tasks remain consisten, and that all tasks implement the require abstract methods needed for the runner (core/PyFynance) to proerly trigger and manage each task.

|

The abstract methods required to be implemented by each task are:

|

* before_task
	Any setup steps required to run your task. e.g. starting the database services

* do_task
	the actual business logic of your task
	
* after_task
	any cleanup / validation required by the task

|

Runner Design
=============
The purpose of the runner (core/PyFynance) within PyFynance is to control the flow of the execution through all tasks. This, along with tasks being abstract meta-classes, ensures that all tasks execute in a predictable way. 

The benefits of this are that tasks always executing the same base steps, in the same order, with the same error management and logging practises built throught. 

This ensure that PyFYnance will always be easy to maintain and extend by simply adding a new child task that implements the abstract base methods of base_task.

All of the orchestration and triggering of tasks are controlled by the runner module, making PyFynance tasks simple to integrate.

|

Package Structure
=================
PyFynance implements a logical package structure to manage the codebase as follows:

|

* Core Package
	Contains all the core code modules required to run the higher level packages such as the runner module, the config service and exception classes.
	
* Resources Package
	Contains all of the data assets required by or created by PyFynance, such as the config jsons and sqlite3 databases
	
* Schemas Package
	Contains all of the marshmallow schemas used by PyFynance of serialisation/deserialisation of data
	
* Services Package
	Contains all of the service modules that Interact with external entities and truely act as API's. Examples include the Database service (sqlite3 API) and the OFX Parser Service
	
* Tasks Package
	Contains all of the tasks that PyFynance can run and their business logic, including the base_task that all tasks inherit from.