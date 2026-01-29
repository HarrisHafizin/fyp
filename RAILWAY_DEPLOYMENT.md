# 🚂 RAILWAY DEPLOYMENT GUIDE
## Rugby Scouting Strategy Optimization System

---

## ✅ PRE-DEPLOYMENT CHECKLIST

All necessary files have been created:

- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Railway start command
- ✅ `runtime.txt` - Python version (3.11.7)
- ✅ `railway.toml` - Railway configuration
- ✅ `.railwayignore` - Files to exclude from deployment
- ✅ `.gitignore` - Git ignore rules
- ✅ `README.md` - Project documentation
- ✅ `app.py` - Updated for production (PORT environment variable)

---

## 🚀 DEPLOYMENT STEPS

### Option 1: Deploy from GitHub (Recommended)

#### Step 1: Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Ready for Railway deployment"

# Add your GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/rugby-optimizer.git

# Push to GitHub
git push -u origin main
```

#### Step 2: Deploy on Railway

1. Go to [Railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway will auto-detect Flask and deploy! 🎉

---

### Option 2: Deploy via Railway CLI

#### Step 1: Install Railway CLI

```bash
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# Or via npm
npm install -g @railway/cli
```

#### Step 2: Login

```bash
railway login
```

#### Step 3: Initialize and Deploy

```bash
# In your project directory
cd d:\xampp\htdocs\fyp

# Initialize Railway project
railway init

# Deploy
railway up
```

#### Step 4: Open Your App

```bash
railway open
```

---

## 🔧 ENVIRONMENT VARIABLES (Optional)

If you're using the Rugby API features, set these in Railway dashboard:

1. Go to your Railway project
2. Click **"Variables"** tab
3. Add:
   - `RUGBY_API_KEY` = your API key from api-sports.io
   - `PORT` = (auto-set by Railway, don't add manually)

---

## 📝 IMPORTANT NOTES

### Files Included in Deployment:

✅ Essential files:
- `app.py` - Main Flask application
- `strategies.py` - Strategy configurations
- `api_config.py` - API settings
- `templates/` - HTML templates
- `static/` - CSS, images, JS
- `Statistic on best rugby players 2023-2024.csv` - Player dataset

❌ Excluded files (via `.railwayignore`):
- Test files (`test_*.py`, `debug_*.py`)
- Development scripts (`run_*.py`, `check_*.py`)
- Reports and documentation
- Backup files (`.bak`)
- Virtual environment (`.venv/`)

### Python Version

- Railway will use **Python 3.11.7** (specified in `runtime.txt`)
- All dependencies will be installed from `requirements.txt`

### Port Configuration

- Railway automatically provides `PORT` environment variable
- App now reads: `port = int(os.environ.get('PORT', 5000))`
- Local dev still uses port 5000

---

## 🎯 POST-DEPLOYMENT

### Check Deployment Status

Railway dashboard shows:
- ✅ Build logs
- ✅ Deploy logs
- ✅ Runtime logs
- ✅ Public URL

### Test Your Deployed App

Visit your Railway URL (e.g., `https://your-app.railway.app`)

Should see:
- 🏉 Rugby Genius landing page
- Working optimization system
- All features functional

### Monitor Logs

```bash
# Via Railway CLI
railway logs
```

Or view in Railway dashboard → Deployments → Logs

---

## 🐛 TROUBLESHOOTING

### Build Fails

**Error:** `No module named 'XXX'`
- **Fix:** Add missing package to `requirements.txt`

**Error:** `Python version not found`
- **Fix:** Update `runtime.txt` to supported version

### App Won't Start

**Error:** `Web process failed to bind to $PORT`
- **Fix:** Check `app.run(host='0.0.0.0', port=port)` in app.py ✅ Already fixed!

**Error:** `gunicorn: command not found`
- **Fix:** Ensure `gunicorn` is in `requirements.txt` ✅ Already added!

### CSV Not Found

**Error:** `FileNotFoundError: Statistic on best rugby players 2023-2024.csv`
- **Fix:** Make sure CSV is committed to Git
- Check `.railwayignore` doesn't exclude it

```bash
# Verify CSV is tracked
git add "Statistic on best rugby players 2023-2024.csv"
git commit -m "Add player dataset"
git push
```

### App Times Out

- **Cause:** GA optimization taking too long
- **Fix:** Already optimized (3-5 seconds typical)
- Railway free tier has 500MB RAM - should be sufficient

---

## 💰 RAILWAY PRICING

### Free Tier (Hobby Plan)

- ✅ $5 free credit/month
- ✅ Enough for development/testing
- ✅ Public URL included
- ✅ Automatic SSL
- ✅ GitHub auto-deploy

### Estimated Usage

This app is lightweight:
- Small memory footprint (~200-300MB)
- Fast response times (3-5s for optimization)
- Minimal database (CSV file)

**Expected cost:** Should fit comfortably in free tier for moderate usage!

---

## 🔄 CONTINUOUS DEPLOYMENT

Railway auto-deploys on every GitHub push:

```bash
# Make changes locally
# ... edit files ...

# Commit and push
git add .
git commit -m "Update feature"
git push

# Railway automatically:
# 1. Detects push
# 2. Builds new image
# 3. Deploys
# 4. Updates public URL
```

---

## 📊 RAILWAY FEATURES

### What You Get

✅ **Custom Domain** - Add your own domain (e.g., rugbygenius.com)
✅ **SSL Certificate** - Automatic HTTPS
✅ **Auto-Scaling** - Handles traffic spikes
✅ **GitHub Integration** - Deploy on push
✅ **Environment Variables** - Secure config management
✅ **Rollback** - One-click to previous deployment
✅ **Metrics** - CPU, Memory, Network monitoring

---

## 🎓 NEXT STEPS AFTER DEPLOYMENT

### 1. Verify Everything Works

- [ ] Visit your Railway URL
- [ ] Test team optimization (10s/15s modes)
- [ ] Check multiple strategies work
- [ ] Test "Complete My Team" feature
- [ ] Verify CSV data loads correctly

### 2. Share Your App

Your Railway URL is public! Share it with:
- Supervisors
- Classmates
- Rugby teams/clubs
- Portfolio/Resume

### 3. Monitor Usage

Railway dashboard shows:
- Request count
- Response times
- Errors
- Resource usage

### 4. Optional Enhancements

Consider adding:
- Custom domain
- Google Analytics
- User authentication
- Database (PostgreSQL on Railway)
- Caching (Redis on Railway)

---

## 📞 SUPPORT

### Railway Documentation
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Support: https://railway.app/help

### Project-Specific Issues

Check these files if something breaks:
- `railway.toml` - Railway config
- `Procfile` - Start command
- `requirements.txt` - Dependencies
- `app.py` lines 1413-1414 - Port configuration

---

## ✨ READY TO DEPLOY!

You're all set! Just run:

```bash
# Option 1: Git + Railway GitHub integration
git init
git add .
git commit -m "Ready for deployment"
git push origin main
# Then connect Railway to your GitHub repo

# Option 2: Railway CLI
railway login
railway init
railway up
```

**Your app will be live in 2-3 minutes!** 🚀

---

**Good luck with your deployment!** 🏉⚡

If you encounter any issues, check the troubleshooting section above or Railway's excellent documentation.
