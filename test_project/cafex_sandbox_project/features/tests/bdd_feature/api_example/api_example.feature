Feature: Testing JSONPlaceholder API

  @api @example
  Scenario Outline: Retrieve post details from JSONPlaceholder
    Given the JSONPlaceholder API is available
    When I send a GET request to retrieve post <post_id>
    Then the response status code should be "200"
    And the response should contain the post title
    Examples:
      | post_id |
      | 1       |
      | 2       |
      | 3       |

  @api @example
  Scenario: Retrieve non-existent post
    Given the JSONPlaceholder API is available
    When I send a GET request to endpoint "/posts/999"
    Then the response status code should be "404"

  @api @example
  Scenario: Retrieve posts with query parameters
    Given the JSONPlaceholder API is available
    When I send a GET request to endpoint "/posts?userId=1"
    Then the response status code should be "200"
    And the response should contain multiple posts

  @api @example
  Scenario: Create a new post
    Given the JSONPlaceholder API is available
    When I create a new post with title "Test Post" and body "This is a test post"
    Then the response status code should be "201"
    And the response should contain the new post details

  @api @example
  Scenario: Update an existing post
    Given the JSONPlaceholder API is available
    When I update post "1" with title "Updated Title"
    Then the response status code should be "200"
    And the response should contain the updated title

  @api @example
  Scenario: Delete a post
    Given the JSONPlaceholder API is available
    When I delete post "1"
    Then the response status code should be "200"