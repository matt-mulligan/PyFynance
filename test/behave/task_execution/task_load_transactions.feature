@manage_transaction_dbs
Feature: task_execution_load_transactions
  As a user of PyFynance
  I want to know that PyFynance will load my transactions correctly
  So that I can use PyFynance to analyse my transactions

  Scenario: load transactions task, triggered with ofx file, success
    Given PyFynance task type is 'load_transactions'
    And no 'transaction' databases are present in the 'current' folder
    And no 'transaction' databases are present in the 'backup' folder
    And no 'banking_transactions' input files are present in the 'landing' folder
    And no 'banking_transactions' input files are present in the 'processed' folder
    And no 'banking_transactions' input files are present in the 'error' folder
    And file resource 'mybank_cc.ofx' is placed in input folder 'banking_transactions' within 'landing'
    When I run PyFynance with the arguments '--task_type load_transactions --institution mybank --account cc'
    Then PyFynance exits with code '0'
    And input file 'mybank_cc.ofx' has been moved to 'banking_transactions' folder within 'processed'
    And database 'transaction' exists in the 'current' folder
    And database 'transaction' exists in the 'backup' folder
    And rowcount for table 'transactions' in database 'transactions' in folder 'current' is 3
    And select column 'narrative' for table 'transactions' in database 'transactions' in folder 'current' returns '[('DINNER',), ('MONEY ADDED TO CARD',), ('COFFEES',)]' when ordered by column 'tran_id'

  Scenario: load transactions task, triggered with qfx file, success
    Given PyFynance task type is 'load_transactions'
    And no 'transaction' databases are present in the 'current' folder
    And no 'transaction' databases are present in the 'backup' folder
    And no 'banking_transactions' input files are present in the 'landing' folder
    And no 'banking_transactions' input files are present in the 'processed' folder
    And no 'banking_transactions' input files are present in the 'error' folder
    And file resource 'bankaus_debit.qfx' is placed in input folder 'banking_transactions' within 'landing'
    When I run PyFynance with the arguments '--task_type load_transactions --institution bankaus --account debit'
    Then PyFynance exits with code '0'
    And input file 'bankaus_debit.qfx' has been moved to 'banking_transactions' folder within 'processed'
    And database 'transaction' exists in the 'current' folder
    And database 'transaction' exists in the 'backup' folder
    And rowcount for table 'transactions' in database 'transactions' in folder 'current' is 3
    And select column 'narrative' for table 'transactions' in database 'transactions' in folder 'current' returns '[('BACON',), ('XBOX - SUBSCRIPTION',), ('SALARY',)]' when ordered by column 'tran_id'


  Scenario: load transactions task, triggered with no file, error raised
    Given PyFynance task type is 'load_transactions'
    And no 'transaction' databases are present in the 'current' folder
    And no 'transaction' databases are present in the 'backup' folder
    And no 'banking_transactions' input files are present in the 'landing' folder
    And no 'banking_transactions' input files are present in the 'processed' folder
    And no 'banking_transactions' input files are present in the 'error' folder
    When I run PyFynance with the arguments '--task_type load_transactions --institution no_file --account credit'
    Then PyFynance exits with code '1'
    And message 'No input ofx/qfx files found in input path' can be found in the PyFynance log

  Scenario: load transactions task, triggered with txt file, error raised
    Given PyFynance task type is 'load_transactions'
    And no 'transaction' databases are present in the 'current' folder
    And no 'transaction' databases are present in the 'backup' folder
    And no 'banking_transactions' input files are present in the 'landing' folder
    And no 'banking_transactions' input files are present in the 'processed' folder
    And no 'banking_transactions' input files are present in the 'error' folder
    And file resource 'bad_file_type.txt' is placed in input folder 'banking_transactions' within 'landing'
    When I run PyFynance with the arguments '--task_type load_transactions --institution bad_file_type --account debit'
    Then PyFynance exits with code '1'
    And message 'Is the file type ofx/qfx?' can be found in the PyFynance log

  Scenario: load transactions task, some transactions already in db, success
    Given PyFynance task type is 'load_transactions'
    And no 'transaction' databases are present in the 'current' folder
    And no 'transaction' databases are present in the 'backup' folder
    And no 'banking_transactions' input files are present in the 'landing' folder
    And no 'banking_transactions' input files are present in the 'processed' folder
    And no 'banking_transactions' input files are present in the 'error' folder
    And file resource 'some_trans.ofx' is placed in input folder 'banking_transactions' within 'landing'
    And db resource 'trans_already_exist.db' is placed in 'current' folder as 'transactions' database named 'transactions.db'
    When I run PyFynance with the arguments '--task_type load_transactions --institution mybank --account cc'
    Then PyFynance exits with code '0'
    And input file 'some_trans.ofx' has been moved to 'banking_transactions' folder within 'processed'
    And database 'transaction' exists in the 'current' folder
    And database 'transaction' exists in the 'backup' folder
    And rowcount for table 'transactions' in database 'transactions' in folder 'current' is 3
    And select column 'narrative' for table 'transactions' in database 'transactions' in folder 'current' returns '[('DINNER',), ('MONEY ADDED TO CARD',), ('COFFEES',)]' when ordered by column 'tran_id'
