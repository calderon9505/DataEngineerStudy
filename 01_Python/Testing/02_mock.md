# [Mock](https://realpython.com/python-mock-library/)

Cuando escribimos pruebas unitarias, generalmente queremos asegurarnos de que solo estamos probando el comportamiento de la unidad de código que nos interesa. Sin embargo, muchas veces esa unidad depende de otros componentes, como APIs o servicios, que no deberían ejecutarse o que son difíciles de manejar en un entorno de prueba. **Mock** permite crear objetos falsos (mock objects) que simulan el comportamiento de esos componentes dependientes,


```py
from unittest.mock import Mock
mock = Mock()
```

Un objeto Mock puede simular cualquier objeto que reemplaza, por lo que puede crear atributos y métodos *sobre la marcha*. 

```py
mock.some_attribute
mock.do_something()
```

el valor de retorno de estos atributos y métodos son otros objetos Mock

```py
>>> json = Mock()
>>> json
<Mock id='2253691730320'>
>>> json.dumps()
<Mock name='mock.dumps()' id='4392249776'>
>>> json.loads('{"k": "v"}').get("k")
<Mock name='mock.loads().get()' id='4379599424'>
```
## Assertions and Inspection

```py
from unittest.mock import Mock
json = Mock()
json.loads('{"key": "value"}')
# <Mock name='mock.loads()' id='4550144184'>

json.loads.assert_called()
json.loads.assert_called_once()
json.loads.assert_called_with('{"key": "value"}')
json.loads.assert_called_once_with('{"key": "value"}')

json.loads.call_count
json.loads.call_args  # The last loads() call
json.loads.call_args_list # List of loads() calls
json.method_calls
```

You can write tests using these attributes to make sure that your objects behave as you intended.

## Mock’s Return Value

Cuando utilizas un Mock, puedes definir qué valor debe devolver cuando se llama a un método o atributo específico.

```py
>>> mock_function = Mock(return_value="any_return_value")
>>> mock_function()
'any_return_value'

>>> mock_function = Mock()
>>> mock_function.get.return_value = "other_return_value"
>>> mock_function.get()
'other_return_value'
```

```py
from datetime import datetime
from unittest.mock import Mock

# Save a couple of test days
wednesday = datetime(year=2025, month=1, day=1)
sunday = datetime(year=2025, month=1, day=5)

# Mock datetime to control today's date
datetime = Mock()

def is_weekday():
    today = datetime.today()
    # Python's datetime library treats Monday as 0 and Sunday as 6
    return (0 <= today.weekday() < 5)

# Mock .today() to return Wednesday
datetime.today.return_value = wednesday
# Test Wednesday is a weekday
assert is_weekday()

# Mock .today() to return Sunday
datetime.today.return_value = sunday
# Test Sunday is not a weekday
assert not is_weekday()
```

> Though mocking datetime like this is a good practice example for using Mock, a fantastic library already exists for mocking datetime called **freezegun**.

si la función is_weekday() estuviera en otro archivo (`holidays.py`) y se importara en el archivo de test `test_holidays.py` de la forma `from holidays import is_weekday`, el test fallaría. The reason for this fail comes from how you mocked the datetime module in your test file. When you import a module in another module, the imported names are bound to that module’s namespace. Mocking datetime in your test file doesn’t affect datetime in is_weekday() because `holidays.py` has already imported the real datetime module.

To correctly mock datetime in holidays.py, you should patch datetime in the namespace where it’s used. The unittest.mock library’s patch() function is useful for this purpose. 

## Mock’s Side Effects

En lugar de simplemente devolver un valor fijo (como ocurre con `return_value`), `side_effect` permite definir un comportamiento dinámico para un mock.

Usos principales de `side_effect`:
* Ejecutar una función en lugar de devolver un valor fijo.

    Esto es util cuando necesitas controlar cómo se comporta un mock en función de las entradas.
    ```py
    def my_side_effect(*args, **kwargs):
        return args[0] * 2

    mock_function = Mock(side_effect=my_side_effect)
    ```

* Simular excepciones que podrían ser lanzadas por una función.

    ```py
    mock_function = Mock(side_effect=ValueError("¡Algo salió mal!"))
    ```

* Devolver valores diferentes en llamadas consecutivas.

    ```py
    mock_function = Mock(side_effect=[1, 2, 3])
    ```

Ejemplo de caso de uso en la vida real

