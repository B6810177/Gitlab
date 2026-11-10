# Gitlab

ใช้สำหรับเรียนแลป Compro ไฟฟ้า

## DC Circuit Calculator

โปรแกรมสำหรับคำนวณและวิเคราะห์วงจรไฟฟ้ากระแสตรง (DC) ทั้งตัวต้านทานแบบอนุกรม ขนาน และผสม โดยรับค่าแรงดันไฟฟ้าและค่าความต้านทานเพื่อคำนวณหาความต้านทานรวม กระแสไฟฟ้า และกำลังไฟฟ้า

## BJT DC Bias Web App (Lab 02)

Flask web app สำหรับคำนวณ DC Operating Point ของวงจร BJT Common-Emitter แบบ
Voltage-Divider Bias — หน้านี้แสดง **ผลลัพธ์ไว้ด้านบน** และ **แบบฟอร์มกรอกค่าอยู่ด้านล่าง**
ดูวิธีติดตั้ง/รัน/ทดสอบได้ที่ [README_BJT.md](README_BJT.md)

### Static version (ป้อนข้อมูลได้ทันที ไม่ต้องรัน Python)

เปิดไฟล์ [`index.html`](index.html) ด้วย Browser ได้โดยตรง หรือเปิดผ่าน GitHub Pages
หน้านี้คำนวณใน Browser ด้วย JavaScript และให้ผลลัพธ์ชุดเดียวกับเวอร์ชัน Flask
(ผลลัพธ์ด้านบน · วงจรตรงกลาง · แบบฟอร์มด้านล่าง)

ถ้าจะใช้ GitHub Pages: Settings → Pages → Source: **Deploy from a branch** →
Branch: **main** / **(root)** → Save แล้วเปิด `https://b6810177.github.io/Gitlab/`


