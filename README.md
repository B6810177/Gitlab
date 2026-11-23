# Gitlab

ใช้สำหรับเรียนแลป Compro ไฟฟ้า

## DC Circuit Calculator

โปรแกรมสำหรับคำนวณและวิเคราะห์วงจรไฟฟ้ากระแสตรง (DC) ทั้งตัวต้านทานแบบอนุกรม ขนาน และผสม โดยรับค่าแรงดันไฟฟ้าและค่าความต้านทานเพื่อคำนวณหาความต้านทานรวม กระแสไฟฟ้า และกำลังไฟฟ้า

## BJT DC Bias Web App (Lab 02–03)

Flask web app สำหรับคำนวณ DC Operating Point ของวงจร BJT Common-Emitter 3 โหมด
(Voltage-Divider Bias / Fixed Bias / Emitter Bias) — หน้าเว็บเรียงจากบนลงล่าง:
**วงจร → ฟอร์มกรอกค่า → ผลลัพธ์ → Engineering Model → ตาราง Validation A1–A5**

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


