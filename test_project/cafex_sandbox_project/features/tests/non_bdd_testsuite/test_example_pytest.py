import pytest

# Test function to check if a number is even
def is_even(number):
    return number % 2 == 0

# Test cases
def test_is_even_with_even_number():
    assert is_even(4) == True

def test_is_even_with_odd_number():
    assert is_even(3) == False

def test_is_even_with_zero():
    assert is_even(0) == True