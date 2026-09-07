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
- [x] เลือก 2-3 บริษัทเป้าหมาย: ~~Agoda, True Digital Group, SCBX~~ → **Agoda, Shopee Thailand,
      Grab Thailand** (เปลี่ยนหลัง Phase 1-2 พบว่า True Digital Group/SCBX มี comment ที่เกี่ยวกับ
      "การเป็นนายจ้าง" น้อยเกินไปจะวิเคราะห์ได้ — ดู note ใน Phase 2)
- [x] สมัคร API key: YouTube Data API, NewsAPI.org, Anthropic — ใส่ครบแล้วใน `.env.local`
      (ข้าม Reddit เพราะ Reddit's Responsible Builder Policy ต้อง request อนุมัติแอปก่อนใช้งาน
      จริง user เลือกไม่สมัคร — สคริปต์รองรับการข้าม source นี้อัตโนมัติ)
- [x] `npx create-next-app@latest employer-brand-perception --tailwind --app`
- [x] Init git repo, สร้าง `.gitignore` (รวม `.env*`, `node_modules`, `__pycache__`)

### Phase 1 — Data Collection
- [x] เขียน `scripts/collect_reddit.py` — ดึง post/comment ที่ mention บริษัท (ข้ามได้ถ้าไม่มี key)
- [x] เขียน `scripts/collect_youtube.py` — ดึง comment จากคลิปที่เกี่ยวข้อง
- [x] เขียน `scripts/collect_news.py` — ดึงข่าวจาก NewsAPI
- [x] รวมข้อมูลทั้งหมดเป็น `data/raw_comments.json` — **รันจริงแล้ว**: 1266 records
      (Agoda 375, Shopee Thailand 387, Grab Thailand 484; ข้าม Reddit)
      หลัง filter junk (emoji/ตัวเลขล้วน) อัตโนมัติใน `scripts/store.py`

### Phase 2 — Analysis
- [x] เขียน `scripts/analyze.py` — ส่ง comment เป็น batch (10 comment/call) ไป Claude
      (`claude-haiku-4-5-20251001`) เพื่อ classify **employer_related** (ใช่/ไม่ใช่) + sentiment
      + theme + confidence — เพิ่ม employer_related เพราะ raw data ส่วนใหญ่เป็นคอมเมนต์เรื่องแอป/
      หุ้น/ตึก ไม่เกี่ยวกับการเป็นนายจ้าง ถ้าไม่กรองจะทำให้ sentiment เพี้ยน
- [x] คำนวณสถิติ: sentiment distribution ต่อบริษัท, theme frequency, trend **รายไตรมาส**
      (เปลี่ยนจากรายเดือนเพราะข้อมูลกระจายหลายปี ทำให้ trend รายเดือนสัญญาณรบกวนสูงเกินไป —
      ไตรมาสที่มี comment น้อยกว่า 3 จะเว้นเป็นช่องว่างแทนการพล็อตค่าที่ error สูง)
- [x] เขียนผลลัพธ์เป็น `data/processed_insights.json`
- [x] chi-square test (`scipy.stats.chi2_contingency`) เปรียบเทียบ theme distribution ระหว่างบริษัท
- [x] cache ผล classification ไว้ที่ `data/classified_comments.json` (ไม่ commit) — รันซ้ำครั้งต่อไป
      (เช่น เปลี่ยน aggregation logic) จะ classify เฉพาะ record ใหม่ ไม่เสีย API cost ซ้ำ

**รันจริงแล้ว**: 1246/1266 records classified สำเร็จ, 418 employer-related (828 ถูกกรองออกเพราะ
ไม่เกี่ยวกับการเป็นนายจ้าง) แบ่งเป็น Agoda 186, Shopee Thailand 130, Grab Thailand 102 —
chi-square significant (p < 0.001) ว่า theme distribution ต่างกันจริงระหว่าง 3 บริษัท

**บั๊กที่เจอและแก้ระหว่างรันจริงครั้งแรก**: `CLASSIFY_PROMPT` เป็น f-string ที่มี JSON ตัวอย่าง
ในตัว ทำให้ `.format()` ครั้งที่สองพยายาม parse JSON นั้นเป็น placeholder ซ้ำ → ทุก batch fail
ด้วย `KeyError` (แก้โดยเลิกใช้ `.format()` ต่อท้าย ใช้ f-string ต่อสตริงตรง ๆ แทน)

### Phase 3 — Dashboard (Next.js)
- [x] หน้า Overview: sentiment score ต่อบริษัท (stacked bar chart) + summary cards
- [x] หน้า Theme Breakdown: stacked bar ต่อหมวด + chi-square test result
- [x] หน้า Trend: line chart net sentiment score ต่อไตรมาส (เว้นช่องว่างเมื่อ sample น้อย)
- [x] Panel "AI Executive Summary" — เรียก Claude API (`/api/summary`) สรุป insight เป็นย่อหน้า
- [x] แสดงตัวอย่าง comment จริงประกอบแต่ละหมวด (3 ตัวอย่าง/บริษัท/หมวด)

**ทดสอบกับข้อมูลจริงผ่าน browser แล้ว** ทุกหน้าแสดงผลถูกต้อง, AI Executive Summary เรียก Claude
จริงและได้ย่อหน้าคุณภาพดี (แก้ปัญหา model แอบใส่ markdown heading ที่ UI render เป็น plain text
โดยเสริม prompt + strip เป็น safety net)

### Phase 4 — Deploy
- [x] สร้าง repo บน GitHub (`brightza234/employer-brand-perception`, public), push โค้ดแล้ว
- [x] เชื่อม Vercel กับ GitHub repo — คำแนะนำให้ user ทำเอง (ต้อง OAuth ด้วยบัญชีตัวเอง)
- [x] ตั้งค่า environment variables ใน Vercel (API keys) — **ห้าม commit .env ขึ้น GitHub เด็ดขาด**
- [x] ตัดสินใจเรื่อง `data/processed_insights.json` — commit ขึ้น repo แล้ว (ผู้ใช้ยืนยันแล้วว่า
      ok เพราะเป็นข้อมูล public + สรุป/ตัวอย่างเท่านั้น ไม่ใช่ raw data ทั้งหมด)
- [x] ตรวจสอบว่า deploy สำเร็จ ได้ live URL — **https://employer-brand-perception.vercel.app**
      ทดสอบทุกหน้า + AI Executive Summary บน production แล้ว ทำงานถูกต้องทั้งหมด

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
