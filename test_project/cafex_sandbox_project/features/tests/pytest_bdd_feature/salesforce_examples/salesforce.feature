@sf @team_cafex @navigation @release_sprint_0_0_0
Feature: Salesforce Opportunity Management Enhancements

  @ui_web @priority_high @regression @salesforce @planned @positive
  Scenario: Create and convert a lead, then update opportunity stage
    Given user log into Salesforce with credentials:
      | username  | password  |
      | test      |           |
      |           |           |
      | test_user | test_pass |
    And user navigates to leads tab
    And user create a lead with default data
    And user create a lead with following data:
      | Field     | Value   |
      | Last Name | Smith   |
      | Company   | Acme    |
    And user will open new created lead and will convert the lead
    When user go to "Opportunity" app
    And user set the "Stage" as "Closed Won" for the created opportunity
    Then user should see the opportunity stage updated to "Closed Won"

  @ui_web @priority_high @regression @salesforce @automated @positive
  Scenario: Clone an opportunity and validate details
    Given the user is on the Opportunity page
    When the user selects an "inc-" opportunity
    And clicks the Clone button
    And appends the opportunity name with clone text
    And clicks the Save button
    And opens the newly cloned opportunity
    Then the opportunity details should be validated

  @ui_web @priority_medium @regression @salesforce @automated @positive
  Scenario: Add a note to an opportunity and validate the title
    Given the user is on the Opportunity page
    When the user selects an "inc-" opportunity
    And clicks the Note button
    And enters a new title "New note to this opportunity" and body content "sample note body content"
    And clicks the Save button
    And opens the newly created note
    Then the note title should be validated as "New note to this opportunity"