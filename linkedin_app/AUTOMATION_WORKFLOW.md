# LinkedIn Automation Workflow

**Current Status:** Phase 1 Complete, Phase 2-4 Need Development

---

## 🎯 Overview

This document explains how the automation will work when fully implemented.

---

## 📊 Development Phases

### ✅ Phase 1: Manual Posting (COMPLETE)

**Status:** 100% Done - Ready to use TODAY

**What's Built:**
- ✅ 88 PDFs generated
- ✅ 88 captions written
- ✅ Tracking system (3 formats)
- ✅ Documentation complete
- ✅ Quick start guide
- ✅ Directory structure organized

**How It Works Now (Manual):**
```
1. Open tracker file
2. Find Day X (first [ ] checkbox)
3. Open data/chXX_topicYY_morning.pdf
4. Copy caption from data/chXX_topicYY_morning.txt
5. Upload PDF to LinkedIn manually
6. Paste caption
7. Post
8. Mark [X] in tracker
```

**Time:** ~5 minutes per day

---

### ⏳ Phase 2: LinkedIn API Integration (NOT BUILT YET)

**Status:** 0% - Needs Development

**What Needs to Be Built:**

#### 2.1 LinkedIn API Setup
```python
# linkedin_app/automation/linkedin_poster.py (needs implementation)

class LinkedInPoster:
    def authenticate(self):
        """
        Implement LinkedIn OAuth 2.0
        - Get access token
        - Store credentials securely
        - Handle token refresh
        """
        pass  # TODO: Implement

    def post_carousel(self, pdf_path, caption):
        """
        Post to LinkedIn via API
        - Convert PDF to images (LinkedIn doesn't accept PDFs via API)
        - Upload each slide as carousel image
        - Add caption and hashtags
        - Publish post
        """
        pass  # TODO: Implement

    def upload_media(self, image_path):
        """
        Upload single image to LinkedIn
        - Register upload
        - Upload binary
        - Get media URN
        """
        pass  # TODO: Implement
```

#### 2.2 PDF to Image Conversion
```python
# NEW FILE: linkedin_app/automation/pdf_converter.py

from pdf2image import convert_from_path

def pdf_to_images(pdf_path):
    """
    Convert PDF slides to images for LinkedIn API
    - LinkedIn API requires images, not PDFs
    - Convert each page to 1080x1080 JPEG
    - Return list of image paths
    """
    images = convert_from_path(
        pdf_path,
        dpi=144,
        size=(1080, 1080)
    )
    # Save images and return paths
    pass  # TODO: Implement
```

#### 2.3 API Configuration
```bash
# linkedin_app/config/.env (needs your credentials)

LINKEDIN_CLIENT_ID=your_app_id
LINKEDIN_CLIENT_SECRET=your_app_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_USER_ID=your_profile_or_page_id
```

**Estimated Time:** 2-3 weeks
**Skills Needed:** Python, LinkedIn API, OAuth 2.0

---

### ⏳ Phase 3: Automated Scheduling (NOT BUILT YET)

**Status:** 0% - Needs Development

**What Needs to Be Built:**

#### 3.1 Daily Scheduler
```python
# linkedin_app/automation/scheduler.py (needs implementation)

from apscheduler.schedulers.blocking import BlockingScheduler
from linkedin_poster import LinkedInPoster
import pytz

class DailyScheduler:
    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.poster = LinkedInPoster()
        self.timezone = pytz.timezone('Asia/Tokyo')

    def schedule_daily_post(self):
        """
        Schedule posting at 8:00 AM daily
        - Runs every day at configured time
        - Gets next post from tracker
        - Posts via LinkedIn API
        - Updates tracker automatically
        """
        self.scheduler.add_job(
            self.daily_post_job,
            'cron',
            hour=8,
            minute=0,
            timezone=self.timezone
        )

    def daily_post_job(self):
        """
        Job that runs daily
        """
        # 1. Get next post
        next_post = self.get_next_post()

        # 2. Post to LinkedIn
        success = self.poster.post_carousel(
            next_post['pdf'],
            next_post['caption']
        )

        # 3. Update tracker
        if success:
            self.mark_complete(next_post['day'])
            self.log_success(next_post)
        else:
            self.retry_later(next_post)

    def start(self):
        """Start the scheduler (runs 24/7)"""
        self.scheduler.start()
```

