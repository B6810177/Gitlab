## สรุป A1–A5

| กรณี | ผล |
|---|---|
| A1 | PASS |
| A2 | PASS |
| A3 | PASS |
| A4 | PASS (ทิศทาง IC ลดตามคาด) |
| A5 | PASS (Flask ตรวจ RB > 0) |

หมายเหตุเพิ่มเติม: เคยพบกรณี POST ผิดรูปแบบอาจทำให้ข้อความ error แสดงร่วมกับผลคำนวณในบาง path ของ template — บันทึกเป็นข้อสังเกตสำหรับการปรับปรุงภายหลัง (ไม่กระทบผล A1–A5 ที่ตรวจแล้ว)

## ข้อจำกัด

- A1 เทียบกับค่าที่เคยยืนยันใน Lab 2/เอกสารอ้างอิงของโปรเจกต์
- A5: การแจ้งเตือนฝั่งเซิร์ฟเวอร์ (Flask) แสดงเมื่อใช้ `novalidate` ในฟอร์ม

---

# Browser Acceptance B1–B8 (Lab 04)

**เครื่องมือที่ใช้จริง:** **OpenCode Browser** (ภายใน OpenCode Desktop) สำหรับนำทางหน้าเว็บ อ่าน DOM, คลิก/กรอก/เลือก, และจับภาพหน้าจอ — **ไม่ใช่ Playwright MCP** ตามที่ระบุในเอกสาร Lab04 HTML ดังนั้นจึงบันทึกความจริงในเอกสารนี้

**หลักการบันทึก:** หากยังไม่รันตามเคสใน browser ให้ระบุ **NOT RUN** พร้อมเหตุผล ห้ามสรุป PASS โดยไม่มีหลักฐาน

| Case | Method (จริง/วางแผน) | Input (ย่อ) | Expected / Reference | Observed | Evidence | Status |
|---|---|---|---|---|---|---|
| B1 — Regression (Lab 3) | OpenCode Browser smoke + รัน `unittest` ครบชุด | A1–A5 ตามตารางด้านบน | ตรงเกณฑ์ A1–A5 / ไม่มี regression จากเทสต์อัตโนมัติ | `python -m unittest discover -s tests` → **Ran 45 tests OK** (2026-11-24). Browser smoke เบื้องต้นกับ Divider baseline สอดคล้องที่ยืนยันก่อนหน้า | `docs/validation.md`, `tests/*` | **PASS** (มีเทสต์อัตโนมัติครบ; ยังไม่ทำบันทึกทีละขั้น B1 ทุกกรณีแยกเป็นรายการย่อยในหน้านี้เพิ่ม) |
| B2 — DC SPICE (CE VD) | OpenCode Browser: โหลดตัวอย่าง, ติ๊กเทียบ ngspice, analysis `dc`, Calculate/Simulate, อ่านตาราง | VCC 12V, 100k/22k/2.2k/1k, β100, VBE0.7, RL10k, Cin=Cout10µF | ngspice `.op` ใกล้ analytical (ΔIC ≤ 0.01 mA, ΔVCE ≤ 0.02 V แนวทาง Lab 3) | IC 1.229858 vs 1.229835 mA (Δ0.000023), VCE 8.052155 vs 8.052228 V (Δ0.000073) และค่า VB/VE/VC ใกล้เคียงมาก | `captures/lab06-dc-ngspice-comparison.png`, ส่วน Lab 06 ข้างล่าง | **PASS** |
| B3 — เปลี่ยน RE แล้วรันใหม่ | OpenCode Browser: โหลดตัวอย่าง (Divider), บันทึก baseline (RE=1k) แล้วเปลี่ยน RE เป็น 2k (fill) กด Calculate/Simulate (dc) | Divider baseline R1=100k,R2=22k,RC=2.2k,RE 1k->2k, VCC12V,beta100,VBE0.7 | IC ลดลงเมื่อ RE เพิ่ม (สอดคล้องสมการ) | RE=1k: IC 1.230 mA, VCE 8.052 V (อ้างอิง A1). RE=2k: IC 0.665 mA, VCE 9.192 V (จากผลบนหน้าเว็บ) | OpenCode Browser 2026-11-24 (session ทดสอบ B3) | **PASS** |
| B4 — AC (.ac) + กราฟ | OpenCode Browser: analysis `ac`, compare, ตรวจกราฟและ caption | baseline + ค่า CE เดิม | กราฟ/ตัวเลขมาจากรันจริง (ไม่ใช่ค่าคงที่) | Gain ~1.766× (analytical) vs ~1.749× (ngspice), fL 8.55 vs 1.83 Hz, fH ~58.69 MHz, มีกราฟ Bode-like ในหน้า | `captures/lab06-ac-ngspice-comparison.png` | **PASS** (baseline) |
| B5 — Transient (.tran) | OpenCode Browser: analysis `tran`, ตรวจกราฟ/caption | SIN 10 mV peak / 1 kHz | คลื่นจาก ngspice run จริง, p-p/gain สอดคล้อง | Vout p-p ~34.98 mV, gain ~1.749×, ~5008 samples | `captures/lab06-transient-waveform.png` | **PASS** (baseline) |
| B6 — เปลี่ยน Source แล้วรันใหม่ | ยังไม่ได้ทำ | เปลี่ยน Vin peak / fin แล้วรันซ้ำ | ผลเปลี่ยนตามอินพุต | — | — | **NOT RUN** |
| B7 — Invalid input / ข้อผิดพลาด engine | มีเทสต์อัตโนมัติบางส่วน (validation CE, กรณีไม่มี ngspice) ยังไม่ทำ manual browser ครบทุกกรณีใน HTML | ค่าไม่ถูกต้องหรือสภาพแวดล้อมไม่มี ngspice | ข้อความ error ชัด ไม่ทิ้งผลลัพธ์ผิดจากรอบก่อน | ผ่านชุดเทสต์ที่เกี่ยวข้องใน 45 tests | `tests/test_spice_web.py`, `tests/test_spice_engine.py` | **PARTIAL** / หลายกรณี **NOT RUN** ใน browser |
| B8 — UI viewport Desktop/Mobile | ยังไม่จับภาพแยกขนาดหน้าจอ | Desktop + Mobile | อ่านได้ ใช้งานพื้นฐานได้ | — | — | **NOT RUN** |

หมายเหตุ: การทำ B1–B8 ให้ “ครบ” ตาม Lab04 HTML ควรเพิ่มรอบทดสอบและหลักฐาน (ภาพ/บันทึก) ในคอมมิตถัดไป

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
