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

_(รันแล้วจะเติมจำนวนเทสต์ ค่าที่ได้ และ commit hash ที่นี่)_

## ขอบเขต

จำกัดเฉพาะ Flask Web App สำหรับ DC Bias — ไม่มี Bode Plot, Transient,
Signal Generator, Overlay Animation หรือ SPICE Solver
