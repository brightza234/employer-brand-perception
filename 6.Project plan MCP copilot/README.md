# AI Analyst Copilot — MCP Server + Claude Skill

<!-- TODO: record a short screen-capture GIF/video of Claude Desktop calling these
tools end-to-end (2-3 questions) and embed it here first — this is the first
thing anyone opening this repo should see. -->

## แนวคิดแบบเข้าใจง่าย (สำหรับคนที่ไม่ใช่สายเทค)

ลองนึกภาพว่า Claude เป็นนักวิเคราะห์ข้อมูลที่เก่ง แต่ปกติเข้าไม่ถึงข้อมูลของบริษัทเรา —
**MCP (Model Context Protocol)** คือสายที่ต่อให้ Claude "เสียบปลั๊ก" เข้ากับข้อมูลจริงได้
โปรเจคนี้เปิดโปรแกรมเล็ก ๆ ตัวหนึ่ง (`server.py`) ที่รู้จักข้อมูลจาก 5 โปรเจคก่อนหน้า แล้วให้
Claude Desktop เรียกใช้ได้ผ่านคำถามภาษาธรรมชาติ เช่น "KOL ช่องนี้คะแนนเท่าไหร่" แล้ว Claude
จะไปดึงตัวเลขจริงมาตอบ ไม่ใช่เดาหรือแต่งขึ้นเอง

ส่วน **Skill** (`analyst-playbook/SKILL.md`) คือ "คู่มือการตีความ" ที่สอน Claude ว่าตัวเลขที่ได้
มาแต่ละตัวมีข้อจำกัดอะไรบ้าง เช่น คะแนน KOL เป็นคะแนนเทียบกลุ่มเท่านั้น ไม่ใช่คะแนนสัมบูรณ์ —
เพื่อให้คำตอบที่ได้อ่านแล้วเหมือนนักวิเคราะห์จริงพูด ไม่ใช่แค่ทิ้งตัวเลขดิบใส่หน้า

## สถาปัตยกรรม

```
5 โปรเจคก่อนหน้า (JSON/SQLite ที่มีอยู่แล้ว)
        │  scripts/export_data.py (copy + dedupe)
        ▼
   data/ ในโปรเจคนี้
        │
        ▼
   MCP Server (server.py, fastmcp, stdio) ─── 5 tools:
        │                   get_employer_perception / get_kol_score /
        │                   get_trend_status / get_survey_validation /
        │                   query_scraped_data
        ▼
   Claude Desktop (claude_desktop_config.json)
        │
        ▼
   Claude Skill (analyst-playbook/SKILL.md) ─── สอนวิธีตีความผลลัพธ์
        │
        ▼
   ผู้ใช้พิมพ์ถามภาษาธรรมชาติ → Claude เรียก tool → ตอบพร้อม caveat ที่ถูกต้อง
```

## ข้อมูลต้นทาง (5 โปรเจคก่อนหน้าในมอนอรีโปนี้)

| Tool | ข้อมูลจากโปรเจค |
|---|---|
| `get_employer_perception` | `1.employee-perception` — Employer Brand Perception Analyzer |
| `get_kol_score` | `2.kol-influence-scoring-model` — KOL Influence & Engagement Scoring Model |
| `get_survey_validation` | `3.survey-social-validation` — Survey × Social Validation |
| `get_trend_status` | `4.Trend Detection Dashboard` |
| `query_scraped_data` | `5.Automated Scraper + ETL Pipeline` |

(ลิงก์เป็น relative path เพราะปัจจุบันทุกโปรเจคยังอยู่ใน monorepo เดียวกัน — ถ้าแยก repo ในอนาคต
ให้อัปเดตลิงก์เป็น URL ของแต่ละ repo)

## เริ่มใช้งาน

```bash
pip install -r requirements.txt
python scripts/export_data.py   # sync ข้อมูลล่าสุดจาก 5 โปรเจคเข้า data/
```

ทดสอบ tool ทั้งหมดโดยไม่ต้องเปิด Claude Desktop ด้วย [MCP Inspector](https://github.com/modelcontextprotocol/inspector):

```bash
npx @modelcontextprotocol/inspector python server.py
```

### เชื่อมกับ Claude Desktop

คัดลอกเนื้อหาจาก [`claude_desktop_config.example.json`](claude_desktop_config.example.json)
เข้าไปใน `claude_desktop_config.json` ของเครื่อง (แก้ path ให้ตรงกับตำแหน่งไฟล์นี้จริง) แล้วเปิด
Claude Desktop ใหม่ — ตอนนี้ถามคำถามที่ต้องใช้ข้อมูลจาก 5 โปรเจคได้เลย เช่น "employer sentiment
ของ Agoda เป็นยังไง" หรือ "KOL ช่อง @iHAVECPU_ คะแนนเท่าไหร่"

## สิ่งที่โปรเจคนี้แสดงให้เห็น

โปรเจคนี้ตอบคำถาม "เข้าใจ AI workflow ที่บริษัทต้องการจริงไหม" ด้วยของจริงที่ใช้งานได้ ไม่ใช่แค่
พูดในทฤษฎี — เอาข้อมูลจาก 5 โปรเจคที่กระจัดกระจายกันมารวมเป็นระบบเดียวที่ Claude เรียกใช้ได้ตรง ๆ
ผ่าน MCP พร้อม Skill ที่สอนให้ตีความผลลัพธ์อย่างมีวิจารณญาณ (sample size, bias, ข้อจำกัดของแต่ละ
แหล่งข้อมูล) แทนที่จะทิ้งตัวเลขดิบให้คนอ่านตีความเอง

## หมายเหตุ

โปรเจคนี้ไม่ deploy เป็นเว็บแอป — deliverable หลักคือ MCP server ที่ทำงานได้จริงบนเครื่อง + Skill
+ วิดีโอสาธิต (ดู TODO ด้านบนสุดของไฟล์นี้)
