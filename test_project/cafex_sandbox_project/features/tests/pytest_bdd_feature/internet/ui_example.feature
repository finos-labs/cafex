Feature: Test the-internet.herokuapp.com
  As a QA
  I want to test various functionalities on the-internet.herokuapp.com
  So that I can ensure the website works as expected

  Background:
    Given the user is on the homepage

  @ui_web
  Scenario: Check for a specific element on the homepage
    Then the user should see the "Welcome to the-internet" text

  @ui_web
  Scenario: Navigate to the "A/B Testing" page and verify its content
    When the user navigates to the "A/B Testing" page
    Then the user should see the "A/B" particular text

  @ui_web
  Scenario: Navigate to the "Add/Remove Elements" page and add an element
    When the user navigates to the "Add/Remove Elements" page
    And the user adds an element
    Then the user should see the "Delete" button

  @ui_web
  Scenario Outline: Navigate to Form Authentication page and validate the login mechanism
    When the user navigates to the Form Authentication page
    And the user enters the username <username> and password <password>
    And the user hits the login button
    Then the user should see the message <message>
    Examples:
      | username | password | message |
      | tomsmith | ENjnpCHhJG89EZ+B8YnWdRp5jITEZY9EPV5NIoifG/w= | You logged into a secure area! |
      | invalid | XVEtyKmWyrp1bbWWdeJIUJN9uOCRNjZIIKzpvXenIvk= | Your username is invalid! |
      | tomsmith | XVEtyKmWyrp1bbWWdeJIUJN9uOCRNjZIIKzpvXenIvk= | Your password is invalid! |

  @ui_web
  Scenario: Navigate to Form Authentication page and validate the login mechanism using config file
    When the user navigates to the Form Authentication page
    And the user enters the credentials
    And the user hits the login button
    Then the user should see the "You logged into a secure area!"




