import math

from flask import Flask, render_template, request

import spice_engine
from bjt_bias import validate, bias
from bjt_bias.validation_results import (
    VALIDATION_CASES,
    VALIDATION_DATE,
    VALIDATION_DOC,
    VALIDATION_SHARED,
    VALIDATION_TOLERANCE,
)

app = Flask(__name__)

FIELDS = (
    "mode", "VCC", "RB", "R1", "R2", "RC", "RE", "beta", "VBE", "unit",
    "analysis", "RL", "CIN", "COUT", "SOURCE_V", "SOURCE_F",
)
UNITS = ("ohm", "kohm")

MODES = ("divider", "fixed", "emitter")
MODE_LABELS = {
    "divider": "Voltage Divider Bias",
    "fixed": "Fixed Bias",
    "emitter": "Emitter Bias",
}
ANALYSES = ("dc", "ac", "tran")
ANALYSIS_LABELS = {
    "dc": "DC Operating Point (.op)",
    "ac": "AC Small-Signal (.ac)",
    "tran": "Transient (.tran)",
}
# ช่องความต้านทานที่ต้องแปลงหน่วย kΩ -> Ω ของแต่ละโหมด
RESISTOR_FIELDS = {
    "divider": ("R1", "R2", "RC", "RE"),
    "fixed": ("RB", "RC"),
    "emitter": ("RB", "RC", "RE"),
}

# ค่าเริ่มต้นของฟอร์ม: เว้นว่างไว้ ให้ผู้ใช้กรอกเอง (unit เริ่มที่ kΩ)
DEFAULT_VALUES = {
    "mode": "divider",
    "VCC": "",
    "RB": "",
    "R1": "",
    "R2": "",
    "RC": "",
    "RE": "",
    "beta": "",
    "VBE": "",
    "unit": "kohm",
    "analysis": "dc",
    "RL": "",
    "CIN": "",
    "COUT": "",
    "SOURCE_V": "",
    "SOURCE_F": "",
}

# Baseline ตามโจทย์ Lab 06: VCC 12 V, 100k/22k/2.2k/1k, RL 10k,
# CIN = COUT = 10 uF, แหล่ง SIN 10 mV peak / 1 kHz
BASELINE_VALUES = {
    **DEFAULT_VALUES,
    "VCC": "12", "R1": "100", "R2": "22", "RC": "2.2", "RE": "1",
    "beta": "100", "VBE": "0.7", "unit": "kohm",
    "RL": "10", "CIN": "10", "COUT": "10",
    "SOURCE_V": "10", "SOURCE_F": "1000", "analysis": "dc",
}


def _prepare(mode, values, unit):
    """ตรวจอินพุตตามโหมด แปลง kΩ → Ω แล้วคืน (ค่าที่ใช้คำนวณ, ฟังก์ชัน)"""
    if unit not in UNITS:
        raise ValueError("unit must be 'ohm' or 'kohm'")
    if mode == "divider":
        v = validate.validate_inputs(
            values["VCC"], values["R1"], values["R2"],
            values["RC"], values["RE"], values["beta"], values["VBE"]
        )
        func = bias.calculate_bias
    elif mode == "fixed":
        v = validate.validate_fixed(
            values["VCC"], values["RB"], values["RC"],
            values["beta"], values["VBE"]
        )
        func = bias.calculate_fixed
    elif mode == "emitter":
        v = validate.validate_emitter(
            values["VCC"], values["RB"], values["RC"], values["RE"],
            values["beta"], values["VBE"]
        )
        func = bias.calculate_emitter
    else:
        raise ValueError(f"unknown bias mode: {mode!r}")

    if unit == "kohm":
        for name in RESISTOR_FIELDS[mode]:
            v[name] *= 1000.0
    return v, func


def _calculate(mode, values, unit):
    """เลือกฟังก์ชันตามโหมด ตรวจเฉพาะช่องที่โหมดนั้นใช้ แล้วแปลงหน่วยความต้านทาน"""
    v, func = _prepare(mode, values, unit)
    return func(**v)


