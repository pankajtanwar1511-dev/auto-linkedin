# AutoLinkedIn - C++ Learning Content for LinkedIn

**88 days of professional C++ learning content ready for LinkedIn posting.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Overview

Complete LinkedIn content automation system with **88 professionally designed carousel PDFs** covering C++ from basics to C++20 features. Each post includes a carousel PDF and corresponding LinkedIn caption, ready to post.

**Content Coverage:** OOP, Memory Management, Smart Pointers, Templates, STL, Multithreading, Design Patterns, C++11-20 features, Software Architecture, Network Programming, and Advanced Implementations.

---

## 📂 Project Structure

```
autolinkedin/
├── data/                    # 88 PDFs + Captions (238 MB)
│   ├── ch01_topic01_morning.pdf
│   ├── ch01_topic01_morning.txt
│   └── ... (176 files total)
│
├── linkedin_app/            # Automation & Tracking
│   ├── tracker/             # Progress tracking files
│   ├── config/              # Configuration
│   ├── automation/          # Auto-posting scripts (planned)
│   ├── README.md            # App documentation
│   ├── QUICKSTART.md        # Quick start guide
│   └── TODO.md              # Development roadmap
│
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

---

## 🚀 Quick Start

### Automated Posting (Recommended)

**Status:** Core automation complete! Just needs LinkedIn API credentials.

```bash
# 1. Read the quick start guide
cat QUICK_START.md

# 2. Check current setup status
python3 linkedin_app/verify_setup.py

# 3. Set up LinkedIn API (30-60 minutes, one-time)
cat linkedin_app/LINKEDIN_API_SETUP.md

# 4. Test and post
cd linkedin_app/automation
python3 auto_poster.py --test-connection
python3 auto_poster.py --dry-run
python3 auto_poster.py  # Post Day 1!
```

**Time:** 30-60 min setup (once) + 30 seconds per day

### Manual Posting (Alternative)

```bash
# Open tracker to find today's post
nano linkedin_app/tracker/posting_tracker.txt

# Upload PDF to LinkedIn manually
# Copy caption from .txt file
# Mark complete in tracker
```

**Time:** 5 minutes per day for 88 days

---

## 📊 Content Details

### 88 Topics Across 20 Chapters

| Chapter | Topics | Subject Area |
|---------|--------|--------------|
| 1-3 | 9 | OOP, Memory, Smart Pointers |
| 4-7 | 9 | References, Moving, Operators, Templates |
| 8-10 | 14 | STL, C++11 Features, RAII |
| 11-12 | 15 | Multithreading, Design Patterns |
| 13-16 | 8 | Compile-Time, Low-Level, C++14-17 |
| 17-20 | 33 | Architecture, Networking, C++20, Advanced |

### Each Post Includes:

- **PDF Carousel** (1080×1080px, 10-15 slides)
  - Theory section with key concepts
  - Edge cases and gotchas
  - Code examples with syntax highlighting

- **LinkedIn Caption** (~600-800 characters)
  - Professional first-person voice
  - Topic-specific insights
  - 20 relevant hashtags
  - Non-demanding engagement questions

---

## 🎯 Features

### Ready to Post
- ✅ **88 Professional PDFs** - All generated and tested
- ✅ **88 Matching Captions** - LinkedIn-optimized copy
- ✅ **Progress Tracking** - Simple checkbox system
- ✅ **Organized Structure** - Easy to find daily content

### Automation Ready
- ✅ **Config Templates** - Ready for LinkedIn API
- ✅ **Scheduler Framework** - Daily posting automation
- ✅ **Analytics Placeholders** - Engagement tracking
- ✅ **Error Handling** - Retry and logging system

---

## 📈 Posting Schedule

### Timeline
- **Total Duration:** 88 days
- **Frequency:** Daily (recommended 8:00 AM)
- **Format:** Square carousel (1080×1080px)
- **Platform:** LinkedIn (personal or company page)

### Milestones
- **Day 1:** Launch - OOP Basics
- **Day 10:** References and Move Semantics
- **Day 33:** Multithreading Begins
- **Day 56:** Software Architecture
- **Day 69:** C++20 Features
- **Day 88:** Final Topic - Spinlock vs Mutex

---

## 🔧 LinkedIn App Features

### ✅ Complete (Phase 1-2): Core Automation
- **LinkedIn API Client** - Direct PDF document upload
- **Auto Poster** - Automated daily posting script
- **Progress Tracking** - Automatic tracker updates
- **Logging System** - JSON-based posting history
- **Verification System** - Setup validation
- **Comprehensive Documentation** - Complete setup guides

### ⏳ Future (Phase 3-4): Advanced Features
- **Phase 3:** Scheduled automation (cron/systemd)
- **Phase 4:** Analytics and engagement tracking

See `PROJECT_STATUS.md` for detailed status.

---

## 📝 File Specifications

### PDF Files
- **Format:** PDF (vector graphics)
- **Dimensions:** 1080×1080px
- **Pages:** 10-15 slides per carousel
- **Size:** ~1-3 MB per file
- **Quality:** 144 DPI, optimized for LinkedIn

### Caption Files
- **Format:** Plain text (.txt)
- **Length:** 600-800 characters
- **Style:** Professional, educational
- **Hashtags:** ~20 relevant tags
- **Structure:** Day number, intro, bullet points, insights

---

## 🛠️ Technical Details

### Dependencies
```bash
# Required for future automation
pip install -r requirements.txt

