"""ngspice adapter for the CE voltage-divider amplifier (Lab 06).

This module knows nothing about Flask or HTML.  It builds a netlist, runs the
ngspice executable in batch mode and parses the printed output into plain
Python dictionaries.  The engineering model used by Lab 2/3 (``dc_bias``)
stays the independent reference — this module only supplies the simulator
side of the comparison.

Units at the public boundary are SI: ohms, farads, volts, hertz, amperes.
"""

import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

K_B = 1.380649e-23  # Boltzmann constant, J/K
Q_E = 1.602176634e-19  # elementary charge, C
DEFAULT_TEMPERATURE_C = 27.0

ANALYSES = ("op", "ac", "tran")
_OP_MODES = ("divider", "fixed", "emitter")
_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
_NODE_KEYS = {
    "vcc": "VCC", "vin": "VIN", "vout": "VOUT",
    "b": "VB", "c": "VC", "e": "VE",
}


class NgspiceError(RuntimeError):
    """ngspice failed to run or produced output the adapter cannot read."""


class NgspiceUnavailable(NgspiceError):
    """No ngspice executable could be found."""


def thermal_voltage(temp_c=DEFAULT_TEMPERATURE_C):
    """VT = kT/q in volts at the given temperature in degrees Celsius."""
    return K_B * (temp_c + 273.15) / Q_E


def saturation_current(ic, vbe, temp_c=DEFAULT_TEMPERATURE_C):
    """IS that makes the exponential BJT model pass through (VBE, IC)."""
    return ic / math.exp(vbe / thermal_voltage(temp_c))


