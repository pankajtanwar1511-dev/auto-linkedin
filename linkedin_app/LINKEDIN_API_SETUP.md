# LinkedIn API Setup Guide

**Complete guide to get LinkedIn API credentials for automation**

---

## 📋 Overview

To use the automated posting system, you need:
1. LinkedIn Developer App
2. OAuth Access Token
3. Your LinkedIn Profile/Page URN

**Time Required:** 30-60 minutes (one-time setup)

---

## 🚀 Step-by-Step Setup

### Step 1: Create LinkedIn Developer App

1. **Go to LinkedIn Developers**
   - Visit: https://www.linkedin.com/developers/apps
   - Click "Create app"

2. **Fill App Details (Personal Account):**
   ```
   App name: C++ Learning Automation
   LinkedIn Page: [You need a company page - see note below]
   Privacy policy URL: https://www.freeprivacypolicy.com/free-privacy-policy-generator/
   App logo: [Upload any logo - can be your profile pic]
   Legal agreement: [Accept]
   ```

   **Note about LinkedIn Page:**
   - LinkedIn requires a "company page" even for personal use
   - **Workaround:** Create a simple company page (takes 2 minutes)
     - Go to: https://www.linkedin.com/company/setup/new/
     - Company name: "Your Name - Personal Projects" or similar
     - It's free and just for API access

   **Note about Privacy Policy:**
   - For personal projects, use a free privacy policy generator
   - Or use: https://yourwebsite.com/privacy (if you have a website)
   - LinkedIn just needs a valid URL (they rarely check for personal projects)

3. **Click "Create app"**

4. **Verify Your App (Usually Instant):**
   - Check your email for verification link
   - Click to verify
   - App should be active immediately

---

### Step 2: Configure App Permissions

1. **Go to "Products" Tab**
   - Request access to: **"Share on LinkedIn"**
   - Request access to: **"Sign In with LinkedIn"**
   - Wait for approval (usually instant, sometimes up to 24 hours)

2. **Go to "Auth" Tab**
   - Note your **Client ID**
   - Note your **Client Secret**
   - Add Redirect URLs:
     ```
     http://localhost:8000/callback
     https://localhost:8000/callback
     ```

---

### Step 3: Get Access Token

#### Option A: Using LinkedIn OAuth Playground (Easiest)

1. Visit: https://www.linkedin.com/developers/tools/oauth
2. Select your app
3. Check scopes:
   - `r_liteprofile`
   - `r_emailaddress`
   - `w_member_social`
4. Click "Request Access Token"
5. **Copy the Access Token** (save it!)

#### Option B: Manual OAuth Flow

```bash
# 1. Authorization URL (paste in browser)
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8000/callback&scope=r_liteprofile%20r_emailaddress%20w_member_social

# 2. After authorization, you'll get redirected to:
http://localhost:8000/callback?code=YOUR_AUTH_CODE

# 3. Exchange code for token (use curl or Postman)
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=authorization_code' \
  -d 'code=YOUR_AUTH_CODE' \
  -d 'client_id=YOUR_CLIENT_ID' \
  -d 'client_secret=YOUR_CLIENT_SECRET' \
  -d 'redirect_uri=http://localhost:8000/callback'

# Response will include:
{
  "access_token": "YOUR_ACCESS_TOKEN",
  "expires_in": 5184000
}
```

**Save your access token!** It's valid for 60 days.

---

### Step 4: Get Your LinkedIn URN

#### Method 1: Using API

```bash
# Use your access token to get profile info
curl -X GET https://api.linkedin.com/v2/me \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'

# Response includes:
{
  "id": "abc123xyz",
  ...
}

# Your URN is: urn:li:person:abc123xyz
```

#### Method 2: Using Python Script

```python
import requests

access_token = "YOUR_ACCESS_TOKEN"

response = requests.get(
    "https://api.linkedin.com/v2/me",
    headers={'Authorization': f'Bearer {access_token}'}
)

profile = response.json()
user_id = profile['id']

print(f"Your URN: urn:li:person:{user_id}")
```

---

### Step 5: Configure Environment

1. **Copy .env.example to .env:**
   ```bash
   cd linkedin_app/config
   cp .env.example .env
   ```

2. **Edit .env file:**
   ```bash
   nano .env
   ```

3. **Add your credentials (Personal Account):**
   ```bash
   # LinkedIn API Credentials
   LINKEDIN_ACCESS_TOKEN=YOUR_ACCESS_TOKEN_HERE
   LINKEDIN_USER_ID=urn:li:person:YOUR_ID_HERE

   # For personal account, use: urn:li:person:YOUR_ID
   # (NOT urn:li:organization - that's for company pages)

   # Other settings
   POSTING_TIME=08:00
   TIMEZONE=Asia/Tokyo
   ```

