# BJT Common-Emitter DC Bias Calculator

Flask web app สำหรับคำนวณ DC Operating Point (Q-point) ของ BJT NPN แบบ Common-Emitter
รองรับ 3 โหมดไบอัส — **Voltage Divider Bias**, **Fixed Bias** และ **Emitter Bias**
(ENG29 2121 · Lab 02–03) พร้อมตารางผลตรวจรับ **A1–A5** แสดงอยู่ในหน้าเว็บ
และต่อยอดเป็น Lab 06: จำลอง CE amplifier ด้วย ngspice (`.op` / `.ac` / `.tran`)
เทียบกับสมการวิศวกรรมในหน้าเดียวกัน

## ข้อมูลส่งงาน

| รายการ | ค่า |
|---|---|
| GitHub repository | <https://github.com/B6810177/Gitlab> |
| Branch | `main` |
| Commit SHA (งาน Lab 3) | `d57f6b22d82e7727e507fa2f0981576c526d26b8` |
| เปิดเว็บ (หลังรัน Flask) | <http://127.0.0.1:5000/> |
| ตารางตรวจรับในแอป | เมนูหน้าเว็บส่วน **04 · VALIDATION A1–A5** |
| ตารางเทียบ ngspice | เมนูหน้าเว็บส่วน **05 · NGSPICE COMPARISON** |
| เอกสารตรวจรับฉบับเต็ม | [`docs/validation.md`](docs/validation.md) |
| ภาพจาก Browser จริง | [`captures/`](captures/) |

> เวอร์ชัน Flask (`app.py` + `templates/`) คือชิ้นงาน Lab 3
> ส่วน `index.html` + `static/app.js` ที่ราก repo เป็นเวอร์ชัน static เดิมของ Lab 2
> (คำนวณใน Browser, มีเฉพาะ Voltage Divider) ใช้เปิดดูได้โดยไม่ต้องรัน Python

## วิธีรันและเปิดเว็บ

ต้องมี Python 3.10+ (ทดสอบด้วย Python 3.14.2) และ Flask 3.0.3 ตาม `requirements.txt`

