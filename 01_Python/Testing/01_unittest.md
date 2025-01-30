# [Testing Your Python Code with unittest](https://realpython.com/python-unittest/)

The unittest framework is directly available in the standard library, so you don’t have to install anything to use this tool.

concepts:
* **Test case**: An individual unit of testing. It examines the output for a given input set.
* **Test suite**: A collection of test cases, test suites, or both. They’re grouped and executed as a whole.
* **Test fixture**: A group of actions required to set up an environment for testing. It also includes the teardown processes after the tests run.
* **Test runner**: A component that handles the execution of tests and communicates the results to the user.

> your tests methods, classes and files should begin with `test` word to take advantage of the default test discovery configuration.

## TestCase Class

```py
# age.py
def categorize_by_age(age):
    if 0 <= age <= 9:
        return "Child"
    elif 9 < age <= 18:
        return "Adolescent"
    elif 18 < age <= 65:
        return "Adult"
    elif 65 < age <= 150:
        return "Golden age"
    else:
        return f"Invalid age: {age}"
```
```py
# test_age.py
import unittest

from age import categorize_by_age

class TestCategorizeByAge(unittest.TestCase):
    def test_child(self):
        self.assertEqual(categorize_by_age(5), "Child")

    def test_adolescent(self):
        self.assertEqual(categorize_by_age(15), "Adolescent")

    def test_adult(self):
        self.assertEqual(categorize_by_age(30), "Adult")

    def test_golden_age(self):
        self.assertEqual(categorize_by_age(70), "Golden age")

    def test_negative_age(self):
        self.assertEqual(categorize_by_age(-1), "Invalid age: -1")

    def test_too_old(self):
        self.assertEqual(categorize_by_age(151), "Invalid age: 151")
    
    def test_boundary_child_adolescent(self):
        self.assertEqual(categorize_by_age(9), "Child")
        self.assertEqual(categorize_by_age(10), "Adolescent")

    def test_boundary_adolescent_adult(self):
        self.assertEqual(categorize_by_age(18), "Adolescent")
        self.assertEqual(categorize_by_age(19), "Adult")

    def test_boundary_adult_golden_age(self):
        self.assertEqual(categorize_by_age(65), "Adult")
        self.assertEqual(categorize_by_age(66), "Golden age")


if __name__ == "__main__":
    unittest.main()
```

> .assertEqual() method inheriths from TestCase

> The `main()` function from unittest allows you to load and run a set of tests `$ python test_age.py`

## Skipping Tests

se usan decoradores para saltarse los test

```py
import sys
import unittest

class SkipTestExample(unittest.TestCase):
    @unittest.skip("Unconditionally skipped test")
    def test_unimportant(self):
        self.fail("The test should be skipped")

    @unittest.skipIf(sys.version_info < (3, 12), "Requires Python >= 3.12")
    def test_using_calendar_constants(self):
        import calendar

        self.assertEqual(calendar.Month(10), calendar.OCTOBER)

    @unittest.skipUnless(sys.platform.startswith("win"), "Requires Windows")
    def test_windows_support(self):
        from ctypes import WinDLL, windll

        self.assertIsInstance(windll.kernel32, WinDLL)
```

## SubTests

similar tests using the `subTest()` context manager

```py
# even.py
def is_even(number):
    return number % 2 == 0
```
```py
import unittest

from even import is_even

class TestIsEven(unittest.TestCase):
    def test_even_number(self):
        for number in [2, 4, 6, -8, -10, -12]:
            with self.subTest(number=number):
                self.assertEqual(is_even(number), True)

    def test_odd_number(self):
        for number in [1, 3, 5, -7, -9, -11]:
            with self.subTest(number=number):
                self.assertEqual(is_even(number), False)

if __name__ == "__main__":
    unittest.main(verbosity=2)
```

## Assert methods

The **TestCase** class provides a set of assert methods.

### Comparing Values.
* .assertEqual(a, b)
* .assertNotEqual(a, b)
* .assertTrue(x)
* .assertFalse(x)

### Comparing Objects by Their Identity
an object’s identity is the memory address where the object lives.
This identity is a unique identifier that distinguishes one object from another.
* .assertIs(a, b)
* .assertIsNot(a, b)
* .assertIsNone(x)
* .assertIsNotNone(x)

### Comparing Collections
compare lists, tuples, strings, dictionaries, and sets.
these compare the values of objects rather than their identities.
* .assertSequenceEqual(a, b)	Equality of two sequences
* .assertMultiLineEqual(a, b)	Equality of two strings
* .assertListEqual(a, b)	Equality of two lists
* .assertTupleEqual(a, b)	Equality of two tuples
* .assertDictEqual(a, b)	Equality of two dictionaries
* .assertSetEqual(a, b)   Equality of two sets

> The .assertEqual() method automatically calls the specialized methods in the table above. So, in most cases, you won’t need to call these methods directly. Instead, you can just use .assertEqual(). However, you can use the specialized methods to add extra clarity to your tests and improve readability.

### Running Membership Tests
* .assertIn(a, b)
* .assertNotIn(a, b)

### Checking for an Object’s Type
* .assertIsInstance(a, b)
* .assertNotIsInstance(a, b)

### Testing for Exceptions, Warnings and Logs
it require use a `with` context 
`with self.assertRaises(TypeError):` 
warnings are a special category of exceptions

* .assertRaises(exc, fun, *args, **kwds)
* .assertRaisesRegex(exc, r, fun, *args, **kwds)
* .assertWarns(warn, fun, *args, **kwds)
* .assertWarnsRegex(warn, r, fun, *args, **kwds)
* .assertLogs(logger, level)
* .assertNoLogs(logger, level)

> it is possible to create custrom Assert Methods. Read the doc for more.

## Running Tests

```sh
$ python -m unittest test_age
$ python -m unittest test_age.TestCategorizeByAge
$ python -m unittest test_age.TestCategorizeByAge.test_child
```

## Test Fixtures

A test fixture is a **preparation** that you perform before and after running one or more tests. The preparations before the test run are known as **setup**, while the tasks that you perform after the test run are called **teardown**.

| Method | Description
| - | - |
.setUp() | An instance method that unittest calls before running each test method in a test case class.
.tearDown() | An instance method that unittest calls after running each test method in a test case class.
.setUpClass() | A class method that unittest calls before running the tests in a test case class.
.tearDownClass() | A class method that unittest calls after running the tests in a test case class.

```py
import unittest

from stack import Stack

class TestStack(unittest.TestCase):
    def setUp(self):
        self.stack = Stack()

    def tearDown(self):
        del self.stack

    def test_push(self):
        self.stack.push(1)
        self.assertEqual(self.stack.items, [1])

    def test_pop(self):
        self.stack.push(2)
        item = self.stack.pop()
        self.assertEqual(item, 2)
```
