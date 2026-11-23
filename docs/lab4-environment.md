# Lab 4 — ผลการเตรียมสภาพแวดล้อม (ข้อ 2.1–2.2)

วันที่ตรวจ: 23 พ.ย. 2026
เครื่องที่ใช้: Windows (x64)
Project ที่พัฒนา: [Gitlab](https://github.com/B6810177/Gitlab)

## 2.1 ติดตั้ง Git และตั้งค่าการบันทึก Commit

| ขั้นตอน | คำสั่งที่ใช้ตรวจ | ผลที่ได้ | สถานะ |
|---|---|---|---|
| ติดตั้ง Git | `git --version` | `git version 2.56.0.windows.4` | ✅ |
| ตั้งชื่อผู้ Commit | `git config --global --get user.name` | `B6810177` | ✅ |
| ตั้งอีเมลผู้ Commit | `git config --global --get user.email` | `peerawitjantall@gmail.com` | ✅ |
| ตรวจ Repository ในเครื่อง | `git status` | อยู่บน branch `main` ตรงกับ `origin/main` ไม่มีไฟล์ค้าง | ✅ |
| Remote GitHub | `git remote -v` | `https://github.com/B6810177/Gitlab.git` (fetch/push) | ✅ |

หมายเหตุ: ทั้ง `user.name` และ `user.email` ตั้งไว้ที่ระดับ global และตรงกับบัญชี GitHub ที่ใช้ส่งงาน

## 2.2 ติดตั้ง OpenCode IDE (Desktop App) และเชื่อม AI Model

| ขั้นตอน | วิธีตรวจ | ผลที่ได้ | สถานะ |
|---|---|---|---|
| ติดตั้ง OpenCode Desktop | ตรวจ process ที่กำลังทำงาน | `OpenCode.exe` จาก `C:\Users\User\AppData\Local\Programs\ai.opencode.desktop\` | ✅ |
| เวอร์ชัน OpenCode | `opencode-cli --version` (CLI ที่มากับแอป) | `opencode v2.2.7` | ✅ |
| เปิด Project Folder | ตรวจ directory ของโปรเจกต์ | `C:\Users\User\Documents\Default Project\Gitlab` (repo งาน Lab) | ✅ |
| เชื่อม AI Model Provider | ทดสอบสนทนากับ Agent ในเซสชันนี้ | ตอบกลับได้ปกติ (provider: `opencode`, model: `deepseek-v4.1-flash-free`) | ✅ |
| ตรวจ Python | `python --version` | `Python 3.12.10` | ✅ |
| ตรวจ Python ใน venv | `.venv\Scripts\python.exe --version` | `Python 3.12.10` | ✅ |
| Flask สำหรับ Web App | `pip show flask` | Flask 3.0.3 | ✅ |

หมายเหตุ: `opencode` CLI ไม่ได้อยู่ใน `PATH` ของเครื่อง (ตามคู่มือระบุว่าไม่จำเป็นสำหรับการติดตั้งแบบ Desktop-only) — ใช้ `opencode-cli.exe` ที่อยู่ในโฟลเดอร์ติดตั้งของแอปได้ถ้าต้องการตรวจเวอร์ชัน

## สรุปสิ่งที่ยังขาด

1. **หลักฐานภาพหน้าจอ (screenshots)** ของ About/Settings ใน OpenCode Desktop และหน้าต่าง Project Folder — ต้องกดเก็บจากเครื่องเอง เพราะเป็นภาพหน้าจอของผู้ใช้
2. **รายละเอียด Lab 4 ข้อถัดไป (2.3 เป็นต้นไป)** ยังไม่ได้รับ จึงยังไม่ทราบว่าต้องส่งชิ้นงาน/ฟีเจอร์อะไรเพิ่ม
3. **Project Folder ที่เปิดใน IDE** ปัจจุบันคือ `Default Project` ซึ่งมี repo อยู่ภายในโฟลเดอร์ `Gitlab` — ถ้าอาจารย์ต้องการให้เปิดที่ root ของ repo โดยตรง สามารถเปิด `Gitlab` เป็น Project Folder ได้

## คำสั่งที่ใช้รันโปรเจกต์ (อ้างอิง)

```powershell
cd "C:\Users\User\Documents\Default Project\Gitlab"
.\.venv\Scripts\python.exe -m flask --app app run --debug --port 5000
```

เปิด <http://127.0.0.1:5000/>
