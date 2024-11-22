import unittest
from app import app
import werkzeug
from flask_jwt_extended import decode_token

# Patch temporário para adicionar o atributo '__version__' em werkzeug
if not hasattr(werkzeug, '__version__'):
    werkzeug.__version__ = "mock-version"

class APITestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Criação do cliente de teste
        cls.client = app.test_client()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "API is running"})

    def test_get_items(self):
        response = self.client.get('/items')
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json)
        self.assertEqual(response.json["items"], ["item1", "item2", "item3"])

    def test_login_and_decode_token(self):
        response = self.client.post('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

        # Decodifica o token JWT retornado dentro do contexto da aplicação
        access_token = response.json['access_token']
        with app.app_context():
            decoded_token = decode_token(access_token)
            print("Decoded Token:", decoded_token)  # Verifica o conteúdo do token
            self.assertIn('sub', decoded_token)  # Garante que 'sub' está no token
            self.assertEqual(decoded_token['sub'], 'user')

    def test_protected_with_valid_token(self):
        # Primeiro, obtemos um token válido
        login_response = self.client.post('/login')
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json['access_token']

        # Usamos o token para acessar a rota protegida
        response = self.client.get('/protected', headers={
            'Authorization': f'Bearer {access_token}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Protected route"})

    def test_protected_no_token(self):
        response = self.client.get('/protected')
        self.assertEqual(response.status_code, 401)

    def test_protected_with_invalid_token(self):
        response = self.client.get('/protected', headers={
            'Authorization': 'Bearer invalid_token'
        })
        self.assertEqual(response.status_code, 422)  # Token inválido gera erro de unprocessable entity

if __name__ == '__main__':
    unittest.main()
