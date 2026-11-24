"""Tests for the ngspice adapter (Lab 06).

The binary is slow/external, so unit tests use canned output captured from
ngspice-47.  One integration test runs the real binary when available.
"""

import math
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import spice_engine as se

OP_OUTPUT = """Circuit: * ce voltage divider amplifier

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

No. of Data Rows : 1
\tNode                                  Voltage
\t----                                  -------
\t----\t-------
\tvout                             0.000000e+00
\te                                1.241200e+00
\tc                                9.298100e+00
\tb                                1.941200e+00
\tvin                              0.000000e+00
\tvcc                              1.200000e+01

\tSource\tCurrent
\t------\t-------

\tvcc#branch                       -1.24200e-03
"""

AC_OUTPUT = """Circuit: * ce ac

Index   frequency       vdb(vout)       vp(vout)
--------------------------------------------------------------------------------
0\t1.000000e+00\t-4.26310e+01\t-1.42126e+00
1\t1.000000e+01\t-3.90000e+01\t-2.00000e+00
2\t1.000000e+02\t-3.51436e+01\t-3.10000e+00
3\t1.000000e+03\t-3.51436e+01\t-3.14159e+00
4\t1.000000e+04\t-3.51436e+01\t-3.14159e+00
5\t1.000000e+05\t-3.90000e+01\t-2.00000e+00
6\t1.000000e+06\t-4.26310e+01\t-1.42126e+00

Index   frequency       vdb(vin)
--------------------------------------------------------------------------------
0\t1.000000e+00\t-4.00000e+01
1\t1.000000e+01\t-4.00000e+01
2\t1.000000e+02\t-4.00000e+01
3\t1.000000e+03\t-4.00000e+01
4\t1.000000e+04\t-4.00000e+01
5\t1.000000e+05\t-4.00000e+01
6\t1.000000e+06\t-4.00000e+01
"""

TRAN_OUTPUT = """Circuit: * ce tran

Index   time            v(vin)          v(vout)
--------------------------------------------------------------------------------
0\t0.000000e+00\t0.000000e+00\t0.000000e+00
1\t1.000000e-04\t1.000000e-02\t-1.766000e-02
2\t2.000000e-04\t0.000000e+00\t0.000000e+00
3\t3.000000e-04\t-1.000000e-02\t1.766000e-02
4\t4.000000e-04\t0.000000e+00\t0.000000e+00
"""

DIVIDER = {
    "VCC": 12.0, "R1": 100000.0, "R2": 22000.0,
    "RC": 2200.0, "RE": 1000.0,
}
CE_DEFAULTS = {
    "RL": 10000.0, "CIN": 10e-6, "COUT": 10e-6,
    "SOURCE_V": 10e-3, "SOURCE_F": 1000.0,
}


class TestThermalAndModel(unittest.TestCase):
    def test_thermal_voltage_at_27c(self):
        # VT = kT/q at 300.15 K, hand-computed from the SI constants
        expected = 1.380649e-23 * 300.15 / 1.602176634e-19
        self.assertAlmostEqual(se.thermal_voltage(), expected, places=12)

    def test_saturation_current_matches_constant_vbe_model(self):
        # IS chosen so the exponential model gives ic exactly at vbe
        ic, vbe = 1.229858e-3, 0.70
        vt = se.thermal_voltage()
        is_expected = ic / math.exp(vbe / vt)
        self.assertAlmostEqual(se.saturation_current(ic, vbe), is_expected, delta=1e-20)


