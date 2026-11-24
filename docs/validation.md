# Validation — ตารางตรวจรับ A1–A5

วันที่ตรวจ: 2026-11-17
แอปที่ตรวจ: BJT DC Bias Calculator (Flask) — `http://127.0.0.1:5000/`
วิธีตรวจที่ใช้จริง: **OpenCode Browser** (Browser Tool ในตัว OpenCode Desktop) — ไม่ได้ใช้ Playwright MCP

ตาราง A1–A5 นี้แสดงอยู่ในหน้าเว็บที่ส่วน **04 · VALIDATION A1–A5**
ข้อมูลส่งมาจาก `bjt_bias/validation_results.py` ผ่าน `app.py` (ไม่มีการคำนวณใน HTML)

## ค่าที่ใช้ร่วมกันทุกกรณี

VCC = 12 V, RC = 2.2 kΩ, β = 100, VBE = 0.70 V
ป้อนค่าตามหน่วยบนฟอร์ม (ฟอร์มเริ่มที่ kΩ; 1 MΩ = 1000 kΩ)

## เกณฑ์ตัดสิน

- IC: |ค่าที่เห็น − ค่าอ้างอิงที่ยังไม่ปัดเศษ| ≤ **0.01 mA**
- VCE: |ค่าที่เห็น − ค่าอ้างอิงที่ยังไม่ปัดเศษ| ≤ **0.02 V**
- ฟอร์มแสดงทศนิยม 3 ตำแหน่ง (IC เป็น mA, VCE เป็น V) → ความคลาดเคลื่อนจากการปัดเศษ ≤ 0.0005 ซึ่งเล็กกว่าเกณฑ์มาก
- A4 ต้องเทียบ "ทิศทาง" ของ IC กับคำทำนายของกลุ่มด้วย
- A5 ต้องมีข้อความให้แก้, หน้าเว็บไม่ล่ม, และไม่แสดงผลของรอบก่อนเป็นผลของรอบนี้

## สมการอ้างอิง (จาก Engineering Electronics — ไม่ได้มาจากโปรแกรมที่ตรวจ)

**Voltage-Divider (A1)**
```
VTH = VCC·R2/(R1+R2)
RTH = R1‖R2
IB  = (VTH − VBE) / [RTH + (β+1)RE]
IC  = β·IB ,  IE = (β+1)·IB
VE  = IE·RE ,  VB = VE + VBE
VC  = VCC − IC·RC ,  VCE = VC − VE
```

**Fixed Bias (A2, A5)** — อิมิตเตอร์ต่อกราวด์ ไม่มี RE
```
IB = (VCC − VBE)/RB ,  IC = β·IB ,  IE = (β+1)·IB
VE = 0 ,  VB = VBE ,  VC = VCC − IC·RC ,  VCE = VC
```

**Emitter Bias (A3, A4)**
```
IB = (VCC − VBE) / [RB + (β+1)RE] ,  IC = β·IB ,  IE = (β+1)·IB
VE = IE·RE ,  VB = VE + VBE ,  VC = VCC − IC·RC ,  VCE = VC − VE
```

### ค่าอ้างอิงที่ยังไม่ปัดเศษ

| กรณี | IB | IC (mA) | IE (mA) | VE (V) | VC (V) | VCE (V) |
|---|---|---|---|---|---|---|
| A1 Divider R1=100k, R2=22k, RE=1k | 12.298581 µA | **1.229858** | 1.242157 | 1.242157 | 9.294312 | **8.052155** |
| A2 Fixed RB=1M | 11.300000 µA | **1.130000** | 1.141300 | 0.000000 | 9.514000 | **9.514000** |
| A3 Emitter RB=1M, RE=1k | 10.263397 µA | **1.026340** | 1.036603 | 1.036603 | 9.742053 | **8.705450** |
| A4 Emitter RB=1M, RE=2k | 9.400998 µA | **0.940100** | 0.949501 | 1.899002 | 9.931780 | **8.032779** |

