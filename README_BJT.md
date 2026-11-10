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
