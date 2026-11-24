# Gitlab

ใช้สำหรับเรียนแลป Compro ไฟฟ้า

## DC Circuit Calculator

โปรแกรมสำหรับคำนวณและวิเคราะห์วงจรไฟฟ้ากระแสตรง (DC) ทั้งตัวต้านทานแบบอนุกรม ขนาน และผสม โดยรับค่าแรงดันไฟฟ้าและค่าความต้านทานเพื่อคำนวณหาความต้านทานรวม กระแสไฟฟ้า และกำลังไฟฟ้า

## BJT Bias &amp; CE Simulator (Lab 02–06)

Flask web app สำหรับคำนวณ DC Operating Point ของวงจร BJT Common-Emitter 3 โหมด
(Voltage-Divider Bias / Fixed Bias / Emitter Bias) และจำลอง CE amplifier ด้วย ngspice
(`.op` / `.ac` / `.tran`) พร้อมตารางเทียบ Analytical vs ngspice — หน้าเว็บเรียงจากบนลงล่าง:
**วงจร → ฟอร์มกรอกค่า → ผลลัพธ์ → Engineering Model → Validation A1–A5 → NGSPICE COMPARISON**

- Repository: <https://github.com/B6810177/Gitlab>
- วิธีติดตั้ง/รัน/ทดสอบ/ตารางตรวจรับ: [README_BJT.md](README_BJT.md)
- เอกสารตรวจรับฉบับเต็ม: [docs/validation.md](docs/validation.md)

### Static version (ป้อนข้อมูลได้ทันที ไม่ต้องรัน Python)

เปิดไฟล์ [`index.html`](index.html) ด้วย Browser ได้โดยตรง หรือเปิดผ่าน GitHub Pages
หน้านี้เป็นเวอร์ชัน static เดิมของ Lab 2 (Voltage Divider เท่านั้น) คำนวณใน Browser ด้วย JavaScript
ส่วนชิ้นงาน Lab 3 ที่มี 3 โหมดและตาราง A1–A5 คือเวอร์ชัน Flask (`app.py`)

ถ้าจะใช้ GitHub Pages: Settings → Pages → Source: **Deploy from a branch** →
Branch: **main** / **(root)** → Save แล้วเปิด `https://b6810177.github.io/Gitlab/`

## Lab 4 — การเตรียมสภาพแวดล้อม

ผลตรวจการติดตั้ง Git / OpenCode Desktop / AI Model / Python:
[docs/lab4-environment.md](docs/lab4-environment.md)

## Lab 4 — ngspice CE amplifier

- ติดตั้ง ngspice 47 แล้วใช้ **console binary** (`ngspice_con.exe`) — `ngspice.exe` เป็น GUI
  และ `-b` ไม่พิมพ์ output เมื่อรันแบบ batch
- ตั้ง `NGSPICE_EXECUTABLE` ให้ชี้ถึง `ngspice_con.exe` (หรือปล่อยให้ `find_executable()` หาเอง)
- กด “โหลดค่าตัวอย่าง” → ติ๊ก “เทียบกับ ngspice” → เลือก `dc` / `ac` / `tran` → กด Calculate / Simulate
- ถ้าไม่มี ngspice แอปยังแสดงผล Analytical และขึ้น error แจ้งว่าติดตั้ง/ตั้ง path ต้องทำเพิ่ม
- ผลเทียบจริง, browser log และ screenshot: [docs/validation.md](docs/validation.md#lab-06--ce-voltage-divider-amplifier--ngspice-comparison)
  และ [captures/](captures/)

[Superpowers workflow record](docs/superpowers/workflow-record.md) — ลำดับการทำงานตามหัวข้อ 05 และหลักฐานที่รันจริง

## โครงสร้าง Web App (หลายไฟล์)

```
Gitlab/
├── app.py                      # Flask route: รับ HTTP request, แปลงหน่วย, ส่งผลให้ template
├── dc_bias.py                  # public entry point → bjt_bias/bias.py (3 โหมด)
├── spice_engine.py             # ngspice adapter: netlist → run → parse → simulate
├── bjt_bias/
│   ├── bias.py                 # สมการ DC bias (VTH, RTH, IB, IC, VCE, region)
│   ├── validate.py             # ตรวจอินพุต (comma, ช่องว่าง, ช่วงค่า)
│   └── validation_results.py   # ข้อมูลตารางตรวจรับ A1–A5
├── templates/
│   ├── base.html               # โครงหน้าเว็บ + โหลด CSS
│   └── index.html              # ฟอร์ม + ผลลัพธ์ (Jinja2)
├── static/
│   ├── style.css               # ธีม/เลย์เอาต์
│   └── app.js                  # ตัวคำนวณของหน้า static เดิม
├── tests/
│   ├── test_dc_bias.py         # ทดสอบสมการ/validation
│   ├── test_web.py             # ทดสอบ GET/POST และ layout
│   ├── test_spice_engine.py    # netlist/parser/corner + ngspice จริง
│   └── test_spice_web.py       # analysis selector, comparison, chart, degrade
├── docs/
│   ├── design-note.md          # สถาปัตยกรรม + data flow
│   ├── validation.md           # ผลตรวจรับ A1–A5 + ngspice Lab 06
│   ├── reflection.md           # สิ่งที่ learned จาก Lab
│   └── lab4-environment.md     # ผลตรวจ 2.1–2.4
├── captures/                   # screenshot จาก Browser จริง (Lab 06)
├── requirements.txt
├── AGENTS.md
└── README.md
```

## วิธีรัน (ต้องเปิดผ่าน Local Server — ห้าม double-click index.html)

```powershell
cd "C:\Users\B6810177\Desktop\Gitlab"
.\.venv\Scripts\python.exe -m flask --app app run --debug --port 5000
```

แล้วเปิด <http://127.0.0.1:5000/>

**ทำไมต้องเป็น Local Server:** หน้าเวอร์ชัน Flask (`app.py` + `templates/`) ต้องการ Backend
รับ `POST /` และให้ Python คำนวณ DC Operating Point — การเปิด `index.html` ด้วย `file://`
จะได้เฉพาะหน้า static (JavaScript คำนวณเอง) ซึ่งไม่ใช่ Web App ตามโจทย์ Lab 4

รันเทสต์: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`


