import unittest
from electrical import analyze_dc, equivalent_resistance


class TestDCAnalyzer(unittest.TestCase):
    def test_known_values(self):
        result = analyze_dc(12, 6)
        self.assertAlmostEqual(result["current_a"], 2.0)
        self.assertAlmostEqual(result["power_w"], 24.0)

    def test_zero_voltage(self):
        result = analyze_dc(0, 10)
        self.assertAlmostEqual(result["current_a"], 0.0)
        self.assertAlmostEqual(result["power_w"], 0.0)

    def test_series_resistance(self):
        self.assertAlmostEqual(equivalent_resistance({"series": [6, 6]}), 12.0)

    def test_parallel_resistance(self):
        self.assertAlmostEqual(equivalent_resistance({"parallel": [6, 6]}), 3.0)

    def test_mixed_resistance(self):
        network = {"series": [10, {"parallel": [20, 30]}]}
        self.assertAlmostEqual(equivalent_resistance(network), 22.0)

    def test_zero_resistance_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze_dc(12, 0)

    def test_negative_resistance_is_rejected(self):
        with self.assertRaises(ValueError):
            analyze_dc(12, -6)


if __name__ == "__main__":
    unittest.main()
