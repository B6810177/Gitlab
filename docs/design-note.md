# Design Note — โครงสร้าง Web App

เอกสารนี้อธิบายว่าแอปทำงานอย่างไรในฐานะ Web App หลายไฟล์
(ไม่ใช่ HTML ไฟล์เดียวที่คำนวณใน Browser)

## ภาพรวม

```
Browser / Form          Flask Server              Engineering Module        DC Results
templates/index.html -> app.py (GET/POST)   ->   bjt_bias/bias.py     ->   voltage / current
static/style.css        HTTP request/response      Python functions          HTML response
```

- **Frontend** = HTML form + CSS ที่ Browser แสดง
- **Backend** = Flask route ใน `app.py` รับ HTTP request
- **Engineering module** = ฟังก์ชัน Python ที่คำนวณ DC bias (`dc_bias.py` → `bjt_bias/bias.py`)
- **Results** = ค่าที่ผ่าน Jinja2 กลับไปแสดงใน Browser

## หน้าที่ของแต่ละไฟล์

| ไฟล์ | หน้าที่ | ไม่ควรทำ |
|---|---|---|
| `app.py` | รับ request, ตรวจ unit, เรียก validate/calculate, ส่งค่าลง template | ไม่เก็บสมการวิศวกรรม |
| `dc_bias.py` | re-export ฟังก์ชันคำนวณตามตัวอย่างโครงสร้าง Lab 04 | ไม่เก็บสมการซ้ำ |
| `bjt_bias/bias.py` | คำนวณ VTH, RTH, IB, IC, IE, VB, VE, VC, VCE และ region | ไม่รู้จัก Flask/HTML |
| `bjt_bias/validate.py` | ตรวจชนิด/ช่วงของอินพุต, ตัด comma | ไม่คำนวณ bias |
| `templates/index.html` | แสดงฟอร์ม/ผลลัพธ์ด้วย Jinja2 | ไม่มีสูตรคำนวณ |
| `templates/base.html` | โครงหน้า, header, footer, โหลด CSS | ไม่มี logic ธุรกิจ |
| `static/style.css` | เลย์เอาต์/สี/responsive | ไม่มีข้อมูลธุรกิจ |
| `tests/` | ตรวจสมการ, validation, HTTP flow, ลำดับหน้า | ไม่เรียกเน็ตเวิร์กจริง |

## ลำดับการทำงานของ 1 request

1. Browser เปิด `GET /` → Flask ส่งฟอร์มว่าง (ช่องกรอกเริ่มว่าง)
2. ผู้ใช้กรอก VCC, R1, R2, RC, RE, β, VBE แล้วกด **Calculate**
3. Browser ส่ง `POST /` พร้อมข้อมูลฟอร์ม (HTML form, `application/x-www-form-urlencoded`)
4. `app.py`:
   - อ่านค่าและหน่วย (kΩ/Ω)
   - เรียก `validate.validate_inputs(...)` → ได้ค่าตัวเลข
   - แปลง kΩ → Ω ถ้าจำเป็น
   - เรียก `bias.calculate_bias(...)`
5. Template แสดง region + ค่า VB, VE, VC, VCE, IC, IB, IE, VTH, RTH
6. ถ้าอินพุตผิด → แสดงข้อความ error ใต้หัวข้อ "ไม่สามารถคำนวณได้" โดยไม่ทำให้หน้าเว็บล่ม

## ทำไมต้องรันผ่าน Local Server

ต้องเปิดที่ `http://127.0.0.1:5000/` เพราะต้องให้ Flask รับ request
และ Python เป็นผู้คำนวณ — การ double-click เปิด `index.html` จะได้ `file://`
ซึ่งไม่มี Backend และไม่ใช่การทำงานของ Web App ตามโจทย์

## การทดสอบ

- `tests/test_dc_bias.py` — สมการอ้างอิง, region, validation, ตัวเลขหลักเยอะ
- `tests/test_web.py` — GET/POST, error case, การแปลงหน่วย, ลำดับ layout
- รัน: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`

## ข้อจำกัด (Week 2)

ทำเฉพาะ DC Bias — ไม่มี Bode Plot, Transient, Signal Generator,
Overlay Animation หรือ SPICE Solver
