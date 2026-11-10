import unittest
from bjt_bias import validate


class TestValidation(unittest.TestCase):
    def test_reject_bool(self):
        with self.assertRaises(ValueError):
            validate.validate_inputs(True, 1, 1, 1, 1, 100, 0.7)

    def test_reject_negative_resistance(self):
        with self.assertRaises(ValueError):
            validate.validate_inputs(10, -1, 1, 1, 1, 100, 0.7)

    def test_reject_zero_vcc(self):
        with self.assertRaises(ValueError):
            validate.validate_inputs(0, 1, 1, 1, 1, 100, 0.7)

    def test_reject_bad_vbe_range(self):
        with self.assertRaises(ValueError):
            validate.validate_inputs(10, 1, 1, 1, 1, 100, 0.3)
        with self.assertRaises(ValueError):
            validate.validate_inputs(10, 1, 1, 1, 1, 100, 10)