#### 3.2 Automatic Tracker Updates
```python
# linkedin_app/automation/tracker_manager.py (NEW FILE)

def update_tracker(day_number):
    """
    Automatically update posting_tracker.txt
    - Change [ ] to [X] for completed day
    - Update stats counter
    - Log timestamp
    """
    pass  # TODO: Implement

def get_next_post():
    """
    Read tracker and find next unposted day
    - Parse posting_tracker.txt
    - Find first [ ] checkbox
    - Return day number and file names
    """
    pass  # TODO: Implement
```

**Estimated Time:** 1-2 weeks
**Skills Needed:** Python, APScheduler, cron jobs

---

### ⏳ Phase 4: Analytics & Monitoring (NOT BUILT YET)

**Status:** 0% - Needs Development

**What Needs to Be Built:**

#### 4.1 Analytics Collection
```python
# linkedin_app/automation/analytics.py (needs implementation)

class LinkedInAnalytics:
    def fetch_post_metrics(self, post_id):
        """
        Get engagement metrics via LinkedIn API
        - Likes
        - Comments
        - Shares
        - Impressions
        - Click-through rate
        """
        pass  # TODO: Implement

    def generate_daily_report(self):
        """
        Generate analytics report
        - Yesterday's post performance
        - Week-to-date summary
        - Top performing topics
        - Growth trends
        """
        pass  # TODO: Implement

    def track_follower_growth(self):
        """
        Track profile/page growth
        - New followers
        - Unfollows
        - Net growth
        - Growth rate
        """
        pass  # TODO: Implement
```

#### 4.2 Performance Dashboard
```python
# NEW FILE: linkedin_app/automation/dashboard.py

def create_dashboard():
    """
    Create visual analytics dashboard
    - Engagement trends chart
    - Best performing topics
    - Posting consistency
    - Follower growth
    """
    pass  # TODO: Implement
```

**Estimated Time:** 2-3 weeks
**Skills Needed:** Python, LinkedIn API, data visualization

---

## 🔄 Complete Automation Workflow (When Built)

### Phase 2-4 Combined Workflow:

```
┌─────────────────────────────────────────┐
│   Daily at 8:00 AM (Automatic)         │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  1. Scheduler Wakes Up                  │
│     - APScheduler triggers job          │
│     - Runs linkedin_poster.py           │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  2. Get Next Post                       │
│     - Read posting_tracker.txt          │
│     - Find first [ ] checkbox           │
│     - Get: Day X, PDF file, caption     │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  3. Prepare Content                     │
│     - Load PDF: data/chXX_topicYY.pdf   │
│     - Load caption: data/chXX_topicYY.txt│
│     - Convert PDF to images (if needed) │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  4. Post to LinkedIn API                │
│     - Authenticate with OAuth token     │
│     - Upload carousel images            │
│     - Add caption and hashtags          │
│     - Publish post                      │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  5. Update Tracker                      │
│     - Change [ ] to [X] in tracker      │
│     - Update stats: Completed +1        │
│     - Log to posting_history.log        │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  6. Collect Analytics (Phase 4)         │
│     - Wait 24 hours                     │
│     - Fetch post metrics                │
│     - Store in database                 │
│     - Update dashboard                  │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  7. Send Notification                   │
│     - Email: "Day X posted ✅"          │
│     - Summary: Likes, comments, etc.    │
└─────────────────────────────────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  Wait 24 hrs  │
            │  Repeat daily │
            └───────────────┘
```

---

## 🛠️ Technical Implementation Details

### LinkedIn API Requirements

**What You Need:**
1. LinkedIn Developer Account
2. Create LinkedIn App
3. Get API credentials:
   - Client ID
   - Client Secret
   - Access Token (OAuth 2.0)

**API Endpoints to Use:**
```
POST /ugcPosts             # Create post
POST /assets               # Upload media
GET /socialActions         # Get analytics
GET /organizationalEntityAcls  # Permissions
```

**Rate Limits:**
- 100 API calls per day (free tier)
- 500 API calls per day (verified app)

### PDF to Image Conversion

**Why Needed:**
LinkedIn API doesn't accept PDFs directly. Must convert to images.

**Libraries:**
```bash
pip install pdf2image
pip install Pillow
```

