import os
import sys
import unittest
sys.path.append("../")
from project import app


class UnitTests(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('PROJECT_SQLALCHEMY_DATABASE')
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    def test_index_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_login_user(self):
        response = self.app.post(
            '/login',
            data=dict(email="farhaan@gmail.com", password="farees"))
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
