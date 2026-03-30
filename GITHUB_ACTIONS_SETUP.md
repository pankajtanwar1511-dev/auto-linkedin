# GitHub Actions Setup Guide

This guide walks you through setting up automated daily LinkedIn posting using GitHub Actions.

---

## ✅ Prerequisites

- [x] LinkedIn automation code pushed to GitHub
- [x] LinkedIn API credentials (access token and user ID)
- [x] GitHub repository: `pankajtanwar1511-dev/auto-linkedin`

---

## 🚀 Setup Steps (5 minutes)

### Step 1: Add GitHub Secrets

1. Go to your GitHub repository:
   ```
   https://github.com/pankajtanwar1511-dev/auto-linkedin
   ```

2. Click **Settings** → **Secrets and variables** → **Actions**

3. Click **"New repository secret"** and add:

   **Secret 1: LINKEDIN_ACCESS_TOKEN**
   ```
   Name: LINKEDIN_ACCESS_TOKEN
   Value: AQVtcvpSITYdP914pqhI3OdreFwKiuVRxHIjqdbwNae58uPntFSgSETZ19wgIBOqeN5r1mu5GpxYImHYewGmA2iqdBVZm5NoRq7ICDaR-ihHydrTjiHRoGv4Sghu3qiTPGOLLkMwH2-72gEhC2Pe6Ut3-ZR5HDrT8Rp85_9bYzz5QOKikGa-8BuarSlkoJKksFDWY7NshmxcG048YsZWT1HOE_ayAhNEetoURchuf1QbRVhHePLsBLIKahqzY4mYw9f86YGRo4bBJBh1a3lGaW9ohWcfdhWd0wtMIrDm_S-xA1ndTBRj4iGLg0y7mU3XTllx5KJ-Iq5VYPrI4jzQpOqdTdsVIA
   ```

   **Secret 2: LINKEDIN_USER_ID**
   ```
   Name: LINKEDIN_USER_ID
   Value: urn:li:person:wSdGRroG-Q
   ```

4. Click **"Add secret"** for each

---

### Step 2: Enable GitHub Actions

1. Go to **Actions** tab in your repository

2. If prompted, click **"I understand my workflows, go ahead and enable them"**

3. You should see the workflow: **"Daily LinkedIn C++ Post"**

---

### Step 3: Test the Workflow (Manual Trigger)

Before waiting for the scheduled run, test it manually:

1. Go to **Actions** tab

2. Click **"Daily LinkedIn C++ Post"** workflow

3. Click **"Run workflow"** button (right side)

4. Select branch: **main**

5. Click **"Run workflow"**

6. Wait ~30 seconds and refresh

7. You should see:
   - ✅ Green checkmark = Success! Day 1 posted
   - ❌ Red X = Failed, click to see logs

---

## 📅 Automatic Schedule

Once set up, the workflow will run automatically **2 times per day**:

### Morning Post
- **Workflow starts:** Every day at 8:00 AM IST (2:30 AM UTC)
- **Random delay:** 0-60 minutes (posts between 8:00-9:00 AM IST)
- **Posts:** Next unposted topic from tracker

### Evening Post
- **Workflow starts:** Every day at 6:00 PM IST (12:30 PM UTC)
- **Random delay:** 0-60 minutes (posts between 6:00-7:00 PM IST)
- **Posts:** Next unposted topic from tracker

**Why 2 posts/day?**
- ✅ Completes all 88 posts in **44 days** (before token expires at 60 days)
- ✅ **16-day safety buffer** for token expiration
- ✅ Better engagement (morning + evening audiences)
- ✅ Still natural with random timing

**Tracking:** Auto-updates `posting_tracker.txt` after each post

**GitHub Actions usage:** 60 min/day average = 1,800 min/month (90% of free tier)

---

## 🔍 Monitoring Your Posts

### View Workflow Runs

```
https://github.com/pankajtanwar1511-dev/auto-linkedin/actions
```

- Click any run to see details
- Green = posted successfully
- Red = failed (check logs)

### Check Posting History

After each successful post, GitHub Actions commits:
- `linkedin_app/tracker/posting_tracker.txt` - Shows [X] for posted days
- `linkedin_app/logs/posting_history.json` - Complete log

---

## 🛠️ Troubleshooting

