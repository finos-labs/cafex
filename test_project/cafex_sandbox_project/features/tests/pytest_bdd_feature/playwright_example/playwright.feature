@spg @team_mi_mobile @navigation @release_sprint_21.11.06
Feature: Validate page title

  @playwright_web @positive @automated @priority_high @rollout @bvt
  Scenario: Validate checkbox functionality
    Given the browser is launched
    When I navigate to "https://the-internet.herokuapp.com/checkboxes"
    Then the page title should contain "The Internet"
    And I verify checkbox with XPath "//input[1]" is unchecked
    And I verify checkbox with XPath "//input[2]" is checked
    When I click on the checkbox with XPath "//input[1]"
    Then the checkbox with XPath "//input[1]" should be checked
    When I click on the checkbox with XPath "//input[2]"
    Then the checkbox with XPath "//input[2]" should be unchecked

  @playwright_web @positive @automated @priority_high @rollout @bvt
  Scenario: Validate user login
    Given the browser is launched
    When I navigate to "https://the-internet.herokuapp.com/login"
    And I enter the username "tomsmith" in the field with XPath "//input[@id='username']"
    And I enter the password "SuperSecretPassword!" in the field with XPath "//input[@id='password']"
    And I click the login button with XPath "//button[@type='submit']"
    Then I should see the secure area with XPath "//div[@id='flash']"