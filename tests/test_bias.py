import unittest
from bjt_bias import validate, bias


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


class TestBiasCalculation(unittest.TestCase):
    def test_known_example_agreement(self):
        v = validate.validate_inputs(10, 10000, 5000, 1000, 500, 100, 0.7)
        res = bias.calculate_bias(**v)
        self.assertAlmostEqual(res["calc_a"]["IC"], res["calc_b"]["IC"], places=9)
        self.assertTrue(res["verification"]["agree"])
        self.assertIn("IC", res)
        self.assertIn("VCE", res)

    def test_cutoff_warning(self):
        v = validate.validate_inputs(1, 10000, 10000, 1000, 1000, 100, 0.9)
        res = bias.calculate_bias(**v)
        self.assertTrue(any("cutoff" in w.lower() for w in res["warnings"]))

    def test_saturation_warning(self):
        v = validate.validate_inputs(5, 1000, 10000, 100, 50, 100, 0.7)
        res = bias.calculate_bias(**v)
        self.assertTrue(any("saturation" in w.lower() for w in res["warnings"]))
