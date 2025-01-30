# [Pytest](https://realpython.com/pytest-python-testing/)

Pytest is a testing framework for Python that simplifies the process of writing and executing tests. pytest offers several advantages over unittest that ships with Python, such as less boilerplate code, more readable output, and a rich plugin ecosystem.

`pip install pytest`

## unittest vs pytest

```py
# test_with_unittest.py
from unittest import TestCase

class TryTesting(TestCase):
    def test_always_passes(self):
        self.assertTrue(True)

    def test_always_fails(self):
        self.assertTrue(False)
```
```py
# test_with_pytest.py
def test_always_passes():
    assert True

def test_always_fails():
    assert False
```

* You don’t have to deal with any imports or classes. All you need to do is include a function with the `test_` prefix

* Because you can use the `assert` keyword, you don’t need to learn or remember all the different `self.assert*` methods in unittest

> Tests should help to make your code more understandable. If the tests themselves are difficult to understand, then you may be in trouble!

## Pytest output

```
==================== test session starts ====================
platform win32 -- Python 3.11.9, pytest-8.3.4, pluggy-1.5.0
rootdir: C:\Users\my.user\GitHub\data-bbog-integration-fraude-tc
configfile: pyproject.toml
plugins: cov-6.0.0
collected 14 items

test\integration\test_example.py .                    [  7%]
test\system\test_example.py .                         [ 14%]
test\unit\backtesting\test_backtesting.py .           [ 21%]
test\unit\common\test_Lineage.py ...                  [ 42%]
test\unit\common\test_common_helper.py ...            [ 64%] 
test\unit\common\test_logger.py .                     [ 71%]
test\unit\common\test_path_helper.py .                [ 78%]
test\unit\preparation\test_preparation.py .           [ 85%]
test\unit\preparation\test_process_fraude.py .        [ 92%] 
test\unit\preparation\test_process_solicitudes.py .   [100%]
```

`$ pytest` run tests

`$ pytest -s` see prints and logs

`$ pytest test/unit/common/` run some tests

`$ pytest --cov=src` coverage

## Fixtures

Fixtures are special functions used to **set up** the necessary environment to run tests, and they can be reused across multiple tests. They are used to manage the preparation and cleanup of resources that a test might need, such as databases, temporary files, network connections, or simply initializing objects and values before tests.

These functions are defined using the `@pytest.fixture` decorator and are then injected into tests as parameters.

```py
import pytest

@pytest.fixture
def db_connection():
    return "Database connection"
    # yield

@pytest.fixture
def user_data():
    return {"user": "test", "password": "1234"}

def test_login(db_connection, user_data):
    assert db_connection == "Database connection"
    assert user_data["user"] == "test"
```

### Fixture Scope

The scope defines how long the fixture will remain available

* **function** (default): The fixture is created and destroyed for each test.
* **class**: The fixture is created once per test class.
* **module**: The fixture is created once per test module.
* **session**: The fixture is created once per entire pytest session.

```py
@pytest.fixture(scope="module")
```

### Autofixtures

Fixtures can also be automatic, meaning pytest will inject them into tests without you having to specify them explicitly.

```py
@pytest.fixture(autouse=True)
```

### conftest.py

conftest.py is a special configuration file in pytest that allows you to define fixtures, hooks, and other configurations that will be available throughout your entire project, without the need to import them into each individual test module.

## Marks

In pytest you can assign Marks to tests and run the tests that have the desired Mark. but the main use of Marks is to skip a test:

* **@pytest.mark.skip**: Skip a test unconditionally.
    ```py
    @pytest.mark.skip(reason="This test is skipped intentionally.")
    ```
* **@pytest.mark.skipif(condition)**: Skip a test based on a condition.
    ```py
    @pytest.mark.skipif(sys.platform == "win32", reason="Does not run on Windows.")
    ```
* **@pytest.mark.xfail**: Mark a test as expected to fail.
    ```py
    @pytest.mark.xfail(reason="Feature not yet implemented.")
    ```
* **pytest.skip()**: Skip a test from within the test body.
    ```py
    def test_skip_inside():
        if some_condition_is_met():
            pytest.skip("Skipping due to some condition.")
    ```

Marks are also useful to parametrize several tests

```py
@pytest.mark.parametrize("palindrome", ["","a","Bob","Never odd or even"])
def test_is_palindrome(palindrome):
    assert is_palindrome(palindrome)

@pytest.mark.parametrize("non_palindrome", ["abc","abab"])
def test_is_palindrome_not_palindrome(non_palindrome):
    assert not is_palindrome(non_palindrome)
```

## Plugins

There are plugins like pytest-randomly, pytest-bdd, pytest-cov, pytest-mock and others.

### pytest-cov

`$ pytest --cov=src --cov-report=term-missing`

```
Name                                     Stmts   Miss  Cover   Missing
----------------------------------------------------------------------
src\__init__.py                              0      0   100%
src\backtesting\backtesting.py              89     10    89%   43-44, 48, 91, 97-103, 111, 118, 122
src\common\AWSDynamo.py                     18      0   100%
src\common\Lineage.py                      153      8    95%   241-248
src\common\__init__.py                       0      0   100%
src\common\common_helper.py                 47      3    94%   41, 82-83
src\common\logger.py                        36      8    78%   48-56, 61
src\common\path_helper.py                   74      4    95%   39-41, 101
src\preparation\__init__.py                  0      0   100%
src\preparation\preparation.py              22      0   100%
src\preparation\process_fraude.py           15      0   100%
src\preparation\process_solicitudes.py      29      3    90%   17-19
----------------------------------------------------------------------
TOTAL                                      483     36    93%
```

* **Stmts**: The total number of executable statements in the file (functions, lines of code, etc.).
* **Miss**: The number of statements that were **not covered** by the tests.
* **Cover**: The percentage of statements that **were covered** by the tests.