## ตารางตรวจรับ

| กรณี | เลือกโหมดและกรอกค่า | คาดหมายก่อนรัน | เห็นจริง | วิธีตรวจ | สถานะ |
|---|---|---|---|---|---|
| A1 · โหมดเดิม | Divider · R1 = 100 kΩ, R2 = 22 kΩ, RC = 2.2 kΩ, RE = 1 kΩ, VCC = 12 V, β = 100, VBE = 0.70 V | ต้องตรงกับ Lab 2 ก่อนแก้: IC = **1.229858 mA** (แสดง 1.230), VCE = **8.052155 V** (แสดง 8.052) | **IC 1.230 mA · VCE 8.052 V** (VB 1.942 V, VE 1.242 V, VC 9.294 V, IB 12.30 µA, IE 1.242 mA, VTH 2.164 V, RTH 18,032.8 Ω) — ΔIC 0.000142, ΔVCE 0.000155 | OpenCode Browser (เลือก Divider, กรอกฟอร์ม, กด Calculate) | **PASS** |
| A2 · Fixed | Fixed · RB = 1 MΩ (1000 kΩ), RC = 2.2 kΩ, VCC = 12 V, β = 100, VBE = 0.70 V — ไม่กรอก RE | IC = **1.130000 mA**, VCE = **9.514000 V**; ฟอร์มต้องไม่มีช่อง RE | **IC 1.130 mA · VCE 9.514 V** (VB 0.700 V, VE 0.000 V, VC 9.514 V, IB 11.30 µA, IE 1.141 mA); ฟอร์มมีเฉพาะ VCC, β, VBE, RB, RC — **ไม่มีช่อง RE** — ΔIC 0.000000, ΔVCE 0.000000 | OpenCode Browser (สลับเป็น Fixed, กรอกฟอร์ม, กด Calculate) | **PASS** |
| A3 · Emitter | Emitter · RB = 1 MΩ (1000 kΩ), RE = 1 kΩ, RC = 2.2 kΩ, VCC = 12 V, β = 100, VBE = 0.70 V | IC = **1.026340 mA**, VCE = **8.705450 V**; ต้องมีช่อง RE และใช้ค่าที่กรอก | **IC 1.026 mA · VCE 8.705 V** (VB 1.737 V, VE 1.037 V, VC 9.742 V, IB 10.26 µA, IE 1.037 mA); มีช่อง RE และใช้ค่า 1 kΩ — ΔIC 0.000340, ΔVCE 0.000450 | OpenCode Browser (สลับเป็น Emitter, กรอกฟอร์ม, กด Calculate) | **PASS** |
| A4 · เปลี่ยนค่าเดียว | Emitter · เหมือน A3 ทุกค่า แต่เปลี่ยน RE = 2 kΩ | **ทำนาย: IC ลดลง** จาก A3 เพราะ RE ใหญ่ขึ้น → ตัวส่วน [RB+(β+1)RE] ใหญ่ขึ้น → IB ลด → IC ลด; คาด IC = **0.940100 mA**, VCE = **8.032779 V** | **IC 0.940 mA · VCE 8.033 V** (VB 2.599 V, VE 1.899 V, VC 9.932 V, IB 9.40 µA, IE 0.950 mA); ก่อนกดคำนวณยืนยันโหมด Emitter และ VCC 12 / RB 1000 / RC 2.2 / β 100 / VBE 0.70 เท่าเดิม เปลี่ยนเฉพาะ RE 1→2 — **IC ลดลงจริง 1.026 → 0.940 mA** — ΔIC 0.000100, ΔVCE 0.000221 | OpenCode Browser (เปลี่ยนเฉพาะช่อง RE, กด Calculate) | **PASS** |
| A5 · อินพุตผิด | Fixed · RB = 0, RC = 2.2 kΩ, VCC = 12 V, β = 100, VBE = 0.70 V | Flask ต้องตอบ error เรื่อง RB (คาดว่า "Fixed Bias: RB must be greater than 0"), หน้าเว็บไม่ล่ม, ไม่มีตัวเลขผลลัพธ์ของรอบนี้ | **"Fixed Bias: RB must be greater than 0"** ใต้หัวข้อ "ไม่สามารถคำนวณได้ — ตรวจสอบข้อมูลที่กรอก"; ไม่มี `.metrics`, ฟอร์มยังอยู่, ขึ้น empty state "ยังไม่มีผลลัพธ์ · Fixed Bias"; POST ตรงถึง Flask (ไม่ผ่านฟอร์ม) ได้ HTTP 200 + ข้อความเดียวกัน และ HTML มี `novalidate` → ข้อความมาจาก **Flask** | OpenCode Browser + POST ตรงถึง Flask (urllib) | **PASS** |

