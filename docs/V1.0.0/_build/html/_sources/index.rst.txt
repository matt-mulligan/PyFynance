======================================
PyFynance - Personal Pythonic Finance!
======================================
PyFynance is a pythonic personal finance tool to help you track, categorise and analyse your spending habits.

|

Getting Started with PyFynance in 3 steps
=========================================
To start using PyFynance simple do the following

1) Clone the `PyFynance Repository <https://github.com/matt-mulligan/PyFynance>`_ to your local machine

|

2) Install the environment manager `pipenv <https://pypi.org/project/pipenv/>`_ if not already installed using the pip tool

.. code-block:: bash

        pip install pipenv

|

3) cd to the directory where PyFynance has been cloned and install the virtual environment with pipenv

.. code-block:: bash

        cd /path/to/PyFynance
        pipenv install

|

And you're done! PyFynance is ready to use! Check out the PyFynance Tasks Section for what PyFynance can do:


PyFynance Tasks
===============
Tasks are the basic building block of PyFynance. A task is a unit of functionality that PyFynance can do for you.

As PyFynance is a command line tool, all tasks are triggered from the command line using the --task_type flag

|

See below the list of tasks that PyFynance currently can perform:

|

    :ref:`task_load_transactions` - Loads your financial transactions from OFX/QFX files into PyFynance for analysis

|


PyFynance Feature Roadmap
=========================
PyFyanance currently have the below features in our backlog for development

* Task: Categorise Transactions - PyFynanace to try and categorise what each transaction is to provide insight on your spending
* Task: Analyse Spending - PyFyanace to perform analytics (basic at first) on loaded and categorised transactions
* Task: Add Custom Categorisation Rules - PyFynance to allow users to provide their own categorisation rules and weightings
* Task: Add / Analyse Goals - PyFyannce to allow users to define spending / saving goals to be tracked against
* Interface: PyFynance GUI Interface - PyFynance to transation from cmd line interface to interactive GUI

|

PyFynance Testing Approach / CICD
=================================
PyFynance utilises TDD/BDD principals and maintains both unit and acceptance test suites.

Unit testing is carried out using the pytest library and is run on all public interfaces. The unit test suite is
maintained at >95% coverage for all branches on the remote repo

Acceptance testing is carried out using the beahve library and run on all tasks/features of PyFynance. All new features
in PyFynance must submit behave tests to fully test their feature

CICD build and test pipelines are setup and maintained using travis-ci. PyFynance CICD pipeline will trigger the following:

* Code styling check via Black library
* Pytest unit testing suite run for success and code coverage
* Behave acceptance test suite run for success

|

PyFynance API Documentation
===========================
This section contains all of the API documentation and design patterns for all of the internal classes of PyFynance.
This is provided as a service to other engineers who wish to modify/fork PyFynance for their own work.
API documentation was generated using Sphinx-apidoc

|

.. toctree::
   :maxdepth: 4
   
	PyFynance Architecture <architecture.rst>
	
.. toctree::
   :maxdepth: 4
   
	PyFynance Tasks <tasks/tasks.rst>
	
.. toctree::
   :maxdepth: 4
   
	PyFynance API Documentation <apidocs.rst>
	
