# Superpowers Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ใช้ Superpowers workflow กับ DC Bias Web App ที่มีอยู่ และเก็บหลักฐานที่ตรวจได้ลงใน repo แล้ว push

**Architecture:** แอปและเทสต์เดิมยังใช้ได้ — ไม่ rebuild ไม่เพิ่มโหมดไบอัส งานที่เหลือคือ (1) เขียนเทสต์ที่บังคับให้มีเอกสารแสดงลำดับ workflow และ (2) รันตรวจจริงแล้วบันทึกผล+push เอกสาร/meta อยู่ใต้ `docs/superpowers/` ตามโครงสร้างเดิม

**Tech Stack:** Python 3.12, `unittest`, Flask 3.0.3, Markdown, Git/GitHub

**Spec:** `docs/superpowers/specs/2026-11-24-superpowers-workflow-design.md`

## Global Constraints

- Scope เฉพาะ **Flask Web App DC Bias** ห้ามเพิ่ม Bode Plot / Transient / Signal Generator / Overlay Animation / SPICE Solver / โหมดใหม่
- ห้ามก็อปข้อความหรือรูปแบบจากภาพตัวอย่าง ให้เขียนด้วยถ้อยคำของเราเอง
- เทสต์เดิม 16 รายการต้องยังผ่านทุกครั้ง (ห้ามแก้เพื่อให้ผ่าน)
- รันเทสต์ด้วย `.\.venv\Scripts\python.exe -m unittest discover -s tests` (ไม่ใช่ pytest)
- Commit message ขึ้นต้นด้วย `test:`, `docs:` หรือ `chore:`
- Push ขึ้น `origin/main` และต้องทำให้ `git status -sb` กลับมาสะอาด

## Review Focus

- `dc_bias.py` หายหรือ re-export ผิด → ทดสอบ import และชื่อฟังก์ชันใน Task 1
- README ไม่บอก Local Server หรือลิงก์หลักฐาน → ทดสอบข้อความใน README ใน Task 1
- เอกสาร Design/Plan/Record ไม่ได้ commit → ทดสอบว่ามีไฟล์จริงใน Task 1
- POST ค่า Divider เพี้ยน (IC/VCE) → ตรวจ HTTP จริงใน Task 2 ด้วยค่า 1.230 / 8.052
- งานค้างใน working tree หรือยังไม่ push → ตรวจ `git status -sb` และ `git rev-parse` ใน Task 2

---

### Task 1: บังคับหลักฐาน workflow ด้วยเทสต์ + เอกสาร record

**Files:**
- Create: `tests/test_structure.py`
- Create: `docs/superpowers/workflow-record.md`
- Modify: `README.md` (เพิ่มลิงก์ไปยัง workflow-record.md)

**Interfaces:**
- Consumes: ไฟล์ที่已有的 `dc_bias.py`, `docs/superpowers/specs/2026-11-24-superpowers-workflow-design.md`, `docs/superpowers/plans/2026-11-24-superpowers-workflow.md`
- Produces: `TestWorkflowArtifacts` (3 tests) ที่ตรวจ path, README, และ import; เอกสาร `workflow-record.md` ที่มีตาราง 6 ขั้นตามลำดับ Tool Setup → Brainstorm → Plan Approval → Execute → Test/Review → GitHub

- [ ] **Step 1: เขียนเทสต์ที่ยัง fail**

`tests/test_structure.py`:

```python
import importlib
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestWorkflowArtifacts(unittest.TestCase):
    def test_workflow_files_exist(self):
        for rel in (
            "docs/superpowers/specs/2026-11-24-superpowers-workflow-design.md",
            "docs/superpowers/plans/2026-11-24-superpowers-workflow.md",
            "docs/superpowers/workflow-record.md",
        ):
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_readme_links_local_server_and_record(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("http://127.0.0.1:5000/", text)
        self.assertIn("docs/superpowers/workflow-record.md", text)

    def test_dc_bias_entry_point_reexports_calculators(self):
        module = importlib.import_module("dc_bias")
        for name in ("calculate_bias", "calculate_fixed", "calculate_emitter"):
            self.assertTrue(hasattr(module, name), name)
```

- [ ] **Step 2: รันเทสต์เพื่อยืนยันว่า fail จริง**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_structure -v`
Expected: FAIL เฉพาะ `test_workflow_files_exist` ด้วยข้อความ `docs/superpowers/workflow-record.md` (อีก 2 tests ผ่าน)

- [ ] **Step 3: สร้าง `docs/superpowers/workflow-record.md`**

เขียนใหม่ด้วยถ้อยคำของเรา เนื้อหาต้องมีหัวข้อ `## Workflow Record` และตารางที่มี 6 แถวชื่อขั้นตรงตามลำดับข้างบน แต่ละแถวมีคอลัมน์ `ขั้น`, `สิ่งที่ทำ`, `หลักฐาน/คำสั่ง` ช่องหลักฐานต้องระบุคำสั่งจริงที่ใช้ในโปรเจกต์ (เช่น `git --version`, `plugin list`, `-m unittest discover -s tests`, `urllib.request` ไปที่ 127.0.0.1:5000, `git push origin main`) ห้ามก็อปข้อความจากภาพ

เพิ่มลิงก์ `[Superpowers workflow record](docs/superpowers/workflow-record.md)` ใต้หัวข้อ Lab 4 ใน `README.md`

- [ ] **Step 4: รันเทสต์จนผ่าน**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_structure -v`
Expected: PASS 3 tests

- [ ] **Step 5: Commit**

```bash
git add tests/test_structure.py docs/superpowers/workflow-record.md README.md
git commit -m "test: pin Superpowers workflow artifacts and record"
```

### Task 2: ตรวจเต็มชุดแล้ว push

**Files:**
- Modify: `docs/superpowers/workflow-record.md` (เติม hash ของ commit และผลตรวจจริงจากขั้นตอนนี้)

**Interfaces:**
- Consumes: `TestWorkflowArtifacts` จาก Task 1, เทสต์เดิม 16 รายการ
- Produces: ผลตรวจจริง + หลักฐานว่าอยู่บน `origin/main`

- [ ] **Step 1: รันชุดเทสต์ทั้งหมด**

Run: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`
Expected: `Ran 19 tests` ... `OK` (16 เดิม + 3 ใหม่)

- [ ] **Step 2: ตรวจ HTTP จริงที่ Local Server**

Run: สคริปต์ `urllib.request` ยิง `GET /` และ `POST /` with `mode=divider, VCC=12, R1=100, R2=22, RC=2.2, RE=1, beta=100, VBE=0.7, unit=kohm`
Expected: status 200 ทั้งคู่ และใน HTML มี `1.230`, `8.052`, `V<sub>TH</sub>`, `18032.8`

- [ ] **Step 3: เติมผลจริงลง record แล้ว commit**

Run: แก้ตารางใน `docs/superpowers/workflow-record.md` ให้มีจำนวนเทสต์ 19, ผล HTTP, และ commit hash ของ Task 1
Expected: ไฟล์มีข้อมูลจริง ไม่มี placeholder

```bash
git add docs/superpowers/workflow-record.md
git commit -m "docs: record Superpowers workflow verification results"
```

- [ ] **Step 4: Push และยืนยันสะอาด**

Run: `git push origin main` ตามด้วย `git status -sb` และ `git log -1 --oneline`
Expected: push สำเร็จ, `## main...origin/main` ไม่มีไฟล์ค้าง, log แสดง commit ล่าสุดของเรา