## หลักฐาน

- Snapshot หลังส่งฟอร์ม A1 (ข้อความจากหน้าเว็บ):
  `"DC Operating Point (Q-Point) · Voltage Divider Bias"` … `"8.052"` `"V"` … `"1.230"` `"mA"`
- Snapshot หลังส่งฟอร์ม A5:
  `"ไม่สามารถคำนวณได้ — ตรวจสอบข้อมูลที่กรอก"` → `"Fixed Bias: RB must be greater than 0"` → `"ยังไม่มีผลลัพธ์ · Fixed Bias"`
- Screenshot A5: `docs/validation-artifacts/A5-fixed-rb0.png`
- Screenshot ตารางในแอป (ส่วน 04 · VALIDATION A1–A5): `docs/validation-artifacts/validation-table.png`
- ทวนซ้ำ A4 ด้วยฟอร์มจริงอีกรอบ: โหมด Emitter, VCC 12 / RB 1000 / RC 2.2 / β 100 / VBE 0.70 คงเดิม
  เปลี่ยนเฉพาะ RE 1 → 2 kΩ แล้วกด Calculate — A3 ได้ IC 1.026 mA · VCE 8.705 V,
  A4 ได้ IC 0.940 mA · VCE 8.033 V (ลดลงตามคำทำนาย)
- ตรวจ Flask ตรงด้วย POST `mode=fixed&RB=0…`: HTTP 200, error เดียวกัน, ไม่มีบล็อก `.metrics`
- ไม่มีการแก้โค้ดระหว่างรอบตรวจนี้ (ผลก่อน–หลังจึงไม่มี); `python -m unittest discover -s tests` ผ่าน 16/16

## สรุป

| กรณี | ผล |
|---|---|
| A1 | PASS |
| A2 | PASS |
| A3 | PASS |
| A4 | PASS (ทิศทาง IC ลดลงตรงคำทำนาย) |
| A5 | PASS (Flask ตรวจ RB > 0) |

หมายเหตุแยกต่างหาก (ไม่เกี่ยวกับ A1–A5): หาก POST `mode=bogus` ตรง ๆ หน้าเว็บจะขึ้นหัวข้อ `· bogus` และวงจร Emitter เพราะ template ตกไปที่ `{% else %}` — ยังแสดง error และไม่คำนวณ แต่ถ้าต้องการให้เรียบร้อยสามารถแก้ภายหลังได้

## หมายเหตุ

- A1 ต้องเทียบกับค่าที่ Lab 2 เดิมได้ (VCE 8.052 V, IC 1.230 mA) — ค่าอ้างอิงตรงกัน
- A5: ฟอร์มมี `novalidate` จึงไม่ถูกบล็อกฝั่งเบราว์เซอร์ ข้อความที่เห็นจึงมาจาก Flask โดยตรง
- ถ้าพบผลไม่ตรง: บันทึกผลก่อน–หลังและรันซ้ำเฉพาะกรณีที่ได้รับผลกระทบ

---

# Lab 06 — CE Voltage Divider Amplifier · ngspice comparison

