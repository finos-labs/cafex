Feature: Automate Notepad Operations
  As a user
  I want to automate Notepad operations
  So that I can replace text and save the file programmatically

  @ui_desktop_client
  Scenario: Replace text and save the file
    Given the user opens Notepad
    When the user types "This is a test.\nLet's replace some text."
    And the user replaces the word "test" with "example"
    And the user saves the file as "sample.txt"
    Then the file "sample.txt" should be saved successfully