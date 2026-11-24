"""HTTP-level tests for Lab 06 analysis selection and ngspice comparison."""

import unittest
from unittest.mock import patch

import spice_engine as se
from app import app

BASE = {
    "VCC": "12", "R1": "100", "R2": "22", "RC": "2.2", "RE": "1",
    "beta": "100", "VBE": "0.7", "unit": "kohm",
    "RL": "10", "CIN": "10", "COUT": "10",
    "SOURCE_V": "10", "SOURCE_F": "1000",
}

OP_OUT = """Node                                  Voltage
vout                             0.000000e+00
e                                1.245198e+00
c                                9.287688e+00
b                                1.941614e+00
vcc                              1.200000e+01
"""

AC_OUT = """Index   frequency       vdb(vout)       vp(vout)
0\t1.000000e+00\t-4.26310e+01\t-1.42126e+00
1\t1.000000e+02\t-3.51436e+01\t-3.10000e+00
2\t1.000000e+03\t-3.51436e+01\t-3.14159e+00
3\t1.000000e+04\t-3.51436e+01\t-3.14159e+00
4\t1.000000e+06\t-4.26310e+01\t-1.42126e+00

Index   frequency       vdb(vin)
0\t1.000000e+00\t-4.00000e+01
1\t1.000000e+02\t-4.00000e+01
2\t1.000000e+03\t-4.00000e+01
3\t1.000000e+04\t-4.00000e+01
4\t1.000000e+06\t-4.00000e+01
"""

TRAN_OUT = """Index   time            v(vin)          v(vout)
0\t0.000000e+00\t0.000000e+00\t0.000000e+00
1\t1.000000e-04\t1.000000e-02\t-1.766000e-02
2\t2.000000e-04\t0.000000e+00\t0.000000e+00
3\t3.000000e-04\t-1.000000e-02\t1.766000e-02
4\t4.000000e-04\t0.000000e+00\t0.000000e+00
"""


class TestSpiceWeb(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_form_exposes_analysis_selector_compare_and_ce_inputs(self):
        html = self.client.get("/").data.decode("utf-8")
        self.assertIn('name="analysis"', html)
        for option in ('value="dc"', 'value="ac"', 'value="tran"'):
            self.assertIn(option, html)
        self.assertIn('name="compare"', html)
        self.assertIn('name="RL"', html)
        self.assertIn('name="CIN"', html)
        self.assertIn('name="SOURCE_F"', html)

    def test_baseline_action_prefills_reference_values(self):
        html = self.client.post("/", data={"action": "baseline"}).data.decode("utf-8")
        self.assertIn('value="12"', html)
        self.assertIn('value="100"', html)
        self.assertIn('value="22"', html)
        self.assertIn('value="10"', html)
        self.assertNotIn('class="metrics"', html)

    def test_dc_comparison_shows_both_sources(self):
        data = {**BASE, "analysis": "dc", "compare": "1"}
        with patch.object(se, "run", return_value=OP_OUT):
            html = self.client.post("/", data=data).data.decode("utf-8")
        self.assertIn("NGSPICE COMPARISON", html)
        self.assertIn("DC Operating Point", html)
        self.assertIn("1.229858", html)  # analytical IC, mA
        self.assertIn("1.232869", html)  # ngspice IC = (12 - 9.287688)/2.2k, mA
        self.assertIn("ngspice", html)

    def test_missing_ngspice_degrades_to_analytical_only(self):
        data = {**BASE, "analysis": "dc", "compare": "1"}
        with patch.object(se, "run", side_effect=se.NgspiceUnavailable("ngspice not found")):
            html = self.client.post("/", data=data).data.decode("utf-8")
        self.assertEqual(self.client.post("/", data={**BASE, "unit": "kohm"}).status_code, 200)
        self.assertIn("ngspice not found", html)
        self.assertIn("1.230", html)
        self.assertNotIn("NGSPICE COMPARISON", html)

    def test_ac_analysis_shows_gain_corners_and_chart(self):
        data = {**BASE, "analysis": "ac", "compare": "1"}
        with patch.object(se, "run", return_value=AC_OUT):
            html = self.client.post("/", data=data).data.decode("utf-8")
        self.assertIn("AC Small-Signal", html)
        self.assertIn('id="ac-chart"', html)
        self.assertIn("fL", html)
        self.assertIn("fH", html)
        self.assertIn("1.749", html)  # midband gain from canned AC sweep

    def test_tran_analysis_shows_waveform_chart(self):
        data = {**BASE, "analysis": "tran", "compare": "1"}
        with patch.object(se, "run", return_value=TRAN_OUT):
            html = self.client.post("/", data=data).data.decode("utf-8")
        self.assertIn("Transient", html)
        self.assertIn('id="tran-chart"', html)
        self.assertIn("35.32", html)  # Vout peak-to-peak in mV

    def test_invalid_capacitor_is_rejected(self):
        data = {**BASE, "analysis": "ac", "compare": "1", "CIN": "0"}
        html = self.client.post("/", data=data).data.decode("utf-8")
        self.assertIn("CIN must be greater than 0", html)

    def test_comparison_is_opt_in(self):
        html = self.client.post("/", data=BASE).data.decode("utf-8")
        self.assertNotIn("NGSPICE COMPARISON", html)
        self.assertIn("1.230", html)

    def test_ac_chart_appears_without_compare(self):
        data = {**BASE, "analysis": "ac"}
        with patch.object(se, "run", return_value=AC_OUT):
            html = self.client.post("/", data=data).data.decode("utf-8")
        self.assertIn('id="ac-chart"', html)
        self.assertIn("midband", html)
        self.assertNotIn("comparison-table", html)

    def test_tran_chart_appears_without_compare(self):
        data = {**BASE, "analysis": "tran"}
        with patch.object(se, "run", return_value=TRAN_OUT):
            html = self.client.post("/", data=data).data.decode("utf-8")
        self.assertIn('id="tran-chart"', html)
        self.assertIn("p-p", html)
        self.assertNotIn("comparison-table", html)


if __name__ == "__main__":
    unittest.main()
