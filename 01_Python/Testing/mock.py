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
