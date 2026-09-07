# Employer Brand Perception Analyzer

## เป้าหมายโปรเจค

วิเคราะห์ว่าคนพูดถึงบริษัท (ในฐานะ "ที่ทำงาน") บนโซเชียลอย่างไร โดยดึงข้อมูลจากแหล่งสาธารณะ
ผ่านกระบวนการเดียวกับงาน social listening / Martech analyst: **pull data → clean → analyze
(sentiment + theme) → visualize → สรุป insight**

### Story ที่ต้องการสื่อ (สำคัญมาก — ใช้ตอบสัมภาษณ์)
โปรเจคนี้คือการเอาประสบการณ์ HR (เข้าใจว่าอะไรที่พนักงาน/คนสมัครงานให้ความสำคัญ) มาผสมกับ
ความรู้จิตวิทยา (การตีความ perception/attitude ไม่ใช่แค่ positive-negative) และ hard skill
ด้าน data pipeline + statistics ที่ต้องมีในตำแหน่ง data analyst สาย Martech

---

## ขอบเขตข้อมูล (Data Sources)

เลือกบริษัท 2-3 บริษัทที่สนใจ (เช่น บริษัทที่อยากสมัครงานด้วย หรือแบรนด์ที่คนพูดถึงเยอะ) แล้วดึงข้อมูลจาก:

| แหล่งข้อมูล | เครื่องมือ | หมายเหตุ |
|---|---|---|
| Reddit | `praw` (Python, Reddit API — ฟรี) | ค้นหา mention ชื่อบริษัท + subreddit ที่เกี่ยวกับงาน |
| YouTube comments | YouTube Data API v3 (ฟรี 10k units/วัน) | คอมเมนต์ใต้คลิปรีครูท/ข่าวบริษัท |
| News | NewsAPI.org (free tier) | เหตุการณ์ที่กระทบ reputation บริษัท |
| (ทางเลือกเสริม) | Kaggle public Glassdoor/Indeed review datasets | ใช้แทนการ scrape ตรง ๆ ซึ่งผิด ToS |

**ข้อควรระวังด้านจริยธรรม/กฎหมาย:** ห้าม scrape Glassdoor/Indeed/LinkedIn โดยตรง (ผิด ToS)
ใช้เฉพาะ API ที่เปิดให้ใช้อย่างเป็นทางการ หรือ dataset ที่เผยแพร่เพื่อการวิจัยอยู่แล้ว

---

## Tech Stack

- **Data collection:** Python 3.11+, `praw`, `google-api-python-client`, `requests`
- **Analysis:** Python (`pandas`), sentiment + theme classification ผ่าน Claude API
  (batch call ให้ AI จัดหมวดคอมเมนต์เข้า HR theme — ดู "Theme Taxonomy" ด้านล่าง)
- **Storage:** JSON files ใน repo (เพียงพอสำหรับ demo) หรือ Supabase (Postgres ฟรี) ถ้าอยากให้ refresh ได้
- **Frontend:** Next.js (App Router) + Tailwind CSS + Recharts
- **Deployment:** GitHub → Vercel (auto-deploy ทุกครั้งที่ push เข้า `main`)

### Theme Taxonomy (จุดขาย HR + Psychology)
จัด comment เข้า 6 หมวดนี้ (ปรับได้ตามข้อมูลจริง):
1. Compensation & Benefits
2. Work-Life Balance
3. Management & Leadership
4. Career Growth & Development
5. Company Culture
6. Job Security & Stability

---

## แผนพัฒนา (Phases)

### Phase 0 — Setup
- [x] เลือก 2-3 บริษัทเป้าหมาย: **Agoda, True Digital Group, SCBX (SCB)**
- [ ] สมัคร API key: Reddit (praw), YouTube Data API, NewsAPI.org — ผู้ใช้ยังไม่ได้สมัคร (ดู guide ก่อนเริ่ม Phase 1)
- [x] `npx create-next-app@latest employer-brand-perception --tailwind --app`
- [x] Init git repo, สร้าง `.gitignore` (รวม `.env*`, `node_modules`, `__pycache__`)

### Phase 1 — Data Collection
- [ ] เขียน `scripts/collect_reddit.py` — ดึง post/comment ที่ mention บริษัท
- [ ] เขียน `scripts/collect_youtube.py` — ดึง comment จากคลิปที่เกี่ยวข้อง
- [ ] เขียน `scripts/collect_news.py` — ดึงข่าวจาก NewsAPI
- [ ] รวมข้อมูลทั้งหมดเป็น `data/raw_comments.json` (schema: source, company, text, date, url)

### Phase 2 — Analysis
- [ ] เขียน `scripts/analyze.py` — ส่ง comment แต่ละอันไป Claude API เพื่อ:
  - classify sentiment (positive/neutral/negative)
  - classify theme (จาก taxonomy ด้านบน)
  - ให้คะแนน confidence
- [ ] คำนวณสถิติ: sentiment distribution ต่อบริษัท, theme frequency, trend ตามเวลา
- [ ] เขียนผลลัพธ์เป็น `data/processed_insights.json`
- [ ] (ถ้ามีเวลา) ทำ statistical test เปรียบเทียบบริษัท เช่น chi-square ว่า theme distribution ต่างกันมีนัยสำคัญไหม

### Phase 3 — Dashboard (Next.js)
- [ ] หน้า Overview: sentiment score ต่อบริษัท (gauge/bar chart)
- [ ] หน้า Theme Breakdown: stacked bar/pie ต่อหมวด
- [ ] หน้า Trend: line chart sentiment over time
- [ ] Panel "AI Executive Summary" — เรียก Claude API สรุป insight เป็นย่อหน้า (ตรงกับ JD ที่บอก
      "feed data ให้ AI วิเคราะห์เป็นก็จบ")
- [ ] แสดงตัวอย่าง comment จริงประกอบแต่ละหมวด (2-3 ตัวอย่าง)

### Phase 4 — Deploy
- [ ] สร้าง repo บน GitHub, `git remote add origin ...`, `git push -u origin main`
- [ ] เชื่อม Vercel กับ GitHub repo (import project ใน Vercel dashboard)
- [ ] ตั้งค่า environment variables ใน Vercel (API keys) — **ห้าม commit .env ขึ้น GitHub เด็ดขาด**
- [ ] ตรวจสอบว่า deploy สำเร็จ ได้ live URL

### Phase 5 — Polish (สำคัญสำหรับสัมภาษณ์)
- [ ] เขียน README.md อธิบาย methodology + ทำไมถึงเลือก theme taxonomy นี้ (เชื่อมกับ HR background)
- [ ] เขียนย่อหน้า "What this project demonstrates" เชื่อม psychology + HR + data skill
      ไว้ใน README เพื่อใช้เตรียมตอบสัมภาษณ์
- [ ] ใส่ screenshot dashboard ใน README

---

## Environment Variables ที่ต้องใช้

```
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
YOUTUBE_API_KEY=
NEWSAPI_KEY=
ANTHROPIC_API_KEY=
```

---

## หมายเหตุสำหรับ Claude Code

เมื่อเริ่มทำงานกับไฟล์นี้ ให้เริ่มจาก Phase 0 → 1 → 2 → 3 → 4 → 5 ตามลำดับ ทำทีละ phase
และ commit เข้า git หลังจบแต่ละ phase (`git commit -m "phase X: ..."`) เพื่อให้ history
สะอาดและ deploy บน Vercel ได้ preview ทีละ step
