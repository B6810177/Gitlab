import unittest
from app import app


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_form(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)

    def test_post_valid(self):
        r = self.client.post('/', data={
            'VCC': '10', 'R1': '10000', 'R2': '5000', 'RC': '1000', 'RE': '500', 'beta': '100', 'VBE': '0.7'
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'I_C', r.data)

    def test_post_invalid(self):
        r = self.client.post('/', data={
            'VCC': '10', 'R1': '-1', 'R2': '5000', 'RC': '1000', 'RE': '500', 'beta': '100', 'VBE': '0.7'
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'error', r.data.lower())