```powershell
# Windows PowerShell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app app run --debug
```

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug
```

เปิด <http://127.0.0.1:5000/> — หน้าเว็บเรียงจากบนลงล่าง:
วงจร → ฟอร์มกรอกค่า → ผลลัพธ์ → Engineering Model → Validation A1–A5 → NGSPICE COMPARISON

### ngspice (Lab 06 — ไม่บังคับสำหรับ Lab 2–3)

ต้องมี ngspice 47 และใช้ไฟล์ **console** (`ngspice_con.exe`) เพราะ `ngspice.exe` เป็น GUI
แล้ว `-b` ไม่พิมพ์ stdout ในเครื่องที่ทดสอบ

```powershell
$env:NGSPICE_EXECUTABLE = "C:\Users\B6810177\AppData\Local\Temp\opencode\ngspice47\Spice64\bin\ngspice_con.exe"
& $env:NGSPICE_EXECUTABLE -v
```

ไม่ตั้ง env ก็ได้ — `spice_engine.find_executable()` จะหาใน `PATH` และตำแหน่งติดตั้งมาตรฐานเอง
ถ้าไม่เจอ หน้าเว็บจะแจ้ง error แต่ผล Analytical ยังแสดงอยู่

## วิธีทดสอบ

```bash
python -m unittest discover -s tests -v
```

ผลปัจจุบัน: **45 tests OK** ครอบคลุมการตรวจอินพุต, ค่าอ้างอิง, region detection,
คำเตือน cutoff/saturation, การแปลงหน่วย kΩ ↔ Ω, HTTP flow และลำดับ layout
(วงจร → ฟอร์ม → ผลลัพธ์), netlist/parser ของ ngspice, การหา fL/fH แบบ interpolate
และ HTTP flow ของ analysis ทั้งสามแบบ (รวมกรณีไม่มี ngspice)

## โหมดไบอัสและสมการ

ใช้ Forward-Active Approximation (β คงที่, V<sub>BE</sub> คงที่)

**Voltage Divider Bias**

```
VTH = VCC · R2 / (R1 + R2)
RTH = R1 · R2 / (R1 + R2)
IB  = (VTH − VBE) / [RTH + (β + 1)·RE]
```

**Fixed Bias** (อิมิตเตอร์ต่อกราวด์ ไม่มี R<sub>E</sub>)

```
IB = (VCC − VBE) / RB
```

**Emitter Bias**

```
IB = (VCC − VBE) / [RB + (β + 1)·RE]
```

ทุกโหมดใช้ร่วมกัน:

```
IC  = β · IB
IE  = (β + 1) · IB
VE  = IE · RE          (Fixed Bias: VE = 0)
VB  = VE + VBE
VC  = VCC − IC · RC
VCE = VC − VE
```

Region: `IB ≤ 0` → **Cutoff**, `VCE ≤ 0.2 V` → **Saturation**, อื่น ๆ → **Forward Active**
(ผลนอก Forward Active จะมีคำเตือนเพราะสมการประมาณไม่ตรงช่วงนั้น)

## จุดที่โค้ดเลือกโหมดและแปลงหน่วย

| งาน | ไฟล์และตำแหน่ง |
|---|---|
| เมนูเลือกโหมดบนฟอร์ม | `templates/index.html` บรรทัด 214 (`<select name="mode">`) |
| อ่านค่า `mode` จาก POST (ไม่ส่งมา = `divider`) | `app.py` `index()` บรรทัด 85 |
| เลือกฟังก์ชันตรวจ/คำนวณตามโหมด | `app.py` `_calculate()` บรรทัด 45–66 |
| รายชื่อช่องความต้านทานของแต่ละโหมด | `app.py` `RESISTOR_FIELDS` บรรทัด 24 |
| แปลง kΩ → Ω ก่อนคำนวณ | `app.py` บรรทัด 68–70 (`if unit == "kohm": v[name] *= 1000.0`) |
| ฟังก์ชันคำนวณ | `bjt_bias/bias.py` (`calculate_bias`, `calculate_fixed`, `calculate_emitter`) |
| ฟังก์ชันตรวจอินพุต | `bjt_bias/validate.py` (`validate_inputs`, `validate_fixed`, `validate_emitter`) |
| ข้อมูลตาราง A1–A5 ที่แสดงบนเว็บ | `bjt_bias/validation_results.py` ส่งผ่าน `app.py` → `render_template` |

ทุกโหมดคืนค่าเป็น `dict` หน้าตาเดียวกัน:
`VB, VE, VC, VCE` (V), `IC, IB, IE` (A), `region`, `warnings`
ส่วน `VTH, RTH, calc_a, calc_b, verification` เป็น `None` ในโหมด Fixed/Emitter
(ไม่มีในสมการของโหมดนั้น)

## ค่าอ้างอิงอิสระ (ไม่ได้มาจากโปรแกรมที่ตรวจ)

คำนวณด้วยสมการตำรา Engineering Electronics โดยตรง (ไม่ import `bjt_bias`)
ใช้ร่วมกัน V<sub>CC</sub> = 12 V, R<sub>C</sub> = 2.2 kΩ, β = 100, V<sub>BE</sub> = 0.70 V

| กรณี | อินพุต | IB (µA) | IC (mA) | VCE (V) |
|---|---|---|---|---|
| A1 Divider | R1 = 100 kΩ, R2 = 22 kΩ, RE = 1 kΩ | 12.298581 | **1.229858** | **8.052155** |
| A2 Fixed | RB = 1 MΩ | 11.300000 | **1.130000** | **9.514000** |
| A3 Emitter | RB = 1 MΩ, RE = 1 kΩ | 10.263397 | **1.026340** | **8.705450** |
| A4 Emitter | RB = 1 MΩ, RE = 2 kΩ | 9.400998 | **0.940100** | **8.032779** |

ตัวอย่างการแทนค่า A3 (Emitter Bias):

```
IB = (12 − 0.70) / [1000 + (100 + 1)(1)] = 0.010263397 mA
IC = 100 × 0.010263397 = 1.026340 mA
VE = 101 × 0.010263397 × 1 = 1.036603 V
VC = 12 − 1.026340 × 2.2 = 9.742053 V
VCE = 9.742053 − 1.036603 = 8.705450 V
```

## ตารางตรวจรับ A1–A5

เกณฑ์: **|ΔIC| ≤ 0.01 mA** และ **|ΔVCE| ≤ 0.02 V** เทียบกับค่าอ้างอิงที่ยังไม่ปัดเศษ
ฟอร์มแสดง 3 ตำแหน่งทศนิยม (ความคลาดจากการปัด ≤ 0.0005)

| กรณี | โหมด / อินพุต | คาดหมาย | เห็นจริง | วิธีตรวจ | สถานะ |
|---|---|---|---|---|---|
| A1 · โหมดเดิม | Divider · R1 100 kΩ, R2 22 kΩ, RC 2.2 kΩ, RE 1 kΩ | IC 1.229858 mA · VCE 8.052155 V | IC 1.230 mA · VCE 8.052 V (ΔIC 0.000142, ΔVCE 0.000155) | OpenCode Browser | **PASS** |
| A2 · Fixed | Fixed · RB 1 MΩ, RC 2.2 kΩ (ไม่กรอก RE) | IC 1.130000 mA · VCE 9.514000 V; ฟอร์มไม่มีช่อง RE | IC 1.130 mA · VCE 9.514 V (Δ 0 / 0); ไม่มีช่อง RE | OpenCode Browser | **PASS** |
| A3 · Emitter | Emitter · RB 1 MΩ, RE 1 kΩ, RC 2.2 kΩ | IC 1.026340 mA · VCE 8.705450 V; มีช่อง RE | IC 1.026 mA · VCE 8.705 V (ΔIC 0.000340, ΔVCE 0.000450) | OpenCode Browser | **PASS** |
| A4 · เปลี่ยนค่าเดียว | Emitter · เหมือน A3 แต่ RE 2 kΩ | **ทำนาย: IC ลดลง** เพราะ RE ใหญ่ขึ้น → ตัวส่วนใหญ่ขึ้น → IB/IC ลด; คาด IC 0.940100 mA · VCE 8.032779 V | IC 0.940 mA · VCE 8.033 V (ΔIC 0.000100, ΔVCE 0.000221) — ลดจาก 1.026 → 0.940 mA ตรงทำนาย | OpenCode Browser | **PASS** |
| A5 · อินพุตผิด | Fixed · RB = 0 | Flask แจ้ง error เรื่อง RB, หน้าเว็บไม่ล่ม, ไม่มีผลรอบก่อน | “Fixed Bias: RB must be greater than 0”, ไม่มี metrics, ฟอร์มยังอยู่ | OpenCode Browser + POST ตรงถึง Flask | **PASS** |

### หลักฐานจากหน้าเว็บ

- Snapshot หลังส่งฟอร์ม A1:
  `"DC Operating Point (Q-Point) · Voltage Divider Bias"` … `"8.052"` `"V"` … `"1.230"` `"mA"`
- Snapshot หลังส่งฟอร์ม A5:
  `"ไม่สามารถคำนวณได้ — ตรวจสอบข้อมูลที่กรอก"` → `"Fixed Bias: RB must be greater than 0"` → `"ยังไม่มีผลลัพธ์ · Fixed Bias"`
- ภาพหน้าจอ A5: [`docs/validation-artifacts/A5-fixed-rb0.png`](docs/validation-artifacts/A5-fixed-rb0.png)
- ภาพหน้าจอตารางในแอป: [`docs/validation-artifacts/validation-table.png`](docs/validation-artifacts/validation-table.png)
- A5 ตรวจซ้ำด้วย POST ตรงถึง Flask (`urllib`, `mode=fixed&RB=0…`): HTTP 200,
  ข้อความเดียวกัน, ไม่มีบล็อก `.metrics` → ยืนยันว่า Flask ตรวจค่าเอง
  (ฟอร์มมี `novalidate` จึงไม่ได้ถูกบล็อกฝั่ง Browser)

## Lab 06 — เปรียบเทียบ Analytical กับ ngspice

ใช้ค่าตัวอย่าง (VCC 12 V · 100k/22k/2.2k/1k · RL 10k · Cin=Cout 10 µF · SIN 10 mV / 1 kHz)
แล้วติ๊ก “เทียบกับ ngspice” ในฟอร์ม

| Analysis | ผล Analytical | ผล ngspice | หมายเหตุ |
|---|---|---|---|
| `.op` | IC 1.229858 mA · VCE 8.052155 V | IC 1.229835 mA · VCE 8.052228 V | ΔIC 0.000023 mA, ΔVCE 0.000073 V |
| `.ac` | Gain 1.766× · fL 8.55 Hz | Gain 1.749× · fL 1.83 Hz · fH 58.69 MHz | แหล่ง AC ในอุดมคติ (Rs=0) ทำให้ Cin ไม่สร้าง high-pass |
| `.tran` | Vout(p-p) 35.323 mV · gain 1.766× | Vout(p-p) 34.981 mV · gain 1.749× | 5,008 samples, ตรงกับ gain จาก `.ac` |

รายละเอียดวิธีตั้งค่า, netlist, browser log และ screenshot: [`docs/validation.md`](docs/validation.md)

## เครื่องมือตรวจและบทบาท MCP

- วิธีที่ใช้จริง: **OpenCode Browser** — Browser Tool ในตัว OpenCode Desktop
  (เปิดหน้าเว็บจริง, เลือกโหมด, กรอกฟอร์ม, กด Calculate, อ่าน Snapshot/DOM)
- **ไม่ได้ใช้ Playwright MCP** เพราะยังไม่ได้ตั้งค่า MCP server ในเครื่อง
  (ติดตั้ง Node.js portable ไว้แล้ว แต่ไม่ได้ดึงแพ็กเกจ `@playwright/mcp`)
  จึงใช้ Browser Tool ในตัวแทน ซึ่งตรวจหน้าเว็บจริงได้เท่ากัน
- MCP ในบริบทนี้คือ protocol ที่ให้ AI เรียกเครื่องมือภายนอก (เช่น Browser MCP)
  เพื่อสั่งเปิด/อ่านหน้าเว็บ วิธีตรวจคนละวิธีให้ผลเท่ากันหากได้รันเคสจริงครบ
  และอ่านค่าจากหน้าจอ/DOM จริง

## AI ช่วยอะไร และนักศึกษาตรวจอะไร

**AI สร้างโค้ดส่วนเหล่านี้**

- `bjt_bias/bias.py` — `calculate_fixed`, `calculate_emitter` และ helper ที่ใช้ร่วมกับ Divider
- `bjt_bias/validate.py` — `validate_fixed`, `validate_emitter` และการตรวจอินพุตร่วม
- `app.py` — route, การเลือกฟังก์ชันตามโหมด (`_calculate`), การแปลงหน่วย kΩ → Ω
- `templates/index.html`, `static/style.css` — ฟอร์ม 3 โหมด, วงจร SVG, ตาราง A1–A5,
  analysis selector, ตารางเทียบ ngspice และกราฟ SVG
- `bjt_bias/validation_results.py` — ข้อมูลผลตรวจที่แสดงบนเว็บ
- `spice_engine.py` — netlist/run/parse สำหรับ `.op` / `.ac` / `.tran`
- `tests/` — unittest 45 เคส และ `docs/validation.md` — เอกสารตรวจรับ (รวม Lab 06)

**นักศึกษาตรวจ**

- ทวนสมการทั้งสามโหมดกับตำรา Engineering Electronics และแทนค่า A3 ด้วยมือ
  (ผลตรงกับค่าอ้างอิสระด้านบน)
- รัน A4 ซ้ำใน Browser: คงโหมด Emitter และ VCC 12 / RB 1000 / RC 2.2 / β 100 / VBE 0.70
  เปลี่ยนเฉพาะ RE 1 → 2 kΩ แล้วกด Calculate — ได้ IC 1.026 → 0.940 mA (ลดลงตามทำนาย)
- ยืนยันว่า Divider ยังได้ IC 1.230 mA · VCE 8.052 V เท่า Lab 2 ก่อนแก้
- รัน Lab 06 ซ้ำใน Browser: โหลดค่าตัวอย่าง → ติ๊กเทียบ ngspice → เปลี่ยน `dc`/`ac`/`tran`
  แล้วดูตาราง 05 · NGSPICE COMPARISON ว่าผลสองวิธีใกล้กัน (DC ΔIC ≤ 0.01 mA)
- ตรวจ `git diff` และ `git diff --staged` ก่อน commit ว่าไม่มี `.venv`, `.env`
  หรือ credentials ถูก stage

## โครงสร้างโปรเจกต์

```
app.py                      Flask route, เลือกโหมด/analysis, แปลงหน่วย kΩ → Ω
spice_engine.py             ngspice adapter (build_netlist/run/parse/simulate)
bjt_bias/
  validate.py               ตรวจอินพุตแยกตามโหมด
  bias.py                   คำนวณ Q-point + ตรวจ region
  validation_results.py     ข้อมูลตาราง A1–A5 ที่แสดงบนเว็บ
templates/
  base.html                 page shell
  index.html                วงจร → ฟอร์ม → ผลลัพธ์ → model → validation → ngspice
static/
  style.css                 responsive layout + validation/comparison table + chart
tests/
  test_bias.py              engineering/unit tests
  test_app.py               Flask HTTP tests
  test_spice_engine.py      netlist/parser/corner + ngspice จริง
  test_spice_web.py         analysis selector/comparison/chart/degrade
docs/
  validation.md             ตารางตรวจรับฉบับเต็ม + สมการ + หลักฐาน + Lab 06
  validation-artifacts/     ภาพหน้าจอหลักฐาน Lab 3
captures/                   ภาพหน้าจอ ngspice comparison จาก Browser จริง
requirements.txt
```

## หมายเหตุการทำซ้ำ

- ทดสอบบน Windows ด้วย Python 3.14.2 และ Flask 3.0.3
- `app.py` ตั้ง `Cache-Control: no-store` ให้หน้า HTML เพื่อไม่ให้เห็นผลเก่าหลังแก้ template
- ไฟล์ที่ไม่ commit: `.venv/`, `.env`, `__pycache__/`, `*.pyc` (อยู่ใน `.gitignore`)