def _ce_values(values, unit):
    """แปลงค่าของ CE amplifier ให้เป็น SI ก่อนส่งเข้า ngspice"""
    ce = validate.validate_ce(
        values["RL"], values["CIN"], values["COUT"],
        values["SOURCE_V"], values["SOURCE_F"]
    )
    if unit == "kohm":
        ce["RL"] *= 1000.0
    ce["CIN"] *= 1e-6  # µF -> F
    ce["COUT"] *= 1e-6
    ce["SOURCE_V"] *= 1e-3  # mV peak -> V peak
    return ce


def _analytical_ac(result, ce):
    """Gain/fL แบบมือจาก Q-point: re = VT/IC, Av = -(RC||RL)/(RE + re)"""
    ic = result["IC"]
    if ic <= 0:
        return {"gain": 0.0, "f_low": float("nan"), "f_high": float("nan")}
    vt = spice_engine.thermal_voltage()
    re = vt / ic
    r_load = 1.0 / (1.0 / ce["RC"] + 1.0 / ce["RL"])
    gain = r_load / (ce["RE"] + re)
    r_in = 1.0 / (
        1.0 / ce["R1"] + 1.0 / ce["R2"] + 1.0 / (ce["beta"] * re)
    )
    f_in = 1.0 / (2 * math.pi * ce["CIN"] * r_in)
    f_out = 1.0 / (2 * math.pi * ce["COUT"] * (ce["RC"] + ce["RL"]))
    return {
        "gain": gain,
        "f_low": math.hypot(f_in, f_out),
        "formula": "Av ≈ (RC∥RL)/(RE + VT/IC)",
    }


def _analytical_tran(result, ce, ac):
    """Vin/Vout peak-to-peak ที่คาดจาก gain midband และแหล่ง SIN 10 mV"""
    vin_pp = 2 * ce["SOURCE_V"]
    return {
        "vin_pp": vin_pp,
        "vout_pp": vin_pp * ac["gain"],
        "gain": ac["gain"],
    }


def _comparison_rows(analysis, analytical, spice):
    """สร้างตารางเทียบ Analytical vs ngspice พร้อมผลต่าง"""
    if analysis == "dc":
        specs = [
            ("IC", "I_C", 1e3, "mA"),
            ("VCE", "V_CE", 1.0, "V"),
            ("VB", "V_B", 1.0, "V"),
            ("VE", "V_E", 1.0, "V"),
            ("VC", "V_C", 1.0, "V"),
        ]
    elif analysis == "ac":
        specs = [
            ("gain", "Gain |Av|", 1.0, "×"),
            ("f_low", "fL (-3 dB)", 1.0, "Hz"),
            ("f_high", "fH (-3 dB)", 1.0, "Hz"),
        ]
    else:
        specs = [
            ("vin_pp", "Vin (p-p)", 1e3, "mV"),
            ("vout_pp", "Vout (p-p)", 1e3, "mV"),
            ("gain", "Gain (p-p)", 1.0, "×"),
        ]
    rows = []
    for key, label, scale, unit in specs:
        if key not in analytical or key not in spice:
            continue
        a, s = analytical[key] * scale, spice[key] * scale
        rows.append({
            "metric": label,
            "analytical": a,
            "ngspice": s,
            "delta": abs(a - s),
            "unit": unit,
        })
    return rows


