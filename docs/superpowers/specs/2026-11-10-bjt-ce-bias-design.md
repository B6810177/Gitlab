# BJT Common-Emitter DC Bias Web App Design

**Date:** 2026-11-10  
**Course:** ENG29 2121  
**Status:** Approved  
**Choices:** 1) (ก) Thevenin base-loop vs independent Nodal/KCL, 2) (ก) Add to existing repo under `bjt-bias/`

## Goal
Create the smallest working Flask web application to compute the DC operating point of a voltage-divider biased BJT Common-Emitter (CE) circuit. Separate engineering logic, Flask routes, HTML templates, CSS, and tests.

## Inputs
- `VCC` (V)
- `R1` (Ω)
- `R2` (Ω)
- `RC` (Ω)
- `RE` (Ω)
- `beta` (dimensionless)
- `VBE` (V)

## Outputs
- DC operating point with units: $I_B, I_C, I_E$ (A/mA), $V_B, V_E, V_C, V_{CE}$ (V), $V_{TH}, R_{TH}$ (V, Ω)
- Input validation with field-level errors
- Region warnings (cutoff/saturation)
- Verification panel comparing two independent calculations

## Architecture

### File Structure
```
Gitlab/
├── bjt_bias/
│   ├── __init__.py
│   ├── bias.py      # Pure engineering logic (no Flask imports)
│   └── validate.py  # Input validation and normalization
├── app.py           # Flask routes only
├── templates/
│   ├── base.html
│   └── index.html   # Form + results + verification + warnings
├── static/
│   └── style.css
├── tests/
│   ├── test_bias.py # Math, regions, validation, agreement
│   └── test_app.py  # Route tests
├── requirements.txt
└── README_BJT.md
```

### Engineering Logic (`bjt_bias/bias.py`)
**Calc A (Primary - Thevenin base-loop):**
- $V_{TH} = V_{CC}\frac{R_2}{R_1+R_2}$
- $R_{TH} = R_1 \parallel R_2 = \frac{R_1 R_2}{R_1 + R_2}$
- $I_B = \frac{V_{TH} - V_{BE}}{R_{TH} + (\beta+1)R_E}$
- $I_C = \beta I_B$, $I_E = (\beta+1)I_B$
- $V_E = I_E R_E$, $V_B = V_E + V_{BE}$, $V_C = V_{CC} - I_C R_C$, $V_{CE} = V_C - V_E$

**Calc B (Independent - Nodal/KCL):**
Compute $I_C$ via an independent node equation set (KCL at base node) and compare with Calc A. Return both values, $|\Delta I_C|$, and pass/fail status.

**Agreement:** Require agreement within tolerance (e.g., $1\times10^{-9}$ relative or absolute). Report in verification panel.

### Validation (`bjt_bias/validate.py`)
- Reject bool, non-finite values
- $V_{CC} > 0$
- $R_1,R_2,R_C,R_E > 0$
- $\beta > 0$ (finite)
- $0.4 \le V_{BE} < V_{CC}$
- Return field-level errors

### Region Detection & Warnings
- $V_{CE(sat)} \approx 0.2\,\text{V}$ (warn only, never clamp)
- **Cutoff:** if $I_B \le 0$ or $I_C \le 0$ → "Transistor likely in cutoff"
- **Saturation:** if $V_{CE} \le V_{CE(sat)} + \epsilon$ (small numerical tolerance) → "Transistor likely in saturation (V_CE near/at saturation)"
- **Active:** otherwise, no region warning

### UI
- Form with inputs for all 7 parameters (with units)
- Results table with all operating point values (A/mA, V, Ω)
- Verification panel: Calc A, Calc B, $|\Delta I_C|$, agreement status
- Inline validation errors and highlighted warnings

### Tests
- Known example test
- Cutoff case
- Saturation case
- Validation error cases
- Independent calculation agreement test
- Basic route tests (GET/POST)

## Dependencies
- `requirements.txt`: `Flask` (stable version)
- Tests use `unittest` (consistent with existing repo style)

## Constraints
- No AC, transient, full circuit editor, or FET
- Engineering logic must be separate from routes
- HTML, CSS, templates, tests all separate as specified

## Workflow (Post-Approval)
1. Create design doc (this file) - done
2. Invoke `writing-plans` to create implementation plan
3. Review plan with user, choose execution approach (`subagent-driven-development` or `executing-plans`)
4. Execute approved tasks with tests/reviews
5. Run localhost demo, commit and push to GitHub today
