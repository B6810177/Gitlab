import math


def _to_float(name, val):
    """Parse a number, tolerating thousands separators and spaces.

    Accepts values such as 1000000, 1,000,000, 1 000 000 or 2.2e3 so the
    input fields can hold arbitrarily long numbers without being truncated.
    """
    if isinstance(val, bool):
        raise ValueError(f"{name} must be a finite number")
    if isinstance(val, str):
        val = val.strip().replace(",", "").replace(" ", "")
    try:
        f = float(val)
    except (TypeError, ValueError) as e:
        raise ValueError(f"{name} must be a finite number") from e
    if not math.isfinite(f):
        raise ValueError(f"{name} must be a finite number")
    return f


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
    result = {name: _to_float(name, val) for name, val in values.items()}

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