def find_executable():
    """Locate ngspice: env override, PATH, then common Windows install dirs."""
    candidates = [
        os.environ.get("NGSPICE_EXECUTABLE"),
        shutil.which("ngspice_con"),
        shutil.which("ngspice"),
        r"C:\Program Files\ngspice\Spice64\bin\ngspice_con.exe",
        r"C:\Program Files (x86)\ngspice\Spice64\bin\ngspice_con.exe",
        str(Path.home() / "ngspice47" / "Spice64" / "bin" / "ngspice_con.exe"),
        str(Path(tempfile.gettempdir()) / "opencode" / "ngspice47"
            / "Spice64" / "bin" / "ngspice_con.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def _fmt(value):
    return f"{value:g}"


def build_netlist(analysis, values, beta, vbe, ic_reference, mode="divider",
                  ac_points=20, ac_start=1.0, ac_stop=1e9,
                  tstep=1e-6, tstop=5e-3):
    """Build a complete ngspice input deck for one analysis.

    ``values`` must already be in SI units (ohms/farads/volts/hertz).  The
    BJT model is tuned with IS so that its exponential I-V curve passes
    through the analytical Q-point (vbe, ic_reference); BF is set to beta
    and VAF is effectively infinite so the comparison is not distorted by
    the Early effect.
    """
    if analysis not in ANALYSES:
        raise ValueError(f"unknown analysis: {analysis!r}")
    if mode not in _OP_MODES:
        raise ValueError(f"unknown bias mode: {mode!r}")

    vcc = values["VCC"]
    lines = [f"* CE amplifier - {analysis} analysis ({mode} bias)"]
    lines.append(f"VCC VCC 0 {_fmt(vcc)}")

    if analysis == "op" and mode in ("fixed", "emitter"):
        lines.append(f"RB VCC B {_fmt(values['RB'])}")
        lines.append(f"RC VCC C {_fmt(values['RC'])}")
        emitter_node = "E" if mode == "emitter" else "0"
        if mode == "emitter":
            lines.append(f"RE E 0 {_fmt(values['RE'])}")
        lines.append(f"Q1 C B {emitter_node} QNPN")
    else:
        # Divider topology is shared by all three analyses; AC and transient
        # add the coupling capacitors, load and sinusoidal source.
        lines.append(f"R1 VCC B {_fmt(values['R1'])}")
        lines.append(f"R2 B 0 {_fmt(values['R2'])}")
        lines.append(f"RC VCC C {_fmt(values['RC'])}")
        lines.append(f"RE E 0 {_fmt(values['RE'])}")
        if analysis in ("ac", "tran"):
            lines.append(f"RL VOUT 0 {_fmt(values['RL'])}")
            lines.append(f"CIN VIN B {_fmt(values['CIN'])}")
            lines.append(f"COUT C VOUT {_fmt(values['COUT'])}")
            source_v = _fmt(values["SOURCE_V"])
            source_f = _fmt(values["SOURCE_F"])
            lines.append(
                f"VS VIN 0 SIN(0 {source_v} {source_f}) AC {source_v} 0"
            )
        lines.append("Q1 C B E QNPN")

    is_current = saturation_current(ic_reference, vbe)
    lines.append(
        # Small parasitics give the AC sweep a real high-frequency corner;
        # they do not change the DC Q-point used for the Lab 2/3 comparison.
        f".model QNPN NPN(BF={_fmt(beta)} IS={is_current:.6e} VAF=1e12 "
        f"CJC=10pF CJE=20pF TF=0.5ns)"
    )

    if analysis == "op":
        lines.append(".op")
    elif analysis == "ac":
        lines.append(f".ac dec {ac_points} {_fmt(ac_start)} {_fmt(ac_stop)}")
        lines.append(".print ac vdb(vout) vdb(vin)")
    else:
        lines.append(f".tran {_fmt(tstep)} {_fmt(tstop)}")
        lines.append(".print tran v(vin) v(vout)")
    lines.append(".end")
    return "\n".join(lines) + "\n"


def run(netlist, executable=None, timeout=60):
    """Run a netlist through ngspice -b and return its stdout as text."""
    executable = executable or find_executable()
    if not executable:
        raise NgspiceUnavailable(
            "ngspice not found — set NGSPICE_EXECUTABLE to ngspice_con.exe"
        )

    with tempfile.TemporaryDirectory() as tmp:
        deck = Path(tmp) / "circuit.cir"
        deck.write_text(netlist, encoding="utf-8")
        try:
            proc = subprocess.run(
                [executable, "-b", str(deck)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmp,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise NgspiceError(f"could not run ngspice: {exc}") from exc
        output = proc.stdout or ""
        problem = proc.stderr or ""
        if proc.returncode != 0 or "Error:" in problem or "Error:" in output:
            raise NgspiceError((problem + output).strip()[:800] or "ngspice failed")
        return output


def parse_operating_point(output):
    """Read node voltages from either ngspice OP table format, in volts."""
    nodes = {}
    colon = re.compile(
        rf"^\s*V\(([A-Za-z0-9_]+)\):\s*({_NUMBER})", re.MULTILINE
    )
    for match in colon.finditer(output):
        key = _NODE_KEYS.get(match.group(1).lower())
        if key:
            nodes[key] = float(match.group(2))

    table = re.compile(
        rf"^\s*([A-Za-z0-9_]+)\s+({_NUMBER})\s*$", re.MULTILINE
    )
    for match in table.finditer(output):
        key = _NODE_KEYS.get(match.group(1).lower())
        if key:
            nodes[key] = float(match.group(2))

    if not {"VB", "VC", "VE"}.issubset(nodes):
        raise NgspiceError("operating point output has no base/collector/emitter voltages")
    return nodes


_TABLE_COLUMNS = {
    "index": None,
    "frequency": "freq",
    "time": "time",
    "vdb(vout)": "vout_db",
    "vdb(vin)": "vin_db",
    "v(vin)": "vin",
    "v(vout)": "vout",
}


def _parse_table_rows(output):
    """Read ngspice .print tables, whether traces share a row or not."""
    rows = []
    columns = {}
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("Index"):
            columns = {}
            for position, token in enumerate(stripped.split()):
                key = _TABLE_COLUMNS.get(token.lower())
                if key:
                    columns[position] = key
            continue
        if not columns or not stripped:
            continue
        parts = stripped.split()
        try:
            float(parts[0])
        except (ValueError, IndexError):
            continue
        row = {}
        for position, key in columns.items():
            if position >= len(parts):
                break
            try:
                row[key] = float(parts[position])
            except ValueError:
                break
        if len(row) > 1:
            rows.append(row)
    return rows


def parse_ac(output):
    """Merge vdb(vout)/vdb(vin) into [{freq, vout_db, vin_db}].

    ngspice-47 prints both traces in one table; older decks print two
    separate tables.  Repeated page-break headers are handled as one sweep.
    """
    by_frequency = {}
    for row in _parse_table_rows(output):
        if "freq" not in row:
            continue
        entry = by_frequency.setdefault(row["freq"], {"freq": row["freq"]})
        for key in ("vout_db", "vin_db"):
            if key in row:
                entry[key] = row[key]
    rows = [
        entry for entry in by_frequency.values()
        if {"vout_db", "vin_db"}.issubset(entry)
    ]
    if not rows:
        raise NgspiceError("AC output has no vdb(vout)/vdb(vin) tables")
    return sorted(rows, key=lambda row: row["freq"])


def parse_transient(output):
    """Read the .print tran table into [{time, vin, vout}] in seconds/volts."""
    rows = [
        row for row in _parse_table_rows(output)
        if {"time", "vin", "vout"}.issubset(row)
    ]
    if not rows:
        raise NgspiceError("transient output has no V(vin)/V(vout) table")
    return rows


def simulate_operating_point(mode, values, beta, vbe, ic_reference, executable=None):
    """Return the ngspice Q-point with currents derived from node voltages."""
    netlist = build_netlist("op", values, beta, vbe, ic_reference, mode=mode)
    nodes = parse_operating_point(run(netlist, executable))
    vb, vc, ve = nodes["VB"], nodes["VC"], nodes["VE"]
    vcc = nodes.get("VCC", values["VCC"])
    ic = (vcc - vc) / values["RC"]
    if mode == "divider":
        ib = (vcc - vb) / values["R1"] - vb / values["R2"]
    else:
        ib = (vcc - vb) / values["RB"]
    return {
        "source": "ngspice",
        "netlist": netlist,
        "VB": vb, "VE": ve, "VC": vc, "VCC": vcc,
        "VCE": vc - ve,
        "IC": ic, "IB": ib, "IE": ic + ib,
    }


def _cutoff_crossing(rows, threshold, rising):
    """Interpolate the frequency where gain_db crosses threshold in log-f."""
    previous = None
    for row in rows:
        if previous is not None:
            x1, y1 = math.log10(previous["freq"]), previous["gain_db"]
            x2, y2 = math.log10(row["freq"]), row["gain_db"]
            crossed = (
                y1 < threshold <= y2 if rising else y1 >= threshold > y2
            )
            if crossed and y2 != y1:
                fraction = (threshold - y1) / (y2 - y1)
                return 10 ** (x1 + fraction * (x2 - x1))
        previous = row
    return rows[0]["freq"] if rising else rows[-1]["freq"]


def simulate_ac(values, beta, vbe, ic_reference, executable=None):
    """Return midband gain and -3 dB corner frequencies from an .ac sweep."""
    netlist = build_netlist("ac", values, beta, vbe, ic_reference)
    rows = parse_ac(run(netlist, executable))
    for row in rows:
        row["gain_db"] = row["vout_db"] - row["vin_db"]
        row["gain"] = 10 ** (row["gain_db"] / 20)

    best = max(rows, key=lambda row: row["gain_db"])
    threshold = best["gain_db"] - 20 * math.log10(math.sqrt(2))
    return {
        "source": "ngspice",
        "netlist": netlist,
        "midband_gain": abs(best["gain"]),
        "midband_db": abs(best["gain_db"]),
        "midband_freq": best["freq"],
        "f_low": _cutoff_crossing(rows, threshold, rising=True),
        "f_high": _cutoff_crossing(rows, threshold, rising=False),
        "points": rows,
    }


def simulate_transient(values, beta, vbe, ic_reference, executable=None):
    """Return Vin/Vout peak-to-peak values from a .tran simulation."""
    netlist = build_netlist("tran", values, beta, vbe, ic_reference)
    rows = parse_transient(run(netlist, executable))
    vin = [row["vin"] for row in rows]
    vout = [row["vout"] for row in rows]
    vin_pp = max(vin) - min(vin)
    vout_pp = max(vout) - min(vout)
    step = max(1, len(rows) // 400)
    return {
        "source": "ngspice",
        "netlist": netlist,
        "vin_pp": vin_pp,
        "vout_pp": vout_pp,
        "gain": vout_pp / vin_pp if vin_pp else float("nan"),
        "samples": len(rows),
        "points": rows[::step],
    }