```py
import unittest
from unittest.mock import Mock
from requests.exceptions import Timeout


class MyService:
    def __init__(self, api_client):
        self.api_client = api_client

    def get_data(self, endpoint):
        # Simula una consulta a la API
        response = self.api_client.get(endpoint)
        return response["data"]


class TestMyService(unittest.TestCase):
    def test_get_data(self):
        # Creamos un mock para el cliente de la API
        mock_api_client = Mock()

        # Definimos side_effect para devolver diferentes respuestas en cada llamada
        mock_api_client.get.side_effect = [
            {"data": "Response 1"},  # Primera llamada
            {"data": "Response 2"},  # Segunda llamada
            {"data": "Response 3"},  # Tercera llamada
        ]

        service = MyService(mock_api_client)

        # Realizamos varias llamadas y verificamos los resultados
        self.assertEqual(service.get_data("/endpoint1"), "Response 1")
        self.assertEqual(service.get_data("/endpoint2"), "Response 2")
        self.assertEqual(service.get_data("/endpoint3"), "Response 3")

    def test_get_data_timeout(self):
        # Creamos un mock para el cliente de la API
        mock_api_client = Mock()

        # Simulamos un Timeout
        mock_api_client.get.side_effect = Timeout  # Lanza una excepción Timeout

        service = MyService(mock_api_client)

        # Llamamos a la función y verificamos que maneja el timeout correctamente
        with self.assertRaises(Timeout):
            service.get_data("/endpoint_timeout")


if __name__ == "__main__":
    unittest.main()
```

## The patch() Function

`patch()` looks up an object in a given module and replaces that object with a Mock.

```py
# holidays.py
from datetime import datetime

import requests

def is_weekday():
    today = datetime.today()
    # Python's datetime library treats Monday as 0 and Sunday as 6
    return (0 <= today.weekday() < 5)

def get_holidays():
    r = requests.get("http://localhost/api/holidays")
    if r.status_code == 200:
        return r.json()
    return None
```

### patch() as a Decorator

```py
# test_holidays.py
import unittest
from unittest.mock import patch

from requests.exceptions import Timeout

from holidays import get_holidays

class TestHolidays(unittest.TestCase):
    @patch("holidays.requests")
    def test_get_holidays_timeout(self, mock_requests):
        mock_requests.get.side_effect = Timeout
        with self.assertRaises(Timeout):
            get_holidays()
            mock_requests.get.assert_called_once()

if __name__ == "__main__":
    unittest.main()
```

### patch() as a Context Manager

Use patch as a Context Manager when you only want to mock an object for a part of the test scope.

```py
# test_holidays.py
import unittest
from unittest.mock import patch

from requests.exceptions import Timeout

from holidays import get_holidays

class TestHolidays(unittest.TestCase):
    def test_get_holidays_timeout(self):
        with patch("holidays.requests") as mock_requests:
            mock_requests.get.side_effect = Timeout
            with self.assertRaises(Timeout):
                get_holidays()
                mock_requests.get.assert_called_once()

if __name__ == "__main__":
    unittest.main()
```

### Patching an Object’s Attributes

If you only want to mock one method of an object instead of the entire object, you can do so by using `patch.object()`.

```py
# test_holidays.py
import unittest
from unittest.mock import patch

from holidays import get_holidays
import requests

class TestHolidays(unittest.TestCase):
    @patch.object(requests, "get", side_effect=requests.exceptions.Timeout)
    def test_get_holidays_timeout(self, mock_requests):
        with self.assertRaises(requests.exceptions.Timeout):
            get_holidays()

if __name__ == "__main__":
    unittest.main()
```

> `patch` y `patch.object` pueden llegar a ser intercambiables en algunos casos, como el ejemplo mostrado. Pero si se intenta parchear un atributo de un objeto específico, solo se puede usar `patch.object`

```py
class MiClase:
    def __init__(self):
        self.datos = "valor real"

    def obtener_datos(self):
        return self.datos

def test_mi_clase():
    mi_objeto = MiClase()
    
    # Usamos patch.object para parchear el atributo 'datos' de esa instancia
    with patch.object(mi_objeto, 'datos', 'valor mockeado'):
        assert mi_objeto.obtener_datos() == 'valor mockeado'

```

> you can also patch dictionaries with `patch.dict()`. The principal aplication is with environment variables.

## Knowing Where to Patch

```py
>>> import holidays
>>> from unittest.mock import patch

>>> with patch("holidays.is_weekday"):
...     holidays.is_weekday()
...
<MagicMock name='is_weekday()' id='4336501256'>
```
```py
>>> from holidays import is_weekday
>>> from unittest.mock import patch

>>> with patch("holidays.is_weekday"):
...     is_weekday()
...
True
```

Notice that even though the target location you passed to `patch()` didn’t change, the result of calling `is_weekday()` is different. The difference comes from the change in how you imported the function.

When you use `from holidays import is_weekday`, you bind the `is_weekday()` to the local scope. So, even though you patch the function later, you ignore the mock because you already have a local reference to the unmocked function.

A good rule of thumb is to patch() the object where it’s looked up.