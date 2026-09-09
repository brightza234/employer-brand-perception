# AI Analyst Copilot — MCP Server + Claude Skill (Capstone)

## เป้าหมายโปรเจค

รวม 5 โปรเจคก่อนหน้า (Employer Brand Perception, KOL Scoring, Survey Validation, Trend
Detection, Scraper ETL) เข้าเป็นระบบเดียวที่ Claude เรียกใช้ได้ผ่าน MCP พร้อม Skill ที่สอน Claude
ให้ตีความผลลัพธ์แบบนักวิเคราะห์ที่เข้าใจข้อจำกัดของแต่ละแหล่งข้อมูล

### Story ที่ต้องการสื่อ
โปรเจคนี้ตอบคำถาม "คุณเข้าใจ AI workflow ที่บริษัทต้องการจริงไหม" ด้วยของจริง ไม่ใช่คำพูด —
ทำให้ JD บรรทัด "feed data ให้ AI วิเคราะห์เป็นก็จบเลย" กลายเป็นระบบที่ใช้งานได้จริง และเปิดสาธิตสด
ในห้องสัมภาษณ์ได้เลย

---

## สถาปัตยกรรม

```
โปรเจคก่อนหน้า 5 อัน (JSON/SQLite ที่มีอยู่แล้ว)
        │  export/copy summary data
        ▼
   data/ ในโปรเจคนี้
        │
        ▼
   MCP Server (Python) ─── expose tools:
        │                   - get_employer_perception(company)
        │                   - get_kol_score(channel)
        │                   - get_trend_status(keyword)
        │                   - get_survey_validation(theme)
        │                   - query_scraped_data(query)
        ▼
   Claude Desktop (เชื่อมผ่าน claude_desktop_config.json)
        │
        ▼
   Claude Skill (analyst-playbook/SKILL.md) ─── สอนวิธีตีความผลลัพธ์
        │
        ▼
   ผู้ใช้พิมพ์ถามภาษาธรรมชาติ → Claude เรียก tool → ตอบพร้อม caveat ที่ถูกต้อง
```

---

## Tech Stack

- **MCP SDK:** Python `mcp` package (official) หรือ `fastmcp` (decorator-based, เขียนง่ายกว่า
  แนะนำเริ่มจากอันนี้)
- **Transport:** stdio (รันในเครื่อง, เชื่อมกับ Claude Desktop โดยตรง — ไม่ต้องมี hosting)
- **Data:** JSON ที่ export มาจาก 5 โปรเจคก่อนหน้า
- **Skill:** SKILL.md ตามฟอร์แมตมาตรฐานของ Anthropic (ดูด้านล่าง)
- **(Optional stretch):** deploy เป็น remote MCP server ผ่าน HTTP/SSE ถ้าอยากให้เข้าถึงได้จากที่อื่น
  โดยไม่ต้องรันในเครื่อง — แต่ demo แบบ local ผ่าน Claude Desktop ก็เพียงพอสำหรับ portfolio แล้ว

---

## Claude Skill — ฟอร์แมตที่ถูกต้อง

Skill คือโฟลเดอร์ที่มี `SKILL.md` เป็นไฟล์หลัก:

```
analyst-playbook/
├── SKILL.md          (required — YAML frontmatter + คำสั่งเป็น markdown)
└── references/        (optional — เอกสารอ้างอิงเพิ่มเติมที่ Claude อ่านเมื่อจำเป็น)
```

`SKILL.md` เริ่มด้วย YAML frontmatter:
```yaml
---
name: analyst-playbook
description: ตีความผลลัพธ์จาก social listening / KOL scoring / trend detection / survey
  validation tools ให้ตอบแบบนักวิเคราะห์ที่รู้ข้อจำกัดของข้อมูล ใช้เมื่อผู้ใช้ถามเกี่ยวกับ
  employer perception, KOL score, trend status, หรือ survey-social validation
---
```

ตามด้วยเนื้อหา markdown ที่สอน Claude เช่น:
- แต่ละ tool คืนค่าอะไร หน่วยไหน ตีความยังไง
- ทุกครั้งที่รายงาน sentiment/score ให้ระบุ sample size และ 1 ข้อจำกัดเสมอ
- เวลาเทียบ survey กับ social data ให้อธิบายด้วย self-selection bias / social desirability bias
- โครงสร้างคำตอบที่ต้องการ (เช่น สรุปสั้น → ตัวเลขอ้างอิง → ข้อจำกัด)

---

## แผนพัฒนา (Phases)