วันที่ตรวจ: 2026-11-24
หน้าเว็บที่ตรวจ: `http://127.0.0.1:5000/` (Flask รันจริง) + **OpenCode Browser**
(ไม่ได้ใช้ Playwright MCP) — อ่านค่าจาก DOM จริงหลังกดปุ่ม ไม่ได้อ่านจากโค้ด

## สิ่งที่เพิ่มจาก Lab 2–3

- `spice_engine.py` — starter adapter แยกจาก Flask: `build_netlist()` → `run()` → `parse_*()` → `simulate_*()`
- ฟอร์มมีตัวเลือก **Analysis**: `dc` (`.op`), `ac` (`.ac`), `tran` (`.tran`)
  และ checkbox **เทียบกับ ngspice** (opt-in — ไม่ติ๊กจะได้เฉพาะผล analytical เหมือนเดิม)
- `templates/index.html` ส่วน **05 · NGSPICE COMPARISON** แสดงตาราง Analytical/ngspice/|Δ|,
  กราฟ SVG (gain vs log f, Vin/Vout vs time) และ netlist ที่ส่งจริง
- `bjt_bias/validate.py` มี `validate_ce()` ตรวจ RL/Cin/Cout/แหล่ง SIN ก่อนแปลงหน่วยที่ `app.py`

## ติดตั้ง / ตั้งค่า ngspice

```powershell
# ใช้ ngspice-console (ไม่ใช่ ngspice.exe ที่เป็น GUI — -b ไม่พิมพ์ stdout)
$env:NGSPICE_EXECUTABLE = "C:\Users\B6810177\AppData\Local\Temp\opencode\ngspice47\Spice64\bin\ngspice_con.exe"
& $env:NGSPICE_EXECUTABLE -v
```

`spice_engine.find_executable()` หาเองตามลำดับ: `NGSPICE_EXECUTABLE` → `PATH`
(`ngspice_con`, `ngspice`) → install dir มาตรฐาน → path ที่ใช้ตรวจในเครื่องนี้
ถ้าไม่เจอจะยก `NgspiceUnavailable` และหน้าเว็บแจ้ง error แต่ผล analytical ยังแสดงอยู่

## แนวทางจำลอง

- หน่วยขอบเขตสาธารณะเป็น SI (Ω, F, V, Hz, A); การแปลง kΩ→Ω, µF→F, mV→V ทำที่ `app.py`
- BJT model: `BF=β`, `VAF=1e12`, `IS = IC_ref / exp(VBE/VT)` ที่ `VT = kT/q` (27 °C)
  → .exp ผ่าน Q-point เดิมของสมการ Lab 2–3 พอดี
- มี `CJC=10pF CJE=20pF TF=0.5ns` เพื่อให้ sweep มี fH จริง (ไม่เปลี่ยน DC Q-point)
- `.ac dec 20 1 1e9`, `.tran 1e-6 5e-3`; `.print ac vdb(vout) vdb(vin)`,
  `.print tran v(vin) v(vout)`
- ngspice-47 พิมพ์ trace ทั้งสองในตารางเดียว → parser อ่านตาม header และรองรับตารางแยกด้วย
- fL/fH หาโดย interpolate จุดที่ gain ตัด −3 dB ใน log-frequency (ไม่ใช่เอา sample แรก/สุดท้าย)

## Baseline ที่ใช้ตรวจ

VCC = 12 V · R1 = 100 kΩ · R2 = 22 kΩ · RC = 2.2 kΩ · RE = 1 kΩ · β = 100 · VBE = 0.70 V
RL = 10 kΩ · Cin = Cout = 10 µF · SIN 10 mV peak / 1 kHz (กด “โหลดค่าตัวอย่าง”)

### DC Operating Point (`.op`)

