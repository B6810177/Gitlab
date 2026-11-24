# Lab 04 — Integration Plan (BJT Bias + ngspice CE Simulator)

เอกสารนี้สรุปแผนการรวม (integration plan) ตามแนวทางใน `Lab04_BJT_Amplifier_Simulator_2-2569 (1).html` (ส่วน 07 Build with Superpowers) สำหรับงานต่อจาก Lab 02–03 ใน repo เดียวกัน โดย **ไม่เปลี่ยนสถาปัตยกรรมหลัก** และคงความสามารถ DC analytical เดิมไว้

## ขอบเขต (v1)
- คงโหมด DC bias analytical 3 แบบ: Fixed / Emitter / Voltage Divider ผ่าน `bjt_bias/bias.py` + `dc_bias.py`
- เพิ่มการจำลอง CE Voltage Divider amplifier ด้วย **ngspice จริง** ผ่าน adapter แยก: `.op`, `.ac`, `.tran`
- ฟอร์ม/หน้าเว็บเดิมขยายด้วยตัวเลือก analysis, checkbox เปรียบเทียบ ngspice, ตารางเทียบ, กราฟ SVG, แสดง netlist
- **ไม่**ทำ Emitter Bypass Capacitor (Ce) เป็น baseline ของ v1 (เป็นงานต่อยอดถ้ามีโจทย์เพิ่ม)
- **ไม่**ทำ animated overlay/visual extras นอกเหนือที่จำเป็นต่อการแสดงผล

## ไฟล์ที่ reuse (ของเดิม)
- `app.py` — route หลัก, validation flow เดิม, หน่วย kΩ↔Ω; ขยาย dispatch/parse ผลสำหรับ analysis
- `dc_bias.py`, `bjt_bias/bias.py`, `bjt_bias/validate.py` (ขยาย `validate_ce`) — สมการ/validation
- `bjt_bias/validation_results.py`, `templates/base.html`, `templates/index.html`, `static/style.css`
- `tests/test_dc_bias.py`, `tests/test_web.py` — ต้องยังผ่าน

## ไฟล์/ส่วนที่เพิ่มใหม่
- `spice_engine.py` — adapter: `build_netlist()`, `run()`, `parse_operating_point()/parse_ac()/parse_transient()`, `simulate_*()`, `find_executable()`, exception `NgspiceUnavailable`/`NgspiceError`
  - ใช้ `ngspice_con.exe` (console) ไม่ใช้ GUI `ngspice.exe` สำหรับ batch `-b`
  - degrade อย่างสุภาพเมื่อไม่พบ binary (แสดง error ในหน้าเว็บ ผล analytical ยังแสดง)
- `tests/test_spice_engine.py`, `tests/test_spice_web.py`
- `captures/lab06-*.png`, เอกสารใน `docs/validation.md`, `README*.md`, `AGENTS.md`

## Data flow (สรุป)
1. Browser ส่ง form (mode, ค่า bias + ค่า CE/แหล่งจ่าย) → `app.py` validate (`validate`, `validate_ce`)
2. คำนวณ analytical DC เสมอ (อ้างอิง/ใช้เป็น `IC_ref` ใน model)
3. ถ้าเลือก analysis ≠ dc หรือผู้ใช้ขอ compare: เรียก `spice_engine.simulate_*` → ได้ผลจาก ngspice (หรือ error)
4. แสดงผล: ตาราง analytical, (ถ้ามี) ตารางเทียบ, กราฟ SVG ตาม analysis, netlist ที่ใช้จริง

## Expected outputs (ตาม analysis)
- **dc (.op)**: `IC, VCE, VB, VE, VC` (SI ใน backend, แปลงหน่วยแสดงผล)
- **ac (.ac)**: `midband_gain`, `f_low`, `f_high`, sweep rows สำหรับกราฟ (dB vs log f)
- **tran (.tran)**: `vin_pp, vout_pp, gain`, samples/time series สำหรับกราฟ

## Error paths ที่ต้องรองรับ
- ไม่พบ ngspice binary → `NgspiceUnavailable` → แจ้งใน UI, ไม่ crash, analytical ยังแสดง
- ngspice run fail / parse fail → แสดงข้อความ error ที่เข้าใจได้
- validation ไม่ผ่าน (ค่าติดลบ/ศูนย์/ช่วงไม่ถูก) → แสดง error list เหมือนเดิม ไม่รัน simulator
- timeout/process error → จับ exception และแสดงผล error ในหน้าเว็บ

## หลักการสำคัญ (จาก 07)
- External process: เรียกผ่าน `subprocess` แบบ list args, หลีกเลี่ยง `shell=True` ตามความเหมาะสม, มี timeout
- แยกหน้าที่: `spice_engine` ไม่ import Flask/request; `app.py` เป็น orchestration + แปลงหน่วย
- ห้าม hard-code ผลสำเร็จหรือซ่อน error ของ ngspice
- ทุกการเปลี่ยนสมการ/logic ที่กระทบผลต้องมีเทสต์และรัน unittest ผ่านก่อน commit

## หลักฐาน/การตรวจสอบ
- `python -m unittest discover -s tests` (ปัจจุบัน 45 tests)
- ทดสอบด้วย Flask + OpenCode Browser: โหลดตัวอย่าง, เลือก analysis, compare, ตรวจ console ไม่มี error
- บันทึกผลใน `docs/validation.md` และภาพใน `captures/`