@team_QA_automation
Feature: Data validation for CIQDeal table
  As a QA
  I want to write this scenario for CIQ Deal table validation
  So that the pipeline data is flowing properly

#  Background: Connecting to database server
#      Given user connects to server "cafex"

  @db @positive @automated @priority_high @e2e
  Scenario Outline: Executing a SQL Query from file
    Given user connects to server "cafex"
    When user executes query from file <filepath>
    Then the result should contain <result>
    Examples:
      | filepath                                 | result                |
      | db_automation\Employee.sql               | Pass                  |

  @db @positive @automated @priority_high @e2e
  Scenario Outline: Executing a PostgreSQL Query from file
    Given user connects to server "cafex_PostgreSQL"
    When user executes query from file <filepath>
    Then the result should contain <result>
    Examples:
      | filepath                                 | result                |
      | db_automation\Postgre.sql                | Pass                  |

  @db @positive @automated @priority_high @e2e
  Scenario Outline: Executing a Oracle Query from file
    Given user connects to server "cafex_oracle"
    When user executes query from file <filepath>
    Then the result should contain <result>
    Examples:
      | filepath                                 | result                |
      | db_automation\Oracle.sql                 | Pass                  |

  @db @positive @automated @priority_high @e2e
  Scenario Outline: Executing a MSSQL Query from file
    Given user connects to server "cafex_mssql"
    When user executes query from file <filepath>
    Then the result should contain <result>
    Examples:
      | filepath                                 | result                |
      | db_automation\MSSQL.sql                  | Pass                  |