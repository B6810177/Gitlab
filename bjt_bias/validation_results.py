"""ผลตรวจรับ A1–A5 สำหรับแสดงบนหน้าเว็บ

ค่าอ้างอิงในไฟล์นี้คำนวณแยกจากโปรแกรมด้วยสมการในตำรา Engineering Electronics
(ดูรายละเอียดและสมการใน docs/validation.md) โดยไม่ได้เรียกใช้ bjt_bias.bias
ผลที่เห็นจริงบันทึกจากการตรวจด้วย OpenCode Browser เมื่อ 2026-11-17

ทุกค่าถูกจัดรูปแบบเป็นข้อความฝั่ง Python เพื่อให้ template มีแต่การแสดงผล
ไม่มี logic การคำนวณใน HTML
"""

VALIDATION_DATE = "2026-11-17"
VALIDATION_SHARED = "VCC = 12 V · RC = 2.2 kΩ · β = 100 · VBE = 0.70 V"
VALIDATION_TOLERANCE = (
    "เกณฑ์: |ΔIC| ≤ 0.01 mA และ |ΔVCE| ≤ 0.02 V "
    "เทียบกับค่าอ้างอิงที่ยังไม่ปัดเศษ"
)
VALIDATION_DOC = "docs/validation.md"
VALIDATION_METHOD = "OpenCode Browser"


def _numeric_row(case_id, title, mode, inputs, exp_ic, exp_vce, obs_ic, obs_vce, note=""):
    """สร้างแถวผลตรวจที่มีตัวเลข IC/VCE พร้อมผลต่าง (คำนวณฝั่ง Python)"""
    return {
        "case_id": case_id,
        "title": title,
        "mode": mode,
        "inputs": inputs,
        "expected": f"IC = {exp_ic:.6f} mA · VCE = {exp_vce:.6f} V",
        "observed": f"IC = {obs_ic:.3f} mA · VCE = {obs_vce:.3f} V",
        "delta": (
            f"ΔIC = {abs(obs_ic - exp_ic):.6f} mA · "
            f"ΔVCE = {abs(obs_vce - exp_vce):.6f} V"
        ),
        "method": VALIDATION_METHOD,
        "status": "PASS",
        "note": note,
    }


VALIDATION_CASES = [
    _numeric_row(
        "A1",
        "โหมดเดิม",
        "Voltage Divider Bias",
        "R1 = 100 kΩ · R2 = 22 kΩ · RC = 2.2 kΩ · RE = 1 kΩ",
        1.229858,
        8.052155,
        1.230,
        8.052,
        "ค่าตรงกับ Lab 2 ก่อนแก้ (IC 1.230 mA · VCE 8.052 V)",
    ),
    _numeric_row(
        "A2",
        "Fixed Bias",
        "Fixed Bias",
        "RB = 1 MΩ (1000 kΩ) · RC = 2.2 kΩ · ไม่ต้องกรอก RE",
        1.130000,
        9.514000,
        1.130,
        9.514,
        "ฟอร์มมีเฉพาะ VCC, β, VBE, RB, RC — ไม่มีช่อง RE",
    ),
    _numeric_row(
        "A3",
        "Emitter Bias",
        "Emitter Bias",
        "RB = 1 MΩ (1000 kΩ) · RE = 1 kΩ · RC = 2.2 kΩ",
        1.026340,
        8.705450,
        1.026,
        8.705,
        "มีช่อง RE และใช้ค่าที่กรอก (1 kΩ)",
    ),
    _numeric_row(
        "A4",
        "เปลี่ยนค่าเดียว",
        "Emitter Bias",
        "เหมือน A3 ทุกค่า แต่เปลี่ยนเฉพาะ RE = 2 kΩ",
        0.940100,
        8.032779,
        0.940,
        8.033,
        "ทำนายก่อนรันว่า IC ต้องลดลงเมื่อ RE ใหญ่ขึ้น — ผลจริงลดลง "
        "1.026 → 0.940 mA ตรงตามทำนาย",
    ),
    {
        "case_id": "A5",
        "title": "อินพุตผิด",
        "mode": "Fixed Bias",
        "inputs": "RB = 0 · RC = 2.2 kΩ · VCC = 12 V · β = 100 · VBE = 0.70 V",
        "expected": "Flask ต้องแจ้ง error เรื่อง RB, หน้าเว็บไม่ล่ม และไม่แสดงผลของรอบก่อน",
        "observed": (
            "“Fixed Bias: RB must be greater than 0” · ไม่มี metrics · "
            "ฟอร์มยังอยู่ · ขึ้น empty state"
        ),
        "delta": None,
        "method": f"{VALIDATION_METHOD} + POST ตรงถึง Flask",
        "status": "PASS",
        "note": (
            "ฟอร์มมี novalidate และ POST ตรงถึง Flask ให้ HTTP 200 พร้อมข้อความเดียวกัน "
            "— ข้อความจึงมาจาก Flask ไม่ใช่แค่การบล็อกของฟอร์ม"
        ),
    },
]
