.. _task_load_transactions:

======================================
PyFynance Task - Load Transactions
======================================


Task Purpose
=======================
The load transactions task is the most basic task that PyFynance provides. Its goal is to load transactions from
OFX/QFX files into PyFynance so that they can be analyse and categorised.

This task type will load transactions from OFX files, parse the transactions to python dictionaries, serialise the
values into OFX Banking Transaction objects within python, then write any new transactions to the
transactions Database.

|

How to call this task
=====================
This task is triggered in PyFynance by calling the PyFynance module from the command line with the following named
values:

        * --task_type       load_transactions
        * --institution     The name of the financial institution the transactions are from
        * --account         The name of the account to associate the transactions with

|

Example Usage of the Task
=========================
.. code-block:: bash

        cd /path/to/PyFynance
        pipenv run python -m PyFynance --task_type load_transactions --institution my_bank --account credit_card

|

Common Errors / Troubleshooting
===============================

**No input ofx/qfx files found in input path**

Fairly self explanatory this one. Seems like you forgot to put the input file in the input/banking_transactions
directory. Another common cause of this error is that the file does not have the extention ".ofx" or ".qfx"
