def _parallel(r1, r2):
    return (r1 * r2) / (r1 + r2)


def _region_and_warnings(IB, IC, VCE):
    """จัดภูมิภาคการทำงานและข้อความเตือน ใช้ร่วมกันทั้งสามโหมด"""
    warnings = []
    if IB <= 0 or IC <= 0:
        warnings.append("Transistor likely in cutoff")
        region = "cutoff"
    else:
        VCE_sat = 0.2
        if VCE <= VCE_sat + 1e-9:
            warnings.append("Transistor likely in saturation (V_CE near/at saturation)")
            region = "saturation"
        else:
            region = "active"
    return region, warnings


def _result(IB, IC, IE, VB, VE, VC, VCE, region, warnings):
    """ผลลัพธ์รูปแบบเดียวกันทุกโหมด: V เป็นโวลต์, กระแสเป็นแอมแปร์"""
    return {
        "region": region,
        "IC": IC,
        "IB": IB,
        "IE": IE,
        "VB": VB,
        "VE": VE,
        "VC": VC,
        "VCE": VCE,
        "VTH": None,
        "RTH": None,
        "calc_a": None,
        "calc_b": None,
        "verification": None,
        "warnings": warnings,
    }


def calculate_fixed(VCC, RB, RC, beta, VBE):
    """Fixed Bias: R_B จาก V_CC ไปเบส, อิมิตเตอร์ลงกราวด์, R_C ที่คอลเลกเตอร์

    I_B = (V_CC - V_BE) / R_B
    """
    IB = (VCC - VBE) / RB
    IC = beta * IB
    IE = (beta + 1) * IB
    VE = 0.0
    VB = VBE
    VC = VCC - IC * RC
    VCE = VC - VE

    region, warnings = _region_and_warnings(IB, IC, VCE)
    return _result(IB, IC, IE, VB, VE, VC, VCE, region, warnings)


def calculate_emitter(VCC, RB, RC, RE, beta, VBE):
    """Emitter Bias: R_B จาก V_CC ไปเบส, R_E ที่อิมิตเตอร์, R_C ที่คอลเลกเตอร์

    I_B = (V_CC - V_BE) / [R_B + (beta + 1) R_E]
    """
    IB = (VCC - VBE) / (RB + (beta + 1) * RE)
    IC = beta * IB
    IE = (beta + 1) * IB
    VE = IE * RE
    VB = VE + VBE
    VC = VCC - IC * RC
    VCE = VC - VE

    region, warnings = _region_and_warnings(IB, IC, VCE)
    return _result(IB, IC, IE, VB, VE, VC, VCE, region, warnings)


def calculate_bias(VCC, R1, R2, RC, RE, beta, VBE):
    """Voltage-Divider Bias (วิธีเดิมของ Lab 2): Thevenin base-loop + nodal check"""
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
    IE_over_IC = (beta + 1) / beta
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
    tol = 1e-9 * max(1.0, abs(IC_a), abs(IC_b))
    agree = delta_ic <= max(tol, 1e-12)

    region, warnings = _region_and_warnings(IB_a, IC_a, VCE_a)

    result = _result(IB_a, IC_a, IE_a, VB_a, VE_a, VC_a, VCE_a, region, warnings)
    result.update({
        "VTH": VTH,
        "RTH": RTH,
        "calc_a": {"IB": IB_a, "IC": IC_a, "IE": IE_a, "VB": VB_a, "VE": VE_a, "VC": VC_a, "VCE": VCE_a},
        "calc_b": {"IB": IB_b, "IC": IC_b, "IE": IE_b, "VB": VB_b, "VE": VE_b, "VC": VC_b, "VCE": VCE_b},
        "verification": {"delta_ic": delta_ic, "agree": agree, "tolerance": tol},
    })
    return result