# Includes:
# - jinja2 (templates)
# - requests (API calls)
# - apscheduler (scheduling)
# - python-dotenv (config)
```

### Configuration
```bash
# LinkedIn API credentials (Phase 2)
linkedin_app/config/.env.example

# App settings
linkedin_app/config/linkedin_config.json
```

---

## 📚 Documentation

### Get Started (Read These First!)
- **`QUICK_START.md`** - 4-step guide to get posting
- **`SETUP_STATUS.md`** - Current setup status and next steps
- **`linkedin_app/LINKEDIN_API_SETUP.md`** - Complete API setup guide

### Reference Documentation
- **`PROJECT_STATUS.md`** - Detailed project phases
- **`README.md`** (this file) - Project overview
- **`CLEANUP_SUMMARY.md`** - What was cleaned up

### Tracking Files
- **`linkedin_app/tracker/posting_tracker.txt`** - Daily checklist (main)
- **`linkedin_app/tracker/posting_schedule.csv`** - Spreadsheet format
- **`linkedin_app/tracker/POSTING_SCHEDULE.md`** - Full documentation

### Automation Scripts
- **`linkedin_app/verify_setup.py`** - Verify your setup is ready
- **`linkedin_app/automation/auto_poster.py`** - Main posting script
- **`linkedin_app/automation/linkedin_api_v2.py`** - LinkedIn API client

---

## 🎯 Use Cases

### Personal Branding
- Build C++ expertise authority
- Daily educational content
- Consistent LinkedIn presence
- Professional network growth

### Company Marketing
- Tech leadership positioning
- Developer community building
- Recruitment tool
- Brand awareness

### Education
- Course supplementary material
- Student engagement
- Learning resource sharing
- Programming education

---

## 🚀 Getting Started

### Step 1: Verify Setup
```bash
cd /home/pankaj/autolinkedin
python3 linkedin_app/verify_setup.py
```

### Step 2: Read Quick Start
```bash
cat QUICK_START.md
```

### Step 3: Set Up LinkedIn API
```bash
# Complete setup guide (30-60 minutes, one-time)
cat linkedin_app/LINKEDIN_API_SETUP.md
```

### Step 4: Configure and Test
```bash
# Create .env file with your credentials
cd linkedin_app/config
cp .env.example .env
nano .env  # Add your token and URN

# Test connection
cd ../automation
python3 auto_poster.py --test-connection
python3 auto_poster.py --dry-run
python3 auto_poster.py  # Post Day 1!
```

---

## 🔍 Content Quality

### Design Features
- High-contrast color schemes
- Syntax-highlighted code blocks
- Professional typography
- Consistent branding
- Mobile-optimized layouts

### Content Features
- Comprehensive C++ coverage
- Real-world examples
- Best practices
- Common pitfalls
- Interview preparation

---

## 📊 Success Metrics

### Engagement Goals (Suggested)
- **Consistency:** 88/88 days posted
- **Reach:** Track views per post
- **Engagement:** Monitor likes, comments, shares
- **Followers:** Track growth over 88 days
- **Network:** New connections from content

---

## 🤝 Contributing

This is a personal automation project. The content and structure can be adapted for your own use cases.

---

## 📄 License

MIT License - Feel free to use and adapt for your needs.

---

## 📧 Support

- **Quick Start:** See `QUICK_START.md`
- **Setup Status:** Run `python3 linkedin_app/verify_setup.py`
- **LinkedIn API Help:** See `linkedin_app/LINKEDIN_API_SETUP.md`
- **Current Status:** See `SETUP_STATUS.md` and `PROJECT_STATUS.md`

---

## 🎉 What's Inside

```
88 PDFs covering:
├── OOP (7 topics)
├── Memory Management (1 topic)
├── Smart Pointers (1 topic)
├── References & Moving (4 topics)
├── Operator Overloading (1 topic)
├── Type System (2 topics)
├── Templates (2 topics)
├── STL (6 topics)
├── C++11 Features (5 topics)
├── RAII (3 topics)
├── Multithreading (7 topics)
├── Design Patterns (8 topics)
├── Compile-Time Magic (1 topic)
├── Low-Level Topics (2 topics)
├── C++14 Features (1 topic)
├── C++17 Features (4 topics)
├── Software Architecture (7 topics)
├── Network Programming (6 topics)
├── C++20 Features (6 topics)
└── Advanced Implementations (14 topics)
```

---

**Last Updated:** March 30, 2026
**Version:** 3.0 - Automation Complete
**Status:** 95% Complete - Ready for LinkedIn API Setup
**Content:** 88 days of C++ learning material

## 🚀 Next Steps

```bash
# 1. Verify everything is ready
python3 linkedin_app/verify_setup.py

# 2. Read the quick start guide
cat QUICK_START.md

# 3. Set up LinkedIn API credentials
cat linkedin_app/LINKEDIN_API_SETUP.md

# 4. Start posting!
cd linkedin_app/automation
python3 auto_poster.py
```

**You're 95% done! Just 30-60 minutes to set up LinkedIn API and you're ready to post! 🎉**
