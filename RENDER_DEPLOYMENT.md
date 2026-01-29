# Deploy to Render - Step by Step

## 🚀 Quick Deploy (5 minutes)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (free, no credit card needed)
3. Authorize Render to access your GitHub repos

### Step 2: Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `algae_box`
3. Render will auto-detect it's a Python app

### Step 3: Configure Service
```
Name: algae-box
Region: Oregon (US West) or Singapore (closest to you)
Branch: main
Root Directory: (leave blank)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

### Step 4: Environment Variables
Click **"Advanced"** and add:
```
PYTHON_VERSION = 3.9
```

### Step 5: Deploy
1. Click **"Create Web Service"**
2. Wait 2-3 minutes for build
3. Your app will be at: `https://algae-box-XXXX.onrender.com`

### Step 6: Test Deployment
Open these URLs in browser:
- `https://algae-box-XXXX.onrender.com/api/health`
- `https://algae-box-XXXX.onrender.com/api/species`

---

## 📱 Update Mobile App & Sensors

### Update main_cloud.py
Change line 15:
```python
API_BASE_URL = "https://algae-box-XXXX.onrender.com"  # Your Render URL
```

### Update Flutter Mobile App
Edit `lib/services/api_service.dart` line 6:
```dart
static const String baseUrl = 'https://algae-box-XXXX.onrender.com';
```

Then rebuild APK:
```bash
cd mobile_app
flutter build apk --release
```

---

## ⚙️ Render Settings

### Auto-Deploy from GitHub
✅ Already enabled - pushes to `main` branch auto-deploy

### Free Tier Limits
- ✅ 750 hours/month (enough for 24/7)
- ✅ Sleeps after 15 min inactivity
- ✅ 30-60s cold start
- ⚠️ Your sensor posts every 10s keep it awake

### Keep Service Always Warm (Optional)
Use cron-job.org or UptimeRobot to ping `/api/health` every 5 minutes

### Database Persistence
SQLite file stored in `/opt/render/project/src/data/`
- Persists across deploys
- Free tier: 1GB storage

---

## 🔧 Troubleshooting

### Build Failed
Check Render logs for missing dependencies in requirements.txt

### 503 Service Unavailable
Service is sleeping - first request wakes it up (30-60s)

### Database Reset
If data lost, check Render persistent disk is enabled

---

## 📊 Monitor Your App

Render Dashboard shows:
- ✅ Deploy history
- ✅ Live logs (sensor posts appear here)
- ✅ CPU/Memory usage
- ✅ Request metrics

---

## 💰 Cost Comparison

| Platform | Free Tier | Cold Start | Always On |
|----------|-----------|------------|-----------|
| **Render** | 750 hrs/month | 30-60s | No |
| Railway | $5 credit | 0s | Yes (until credit runs out) |
| Fly.io | 3 VMs | 1s | Yes |
| Koyeb | $5.50 credit | 0s | Yes |

**Render wins for completely free, no credit card needed.**
