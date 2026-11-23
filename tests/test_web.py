import unittest

from app import app

VALID_KOHM = {
    'VCC': '12', 'R1': '100', 'R2': '22', 'RC': '2.2', 'RE': '1',
    'beta': '100', 'VBE': '0.7', 'unit': 'kohm',
}
VALID_OHM = {
    'VCC': '12', 'R1': '100000', 'R2': '22000', 'RC': '2200', 'RE': '1000',
    'beta': '100', 'VBE': '0.7', 'unit': 'ohm',
}


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_form(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'name="VCC"', r.data)
        # ค่าที่กรอกต้องเริ่มจากช่องว่าง ไม่ pre-fill ตัวเลข
        self.assertNotIn(b'value="12"', r.data)
        self.assertNotIn(b'value="100"', r.data)

    def test_post_empty_shows_error(self):
        r = self.client.post('/', data={'unit': 'kohm'})
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'alert-error', r.data)
        self.assertIn(b'must be a finite number', r.data)

    def test_layout_order_circuit_form_results(self):
        r = self.client.get('/')
        html = r.data.decode('utf-8')
        # วงจรอยู่บนสุด ตามด้วยฟอร์มป้อนข้อมูล และผลลัพธ์อยู่ล่างสุด
        self.assertLess(html.index('Voltage-Divider Bias'), html.index('id="input"'))
        self.assertLess(html.index('id="input"'), html.index('id="results"'))

    def test_post_valid(self):
        r = self.client.post('/', data=VALID_OHM)
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'DC Operating Point', r.data)
        self.assertIn(b'Forward Active', r.data)
        # VCE = 8.052 V, IC = 1.230 mA from the reference example
        self.assertIn(b'8.052', r.data)
        self.assertIn(b'1.230', r.data)

    def test_kohm_unit_conversion_matches_ohm(self):
        r_kohm = self.client.post('/', data=VALID_KOHM)
        r_ohm = self.client.post('/', data=VALID_OHM)
        self.assertIn(b'8.052', r_kohm.data)
        self.assertIn(b'8.052', r_ohm.data)

    def test_post_accepts_thousands_separators(self):
        r = self.client.post('/', data={
            'VCC': '12', 'R1': '100,000', 'R2': '22,000', 'RC': '2,200',
            'RE': '1,000', 'beta': '100', 'VBE': '0.7', 'unit': 'ohm',
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'8.052', r.data)

    def test_post_invalid(self):
        r = self.client.post('/', data={
            'VCC': '10', 'R1': '-1', 'R2': '5000', 'RC': '1000', 'RE': '500',
            'beta': '100', 'VBE': '0.7', 'unit': 'ohm',
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'alert-error', r.data)
        self.assertNotIn(b'class="metrics"', r.data)


if __name__ == '__main__':
    unittest.main()
