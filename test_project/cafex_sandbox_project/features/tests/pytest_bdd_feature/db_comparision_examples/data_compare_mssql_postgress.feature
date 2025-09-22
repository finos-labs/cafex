@team_automation_cafex

Feature: Data validation between mssql and postgres
  As a QE
  I want to validate the data
  So that I can perform the data comparison between sql and postgres

  @db @positive @automated @priority_high @e2e
  Scenario Outline: Count of rows in sql db and postgres db are same
    Given user is connected to Postgres "cafex_PostgreSQL" db server
    And user is connected to MSSQL "cafex_mssql" db server
    When user executes Postgres query from file "db_automation\\Postgre.sql"
    And user executes MSSQL query from file "db_automation\\MSSQL.sql"
    Then the result should contain <result>

    Examples:
      | result |
      | pass   |