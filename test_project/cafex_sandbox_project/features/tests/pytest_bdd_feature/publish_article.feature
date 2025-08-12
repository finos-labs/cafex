Feature: Step arguments

    @api
    Scenario: Arguments for given, when, then
        Given there are 5 cucumbers
        When I eat 3 cucumbers
        And I eat 2 cucumbers
        Then I should have 0 cucumbers

    @api
    Scenario Outline: Outlined given, when, then
    Given there are <start> cucumbers
    When I eat <eat> cucumbers
    Then I should have <left> cucumbers

    Examples:
    | start | eat | left |
    |  12   |  5  |  7   |
    |6      |3    |3     |