### Phase 0 — Setup
- [x] Repo ใหม่: ~~`mkdir analyst-copilot-mcp && cd analyst-copilot-mcp`~~ — ใช้โฟลเดอร์
      `6.Project plan MCP copilot` ที่มีอยู่แล้วเป็น project root แทน (สอดคล้องกับ 5 โปรเจคก่อนหน้า
      ที่แต่ละโปรเจคเป็นโฟลเดอร์เลขลำดับใน monorepo เดียวกัน)
- [x] Export summary JSON จากแต่ละโปรเจคก่อนหน้า มาเก็บไว้ใน `data/` ของ repo นี้ —
      ดู [`scripts/export_data.py`](scripts/export_data.py) (รันซ้ำได้ทุกครั้งที่ข้อมูลต้นทางอัปเดต)
- [x] ติดตั้ง `fastmcp`: `pip install fastmcp`

### Phase 1 — MCP Server
- [x] เขียน `server.py` — 5 tools อ่านจาก `data/` ที่ export มาใน Phase 0
- [x] ทดสอบด้วย MCP Inspector: `npx @modelcontextprotocol/inspector --cli python server.py
      --method tools/list` และ `tools/call` — ยืนยันแล้วว่าทุก tool คืนค่าถูกต้อง (พบและแก้บั๊ก
      duplicate rows ใน `5.Automated Scraper + ETL Pipeline/data/scraped.db` ระหว่างทาง — ดู
      `scripts/export_data.py` ที่ dedupe ไว้ และ flag แยกไปแก้ที่ repo ต้นทาง)

### Phase 2 — เชื่อมกับ Claude Desktop
- [x] แก้ไข `claude_desktop_config.json` เพิ่ม server นี้เข้าไป — path config จริงอยู่ที่
      `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`
      (แอปติดตั้งผ่าน Microsoft Store เลย AppData ถูก virtualize ไปที่นี่แทน path ปกติ)
- [x] เปิด Claude Desktop ใหม่ ทดสอบถามคำถามที่ต้องใช้แต่ละ tool — เชื่อมสำเร็จ, tool call จริงยืนยันแล้ว

### Phase 3 — เขียน Skill
- [x] ร่าง `analyst-playbook/SKILL.md` ตามฟอร์แมตด้านบน
- [x] ทดสอบถามคำถามจริง เทียบคำตอบก่อน/หลังมี skill ว่าตีความข้อมูลดีขึ้นไหม — ทดสอบด้วยคำถาม
      "employer sentiment ของ Agoda เป็นยังไง" คำตอบมีตัวเลขอ้างอิงครบ + caveat เรื่อง
      self-selection bias ต่อท้ายเสมอ ตรงตามที่ SKILL.md กำหนด
- [x] ปรับ SKILL.md ตามผลทดสอบ — คำตอบผ่านเกณฑ์ตั้งแต่รอบแรก ไม่ต้องปรับเพิ่ม

### Phase 4 — Demo Recording (สำคัญมากสำหรับสัมภาษณ์)
- [x] อัดหน้าจอ/ทำ GIF สาธิต Claude Desktop เรียก tool จริงแบบ end-to-end 2-3 คำถาม —
      ดู [`Demo.mp4`](Demo.mp4)
- [x] ใส่ GIF/วิดีโอนี้ไว้บนสุดของ README — นี่คือสิ่งแรกที่คนดู repo จะเห็น

### Phase 5 — Polish
- [x] README: อธิบาย MCP/Skill concept แบบเข้าใจง่ายสำหรับคนที่ไม่ใช่สายเทค + ลิงก์ไปยัง 5 โปรเจค
      ก่อนหน้าที่เป็นแหล่งข้อมูล
- [x] เขียนย่อหน้า "What this demonstrates" เชื่อมกับ JD บรรทัด AI-analysis workflow ตรง ๆ

---

## หมายเหตุสำหรับ Claude Code

โปรเจคนี้ไม่จำเป็นต้อง deploy web app บน Vercel เหมือน 5 โปรเจคก่อน — deliverable หลักคือ
MCP server ที่ทำงานได้จริงบนเครื่อง + Skill + วิดีโอ demo ถ้าอยากมีหน้าเว็บ landing page อธิบาย
โปรเจคเพิ่มเติมเพื่อความสม่ำเสมอของพอร์ตก็ทำได้ แต่ไม่ใช่ส่วนที่ต้องทำก่อน

**สถานะปัจจุบัน:** ครบทุก Phase (0-5) แล้ว — MCP server เชื่อม Claude Desktop จริง, Skill ทดสอบผ่าน,
มีวิดีโอ demo ใน README
