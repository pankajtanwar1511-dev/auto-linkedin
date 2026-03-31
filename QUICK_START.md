# Quick Start Guide - LinkedIn Automation

## Current Status

✅ **Phase 1 Complete:** Content ready (88 PDFs + captions)
✅ **Phase 2 Complete:** Automation scripts written
⏳ **Next:** Configure LinkedIn API and start posting

---

## 🚀 Get Started in 4 Steps

### Step 1: Verify Setup (2 minutes)

```bash
cd /home/pankaj/autolinkedin
python3 linkedin_app/verify_setup.py
```

**Expected Output:**
- ✅ All checks passed = Ready for Step 2
- ❌ Issues found = Fix issues then re-run

---

### Step 2: Get LinkedIn API Credentials (30 minutes)

**For Personal Account (posting to YOUR profile):**

```bash
# Follow the quick personal account guide
cat linkedin_app/PERSONAL_ACCOUNT_SETUP.md
```

**For Company Page:**

```bash
# Follow the complete guide
cat linkedin_app/LINKEDIN_API_SETUP.md
```

**What you'll get:**
1. LinkedIn Developer App
2. OAuth Access Token (valid 60 days)
3. Your LinkedIn URN (user ID)

**Quick Links:**
- LinkedIn Developers: https://www.linkedin.com/developers/apps
- OAuth Playground: https://www.linkedin.com/developers/tools/oauth

---

### Step 3: Configure Environment (5 minutes)

```bash
cd linkedin_app/config

# Copy template
cp .env.example .env

# Edit and add your credentials
nano .env
```

**Required values:**
```bash
LINKEDIN_ACCESS_TOKEN=AQV...your_token_here...xyz
LINKEDIN_USER_ID=urn:li:person:YOUR_ID_HERE
```

Save and close (Ctrl+X, Y, Enter).

---

### Step 4: Test and Post (10 minutes)

#### 4a. Test Connection

```bash
cd /home/pankaj/autolinkedin/linkedin_app/automation
python3 auto_poster.py --test-connection
```

**Expected:**
```
✅ Connected as: Your Name
✅ Connection successful! Ready to post.
```

#### 4b. Dry Run (Test Without Posting)

```bash
python3 auto_poster.py --dry-run
```

**Expected:**
```
📅 Day 1: Classes, Structs, and Access Specifiers
📄 PDF: ch01_topic01_morning.pdf
📝 Caption: ch01_topic01_morning.txt
🔍 DRY RUN - Not actually posting
Would post: [caption preview...]
```

#### 4c. Post Day 1 (FOR REAL!)

```bash
python3 auto_poster.py
```

**Expected:**
```
📤 Posting to LinkedIn...
✅ Day 1 posted successfully!
✅ Marked Day 1 as complete in tracker
```

---

## 📊 Track Progress

### View Posting Schedule

```bash
cat linkedin_app/tracker/posting_tracker.txt
```

### View Posting History

```bash
cat linkedin_app/logs/posting_history.json
```

---

## ⚙️ Daily Posting Workflow

Once LinkedIn API is set up:

**Option 1: Manual Daily**
```bash
# Every morning at 8 AM
cd /home/pankaj/autolinkedin/linkedin_app/automation
python3 auto_poster.py
```

**Option 2: Automated (Future - Phase 3)**
- Set up cron job or systemd timer
- Automatic daily posting at scheduled time
- Email notifications on success/failure

---

## 🛠️ Troubleshooting

### Error: "Invalid access token"

**Solution:**
1. Token expired (60 days max)
2. Generate new token from LinkedIn OAuth
3. Update `.env` file
4. Test again

### Error: "Connection failed"

**Solution:**
1. Check internet connection
2. Verify access token is correct
3. Verify user URN format: `urn:li:person:XXXXX`

### Error: "PDF not found"

**Solution:**
1. Check file exists: `ls data/ch01_topic01_morning.pdf`
2. Verify file naming matches tracker
3. Re-run verification: `python3 linkedin_app/verify_setup.py`

### Error: "Permission denied"

**Solution:**
1. LinkedIn app needs "Share on LinkedIn" permission
2. Go to app settings → Products → Request access
3. Wait for approval (usually instant)

---

## 📁 Important Files

### Configuration
- `linkedin_app/config/.env` - Your LinkedIn credentials
- `linkedin_app/config/linkedin_config.json` - Posting schedule settings

### Tracking
- `linkedin_app/tracker/posting_tracker.txt` - Daily progress (✅ = posted)
- `linkedin_app/logs/posting_history.json` - Complete posting log

### Content
- `data/chXX_topicYY_morning.pdf` - 88 PDF slides
- `data/chXX_topicYY_morning.txt` - 88 captions

### Scripts
- `linkedin_app/automation/auto_poster.py` - Main automation script
- `linkedin_app/automation/linkedin_api_v2.py` - LinkedIn API client

---

## 📈 What's Next After Testing?

Once you successfully post Day 1:

1. **Manual Posting (88 days)**
   - Run `auto_poster.py` daily
   - Each run posts next unposted day
   - Automatically tracks progress

2. **Set Up Automation (Phase 3)**
   - Schedule daily posting at 8 AM
   - Use cron or systemd timer
   - Add notifications

3. **Analytics (Phase 4)**
   - Track engagement metrics
   - Optimize posting times
   - Performance dashboard

---

## ✅ Quick Checklist

Before first post:

- [ ] Ran `verify_setup.py` - all checks passed
- [ ] LinkedIn Developer App created
- [ ] OAuth access token obtained
- [ ] User URN obtained
- [ ] `.env` file configured with credentials
- [ ] Connection test passed (`--test-connection`)
- [ ] Dry run tested (`--dry-run`)
- [ ] Ready to post Day 1!

---

## 📞 Need Help?

**Documentation:**
- Full setup guide: `linkedin_app/LINKEDIN_API_SETUP.md`
- Verification system: `linkedin_app/verify_setup.py`
- Project status: `PROJECT_STATUS.md`

**LinkedIn API Docs:**
- Authentication: https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication
- UGC Posts: https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api

---

**Last Updated:** March 30, 2026
**Status:** Ready for LinkedIn API setup
**Total Content:** 88 days ready to post
