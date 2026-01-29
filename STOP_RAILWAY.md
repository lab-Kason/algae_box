# How to Shut Down Railway Deployment

## 🛑 Stop Railway Service

### Method 1: Delete Project (Recommended)
1. Go to https://railway.app/dashboard
2. Find your `algae_box` project
3. Click project name → **Settings** (gear icon)
4. Scroll to bottom → **"Danger Zone"**
5. Click **"Delete Project"**
6. Confirm deletion

**Result:** Project completely removed, no charges

---

### Method 2: Pause Deployment (Temporary)
1. Go to Railway dashboard
2. Click your project
3. Click the service (web service)
4. Click **"Settings"** tab
5. Toggle **"Sleep Service"** or click pause icon

**Result:** Service stopped, can resume later

---

### Method 3: Remove GitHub Connection
1. Railway dashboard → Project → Settings
2. Find **"GitHub Repository"** section
3. Click **"Disconnect"**

**Result:** No more auto-deploys from GitHub

---

## 🔄 Migrate Data (Before Deleting)

### Download Database from Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Download database
railway run python -c "import shutil; shutil.copy('data/algae_cultivation.db', 'backup.db')"
```

Or use Railway dashboard → **"Data"** tab → Download SQLite file

---

## ✅ Verify Railway is Stopped

Test old Railway URL:
```bash
curl https://web-production-f856a8.up.railway.app/api/health
```

Should return:
- `404 Not Found` (project deleted)
- `Service Unavailable` (project paused)

---

## 🧹 Cleanup Checklist

- ✅ Delete Railway project
- ✅ Remove Railway URL from code
- ✅ Update mobile app to Render URL
- ✅ Rebuild mobile APK
- ✅ Update main_cloud.py sensor script
- ✅ Test Render deployment works

---

## 💡 Why Switch to Render?

| Feature | Railway (Current) | Render (Free) |
|---------|------------------|---------------|
| **Free Tier** | $5 credit/month | 750 hours/month |
| **Credit Card** | Required | Not required |
| **Always On** | Until credit runs out | Sleeps after 15 min |
| **Cold Start** | 0s | 30-60s |
| **Best For** | Production | Testing/Development |

**Your use case:** Sensor posts every 10s keep Render awake → No cold starts
