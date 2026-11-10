# BJT Common-Emitter DC Bias Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest working Flask web app for voltage-divider biased BJT Common-Emitter DC bias calculation with input validation, region warnings, and independent calculation comparison.

**Architecture:** Separate pure Python engineering logic (`bjt_bias/`) from Flask routes (`app.py`), templates/CSS, and tests. Two independent calculation methods (Thevenin base-loop + nodal/KCL) for verification.

**Tech Stack:** Python 3.12, Flask, HTML, CSS, unittest

**Spec:** `docs/superpowers/specs/2026-11-10-bjt-ce-bias-design.md`

## Global Constraints

- Inputs: VCC, R1, R2, RC, RE, beta, VBE
- No AC, transient, full circuit editor, or FET
- Engineering logic must be separate from Flask routes
- Compare results with independent engineering calculation (Thevenin vs nodal/KCL)
- Output with units, validation, and region warnings
- $V_{CE(sat)} \approx 0.2\,\text{V}$ warn only (never clamp)
- Use unittest style consistent with existing repo

## Review Focus

- **Invalid numeric inputs (bool/inf/nan):** Must be rejected with clear errors (not crash)
- **Boundary conditions (I_B<=0, V_CE near 0.2V):** Must produce correct cutoff/saturation warnings
- **Independent calc agreement:** $|\Delta I_C|$ must be reported; large disagreement indicates bug
- **Division by zero / missing values:** All validated before calculation
- **Separation of concerns:** `bjt_bias/` must not import Flask

---

### Task 1: Setup dependencies and venv

**Files:**
- Create: `requirements.txt`
- Create: `README_BJT.md`

**Interfaces:**
- Consumes: None
- Produces: Dependencies for Flask app

- [ ] **Step 1: Create requirements.txt**

```txt
Flask==3.0.3
```

- [ ] **Step 2: Create README_BJT.md with basic usage**

```markdown
# BJT Common-Emitter DC Bias Calculator

Flask web app for voltage-divider biased BJT CE DC operating point.

## Setup
```bash
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
flask --app app run --debug
```

## Test
```bash
python -m unittest discover -s tests
```
```

- [ ] **Step 3: Commit**

```bash
git add requirements.txt README_BJT.md
git commit -m "chore: add requirements and README for BJT bias app"
```

### Task 2: Input validation module

**Files:**
- Create: `bjt_bias/__init__.py`
- Create: `bjt_bias/validate.py`
- Test: `tests/test_validate.py` (will be added to test_bias or separate - add to tests/test_bias.py)

**Interfaces:**
- Consumes: None
- Produces: `validate_inputs(...)` returning dict of floats or raising ValueError with field info

- [ ] **Step 1: Write failing tests for validation**

Add to `tests/test_bias.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:\Users\B6810177\Desktop\Gitlab
python -m unittest tests.test_bias.TestValidation -v
```
Expected: FAIL (module not found)

- [ ] **Step 3: Create bjt_bias package and validate module**

`bjt_bias/__init__.py`:
```python
__all__ = ["validate", "bias"]
```

`bjt_bias/validate.py`:
```python
import math


def validate_inputs(vcc, r1, r2, rc, re, beta, vbe):
    values = {
        "VCC": vcc,
        "R1": r1,
        "R2": r2,
        "RC": rc,
        "RE": re,
        "beta": beta,
        "VBE": vbe,
    }
    result = {}
    for name, val in values.items():
        if isinstance(val, bool):
            raise ValueError(f"{name} must be a finite number")
        try:
            f = float(val)
        except (TypeError, ValueError) as e:
            raise ValueError(f"{name} must be a finite number") from e
        if not math.isfinite(f):
            raise ValueError(f"{name} must be a finite number")
        result[name] = f

    if result["VCC"] <= 0:
        raise ValueError("VCC must be greater than 0")
    for rname in ["R1", "R2", "RC", "RE"]:
        if result[rname] <= 0:
            raise ValueError(f"{rname} must be greater than 0")
    if result["beta"] <= 0:
        raise ValueError("beta must be greater than 0")
    if result["VBE"] < 0.4 or result["VBE"] >= result["VCC"]:
        raise ValueError("VBE must be between 0.4 V and VCC (exclusive of VCC)")
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m unittest tests.test_bias.TestValidation -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add bjt_bias/__init__.py bjt_bias/validate.py tests/test_bias.py
git commit -m "feat: add input validation for BJT bias parameters"
```