class TestNetlist(unittest.TestCase):
    def test_operating_netlist_divider_has_all_five_resistors(self):
        netlist = se.build_netlist("op", DIVIDER, 100, 0.70, 1.229858e-3)
        self.assertIn("VCC VCC 0 12", netlist)
        self.assertIn("R1 VCC B 100000", netlist)
        self.assertIn("R2 B 0 22000", netlist)
        self.assertIn("RC VCC C 2200", netlist)
        self.assertIn("RE E 0 1000", netlist)
        self.assertIn("Q1 C B E QNPN", netlist)
        self.assertIn("BF=100", netlist)
        self.assertIn("CJC=10pF", netlist)
        self.assertIn("CJE=20pF", netlist)
        self.assertIn("TF=0.5ns", netlist)
        self.assertIn(".op", netlist)
        self.assertTrue(netlist.rstrip().endswith(".end"))

    def test_operating_netlist_fixed_uses_grounded_emitter(self):
        values = {"VCC": 12.0, "RB": 1000000.0, "RC": 2200.0}
        netlist = se.build_netlist("op", values, 100, 0.70, 1.13e-3, mode="fixed")
        self.assertIn("RB VCC B 1e+06", netlist)
        self.assertIn("Q1 C B 0 QNPN", netlist)
        self.assertNotIn("R1 VCC B", netlist)

    def test_ac_netlist_has_coupling_caps_load_and_ac_source(self):
        netlist = se.build_netlist("ac", {**DIVIDER, **CE_DEFAULTS}, 100, 0.70, 1.229858e-3)
        self.assertIn("CIN VIN B 1e-05", netlist)
        self.assertIn("COUT C VOUT 1e-05", netlist)
        self.assertIn("RL VOUT 0 10000", netlist)
        self.assertIn("AC 0.01 0", netlist)
        self.assertIn(".ac dec 20 1 1e+09", netlist)
        self.assertIn(".print ac vdb(vout) vdb(vin)", netlist)

    def test_tran_netlist_uses_sine_source_and_positive_tstep(self):
        netlist = se.build_netlist("tran", {**DIVIDER, **CE_DEFAULTS}, 100, 0.70, 1.229858e-3)
        self.assertIn("SIN(0 0.01 1000)", netlist)
        self.assertIn(".tran 1e-06 0.005", netlist)
        self.assertIn(".print tran v(vin) v(vout)", netlist)


class TestParsers(unittest.TestCase):
    def test_parse_operating_point_reads_node_table(self):
        op = se.parse_operating_point(OP_OUTPUT)
        self.assertAlmostEqual(op["VB"], 1.9412)
        self.assertAlmostEqual(op["VE"], 1.2412)
        self.assertAlmostEqual(op["VC"], 9.2981)
        self.assertAlmostEqual(op["VCC"], 12.0)

    def test_parse_operating_point_reads_colon_format(self):
        text = "V(vcc): 1.2e+01 voltage\nV(b): 7.000000e-01 voltage\nV(c): 9.514000e+00 voltage\nV(e): 0 voltage\n"
        op = se.parse_operating_point(text)
        self.assertAlmostEqual(op["VB"], 0.7)
        self.assertAlmostEqual(op["VC"], 9.514)
        self.assertAlmostEqual(op["VE"], 0.0)

    def test_parse_operating_point_rejects_output_without_nodes(self):
        with self.assertRaises(se.NgspiceError):
            se.parse_operating_point("Error: no such node\n")

    def test_parse_ac_merges_vout_and_vin_tables_by_frequency(self):
        rows = se.parse_ac(AC_OUTPUT)
        self.assertEqual(len(rows), 7)
        self.assertAlmostEqual(rows[0]["freq"], 1.0)
        self.assertAlmostEqual(rows[0]["vout_db"], -42.6310)
        self.assertAlmostEqual(rows[0]["vin_db"], -40.0)
        self.assertAlmostEqual(rows[3]["vout_db"], -35.1436)

    def test_parse_ac_reads_combined_ngspice_table(self):
        # Real ngspice-47 prints both traces on one line per frequency.
        combined = (
            "Index   frequency       vdb(vout)       vdb(vin)        \n"
            "---------------------------------------------------------\n"
            "0\t1.000000e+00\t-4.26314e+01\t-4.00000e+01\t\n"
            "1\t1.000000e+01\t-3.90000e+01\t-4.00000e+01\t\n"
        )
        rows = se.parse_ac(combined)
        self.assertEqual(len(rows), 2)
        self.assertAlmostEqual(rows[0]["vout_db"], -42.6314)
        self.assertAlmostEqual(rows[0]["vin_db"], -40.0)
        self.assertAlmostEqual(rows[1]["vout_db"], -39.0)

    def test_parse_transient_reads_time_and_voltages(self):
        rows = se.parse_transient(TRAN_OUTPUT)
        self.assertEqual(len(rows), 5)
        self.assertAlmostEqual(rows[3]["time"], 3e-4)
        self.assertAlmostEqual(rows[3]["vin"], -0.01)
        self.assertAlmostEqual(rows[3]["vout"], 0.01766)


