======================================
PyFynance Test Results - V1.0
======================================

PyFynance has been developed with testing in mind to allow for safe refactoring and easy extendability of the codebase. This page will document our testing approach and will show the current state of our testing suites 

|

PyFynance Testing Approach
==========================
PyFynance maintains both unit and acceptance testing suites to ensure that our code is adequately covered with tests to ensure no regressions are made and to improve development cycles.

We use pytest (https://pypi.org/project/pytest/) for our unit testing suite and Behave (https://pypi.org/project/behave/) for our acceptance testing suite.

|

Unit Test Suite Results
=======================

.. test-results:: tests/unit/PyFynance_unit_tests.xml

|

Acceptance Test Suite Results
=============================

.. test-results:: tests/acceptance/PyFynance_acceptance_tests.xml