### Task 3: Core bias calculation with independent verification

**Files:**
- Create: `bjt_bias/bias.py`
- Test: `tests/test_bias.py` (extend)

**Interfaces:**
- Consumes: validated float values from `validate_inputs`
- Produces: dict with operating point, verification data, warnings

- [ ] **Step 1: Write failing tests**

Add to `tests/test_bias.py`:
```python
from bjt_bias import bias, validate


class TestBiasCalculation(unittest.TestCase):
    def test_known_example_agreement(self):
        v = validate.validate_inputs(10, 10000, 5000, 1000, 500, 100, 0.7)
        res = bias.calculate_bias(**v)
        self.assertAlmostEqual(res["calc_a"]["IC"], res["calc_b"]["IC"], places=9)
        self.assertTrue(res["verification"]["agree"])
        self.assertIn("IC", res)
        self.assertIn("VCE", res)

    def test_cutoff_warning(self):
        v = validate.validate_inputs(5, 1000000, 1000000, 1000, 1000, 100, 0.7)
        res = bias.calculate_bias(**v)
        self.assertTrue(any("cutoff" in w.lower() for w in res["warnings"]))

    def test_saturation_warning(self):
        # Force low VCE
        v = validate.validate_inputs(5, 1000, 10000, 10, 1000, 100, 0.7)
        res = bias.calculate_bias(**v)
        self.assertTrue(any("saturation" in w.lower() for w in res["warnings"]))
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m unittest tests.test_bias.TestBiasCalculation -v
```
Expected: FAIL

- [ ] **Step 3: Implement bias calculation**

`bjt_bias/bias.py`:
```python
import math


def _parallel(r1, r2):
    return (r1 * r2) / (r1 + r2)


def calculate_bias(VCC, R1, R2, RC, RE, beta, VBE):
    # Calc A: Thevenin base-loop
    VTH = VCC * R2 / (R1 + R2)
    RTH = _parallel(R1, R2)
    IB_a = (VTH - VBE) / (RTH + (beta + 1) * RE)
    IC_a = beta * IB_a
    IE_a = (beta + 1) * IB_a
    VE_a = IE_a * RE
    VB_a = VE_a + VBE
    VC_a = VCC - IC_a * RC
    VCE_a = VC_a - VE_a

    # Calc B: Independent nodal/KCL
    # From KCL at base: (VCC-VB)/R1 = VB/R2 + IB, IB = IC/beta, IE = IC+IB, VE = IE*RE, VB = VE+VBE
    # Substitute: (VCC - (VE+VBE))/R1 = (VE+VBE)/R2 + IC/beta, VE = (IC + IC/beta)*RE = IC*RE*(beta+1)/beta
    # Solve for IC
    IE_over_IC = (beta + 1) / beta
    # (VCC - VBE - IC*RE*IE_over_IC)/R1 - (VBE + IC*RE*IE_over_IC)/R2 = IC/beta
    # VCC-VBE)/R1 - VBE/R2 = IC/beta + IC*RE*IE_over_IC*(1/R1 + 1/R2)
    left = (VCC - VBE) / R1 - VBE / R2
    right_coeff = 1.0 / beta + RE * IE_over_IC * (1.0 / R1 + 1.0 / R2)
    if abs(right_coeff) < 1e-18:
        IC_b = float('nan')
    else:
        IC_b = left / right_coeff
    IB_b = IC_b / beta if beta != 0 else float('nan')
    IE_b = IC_b + IB_b
    VE_b = IE_b * RE
    VB_b = VE_b + VBE
    VC_b = VCC - IC_b * RC
    VCE_b = VC_b - VE_b

    delta_ic = abs(IC_a - IC_b)
    # Use reasonable tolerance
    tol = 1e-9 * max(1.0, abs(IC_a), abs(IC_b))
    agree = delta_ic <= max(tol, 1e-12)

    warnings = []
    if IB_a <= 0 or IC_a <= 0:
        warnings.append("Transistor likely in cutoff")
    VCE_sat = 0.2
    if VCE_a <= VCE_sat + 1e-9:
        warnings.append("Transistor likely in saturation (V_CE near/at saturation)")

    return {
        "IC": IC_a,
        "IB": IB_a,
        "IE": IE_a,
        "VB": VB_a,
        "VE": VE_a,
        "VC": VC_a,
        "VCE": VCE_a,
        "VTH": VTH,
        "RTH": RTH,
        "calc_a": {"IB": IB_a, "IC": IC_a, "IE": IE_a, "VB": VB_a, "VE": VE_a, "VC": VC_a, "VCE": VCE_a},
        "calc_b": {"IB": IB_b, "IC": IC_b, "IE": IE_b, "VB": VB_b, "VE": VE_b, "VC": VC_b, "VCE": VCE_b},
        "verification": {"delta_ic": delta_ic, "agree": agree, "tolerance": tol},
        "warnings": warnings,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m unittest tests.test_bias.TestValidation tests.test_bias.TestBiasCalculation -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add bjt_bias/bias.py tests/test_bias.py
git commit -m "feat: add BJT CE bias calculation with independent verification"
```