4. **Save and close** (Ctrl+X, Y, Enter)

---

### Step 6: Test Connection

```bash
cd /home/pankaj/autolinkedin/linkedin_app/automation

# Test API connection
python3 auto_poster.py --test-connection
```

**Expected Output:**
```
🔍 Testing LinkedIn API connection...
✅ Connected as: Your Name
✅ Connection successful! Ready to post.
```

---

## 🧪 Testing Before Going Live

### Test 1: Dry Run

```bash
# Simulates posting without actually posting
python3 auto_poster.py --dry-run
```

**Output:**
```
📅 Day 1: Classes, Structs, and Access Specifiers
📄 PDF: ch01_topic01_morning.pdf
📝 Caption: ch01_topic01_morning.txt
🔍 DRY RUN - Not actually posting
Would post:
Day: 1

Good morning, C++ developers...
```

### Test 2: Manual Single Post

```bash
# Actually post Day 1 (for real!)
python3 auto_poster.py
```

**If successful:**
```
📅 Day 1: Classes, Structs, and Access Specifiers
📤 Posting to LinkedIn...
✅ Day 1 posted successfully!
✅ Marked Day 1 as complete in tracker
```

---

## 🔧 Troubleshooting

### Error: "Invalid access token"

**Cause:** Token expired or incorrect

**Solution:**
1. Generate new access token (Step 3)
2. Update `.env` file
3. Try again

### Error: "Insufficient permissions"

**Cause:** App doesn't have required permissions

**Solution:**
1. Go to app settings
2. Request "Share on LinkedIn" product
3. Wait for approval
4. Try again

### Error: "User ID not found"

**Cause:** Wrong URN format

**Solution (Personal Account):**
- Format must be: `urn:li:person:YOUR_ID`
- Example: `urn:li:person:abc123xyz`
- Get your ID: `curl -H "Authorization: Bearer TOKEN" https://api.linkedin.com/v2/me`
- The `"id"` field in response is your ID
- Add `urn:li:person:` prefix to that ID

### Error: "Document upload failed"

**Cause:** File too large or wrong format

**Solution:**
- LinkedIn limit: 100 MB per document
- Format must be PDF
- Check PDF isn't corrupted

---

## 📊 Token Management

### Token Expiration

LinkedIn access tokens expire after **60 days**.

**Solution:**
1. Set reminder to refresh token every 50 days
2. OR: Implement token refresh flow (advanced)

### Refresh Token Flow (Advanced)

```python
# If you got refresh_token during OAuth
import requests

response = requests.post(
    'https://www.linkedin.com/oauth/v2/accessToken',
    data={
        'grant_type': 'refresh_token',
        'refresh_token': 'YOUR_REFRESH_TOKEN',
        'client_id': 'YOUR_CLIENT_ID',
        'client_secret': 'YOUR_CLIENT_SECRET'
    }
)

new_token = response.json()['access_token']
# Update .env file with new token
```

---

## 🎯 Quick Reference

### Required Scopes
- `r_liteprofile` - Read basic profile
- `r_emailaddress` - Read email
- `w_member_social` - Post content

### API Endpoints Used
```
GET  /v2/me                    # Get profile info
POST /v2/assets                # Register upload
PUT  [upload_url]              # Upload PDF
POST /v2/ugcPosts              # Create post
```

### Rate Limits
- **Free tier:** 100 API calls/day
- **Verified app:** 500 API calls/day
- Our usage: ~3-4 calls per post

---

## ✅ Checklist

Before running automation:

- [ ] LinkedIn Developer App created
- [ ] "Share on LinkedIn" product approved
- [ ] Access token generated
- [ ] User URN obtained
- [ ] `.env` file configured
- [ ] Connection test passed
- [ ] Dry run tested
- [ ] Single post tested successfully

---

## 🚀 Next Steps

Once setup is complete:

1. **Test manually first:**
   ```bash
   python3 auto_poster.py
   ```

2. **If successful, set up scheduling:**
   - See: `linkedin_app/TODO.md` (Phase 3)
   - Use cron or systemd for daily posting

3. **Monitor logs:**
   ```bash
   tail -f linkedin_app/logs/posting_history.log
   ```

---

## 📞 Need Help?

**LinkedIn API Documentation:**
- https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
- https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication

**Common Issues:**
- Check logs: `linkedin_app/logs/posting_history.log`
- Verify credentials: `python3 auto_poster.py --test-connection`
- Test without posting: `python3 auto_poster.py --dry-run`

---

**Last Updated:** March 30, 2026
**Status:** Ready for testing
**Estimated Setup Time:** 30-60 minutes
