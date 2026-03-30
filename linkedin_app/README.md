# LinkedIn Posting Automation App

**Automated LinkedIn posting system for C++ learning content.**

---

## 📋 Overview

This app manages the daily posting of 88 C++ learning carousels to LinkedIn. Currently in **manual phase** with plans for full automation.

**Status:** Phase 1 - Manual Posting with Tracking ✅

---

## 📂 Directory Structure

```
linkedin_app/
├── README.md                    # This file
├── TODO.md                      # Roadmap and requirements
├── config/                      # Configuration files
│   ├── .env.example            # Environment template
│   └── linkedin_config.json   # App configuration
├── tracker/                     # Posting progress tracking
│   ├── posting_tracker.txt     # Daily checklist (MAIN FILE)
│   ├── posting_schedule.csv    # CSV format for spreadsheets
│   └── POSTING_SCHEDULE.md     # Full documentation
├── automation/                  # Future automation scripts
│   ├── linkedin_poster.py     # (PLANNED) Auto-posting script
│   ├── scheduler.py            # (PLANNED) Daily scheduler
│   └── analytics.py            # (PLANNED) Analytics tracker
└── logs/                        # Posting logs
    └── posting_history.log     # Auto-generated posting log
```

---

## 🎯 Current Workflow (Manual)

### Daily Posting Process

1. **Open tracker:**
   ```bash
   nano ~/autolinkedin/linkedin_app/tracker/posting_tracker.txt
   ```

2. **Find today's post:**
   - Look for first `[ ]` TODO item
   - Example: `[ ] Day 1  | ch01_topic01_morning | Classes, Structs...`

3. **Get files:**
   - PDF: `/home/pankaj/autolinkedin/data/ch01_topic01_morning.pdf`
   - Caption: `/home/pankaj/autolinkedin/data/ch01_topic01_morning.txt`

4. **Post to LinkedIn:**
   - Upload PDF as carousel
   - Copy caption from .txt file
   - Add hashtags (included in caption)
   - Post

5. **Mark complete:**
   - Change `[ ]` to `[X]` in posting_tracker.txt
   - Update QUICK STATS counter

---

## 📊 Tracking Files

### 1. posting_tracker.txt (Primary)
- **Format:** Simple checkbox list
- **Use:** Daily tracking
- **Update:** Change [ ] to [X] when posted

### 2. posting_schedule.csv
- **Format:** CSV spreadsheet
- **Use:** Import to Excel/Google Sheets
- **Columns:** Day, Status, PDF_File, Caption_File, Topic, Chapter, Posted_Date

### 3. POSTING_SCHEDULE.md
- **Format:** Full markdown documentation
- **Use:** Reference and overview
- **Content:** Complete schedule, milestones, statistics

---

## 🚀 Future Automation Features

### Phase 1: Manual Posting ✅ (CURRENT)
- ✅ 88 PDFs generated
- ✅ 88 LinkedIn captions created
- ✅ Tracking system in place
- ✅ Daily workflow documented

### Phase 2: LinkedIn API Integration 🔄 (PLANNED)
- [ ] LinkedIn Graph API setup
- [ ] OAuth authentication
- [ ] Test posting via API
- [ ] Error handling and retries

### Phase 3: Automated Scheduling ⏳ (PLANNED)
- [ ] Daily scheduler (8:00 AM posting)
- [ ] Queue management
- [ ] Automatic tracker updates
- [ ] Failure notifications

### Phase 4: Analytics & Monitoring ⏳ (PLANNED)
- [ ] Engagement tracking
- [ ] Performance analytics
- [ ] Optimal posting time analysis
- [ ] Growth metrics dashboard

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# LinkedIn API Credentials
INSTAGRAM_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_USER_ID=your_user_id_here

# Posting Configuration
POSTING_TIME=08:00
TIMEZONE=Asia/Tokyo

# Content Paths
PDF_PATH=/home/pankaj/autolinkedin/data
TRACKER_PATH=/home/pankaj/autolinkedin/linkedin_app/tracker

# Logging
LOG_LEVEL=INFO
LOG_FILE=/home/pankaj/autolinkedin/linkedin_app/logs/posting_history.log
```

### linkedin_config.json

```json
{
  "content_location": "/home/pankaj/autolinkedin/data",
  "tracker_file": "tracker/posting_tracker.txt",
  "total_days": 88,
  "posting_schedule": {
    "time": "08:00",
    "timezone": "Asia/Tokyo",
    "skip_weekends": false
  },
  "linkedin": {
    "max_carousel_size": 10,
    "image_format": "PDF",
    "dimensions": "1080x1080"
  },
  "retry_policy": {
    "max_attempts": 3,
    "retry_delay": 300
  }
}
```

---

## 📈 Content Statistics

- **Total Posts:** 88 days
- **Format:** Square carousel (1080×1080px)
- **Content:** C++ learning topics from basics to C++20
- **Chapters:** 20 chapters covering full C++ curriculum
- **Average Slides:** 10-15 per PDF carousel

---

## 🛠️ Development Setup (For Future Automation)

### Prerequisites

```bash
# Python 3.10+
python3 --version

# Install dependencies
pip install -r ../requirements.txt

# Additional dependencies for automation
pip install instagrapi  # LinkedIn API wrapper
pip install schedule    # Task scheduling
```

### LinkedIn API Setup (When Ready)

1. Create Facebook Developer App
2. Configure LinkedIn Graph API
3. Get access token
4. Test API connection
5. Implement posting logic

---

## 📝 Usage Examples

### Check Today's Post

```bash
# View next post to upload
head -40 tracker/posting_tracker.txt | grep "^\[ \]" | head -1
```

### Mark Post as Complete

```bash
# Edit tracker file
nano tracker/posting_tracker.txt
# Change [ ] to [X] for the day posted
```

### View Progress

```bash
# Count completed posts
grep "^\[X\]" tracker/posting_tracker.txt | wc -l

# Count remaining posts
grep "^\[ \]" tracker/posting_tracker.txt | wc -l
```

### Export to Spreadsheet

```bash
# Open CSV in LibreOffice/Excel
libreoffice tracker/posting_schedule.csv
```

---

## 🔍 Troubleshooting

### Issue: Can't find PDF file
**Solution:** PDFs are in `/home/pankaj/autolinkedin/data/`

### Issue: Caption file missing
**Solution:** Caption .txt files are in same folder as PDFs

### Issue: Lost tracking progress
**Solution:** Check `tracker/posting_tracker.txt` - all marked [X] are completed

### Issue: Need to skip a day
**Solution:** Just skip to next [ ] item, doesn't have to be sequential

---

## 📚 Related Documentation

- **[../README.md](../README.md)** - Main project documentation
- **[../docs/](../docs/)** - Technical documentation
- **[TODO.md](TODO.md)** - Development roadmap and tasks

---

## 📧 Notes

- Always backup tracker file before editing
- Keep CSV file updated for analytics
- Test automation features in staging before production
- LinkedIn has rate limits - max 25 posts/day (we post 1/day)

---

**Created:** March 30, 2026
**Status:** Active - Manual Phase
**Next Phase:** LinkedIn API Integration (when ready)
