.. _task_categorize_transactions:

============================================
PyFynance Task - Categorize Transactions
============================================


Task Purpose
=======================
The categorize transactions task will load all ingested transactions from the PyFynance transactions database, run them
though the categorisation engine and write the results back to the PyFynance database.

This task relies on the defined categorisation rules within PyFynance to attempt to categorize transaction. All rules
within PyFynance have a confidence rating scale (0-100 for base rules) that defines how confident the categorisation
engine is of its decision.

Rule categorisation in PyFynance is based off of the transaction narratives, with PyFynance attempting to determine
the transaction type off of these values. The categorisation engine in PyFynance has multiple supported operation types
that rules can use to match against transaction narratives. The current supported rule operations are:

    * contains - does the narrative contain this value? (case insensitive)
    * multi-contains - does the narrative contain all of these substrings (case insensitive, must be the same order as presented in the rule)
    * regex - does the narrative meet this regex string (case sensitive)
    * starts_with - does the narrative begin with this (case insensitive)
    * ends_with - does the narrative end with this (case insensitive)

|

How to call this task
=====================
This task is triggered in PyFynance by calling the PyFynance module from the command line with the following named
values:

        * --task_type       categorize_transactions

|

Example Usage of the Task
=========================
.. code-block:: bash

        cd /path/to/PyFynance
        pipenv run python -m PyFynance --task_type categorize_transactions

|

Common Errors / Troubleshooting
===============================

**What is RB99999999?**

The categorization engine in PyFynance currently uses relatively rudimentary categorisation techniques and the
ruleset is very small. as such it will not be able to categorise all transactions. RB99999999 is the rule code given
to transactions that PyFynance couldn't  currently categorise. We are always expanding the ruleset used so make sure
to get the latest update and recategorise your transactions. Support for custom rules is planning to be released in
the next update as well so that users can define their own rules to meet any specific requirements they have.
