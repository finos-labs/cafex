@spg @team_mi_mobile @navigation @release_sprint_21.11.06
Feature: Verify the mongodb utils
  As a user
  I want to verify the mongodb utils
  So that I can check the connection

  @db @positive @automated @priority_high @rollout
  Scenario: Check mongodb connection
    Given I have a mongodb connection
    When I check the connection
    Then I will execute the query
    Then I will execute query with parameters
    Then I will get collection count
    Then I will get specific document from the collection
    Then I will close the connection