def _polyline(points, xkey, ykeys, logx=False, width=600, height=180):
    """แปลงข้อมูลเป็นพิกัด SVG ให้ template แสดงกราฟโดยไม่ต้องคำนวณเอง"""
    def xval(point):
        return math.log10(point[xkey]) if logx else point[xkey]

    xs = [xval(p) for p in points]
    ys = [p[k] for k in ykeys for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmax == xmin:
        xmax = xmin + 1
    if ymax == ymin:
        ymax = ymin + 1

    def sx(x):
        return 12 + (x - xmin) / (xmax - xmin) * (width - 24)

    def sy(y):
        return height - 14 - (y - ymin) / (ymax - ymin) * (height - 28)

    series = {
        key: " ".join(f"{sx(xval(p)):.2f},{sy(p[key]):.2f}" for p in points)
        for key in ykeys
    }
    return {
        "series": series,
        "width": width,
        "height": height,
        "ymin": ymin,
        "ymax": ymax,
    }


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    errors = []
    values = dict(DEFAULT_VALUES)
    mode = DEFAULT_VALUES["mode"]
    unit = DEFAULT_VALUES["unit"]
    analysis = "dc"
    compare = False
    spice = None
    spice_error = None
    analytical_ac = None
    analytical_tran = None
    comparison = []
    chart = None
    netlist = None

    if request.method == "POST":
        values = {k: request.form.get(k, "") for k in FIELDS}
        # ไม่ส่ง mode มา = ใช้โหมด Divider เดิม (คงความเข้ากันได้กับเทสต์เดิม)
        mode = values.get("mode") or DEFAULT_VALUES["mode"]
        unit = values.get("unit") or "ohm"
        analysis = values.get("analysis") or "dc"
        compare = request.form.get("compare") == "1"
        action = request.form.get("action", "calculate")

        if action == "baseline":
            values = dict(BASELINE_VALUES)
            mode, unit, analysis = (
                values["mode"], values["unit"], values["analysis"]
            )
        elif mode not in MODES:
            errors.append(
                f"ไม่รู้จักโหมดไบอัส {mode!r} — เลือกได้เฉพาะ divider, fixed หรือ emitter"
            )
        elif analysis not in ANALYSES:
            errors.append(
                f"ไม่รู้จัก analysis {analysis!r} — เลือกได้เฉพาะ dc, ac หรือ tran"
            )
        elif action == "switch":
            # เปลี่ยนโหมดแล้วโหลดฟอร์มใหม่ ไม่คำนวณและไม่ค้างผลรอบก่อน
            result = None
        else:
            try:
                v, func = _prepare(mode, values, unit)
                result = func(**v)
                ce = None
                if analysis in ("ac", "tran"):
                    if mode != "divider":
                        raise ValueError(
                            "AC/Transient ใช้ได้เฉพาะ Voltage Divider Bias"
                        )
                    ce = _ce_values(values, unit)
                    ce.update(v)
                    analytical_ac = _analytical_ac(result, ce)
                    if analysis == "tran":
                        analytical_tran = _analytical_tran(
                            result, ce, analytical_ac
                        )
                if compare:
                    try:
                        ic_ref = result["IC"]
                        if analysis == "dc":
                            spice = spice_engine.simulate_operating_point(
                                mode, v, v["beta"], v["VBE"], ic_ref
                            )
                            comparison = _comparison_rows("dc", result, spice)
                        elif analysis == "ac":
                            spice = spice_engine.simulate_ac(
                                ce, v["beta"], v["VBE"], ic_ref
                            )
                            comparison = _comparison_rows(
                                "ac", analytical_ac, spice
                            )
                            chart = _polyline(
                                spice["points"], "freq", ("gain_db",), logx=True
                            )
                        else:
                            spice = spice_engine.simulate_transient(
                                ce, v["beta"], v["VBE"], ic_ref
                            )
                            comparison = _comparison_rows(
                                "tran", analytical_tran, spice
                            )
                            chart = _polyline(
                                spice["points"], "time", ("vin", "vout")
                            )
                        netlist = spice["netlist"]
                    except spice_engine.NgspiceError as exc:
                        spice = None
                        comparison = []
                        chart = None
                        spice_error = str(exc)
            except Exception as e:
                errors.append(f"{MODE_LABELS[mode]}: {e}")

    return render_template(
        "index.html",
        result=result,
        errors=errors,
        values=values,
        unit=unit,
        mode=mode,
        mode_label=MODE_LABELS.get(mode, mode),
        analysis=analysis,
        analysis_label=ANALYSIS_LABELS.get(analysis, analysis),
        compare=compare,
        spice=spice,
        spice_error=spice_error,
        analytical_ac=analytical_ac,
        analytical_tran=analytical_tran,
        comparison=comparison,
        chart=chart,
        netlist=netlist,
        validation_cases=VALIDATION_CASES,
        validation_date=VALIDATION_DATE,
        validation_shared=VALIDATION_SHARED,
        validation_tolerance=VALIDATION_TOLERANCE,
        validation_doc=VALIDATION_DOC,
    )


@app.after_request
def no_store_html(response):
    """กันเบราว์เซอร์แคชหน้า HTML ไว้ ทำให้แก้ template แล้วเห็นผลทันที"""
    if response.mimetype == "text/html":
        response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


if __name__ == "__main__":
    app.run(debug=True)
