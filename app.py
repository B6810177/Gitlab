from flask import Flask, render_template, request

from bjt_bias import validate, bias
from bjt_bias.validation_results import (
    VALIDATION_CASES,
    VALIDATION_DATE,
    VALIDATION_DOC,
    VALIDATION_SHARED,
    VALIDATION_TOLERANCE,
)

app = Flask(__name__)

FIELDS = ("mode", "VCC", "RB", "R1", "R2", "RC", "RE", "beta", "VBE", "unit")
UNITS = ("ohm", "kohm")

MODES = ("divider", "fixed", "emitter")
MODE_LABELS = {
    "divider": "Voltage Divider Bias",
    "fixed": "Fixed Bias",
    "emitter": "Emitter Bias",
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
}


def _calculate(mode, values, unit):
    """เลือกฟังก์ชันตามโหมด ตรวจเฉพาะช่องที่โหมดนั้นใช้ แล้วแปลงหน่วยความต้านทาน"""
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
    return func(**v)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    errors = []
    values = dict(DEFAULT_VALUES)
    mode = DEFAULT_VALUES["mode"]
    unit = DEFAULT_VALUES["unit"]

    if request.method == "POST":
        values = {k: request.form.get(k, "") for k in FIELDS}
        # ไม่ส่ง mode มา = ใช้โหมด Divider เดิม (คงความเข้ากันได้กับเทสต์เดิม)
        mode = values.get("mode") or DEFAULT_VALUES["mode"]
        unit = values.get("unit") or "ohm"
        action = request.form.get("action", "calculate")

        if mode not in MODES:
            errors.append(
                f"ไม่รู้จักโหมดไบอัส {mode!r} — เลือกได้เฉพาะ divider, fixed หรือ emitter"
            )
        elif action == "switch":
            # เปลี่ยนโหมดแล้วโหลดฟอร์มใหม่ ไม่คำนวณและไม่ค้างผลรอบก่อน
            result = None
        else:
            try:
                if unit not in UNITS:
                    raise ValueError("unit must be 'ohm' or 'kohm'")
                result = _calculate(mode, values, unit)
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
