@manage_transaction_dbs
Feature: task_execution_categorize_transactions
  As a user of PyFynance
  I want to know that PyFynance will categorize my transactions correctly
  So that I can use PyFynance to analyse my transactions

  Scenario: categorize transactions task, transactions db exists, base and custom rules exist, success
    Given PyFynance task type is 'categorize_transactions'
    And no 'transaction' databases are present in the 'current' folder
    And no 'transaction' databases are present in the 'backup' folder
    And no 'rules_custom' databases are present in the 'current' folder
    And no 'rules_custom' databases are present in the 'backup' folder
    And db resource 'categorize_transactions.db' is placed in 'current' folder as 'transactions' database named 'transactions.db'
    And db resource 'rules_custom.db' is placed in 'current' folder as 'rules' database named 'rules_custom.db'
    When I run PyFynance with the arguments '--task_type categorize_transactions'
    Then PyFynance exits with code '0'
    And database 'transaction' exists in the 'current' folder
    And database 'transaction' exists in the 'backup' folder
    And select column 'tran_id, primary_rule_id, supp_rule_ids' for table 'transactions' in database 'transactions' in folder 'current' returns '[('201712140004', 'RB00000122', None), ('201712180010', 'RB00000139', None), ('201712180012', 'RC00000001', 'RB00000091'), ('201712180014', 'RB00000021', 'RB00000132'), ('201712210001', 'RB00000095', 'RC00000002'), ('201712270003', 'RB00000124', 'RB00000150'), ('201712270005', 'RB00000036', None), ('201712290001', 'RC00000004', 'RB00000052,RB00000132')]' when ordered by column 'tran_id'

