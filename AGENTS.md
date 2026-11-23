# AGENTS.md — แนวทางสำหรับ AI/ผู้พัฒนาที่แก้โค้ดใน repo นี้

## โปรเจกต์คืออะไร

Flask Web Application สำหรับคำนวณ DC Operating Point ของวงจร BJT Common-Emitter
(Voltage Divider / Fixed / Emitter Bias) — งาน Lab 02–04 ของ ENG29 2121

## Stack

- Python 3.12 + Flask 3.0.3
- Jinja2 templates + CSS (ไม่มี JavaScript framework)
- unittest (tests/), GitHub (origin/main)
- Static page (`index.html` + `static/app.js`) เป็นเวอร์ชันเสริมของ Lab 2

## โครงสร้างและหน้าที่

```
app.py                    HTTP routes, form parsing, unit conversion
dc_bias.py                public entry point → bjt_bias.bias (ตามตัวอย่าง Lab 04)
bjt_bias/bias.py          สมการวิศวกรรม (ไม่รู้จัก HTML/HTTP)
bjt_bias/validate.py      ตรวจสอบอินพุต (รวม comma/ช่องว่าง)
bjt_bias/validation_results.py  ข้อมูลตารางตรวจรับ A1–A5
templates/index.html      ฟอร์ม + ผลลัพธ์ (Jinja2)
templates/base.html       โครงหน้าเว็บ
static/style.css          หน้าตา/เลย์เอาต์
static/app.js             ตัวคำนวณฝั่ง Browser (static version)
tests/                    unittest: สมการ, validation, HTTP flow, layout
docs/                     design-note, validation, reflection, lab4
```

## คำสั่งที่ใช้

```powershell
# ติดตั้ง (ครั้งแรก)
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# รันเว็บ (ต้องเปิดผ่าน Local Server เท่านั้น)
.\.venv\Scripts\python.exe -m flask --app app run --debug --port 5000

# ทดสอบ
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## กติกาการแก้โค้ด

1. **แยกหน้าที่**: `bjt_bias/` ห้าม import Flask หรืออ่าน request; template ห้ามมีสมการคำนวณ; route ทำแค่รับค่า/เรียกฟังก์ชัน/ส่งผล
2. **ทุกการแก้สมการต้องมีเทสต์** และรัน `unittest` ให้ผ่านก่อน commit
3. **อินพุตผู้ใช้ต้องผ่าน `validate`** — รองรับ comma คั่นหลักพัน, ตรวจค่าติดลบ/ศูนย์/ช่วง VBE
4. **หน่วย kΩ ↔ Ω** แปลงที่ `app.py` ก่อนเรียกฟังก์ชันคำนวณ
5. **UI ภาษาไทย** ใช้ `static/style.css` ร่วมกันทุกหน้า; รักษาความสอดคล้องของธีม
6. **ห้าม commit** ไฟล์ `.venv/`, `__pycache__/`, ข้อมูลลับ หรือ token
7. Commit message ภาษาอังกฤษ ขึ้นต้นด้วย `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
8. ก่อนบอกว่างานเสร็จ ให้รันเทสต์และรายงานผลจริง (evidence before claims)
