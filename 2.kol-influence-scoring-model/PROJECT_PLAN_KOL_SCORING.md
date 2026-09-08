# KOL Influence & Engagement Scoring Model

## เป้าหมายโปรเจค

สร้าง statistical model จัดอันดับ KOL/creator ตาม influence และ engagement จริง ไม่ใช่แค่ยอด
follower ดิบ ๆ — ตรงกับงาน "trend KOLs" ใน JD สาย Martech โดยใช้สถิติเป็นแกนหลัก

### Story ที่ต้องการสื่อ
โปรเจคนี้โชว์ hard skill สถิติตรงที่สุดในพอร์ต — การ normalize ตัวแปรที่หน่วยต่างกัน, การถ่วงน้ำหนัก
อย่างมีเหตุผล, และการทดสอบความสัมพันธ์ระหว่างตัวแปรด้วย correlation/regression คือทักษะที่
data analyst ต้องมี ไม่ใช่แค่การทำ dashboard สวย ๆ

---

## ขอบเขตข้อมูล (Data Source)

**แหล่งหลัก: YouTube Data API v3** (ใช้ key เดิมจาก project แรกได้เลย ไม่ต้องขอใหม่)

- [ ] เลือก niche 1 อัน (เช่น รีวิวเทค, ความงาม, อาหาร, การเงิน) — เลือกอะไรที่คุณรู้จัก content
      ในวงการนั้นบ้าง จะช่วยตอน interpret ผลลัพธ์
- [ ] Curate รายชื่อ YouTube channel 15-25 ช่องในวงการเดียวกัน (ขนาดหลากหลาย ทั้งเล็กและใหญ่
      เพื่อให้เห็น distribution ที่มีความหมายทางสถิติ)
- [ ] (ทางเลือกเสริม) ใช้ NEWSAPI_KEY เช็คว่า KOL คนไหนเคยเป็นข่าว (controversy/รางวัล) เพื่อ
      เพิ่มมิติ "reputation" เข้าไปในการวิเคราะห์

---

## Tech Stack

- **Data collection:** Python 3.11+, `google-api-python-client`
- **Stats/Analysis:** Python (`pandas`, `numpy`, `scipy.stats`) — z-score, Pearson correlation,
  linear regression
- **AI layer:** Claude API — จัดหมวด content theme ของวิดีโอจาก title/description
- **Storage:** JSON files ใน repo
- **Frontend:** Next.js + Tailwind + Recharts (scatter plot, bar leaderboard, line trend)
- **Deployment:** GitHub → Vercel

---

## Statistical Methodology (หัวใจของโปรเจค)

### 1. Metrics ต่อ KOL (คำนวณจาก 10-15 วิดีโอล่าสุด)
- `avg_views` — ยอดวิวเฉลี่ย
- `engagement_rate = (avg_likes + avg_comments) / avg_views` — สัดส่วนคนที่ engage ต่อคนดู
- `upload_consistency` — จำนวนวิดีโอที่ลงในช่วง 90 วันล่าสุด (สม่ำเสมอ = สัญญาณ active creator)
- `subscriber_count` — ยอด subscriber ปัจจุบัน (baseline size)

### 2. Normalization — ทำไมต้องทำ
`subscriber_count` อยู่ในหลักแสน-ล้าน ส่วน `engagement_rate` อยู่ในหลัก 0.01-0.1 ถ้ารวมตรง ๆ
subscriber_count จะครอบงำคะแนนทั้งหมด ต้องแปลงทุกตัวแปรเป็น **z-score** ก่อน:

```
z(x) = (x - mean(x)) / std(x)
```

คำนวณ z-score แยกในกลุ่ม KOL ที่ curate มา (relative to peer group ไม่ใช่ absolute scale)

### 3. Composite Score
```
score = 0.4 * z(engagement_rate) + 0.3 * z(avg_views) + 0.3 * z(upload_consistency)
```
น้ำหนัก 0.4/0.3/0.3 เป็นจุดเริ่มต้น — ต้องเขียนอธิบายเหตุผลการเลือกน้ำหนักไว้ใน README
(เช่น ให้ engagement_rate น้ำหนักสูงสุดเพราะสะท้อน "influence จริง" มากกว่าขนาด channel)