class TestSimulate(unittest.TestCase):
    def test_op_simulation_derives_currents_from_node_voltages(self):
        with patch.object(se, "run", return_value=OP_OUTPUT):
            result = se.simulate_operating_point("divider", DIVIDER, 100, 0.70, 1.229858e-3)
        # IC = (12 - 9.2981)/2200 = 1.22818 mA
        self.assertAlmostEqual(result["IC"], (12 - 9.2981) / 2200, places=9)
        # IB = (12 - 1.9412)/100k - 1.9412/22k = 19.073 uA
        ib = (12 - 1.9412) / 100000 - 1.9412 / 22000
        self.assertAlmostEqual(result["IB"], ib, places=9)
        self.assertAlmostEqual(result["IE"], result["IC"] + result["IB"], places=9)
        self.assertAlmostEqual(result["VCE"], 9.2981 - 1.2412, places=9)
        self.assertEqual(result["source"], "ngspice")

    def test_ac_simulation_computes_gain_and_cutoff_frequencies(self):
        with patch.object(se, "run", return_value=AC_OUTPUT):
            result = se.simulate_ac({**DIVIDER, **CE_DEFAULTS}, 100, 0.70, 1.229858e-3)
        # midband gain: -35.1436 dBV out - (-40 dBV in) = +4.8564 dB => 1.7517
        self.assertAlmostEqual(result["midband_gain"], 10 ** (4.8564 / 20), places=3)
        # -3 dB threshold is 4.8564 - 3.0103 = 1.8461 dB.  Interpolating in
        # log-frequency between the sweep points gives ~17 Hz / ~58.9 kHz,
        # not simply the first/last in-band sample (100 Hz / 10 kHz).
        self.assertAlmostEqual(result["f_low"], 16.96, delta=0.5)
        self.assertAlmostEqual(result["f_high"], 58900.0, delta=1500.0)

    def test_tran_simulation_computes_peak_to_peak(self):
        with patch.object(se, "run", return_value=TRAN_OUTPUT):
            result = se.simulate_transient({**DIVIDER, **CE_DEFAULTS}, 100, 0.70, 1.229858e-3)
        self.assertAlmostEqual(result["vin_pp"], 0.02, places=9)
        self.assertAlmostEqual(result["vout_pp"], 0.03532, places=9)
        self.assertAlmostEqual(result["gain"], 0.03532 / 0.02, places=9)

    def test_missing_executable_raises_unavailable(self):
        with patch.object(se, "find_executable", return_value=None):
            with self.assertRaises(se.NgspiceUnavailable):
                se.run("*.end\n")


@unittest.skipUnless(
    shutil.which("ngspice_con") or os.environ.get("NGSPICE_EXECUTABLE")
    or Path(r"C:\Users\B6810177\AppData\Local\Temp\opencode\ngspice47\Spice64\bin\ngspice_con.exe").exists(),
    "ngspice binary not available",
)
class TestRealNgspice(unittest.TestCase):
    def test_real_operating_point_matches_analytical_within_5_percent(self):
        from dc_bias import calculate_bias

        expected = calculate_bias(12.0, 100000.0, 22000.0, 2200.0, 1000.0, 100.0, 0.70)
        result = se.simulate_operating_point("divider", DIVIDER, 100, 0.70, expected["IC"])
        self.assertLess(abs(result["IC"] - expected["IC"]) / expected["IC"], 0.05)
        self.assertLess(abs(result["VCE"] - expected["VCE"]) / expected["VCE"], 0.05)

    def test_real_ac_sweep_finds_a_high_frequency_corner(self):
        values = {**DIVIDER, **CE_DEFAULTS}
        result = se.simulate_ac(values, 100, 0.70, 1.229858e-3)
        self.assertGreater(result["midband_gain"], 1.0)
        self.assertLess(result["f_low"], 100.0)
        self.assertGreater(result["f_high"], 1e6)
        self.assertLess(result["f_high"], 1e9)


if __name__ == "__main__":
    unittest.main()