### Error: "Invalid access token"

**Cause:** Token expired (60 days max)

**Fix:**
1. Generate new token from LinkedIn OAuth
2. Update `LINKEDIN_ACCESS_TOKEN` secret in GitHub
3. Re-run workflow

### Error: "Permission denied" or "Push failed"

**Cause:** GitHub Actions can't push tracker updates

**Fix:**
1. Go to Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Click Save

### Error: "PDF not found"

**Cause:** PDF files not in repository

**Fix:**
```bash
# Add PDFs to repository
git add data/*.pdf
git commit -m "Add C++ learning PDFs"
git push
```

---

## ⚙️ Customization

### Change Posting Time

Edit `.github/workflows/linkedin_daily_post.yml`:

```yaml
on:
  schedule:
    # Change this cron expression
    - cron: '30 2 * * *'  # 8:00 AM IST
```

**Common times:**
- 7:00 AM IST: `cron: '30 1 * * *'`
- 9:00 AM IST: `cron: '30 3 * * *'`
- 6:00 PM IST: `cron: '30 12 * * *'`

Use [crontab.guru](https://crontab.guru/) to generate cron expressions.

### Post Multiple Times Per Day

Add multiple schedule entries:

```yaml
on:
  schedule:
    - cron: '30 2 * * *'  # 8:00 AM IST
    - cron: '30 12 * * *' # 6:00 PM IST
```

### Skip Weekends

Modify the script to check day of week:

```python
# Add to auto_poster.py
import datetime
if datetime.datetime.now().weekday() >= 5:  # 5=Sat, 6=Sun
    print("Skipping weekend")
    sys.exit(0)
```

---

## 📊 Usage Limits

**GitHub Actions Free Tier:**
- 2,000 minutes/month (public repos)
- Your usage breakdown (2 workflows/day):
  - Workflow startup: ~5 seconds × 2 = 10 seconds
  - Random delay: 0-60 min (avg: 30 min) × 2 = 60 min average
  - Posting: ~30 seconds × 2 = 60 seconds
  - **Total per day: ~60 minutes average**
  - **Monthly: 30 days × 60 min = 1,800 minutes**
  - **Usage: 90% of free tier** ✅

**Worst case:** 120 min/day × 30 days = 3,600 min (would exceed free tier)
- But this is extremely unlikely (requires max delay both times every day)
- Average case keeps you well within limits

**For 44-day campaign:** 44 days × 60 min = 2,640 min total (would exceed monthly limit slightly if all in one month)
- Solution: Split across 2 months (1,320 min/month each) ✅

**Cost:** $0 (completely free)

---

## 🎯 What Happens Next?

Once set up:

1. **Tomorrow 8 AM IST:** Day 1 posts automatically (morning)
2. **Tomorrow 6 PM IST:** Day 2 posts automatically (evening)
3. **Day 2 onwards:** 2 posts per day (morning + evening)
4. **Day 44:** All 88 posts completed! 🎉

**Timeline:**
- Start: Day 1
- Finish: Day 44 (all 88 posts done)
- Token expires: Day 60
- **Safety buffer: 16 days** ✅

**No action needed from you!** Just check LinkedIn twice daily to see your posts going live.

---

## 🔐 Security Notes

✅ **Secrets are encrypted** - GitHub encrypts all secrets
✅ **Not visible in logs** - Secrets are masked in workflow logs
✅ **Repository access only** - Only your repo can use these secrets

❌ **Never commit .env to git** - Already in .gitignore
❌ **Don't share access token** - Personal token only

---

## 📞 Need Help?

**Check workflow logs:**
```
https://github.com/pankajtanwar1511-dev/auto-linkedin/actions
```

**Common issues:**
- Token expired → Regenerate and update secret
- Workflow not running → Check Actions are enabled
- PDF not found → Ensure PDFs are committed to repo

---

## 🎉 You're All Set!

Your LinkedIn automation is now:
- ✅ Running on GitHub's infrastructure
- ✅ Posting daily at 8 AM IST
- ✅ Completely free (no server costs)
- ✅ Tracked and logged automatically
- ✅ Will run for all 88 days

**Next step:** Go to Actions tab and run your first test!

---

**Last Updated:** March 30, 2026
**Repository:** https://github.com/pankajtanwar1511-dev/auto-linkedin