### 4. Statistical Validation (ส่วนที่ทำให้ project นี้แข็งแรง)
- [ ] คำนวณ **Pearson correlation matrix** ระหว่าง subscriber_count, engagement_rate,
      upload_consistency — ตอบคำถาม เช่น "ช่องใหญ่ engagement ต่ำกว่าจริงไหม" (มักเป็นจริงและ
      น่าสนใจถ้าพิสูจน์ได้ด้วยข้อมูลจริง)
- [ ] ทำ **simple linear regression**: predict engagement_rate จาก subscriber_count +
      upload_consistency รายงานค่า R² และแปลความหมายว่าตัวแปรอธิบาย engagement ได้กี่เปอร์เซ็นต์
- [ ] ระบุ limitation ตรง ๆ ใน README เช่น sample size เล็ก (15-25 ช่อง) ทำให้ผลทางสถิติมี
      confidence จำกัด — การพูดถึง limitation คือสัญญาณของคนที่เข้าใจสถิติจริง

### 5. Trend Classification (ตอบโจทย์ "trend KOL" ตรง ๆ)
รัน collector ซ้ำทุกสัปดาห์ (ผ่าน GitHub Actions cron) เก็บ score ของแต่ละ KOL เป็น time series
แล้ว label เป็น **Rising / Stable / Declining** จาก% การเปลี่ยนแปลง score ระหว่างสัปดาห์
(ฟีเจอร์นี้เป็น stretch goal — ถ้าเวลาไม่พอ ใช้ snapshot เดียวไปก่อนแล้วระบุใน README ว่าเป็น
ส่วนต่อยอดในอนาคต)

---

## แผนพัฒนา (Phases)

### Phase 0 — Setup
- [ ] เลือก niche + curate รายชื่อ KOL 15-25 ช่อง (เก็บเป็น `data/kol_list.json`)
- [ ] Repo ใหม่แยกจาก project แรก: `npx create-next-app@latest kol-scoring-model --tailwind --app`
- [ ] Init git, `.gitignore`

### Phase 1 — Data Collection
- [ ] เขียน `scripts/collect_youtube.py` — ดึง channel statistics + video statistics (views,
      likes, comments, publish date) ของแต่ละ KOL ใน list
- [ ] เก็บผลเป็น `data/raw_kol_stats.json`

### Phase 2 — Statistical Analysis
- [ ] เขียน `scripts/compute_scores.py` — คำนวณ metrics, z-score, composite score,
      correlation matrix, regression
- [ ] เขียน `scripts/classify_themes.py` — ส่ง video title/description ไป Claude API
      จัดหมวด content theme
- [ ] Export เป็น `data/kol_scores.json`

### Phase 3 — Dashboard (Next.js)
- [ ] หน้า Leaderboard: ตารางจัดอันดับ KOL ตาม composite score
- [ ] Scatter plot: subscriber_count (x) vs engagement_rate (y) — ให้เห็น outlier ชัด ๆ
- [ ] Correlation/regression summary panel — โชว์ตัวเลขสถิติพร้อมคำอธิบายภาษาคน
- [ ] Content theme breakdown ต่อ KOL

### Phase 4 — Deploy
- [ ] Push ขึ้น GitHub repo ใหม่
- [ ] เชื่อม Vercel, ตั้งค่า env vars

### Phase 5 — Polish
- [ ] README อธิบาย methodology, การเลือกน้ำหนัก score, และ limitation ของ sample size
- [ ] ย่อหน้า "What this demonstrates" เชื่อมกับทักษะสถิติที่ตำแหน่งต้องการ

---

## Environment Variables

```
YOUTUBE_API_KEY=
ANTHROPIC_API_KEY=
NEWSAPI_KEY=       # optional, สำหรับเช็ค reputation/controversy
```

---

## หมายเหตุสำหรับ Claude Code

ทำทีละ Phase ตามลำดับ Phase 2 (Statistical Analysis) คือส่วนที่สำคัญที่สุด — ให้เขียน docstring
อธิบายสูตรและเหตุผลของแต่ละ metric ไว้ในโค้ดด้วย เพื่อให้กลับมาอธิบายตอนสัมภาษณ์ได้ง่าย
