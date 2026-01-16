# Algae Box - Deployment Guide

## Quick Deploy to Railway

### 1. Push to GitHub
```bash
git add .
git commit -m "Add Flask API backend"
git push origin main
```

### 2. Deploy on Railway
1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose `algae_box` repository
5. Railway auto-detects Python and deploys!

### 3. Get Your API URL
- Railway will give you a URL like: `https://algae-box-production.up.railway.app`
- Your API endpoints will be at: `https://your-app.railway.app/api/...`

### 4. Test Deployment
Open in browser:
- `https://your-app.railway.app/` - API docs
- `https://your-app.railway.app/api/health` - Health check
- `https://your-app.railway.app/api/species` - Algae species

### Environment Variables (Optional)
If needed, set in Railway dashboard:
- `PORT` - Auto-set by Railway
- `DATABASE_URL` - Auto-uses SQLite (can upgrade to PostgreSQL later)

### Alternative: Deploy via CLI
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

## Free Tier Limits
- Railway free tier: $5/month credit
- Should be sufficient for testing and development
- Upgrades available if needed

## When Hardware Arrives
Change Flutter app API URL from Railway to:
`http://[RASPBERRY_PI_IP]:5001`
