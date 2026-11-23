# Superpowers Workflow — Lab 05

## Workflow Record

บันทึกการใช้ Superpowers กับ Web App ที่มีอยู่แล้ว เรียงตามลำดับที่โจทย์กำหนด
ไม่ได้สร้างโปรเจกต์ใหม่ และไม่เพิ่มฟีเจอร์นอกเหนือจาก DC Bias

| ขั้น | สิ่งที่ทำ | หลักฐาน/คำสั่ง |
|---|---|---|
| Tool Setup | ตรวจ Git, Python, venv, Flask และ OpenCode Desktop พร้อม Superpowers Plugin | `git --version`, `python --version`, `.\.venv\Scripts\python.exe -m pip show flask`, `opencode-cli plugin list` → `superpowers 22f0b46` |
| Brainstorm | ทบทวนแอปที่มีอยู่และสรุปทางเลือก: สร้างใหม่ / ใช้ workflow กับของเดิม / เขียนเอกสารอย่างเดียว → เลือกทางกลาง | `docs/superpowers/specs/2026-11-24-superpowers-workflow-design.md` |
| Plan Approval | แยกงานเป็น 2 Task พร้อม interface, ข้อจำกัด และ Review Focus | `docs/superpowers/plans/2026-11-24-superpowers-workflow.md` |
| Execute | เขียนเทสต์ก่อน (RED) ให้บังคับว่าต้องมี record และลิงก์ใน README แล้วค่อยสร้างไฟล์ (GREEN) | `.\.venv\Scripts\python.exe -m unittest tests.test_structure -v` |
| Test/Review | รันชุดเทสต์ทั้งหมด + ยิง HTTP จริงที่ Local Server และตรวจค่าอ้างอิง DC Bias | `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`, `urllib.request` ไปที่ `http://127.0.0.1:5000/` |
| GitHub | commit แต่ละขั้นแล้ว push ขึ้น branch หลัก | `git commit -m ...`, `git push origin main`, `git status -sb` |

## ผลตรวจจริง

- `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` → **Ran 19 tests … OK**
  (เดิม 16 + `tests/test_structure.py` 3 รายการ)
- `GET http://127.0.0.1:5000/` → 200, ฟอร์มครบ 7 ช่อง และมี SVG ของวงจร
- `POST /` ด้วยชุดค่า Divider (VCC 12, R1 100k, R2 22k, RC 2.2k, RE 1k, β 100, VBE 0.7) → 200
  ค่าที่แสดงตรงอ้างอิง: IC **1.230 mA**, VCE **8.052 V**, VB **1.942 V**,
  VTH **2.164 V**, RTH **18032.8 Ω**
- RED → GREEN: ก่อนสร้าง record และลิงก์ README เทสต์ `test_workflow_files_exist`
  และ `test_readme_links_local_server_and_record` ล้มเหลว หลังสร้างผ่านทั้งคู่
- Commit ของขั้น Execute: `e53470e` (`test: pin Superpowers workflow artifacts and record`)

## ขอบเขต

จำกัดเฉพาะ Flask Web App สำหรับ DC Bias — ไม่มี Bode Plot, Transient,
Signal Generator, Overlay Animation หรือ SPICE Solver