### Task 4: Flask app and routes

**Files:**
- Create: `app.py`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: `bjt_bias.validate`, `bjt_bias.bias`
- Produces: Web interface at `/`

- [ ] **Step 1: Write failing route test**

`tests/test_app.py`:
```python
import unittest
from app import app


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_form(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)

    def test_post_valid(self):
        r = self.client.post('/', data={
            'VCC': '10', 'R1': '10000', 'R2': '5000', 'RC': '1000', 'RE': '500', 'beta': '100', 'VBE': '0.7'
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'IC', r.data)

    def test_post_invalid(self):
        r = self.client.post('/', data={
            'VCC': '10', 'R1': '-1', 'R2': '5000', 'RC': '1000', 'RE': '500', 'beta': '100', 'VBE': '0.7'
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'error', r.data.lower())
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m unittest tests.test_app -v
```
Expected: FAIL

- [ ] **Step 3: Implement app.py**

`app.py`:
```python
from flask import Flask, render_template, request

from bjt_bias import validate, bias

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    errors = []
    values = {}
    if request.method == 'POST':
        form = request.form
        values = {k: form.get(k, '') for k in ['VCC', 'R1', 'R2', 'RC', 'RE', 'beta', 'VBE']}
        try:
            v = validate.validate_inputs(
                values['VCC'], values['R1'], values['R2'],
                values['RC'], values['RE'], values['beta'], values['VBE']
            )
            result = bias.calculate_bias(**v)
        except Exception as e:
            errors.append(str(e))
    return render_template('index.html', result=result, errors=errors, values=values)


if __name__ == '__main__':
    app.run(debug=True)
```

- [ ] **Step 4: Run tests to verify they fail (still need templates)**

```bash
python -m unittest tests.test_app -v
```
Expected: FAIL (template not found) - proceed to next task

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_app.py
git commit -m "feat: add Flask routes for BJT bias calculator"
```

### Task 5: HTML templates and CSS

**Files:**
- Create: `templates/base.html`
- Create: `templates/index.html`
- Create: `static/style.css`

**Interfaces:**
- Consumes: data from app.py
- Produces: Form UI with results, verification, warnings

- [ ] **Step 1: Create base template**

`templates/base.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BJT CE DC Bias Calculator</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <h1>BJT Common-Emitter DC Bias Calculator (ENG29 2121)</h1>
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

- [ ] **Step 2: Create main template with form, results, verification**

