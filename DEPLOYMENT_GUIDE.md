# 🚀 Khaznati DZ Deployment Guide

This is a **complete beginner-friendly guide** to deploy your Khaznati DZ application to the cloud.

---

## 📋 Table of Contents

1. [Part 1: Push to GitHub](#part-1-push-to-github)
2. [Part 2: Deploy on Render](#part-2-deploy-on-render)
3. [Part 3: Configure Environment Variables](#part-3-configure-environment-variables)
4. [Part 4: Verify Everything Works](#part-4-verify-everything-works)
5. [Troubleshooting](#troubleshooting)

---

## Part 1: Push to GitHub

### 🎯 What is GitHub?

Think of **GitHub** as Google Drive, but for code. It stores your code online, tracks every change you make, and lets you collaborate with others.

### Step 1.1: Create a GitHub Account

1. Go to [github.com](https://github.com)
2. Click **Sign up**
3. Enter your email, create a password, choose a username
4. Verify your email

### Step 1.2: Install Git on Your Computer

Git is the tool that connects your computer to GitHub.

1. Download Git: [git-scm.com/download/win](https://git-scm.com/download/win)
2. Run the installer (keep all default settings)
3. After installation, restart your terminal/PowerShell

**Verify installation** - open PowerShell and type:
```powershell
git --version
```
You should see something like `git version 2.43.0`

### Step 1.3: Configure Git (First Time Only)

Open PowerShell and run these commands (replace with YOUR information):

```powershell
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

### Step 1.4: Create a Personal Access Token

GitHub needs a "password" to upload code. Here's how to create one:

1. Go to [github.com](https://github.com) and log in
2. Click your profile picture (top right) → **Settings**
3. Scroll down, click **Developer settings** (left sidebar, bottom)
4. Click **Personal access tokens** → **Tokens (classic)**
5. Click **Generate new token** → **Generate new token (classic)**
6. Give it a name like "My Computer"
7. Set expiration to **90 days** (or "No expiration")
8. Check these boxes:
   - ✅ `repo` (Full control of repositories)
9. Click **Generate token**
10. ⚠️ **COPY THIS TOKEN NOW** - you won't see it again!
11. Save it somewhere safe (like a password manager)

### Step 1.5: Create a Repository on GitHub

1. Go to [github.com](https://github.com)
2. Click the **+** button (top right) → **New repository**
3. Fill in:
   - **Repository name**: `khaznati-dz`
   - **Description**: Cloud storage for Algerian users ☁️
   - **Visibility**: Public (or Private if you prefer)
   - ❌ Do NOT check "Add a README file" (we already have one)
4. Click **Create repository**

### Step 1.6: Push Your Code to GitHub

Now open PowerShell and run these commands **one by one**:

```powershell
# 1. Navigate to your project folder
cd "C:\Users\abdou1\Documents\khaznati new"

# 2. Initialize Git (tell Git to track this folder)
git init

# 3. Stage all files (prepare them for upload)
git add .

# 4. Create your first snapshot (commit)
git commit -m "Initial commit: Khaznati DZ v1"

# 5. Rename the branch to 'main'
git branch -M main

# 6. Connect to GitHub (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/khaznati-dz.git

# 7. Push (upload) your code
git push -u origin main
```

**When prompted for credentials:**
- Username: your GitHub username
- Password: paste your **Personal Access Token** (not your GitHub password!)

✅ **Success!** Your code is now on GitHub! Visit `https://github.com/YOUR_USERNAME/khaznati-dz` to see it.

---

## Part 2: Deploy on Render

### 🎯 What is Render?

**Render** is a cloud platform that runs your application online. It's like turning your local computer into a website that anyone can access.

### Step 2.1: Create a Render Account

1. Go to [render.com](https://render.com)
2. Click **Get Started for Free**
3. Choose **Sign up with GitHub** (easiest option!)
4. Authorize Render to access your GitHub

### Step 2.2: Deploy as a Single Web Service

We are deploying the entire application (Backend + Frontend) as a single **Web Service**. This is simpler and more efficient for the free tier.

1. Go to your Render Dashboard
2. Click **New** → **Web Service**
3. Connect your GitHub repository (`khaznati-dz`)
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `khaznati-dz` |
| **Region** | Frankfurt (EU) |
| **Branch** | `main` |
| **Root Directory** | (leave empty - root of project) |
| **Runtime** | `Python 3` |
| **Build Command** | `cd backend && pip install -r requirements.txt && cd ../frontend && npm install && npm run build` |
| **Start Command** | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

---

## Part 3: Configure Environment Variables

Environment variables are secret settings your app needs to run.

### Step 3.1: Required Variables

1. Go to your **khaznati-dz** service on Render
2. Click **Environment** in the left sidebar
3. Add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| **Supabase (Database)** | | |
| `SUPABASE_URL` | `https://xxxx.supabase.co` | From Supabase Settings |
| `SUPABASE_KEY` | `your-anon-key` | From Supabase Settings |
| **Telegram (Storage)** | | |
| `API_ID` | `1234567` | From my.telegram.org |
| `API_HASH` | `abcdef...` | From my.telegram.org |
| `BOT_TOKEN` | `123:ABC...` | From @BotFather |
| `STORAGE_CHANNEL_ID` | `-100...` | ID of your private channel |
| **Application** | | |
| `SECRET_KEY` | (click "Generate") | Session encryption |
| `SESSION_SECRET` | (click "Generate") | Auth sessions |
| `ALLOWED_ORIGINS` | `https://khaznati-dz.onrender.com` | Your service URL |
| `APP_ENV` | `production` | Set to production |

4. Click **Save Changes**
5. Your service will automatically redeploy

---

## Part 4: Verify Everything Works

### Test the Backend Health
1. Go to: `https://khaznati-dz.onrender.com/api/health`
2. You should see `{"status": "healthy", "storage": "connected"}`

### Test the Website
1. Go to: `https://khaznati-dz.onrender.com`
2. You should see your Khaznati login page!


---

## Part 4: Verify Everything Works

### Test the Backend

1. Open your browser
2. Go to: `https://khaznati-backend.onrender.com/health`
3. You should see:
```json
{
  "status": "healthy",
  "app": "Khaznati DZ",
  "version": "1.0.0"
}
```

### Test the Frontend

1. Go to: `https://khaznati-frontend.onrender.com`
2. You should see your Khaznati website!

### Test the API Docs (Development Only)

If you set `DEBUG=true`, you can access:
- API Docs: `https://khaznati-backend.onrender.com/docs`
- ReDoc: `https://khaznati-backend.onrender.com/redoc`

---

## Troubleshooting

### ❌ "Permission denied" when pushing to GitHub

**Solution**: Make sure you're using your Personal Access Token as the password, not your GitHub password.

### ❌ Build fails on Render

**Common causes:**
1. Missing dependencies in `requirements.txt` or `package.json`
2. Python version mismatch (specify `python-3.11` in Render settings)

**To fix:**
1. Go to your service on Render
2. Click **Logs** to see the error
3. Fix the issue in your code
4. Push to GitHub (Render auto-deploys on new commits)

### ❌ "Database connection failed"

**Solution**: 
1. Check that `DATABASE_URL` is set correctly
2. Make sure to copy the **Internal Database URL** from Render PostgreSQL

### ❌ Frontend can't connect to backend

**Solutions:**
1. Check `VITE_API_URL` is set correctly
2. Check `ALLOWED_ORIGINS` includes your frontend URL
3. Make sure there's no trailing slash in URLs

### ❌ App works locally but not on Render

**Common issues:**
1. Environment variables not set
2. Using `localhost` instead of `0.0.0.0`
3. Hardcoded paths that don't exist on Render

---

## 🎉 Congratulations!

Your Khaznati DZ application is now live on the internet! 

**Your URLs:**
- Frontend: `https://khaznati-frontend.onrender.com`
- Backend API: `https://khaznati-backend.onrender.com`
- API Docs: `https://khaznati-backend.onrender.com/docs` (if DEBUG=true)

### Next Steps

1. **Custom Domain**: You can add a custom domain like `khaznati.dz` in Render settings
2. **Upgrade Plan**: The free tier sleeps after 15 minutes of inactivity. Upgrade for always-on service.
3. **Monitoring**: Set up alerts in Render to get notified of issues

---

## 📚 Quick Reference

### Git Commands Cheat Sheet

```powershell
# Check status of your changes
git status

# Stage all changes
git add .

# Create a commit (snapshot)
git commit -m "Your message here"

# Push changes to GitHub
git push

# Pull latest changes from GitHub
git pull
```

### Updating Your Live App

Every time you push to GitHub, Render automatically redeploys:

```powershell
# 1. Make your code changes
# 2. Stage and commit
git add .
git commit -m "Fixed login bug"

# 3. Push to GitHub
git push

# 4. Wait 2-5 minutes for Render to redeploy
```

---

**Questions?** Check the [Render Docs](https://render.com/docs) or [GitHub Docs](https://docs.github.com)
