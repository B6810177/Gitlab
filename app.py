from flask import Flask, render_template, request

from bjt_bias import validate, bias

app = Flask(__name__)

FIELDS = ("VCC", "R1", "R2", "RC", "RE", "beta", "VBE", "unit")
RESISTOR_FIELDS = ("R1", "R2", "RC", "RE")
UNITS = ("ohm", "kohm")

# ค่าตั้งต้นตามตัวอย่างในเอกสาร Lab 02 (ตัวต้านทานหน่วย kΩ)
DEFAULT_VALUES = {
    "VCC": "12",
    "R1": "100",
    "R2": "22",
    "RC": "2.2",
    "RE": "1",
    "beta": "100",
    "VBE": "0.70",
    "unit": "kohm",
}


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    errors = []
    values = dict(DEFAULT_VALUES)
    unit = DEFAULT_VALUES["unit"]

    if request.method == "POST":
        values = {k: request.form.get(k, "") for k in FIELDS}
        unit = values.get("unit") or "ohm"
        try:
            if unit not in UNITS:
                raise ValueError("unit must be 'ohm' or 'kohm'")
            v = validate.validate_inputs(
                values["VCC"], values["R1"], values["R2"],
                values["RC"], values["RE"], values["beta"], values["VBE"]
            )
            if unit == "kohm":
                for name in RESISTOR_FIELDS:
                    v[name] *= 1000.0
            result = bias.calculate_bias(**v)
        except Exception as e:
            errors.append(str(e))

    return render_template(
        "index.html", result=result, errors=errors, values=values, unit=unit
    )


if __name__ == "__main__":
    app.run(debug=True)