`templates/index.html`:
```html
{% extends "base.html" %}
{% block content %}
<form method="post">
    <div class="grid">
        <label>VCC (V) <input name="VCC" value="{{ values.get('VCC','') }}" required></label>
        <label>R1 (Ω) <input name="R1" value="{{ values.get('R1','') }}" required></label>
        <label>R2 (Ω) <input name="R2" value="{{ values.get('R2','') }}" required></label>
        <label>RC (Ω) <input name="RC" value="{{ values.get('RC','') }}" required></label>
        <label>RE (Ω) <input name="RE" value="{{ values.get('RE','') }}" required></label>
        <label>beta <input name="beta" value="{{ values.get('beta','') }}" required></label>
        <label>VBE (V) <input name="VBE" value="{{ values.get('VBE','') }}" required></label>
    </div>
    <button type="submit">Calculate</button>
</form>

{% if errors %}
<div class="errors">
    {% for e in errors %}<p>{{ e }}</p>{% endfor %}
</div>
{% endif %}

{% if result %}
<h2>DC Operating Point</h2>
<table>
    <tr><th>Parameter</th><th>Value</th></tr>
    <tr><td>I_B</td><td>{{ '%.6g'|format(result.IB) }} A</td></tr>
    <tr><td>I_C</td><td>{{ '%.6g'|format(result.IC) }} A</td></tr>
    <tr><td>I_E</td><td>{{ '%.6g'|format(result.IE) }} A</td></tr>
    <tr><td>V_B</td><td>{{ '%.6g'|format(result.VB) }} V</td></tr>
    <tr><td>V_E</td><td>{{ '%.6g'|format(result.VE) }} V</td></tr>
    <tr><td>V_C</td><td>{{ '%.6g'|format(result.VC) }} V</td></tr>
    <tr><td>V_CE</td><td>{{ '%.6g'|format(result.VCE) }} V</td></tr>
    <tr><td>V_TH</td><td>{{ '%.6g'|format(result.VTH) }} V</td></tr>
    <tr><td>R_TH</td><td>{{ '%.6g'|format(result.RTH) }} Ω</td></tr>
</table>

<h2>Verification (Independent Calculation)</h2>
<table>
    <tr><th>Method</th><th>I_C (A)</th></tr>
    <tr><td>Calc A (Thevenin base-loop)</td><td>{{ '%.9g'|format(result.calc_a.IC) }}</td></tr>
    <tr><td>Calc B (Nodal/KCL)</td><td>{{ '%.9g'|format(result.calc_b.IC) }}</td></tr>
    <tr><td>|ΔI_C|</td><td>{{ '%.9g'|format(result.verification.delta_ic) }}</td></tr>
    <tr><td>Agreement</td><td>{{ 'PASS' if result.verification.agree else 'FAIL' }}</td></tr>
</table>

{% if result.warnings %}
<h2>Region Warnings</h2>
<div class="warnings">
    {% for w in result.warnings %}<p>{{ w }}</p>{% endfor %}
</div>
{% endif %}
{% endif %}
{% endblock %}
```

- [ ] **Step 3: Create CSS**

`static/style.css`:
```css
body { font-family: Arial, sans-serif; margin: 20px; background: #f7f7f7; }
.container { max-width: 900px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
label { display: flex; flex-direction: column; }
input { padding: 6px; }
button { margin-top: 10px; padding: 8px 16px; }
table { border-collapse: collapse; width: 100%; margin-top: 10px; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { background: #f0f0f0; }
.errors { color: #d33; background: #fee; padding: 10px; border-radius: 4px; }
.warnings { color: #b60; background: #fff3cd; padding: 10px; border-radius: 4px; }
```

- [ ] **Step 4: Run all tests**

```bash
python -m unittest discover -s tests -v
```
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add templates/base.html templates/index.html static/style.css
git commit -m "feat: add templates and CSS for BJT bias web UI"
```

### Task 6: Integration test and localhost demo

**Files:**
- Modify: None (verification only)

- [ ] **Step 1: Run all tests one final time**

```bash
python -m unittest discover -s tests -v
```
Expected: All tests pass

- [ ] **Step 2: Start Flask app for localhost demo**

```bash
flask --app app run --debug
```
Note: Keep this running for demonstration. Open browser to http://127.0.0.1:5000

- [ ] **Step 3: Test with known example in browser/form**
Use: VCC=10, R1=10000, R2=5000, RC=1000, RE=500, beta=100, VBE=0.7
Verify: results shown, verification passes, no unexpected errors

- [ ] **Step 4: Commit any final changes if needed**

```bash
git add -A
git commit -m "test: verify BJT bias app integration" || echo "nothing to commit"
```

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-11-10-bjt-ce-bias-web-app.md`. 

Please review the plan. Which execution approach would you prefer?

- **Subagent-driven** - A fresh subagent implements each task and a fresh reviewer checks it before the next one starts, then a whole-branch review at the end. Most thorough.
- **Native** - I implement every task myself in this session, then one review of the whole branch at the end. Cheapest and fastest.

For this plan I recommend **Native** (small plan with clear tasks, good for completing today with localhost demo and commit). 

Does the plan capture what you want, and which approach should we use?
