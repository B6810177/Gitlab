# Design — ใช้ Superpowers Workflow กับ DC Bias Web App (Lab 05)

## Intent

ทำงานตามหัวข้อ **05 / REAL SUPERPOWERS WORKFLOW**: ใช้ Skill ของ Superpowers
กับงาน Lab ที่มีอยู่แล้ว ให้ครบลำดับ Brainstorm → Design Doc → Implementation
Plan → Plan Review → Execute → Test/Review → Push โดยยังได้ Web App
ที่ทำงานจริงอยู่เสมอ

## Goals

- เก็บ Design Doc และ Implementation Plan ไว้ใน repo เป็นหลักฐานของขั้นตอน
- ดำเนินการตาม Plan จริง และตรวจด้วยคำสั่งที่รันได้ (tests + HTTP)
- รักษาขอบเขต Lab ให้เป็น **Flask Web App สำหรับ DC Bias เท่านั้น**

## Non-goals / Anti-goals

- ไม่สร้าง Bode Plot, Transient, Signal Generator, Overlay Animation หรือ SPICE Solver
- ไม่เพิ่มโหมด/ฟีเจอร์ใหม่ที่โจทย์ไม่ได้สั่ง
- ไม่ก็อปข้อความหรือโครงสร้างจากภาพตัวอย่างมาใส่ในเอกสารของเรา
- ไม่ rebuild แอปที่ทำงานอยู่แล้วทิ้ง

## Constraints

- แอปปัจจุบัน: Python 3.12 + Flask 3.0.3, โมดูล `bjt_bias/`, entry `dc_bias.py`,
  template Jinja2, tests 16 รายการ, remote `origin/main`
- Timebox ในภาพ: Tool Setup 40, Brainstorm 15, Plan Approval 15,
  Execute 75, Test/Review 25, GitHub 10 นาที — ในเซสชันนี้บีบให้ทำต่อเนื่อง
- ผู้พัฒนาบอกให้ทำต่อโดยไม่ต้องรอถาม และจะตรวจตอนเสร็จ → ถือว่า opt out จากรอบคำถาม

## Approaches

| ทางเลือก | ข้อดี | ข้อเสีย | ตัดสินใจ |
|---|---|---|---|
| A. สร้างแอปใหม่ทั้งหมดตาม workflow | ได้ของใหม่หมด | ทิ้งโค้ดที่ผ่านเทสต์แล้ว เสียเวลา และอาจ偏离 scope | ไม่เลือก |
| B. ใช้ workflow กับแอปที่มีอยู่ + เก็บ design/plan/หลักฐาน | ตรงโจทย์ ไม่แต่งฟีเจอร์ มีหลักฐานตรวจได้ | ต้องเขียนเอกสารเพิ่ม | **เลือก** |
| C. เขียนเอกสารอย่างเดียว | เร็ว | ไม่มีหลักฐานว่าแอปยังทำงาน | ไม่เลือก |

## สิ่งที่ตกลงแล้ว (calls ที่ผู้พัฒนามอบให้)

- ใช้ Skill ตามลำดับ: `brainstorming` → `writing-plans` → `executing-plans`
  → ตรวจด้วย `verification-before-completion` → push ขึ้น `origin/main`
- ไฟล์ไปอยู่ที่ `docs/superpowers/specs/` และ `docs/superpowers/plans/` (ตามที่มีอยู่แล้ว)
- เนื้อหาเขียนใหม่ด้วยถ้อยคำของเรา ไม่ก็อปตัวอย่าง
- ถ้า Plan พบว่าทุกอย่างครบแล้ว ให้ทำแค่ "ยืนยันด้วยคำสั่ง + บันทึกผล" ไม่สร้างงานเทียม

## สิ่งที่เหลือให้ผู้ทำตาม Plan ตัดสินเอง

- รายการตรวจในขั้น Execute ว่าควรเพิ่ม/แก้ไฟล์ไหน ให้ยึดตามผลที่รันจริง
- รูปแบบบันทึกผล Test/Review ให้สั้นและอ้างคำสั่งได้
