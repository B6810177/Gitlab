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


def _check_vcc(result):
    if result["VCC"] <= 0:
        raise ValueError("VCC must be greater than 0")


def _check_resistors(result, names):
    for name in names:
        if result[name] <= 0:
            raise ValueError(f"{name} must be greater than 0")


def _check_device(result):
    if result["beta"] <= 0:
        raise ValueError("beta must be greater than 0")
    if result["VBE"] < 0.4 or result["VBE"] >= result["VCC"]:
        raise ValueError("VBE must be between 0.4 V and VCC (exclusive of VCC)")


def validate_inputs(vcc, r1, r2, rc, re, beta, vbe):
    """ตรวจอินพุตของโหมด Voltage-Divider Bias"""
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

    _check_vcc(result)
    _check_resistors(result, ("R1", "R2", "RC", "RE"))
    _check_device(result)
    return result


def validate_fixed(vcc, rb, rc, beta, vbe):
    """ตรวจอินพุตของโหมด Fixed Bias (ไม่มี R_E)"""
    values = {
        "VCC": vcc,
        "RB": rb,
        "RC": rc,
        "beta": beta,
        "VBE": vbe,
    }
    result = {name: _to_float(name, val) for name, val in values.items()}

    _check_vcc(result)
    _check_resistors(result, ("RB", "RC"))
    _check_device(result)
    return result


def validate_emitter(vcc, rb, rc, re, beta, vbe):
    """ตรวจอินพุตของโหมด Emitter Bias"""
    values = {
        "VCC": vcc,
        "RB": rb,
        "RC": rc,
        "RE": re,
        "beta": beta,
        "VBE": vbe,
    }
    result = {name: _to_float(name, val) for name, val in values.items()}

    _check_vcc(result)
    _check_resistors(result, ("RB", "RC", "RE"))
    _check_device(result)
    return result


def validate_ce(rl, cin, cout, source_v, source_f):
    """ตรวจค่าของ CE amplifier ที่ใช้ใน analysis แบบ ac/tran

    ค่าที่ส่งเข้ามายังเป็นหน่วยที่ผู้ใช้กรอก (RL เป็น Ω หรือ kΩ ตาม unit,
    C เป็น µF, แหล่งเป็น mV peak และ Hz) — การแปลงหน่วยทำที่ app.py
    """
    values = {
        "RL": rl,
        "CIN": cin,
        "COUT": cout,
        "SOURCE_V": source_v,
        "SOURCE_F": source_f,
    }
    result = {name: _to_float(name, val) for name, val in values.items()}
    for name, value in result.items():
        if value <= 0:
            raise ValueError(f"{name} must be greater than 0")
    return result
