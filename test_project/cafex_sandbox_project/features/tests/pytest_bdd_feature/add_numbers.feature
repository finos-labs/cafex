Feature: Adding two numbers

  Scenario: Add two numbers
    Given there are two numbers 2 and 3
    When I add them together
    Then the sum should be 5