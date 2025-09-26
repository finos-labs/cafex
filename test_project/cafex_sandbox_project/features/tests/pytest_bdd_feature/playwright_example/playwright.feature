Feature: Validate page title

  @playwright_web
  Scenario: Validate checkbox functionality
    Given the browser is launched
    When I navigate to the checkboxes page
    Then the page title should contain "The Internet"
    And I verify the first checkbox is unchecked
    And I verify the second checkbox is checked
    When I click on the first checkbox
    Then the first checkbox should be checked
    When I click on the second checkbox
    Then the second checkbox should be unchecked

  @playwright_web
  Scenario: Validate user login
    Given the browser is launched
    When I navigate to the login page
    And I enter the username "tomsmith"
    And I enter the password "SuperSecretPassword!"
    And I click the login button
    Then I should see the secure area