**Implementation:**
```python
from pdf2image import convert_from_path

def convert_pdf_for_linkedin(pdf_path):
    images = convert_from_path(
        pdf_path,
        dpi=144,
        fmt='jpeg',
        size=(1080, 1080)
    )

    image_paths = []
    for i, image in enumerate(images):
        path = f"temp_slide_{i}.jpg"
        image.save(path, 'JPEG', quality=95)
        image_paths.append(path)

    return image_paths
```

### Scheduler Setup

**Run as Service (Linux):**
```bash
# Create systemd service
sudo nano /etc/systemd/system/linkedin-poster.service

[Unit]
Description=LinkedIn Daily Poster
After=network.target

[Service]
Type=simple
User=pankaj
WorkingDirectory=/home/pankaj/autolinkedin
ExecStart=/usr/bin/python3 linkedin_app/automation/scheduler.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable linkedin-poster
sudo systemctl start linkedin-poster
```

**Or Run in Screen/Tmux:**
```bash
screen -S linkedin-poster
cd /home/pankaj/autolinkedin
python3 linkedin_app/automation/scheduler.py
# Ctrl+A, D to detach
```

---

## 📝 Development Roadmap

### Week 1-2: Phase 2 Foundation
- [ ] Set up LinkedIn Developer account
- [ ] Create LinkedIn App
- [ ] Implement OAuth authentication
- [ ] Test API connection
- [ ] Implement PDF to image conversion

### Week 3-4: Phase 2 Core
- [ ] Implement post_carousel()
- [ ] Handle API errors and retries
- [ ] Test posting (use test account)
- [ ] Verify image quality
- [ ] Validate caption formatting

### Week 5-6: Phase 3 Scheduling
- [ ] Implement scheduler.py
- [ ] Add automatic tracker updates
- [ ] Set up cron job or systemd service
- [ ] Implement error notifications
- [ ] Test 7-day automated run

### Week 7-9: Phase 4 Analytics
- [ ] Implement analytics collection
- [ ] Create metrics database
- [ ] Build performance dashboard
- [ ] Set up weekly reports
- [ ] Optimize posting strategy

---

## 🎯 Current Status Summary

| Phase | Status | Can Use? | Needs Work |
|-------|--------|----------|------------|
| **Phase 1** | ✅ 100% | **YES** | Nothing |
| **Phase 2** | ⏳ 0% | NO | Everything |
| **Phase 3** | ⏳ 0% | NO | Everything |
| **Phase 4** | ⏳ 0% | NO | Everything |

---

## 🚀 What You Can Do NOW

### Option 1: Start Posting Manually (Recommended)

**Why:** Content is ready, start building audience immediately

```bash
# Read quick start
cat linkedin_app/QUICKSTART.md

# Start posting Day 1
# Takes 5 minutes per day
```

**Timeline:** Start today, complete in 88 days

### Option 2: Build Automation First

**Why:** Save time in the long run, but delays content launch

**Steps:**
1. Complete Phase 2 (2-3 weeks)
2. Complete Phase 3 (1-2 weeks)
3. Test thoroughly (1 week)
4. Start automated posting

**Timeline:** Start in ~6 weeks

### Option 3: Hybrid Approach (Best)

**Why:** Get best of both worlds

**Steps:**
1. **Week 1-2:** Post Days 1-14 manually
2. **Week 3-4:** Build Phase 2 (API posting)
3. **Week 5-6:** Build Phase 3 (scheduling)
4. **Week 7:** Test automation
5. **Week 8+:** Switch to automation for Days 15-88

**Benefits:**
- ✅ Start building audience immediately
- ✅ Understand workflow before automating
- ✅ Test content performance
- ✅ Automate the remaining 74 days

---

## 📞 Need Help?

**For Manual Posting:**
- See: `linkedin_app/QUICKSTART.md`

**For Automation Development:**
- See: `linkedin_app/TODO.md`
- LinkedIn API Docs: https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api

**Questions to Answer Before Building:**
1. Do you have LinkedIn API access?
2. Do you want to build this yourself or hire a developer?
3. Should posting be fully automatic or semi-automatic (requires approval)?
4. Do you need analytics tracking?

---

**Summary:** Phase 1 is complete and ready to use. Phases 2-4 need development work (6-9 weeks total).

**Recommendation:** Start posting manually NOW while planning/building automation.
