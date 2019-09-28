@manage_transaction_dbs
Feature: PyFynance_load_transactions_task
  As a user of PyFynance
  I want to know that PyFynance will load my transactions correctly
  So that I can use PyFynance to analyse my transactions

  Scenario: load transactions task, triggered with ofx file, success
    Given PyFynance task type is 'load_transactions'
    And no 'transaction' databases are present in the 'current' folder
    And no 'transaction' databases are present in the 'backup' folder
    And no files are present in input 'banking_transactions' folder
    And file resource 'mybank_cc.ofx' is placed in the input 'banking_transactions' folder
    When I run PyFynance with the arguments '--task_type load_transactions --institution mybank --account cc'
    Then PyFynance exits with code '0'
    And input file has been moved to 'ingested' folder
    And 'transaction' database exists in the 'current' folder
    And 'transaction' database exists in the 'backup' folder
    And rowcount for 'transaction' 'current' database is 3
    And select statement for 'transaction' 'current' database returns 'values' when filtered by 'filter_condition'

  Scenario: load transactions task, triggered with qfx file, success
    Given PyFynance task type is 'load_transactions'
    And no 'transaction' databases are present in the 'current' folder
    And no 'transaction' databases are present in the 'backup' folder
    And no files are present in input 'banking_transactions' folder
    And file resource 'mybank_debit.qfx' is placed in the input 'banking_transactions' folder
    When I run PyFynance with the arguments '--task_type load_transactions --institution mybank --account debit'
    Then PyFynance exits with code '0'
    And input file has been moved to 'ingested' folder
    And 'transaction' database exists in the 'current' folder
    And 'transaction' database exists in the 'backup' folder
    And rowcount for 'transaction' 'current' database is 3
    And select statement for 'transaction' 'current' database returns 'values' when filtered by 'filter_condition'

  Scenario: load transactions task, triggered with no file, error raised
    Given PyFynance task type is 'load_transactions'
    And no 'transaction' databases are present in the 'current' folder
    And no 'transaction' databases are present in the 'backup' folder
    And no files are present in input 'banking_transactions' folder
    When I run PyFynance with the arguments '--task_type load_transactions --institution mybank --account debit'
    Then PyFynance exits with code '1'
    And message 'LOGMESSAGE' can be found in the PyFynance log

  Scenario: load transactions task, triggered with txt file, error raised
    Given PyFynance task type is 'load_transactions'
    And no 'transaction' databases are present in the 'current' folder
    And no 'transaction' databases are present in the 'backup' folder
    And no files are present in input 'banking_transactions' folder
    And file resource 'badfile.txt' is placed in the input 'banking_transactions' folder
    When I run PyFynance with the arguments '--task_type load_transactions --institution mybank --account debit'
    Then PyFynance exits with code '1'
    And message 'LOGMESSAGE' can be found in the PyFynance Run Log

  Scenario: load transactions task, some transactions already in db, success
    Given PyFynance task type is 'load_transactions'
    And no 'transaction' databases are present in the 'current' folder
    And no 'transaction' databases are present in the 'backup' folder
    And no files are present in input 'banking_transactions' folder
    And database resource 'transactions_cc' is placed in database 'current' folder
    And file resource 'mybank_cc.ofx' is placed in the input 'banking_transactions' folder
    When I run PyFynance with the arguments '--task_type load_transactions --institution mybank --account cc'
    Then PyFynance exits with code '0'
    And input file has been moved to 'ingested' folder
    And 'transaction' database exists in the 'current' folder
    And 'transaction' database exists in the 'backup' folder
    And rowcount for 'transaction' 'current' database is 3
    And select statement for 'transaction' 'current' database returns 'values' when filtered by 'filter_condition'