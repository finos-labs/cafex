from pytest_bdd import scenario, given, when, then

@scenario("add_numbers.feature", "Add two numbers")
def test_add_numbers():
    pass

@given("there are two numbers 2 and 3")
def step_given_two_numbers():
    global num1, num2
    num1 = 2
    num2 = 3

@when("I add them together")
def step_add_numbers():
    global result
    result = num1 + num2

@then("the sum should be 5")
def step_verify_sum():
    assert result == 5