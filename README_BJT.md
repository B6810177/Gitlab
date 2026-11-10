# BJT Common-Emitter DC Bias Calculator

Flask web app for the DC operating point of a voltage-divider biased NPN BJT
common-emitter stage (ENG29 2121 · Lab 02).

## UI layout

The page is intentionally ordered **circuit first, input form in the middle, results last**:

1. **Circuit diagram** — voltage-divider bias reference schematic.
2. **Input form** — V<sub>CC</sub>, β, V<sub>BE</sub> and R1/R2/R<sub>C</sub>/R<sub>E</sub>
   with a kΩ / Ω unit selector.
3. **DC Operating Point** — region banner, V<sub>B</sub>, V<sub>E</sub>,
   V<sub>C</sub>, V<sub>CE</sub>, I<sub>C</sub>, secondary values and warnings.

On the first visit the results panel shows an empty state and all input fields
start blank. After submitting the form the page scrolls down to the results so
the new values are immediately visible.

Number fields accept long values and thousands separators (for example
`1,000,000` or `1000000`), and long result values wrap inside their cards instead
of being cut off.

## Static (browser-only) version

`index.html` + `static/app.js` implement the same UI and the same equations in
JavaScript, so the calculator can be used by opening `index.html` directly or
through GitHub Pages — no Python server required. The Flask version remains the
Lab 02 deliverable and the reference implementation covered by the tests.

## Project structure

```
app.py              Flask routes, form parsing and kΩ → Ω conversion
bjt_bias/
  validate.py       input validation
  bias.py           engineering calculations + region detection
templates/
  base.html         page shell
  index.html        schematic (top) + input form + results (bottom)
static/
  style.css         responsive layout
tests/
  test_bias.py      engineering/unit tests
  test_app.py       Flask HTTP tests
requirements.txt
```

## Model (Forward-Active Approximation)

```
VTH = VCC · R2 / (R1 + R2)
RTH = R1 · R2 / (R1 + R2)
IB  = (VTH − VBE) / (RTH + (β + 1)·RE)
IC  = β · IB
IE  = (β + 1) · IB
VE  = IE · RE
VB  = VE + VBE
VC  = VCC − IC · RC
VCE = VC − VE
```

Region detection: `IB ≤ 0` → **Cutoff**, `VCE ≤ 0.2 V` → **Saturation**,
otherwise **Forward Active**. Cutoff/saturation results are shown with a warning
because the forward-active approximation no longer applies.

## Reference example

V<sub>CC</sub> = 12 V, R1 = 100 kΩ, R2 = 22 kΩ, R<sub>C</sub> = 2.2 kΩ,
R<sub>E</sub> = 1 kΩ, β = 100, V<sub>BE</sub> = 0.70 V:

| Quantity | Value |
| --- | --- |
| V<sub>TH</sub> | 2.164 V |
| R<sub>TH</sub> | 18.033 kΩ |
| I<sub>B</sub> | 12.30 µA |
| I<sub>C</sub> | 1.230 mA |
| I<sub>E</sub> | 1.242 mA |
| V<sub>E</sub> | 1.242 V |
| V<sub>B</sub> | 1.942 V |
| V<sub>C</sub> | 9.294 V |
| V<sub>CE</sub> | 8.052 V |

The app also recomputes I<sub>C</sub> with an independent nodal/KCL method and
shows the difference, so the result is not accepted from a single equation path.

## Setup

```bash
py -m venv .venv
.\.venv\Scripts\activate        # Windows PowerShell
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
```

## Run

```bash
flask --app app run --debug
# open http://127.0.0.1:5000/
```

## Test

```bash
python -m unittest discover -s tests -v
```

16 tests cover validation, the reference calculation, cutoff/saturation
warnings, region detection, unit conversion (kΩ vs Ω), the HTTP form flow and
the circuit → form → results layout order.