| ปริมาณ | Analytical | ngspice |  |Δ| | หน่วย |
|---|---|---|---|---|
| I_C | 1.229858 | 1.229835 | 0.000023 | mA |
| V_CE | 8.052155 | 8.052228 | 0.000073 | V |
| V_B | 1.942157 | 1.942161 | 0.000004 | V |
| V_E | 1.242157 | 1.242134 | 0.000023 | V |
| V_C | 9.294312 | 9.294362 | 0.000050 | V |

ngspice กับสมการมือตรงกันภายใน ~0.002% — ผ่านเกณฑ์ Lab 3 (≤0.01 mA / ≤0.02 V) อย่างสบาย

### AC Small-Signal (`.ac`)

| ปริมาณ | Analytical | ngspice | หน่วย |
|---|---|---|---|
| Gain | 1.766135 | 1.749041 | × |
| fL (−3 dB) | 8.550391 | 1.827041 | Hz |
| fH (−3 dB) | — | 58,689,047 | Hz |

- Gain ต่างกัน ~1% (สมการใช้ `(RC∥RL)/(RE+VT/IC)`)
- fL ไม่ตรงกันเพราะ netlist ใช้แหล่ง AC ในอุดมคติ (Rs = 0) → C<sub>in</sub> ไม่สร้าง high-pass,
  ngspice เห็นเฉพาะ pole ของ C<sub>out</sub>; สมการ analytical รวม C<sub>in</sub> ผ่าน R<sub>TH</sub>∥βr<sub>e</sub>
  → คาด ~8.55 Hz นี่เป็นความต่างของแบบจำลอง ไม่ใช่ bug
- fH ไม่มีสมการอ้างอิงใน Lab 2–3 จึงแสดงเฉพาะค่าจาก ngspice ใน caption ของกราฟ

### Transient (`.tran`)

| ปริมาณ | Analytical | ngspice | หน่วย |
|---|---|---|---|
| Vin (p-p) | 20.000000 | 19.999965 | mV |
| Vout (p-p) | 35.322708 | 34.980700 | mV |
| Gain (p-p) | 1.766135 | 1.749038 | × |

ngspice เก็บ 5,008 samples; gain ตรงกับผล `.ac` (1.749) ภายใน 4 หลัก

## Browser log (ทำจริง)

1. `tabs.open("http://127.0.0.1:5000/")` → title `BJT Bias & CE Simulator | ENG29 2121`, HTTP 200
2. คลิก **โหลดค่าตัวอย่าง** → ฟอร์มมี 12 / 100 / 22 / 2.2 / 1 / 100 / 0.7 / 10 / 10 / 10 / 10 / 1000
3. ติ๊ก **เทียบกับ ngspice**, เลือก `dc` → กด **Calculate / Simulate**
   → DOM `.comparison-table` มี 5 แถว, `IC 1.229858 | 1.229835 | 0.000023 mA`
4. เปลี่ยนเป็น `ac` → กด Calculate → `#ac-chart` ปรากฏ,
   caption `midband 1.749× · fL 1.83 Hz · fH 58689047.13 Hz`
5. เปลี่ยนเป็น `tran` → กด Calculate → `#tran-chart` ปรากฏ,
   caption `5008 samples · Vout p-p 34.98 mV`
6. `browser.console(level = "error")` → **ไม่มี error**

## หลักฐานภาพจาก Browser จริง

- `captures/lab06-dc-ngspice-comparison.png` — ตารางเทียบ DC
- `captures/lab06-ac-ngspice-comparison.png` — กราฟ gain และ fL/fH
- `captures/lab06-transient-waveform.png` — รูปคลื่น Vin/Vout

## เทสต์หลังการแก้

```
python -m unittest discover -s tests -v
Ran 45 tests ... OK
```

แบ่งเป็น: สมการ/validation เดิม, HTTP flow เดิม, `tests/test_spice_engine.py`
(netlist/parser/derived current/corner interpolation + ngspice จริงเมื่อมี binary),
`tests/test_spice_web.py` (selector, opt-in comparison, degrade เมื่อไม่มี ngspice,
ac/tran chart, validation ของ C<sub>in</sub>)
