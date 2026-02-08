# Render Deployment Guide

This guide will help you deploy the Surveillance Computer Vision System to Render.

## 📋 Prerequisites

1. **GitHub/GitLab/Bitbucket Account**: Your code needs to be in a Git repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Push your code** to your Git repository

## 🚀 Deployment Steps

### Step 1: Push Code to Git Repository

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your Git repository
4. Select the repository containing this project

### Step 3: Configure Service

Render will auto-detect the `render.yaml` file, but you can also configure manually:

**Basic Settings:**
- **Name**: `surveillance-app` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)

**Build & Start:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.app:app --host 0.0.0.0 --port $PORT`

### Step 4: Environment Variables

Add these environment variables in Render dashboard (Settings → Environment):

```
EMAIL_SENDER=adabbawa10@gmail.com
EMAIL_PASSWORD=ccgfdsohymdvgixw
EMAIL_RECEIVER=adabbawa06@gmail.com
DATABASE_URL=sqlite:///surveillance.db
```

**Note**: For production, consider using:
- **PostgreSQL** instead of SQLite (more reliable on Render)
- **Environment variables** for sensitive data (already configured)

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will start building and deploying
3. First deployment may take 10-15 minutes (model downloads)
4. Monitor the logs for any issues

## ⚙️ Configuration Files Created

### `render.yaml`
- Auto-configuration file for Render
- Defines service type, build, and start commands
- Sets default environment variables

### `.renderignore`
- Excludes unnecessary files from deployment
- Reduces build time and size

### `runtime.txt`
- Specifies Python version (3.11.0)

## 🔧 Key Changes for Render

### 1. **No Webcam Access**
- Modified `app/app.py` to use uploaded video files instead
- Users must upload video files through the web interface

### 2. **OpenCV Headless**
- Changed to `opencv-python-headless` (no GUI dependencies)
- Better for server environments

### 3. **Environment Variables**
- Email credentials use environment variables
- Database URL configurable via environment

### 4. **Health Check Endpoint**
- Added `/health` endpoint for Render monitoring
- Returns service status and model loading state

## 📝 Usage After Deployment

1. **Access your app**: `https://your-app-name.onrender.com`
2. **Upload a video**: Use the upload button on the main page
3. **View processing**: Video feed will show processed frames
4. **Check database**: Visit `/database` endpoint
5. **View alerts**: Check `/api/alerts` for generated alerts

## ⚠️ Important Notes

### Model Loading
- Models download on first startup (takes 5-10 minutes)
- Subsequent restarts are faster (models cached)
- Free tier may have memory limits - consider upgrading if needed

### Database
- SQLite works but is **ephemeral** on free tier (data lost on restart)
- For production, use **PostgreSQL**:
  1. Create PostgreSQL database on Render
  2. Update `DATABASE_URL` environment variable
  3. Update `requirements.txt` to include `psycopg2-binary` (already included)

### Performance
- Free tier has resource limits
- Heavy ML models may require paid plan
- Consider using smaller models or optimizing for production

### Video Upload Limits
- Free tier has file size limits
- Large videos may need cloud storage (S3, etc.)
- Current implementation stores files temporarily

## 🐛 Troubleshooting

### Build Fails
- Check logs for specific errors
- Ensure all dependencies are in `requirements.txt`
- Verify Python version in `runtime.txt`

### Models Not Loading
- Check memory limits (free tier: 512MB)
- Review build logs for download errors
- Models may take time to download

### Database Issues
- SQLite may not persist on free tier
- Switch to PostgreSQL for production
- Check `DATABASE_URL` environment variable

### Video Not Processing
- Ensure video file is uploaded successfully
- Check video format (MP4 recommended)
- Review application logs for errors

## 🔄 Updating Deployment

After making changes:

```bash
git add .
git commit -m "Update description"
git push origin main
```

Render will automatically detect changes and redeploy.

## 📊 Monitoring

- **Logs**: View real-time logs in Render dashboard
- **Metrics**: Monitor CPU, memory, and request metrics
- **Health**: Check `/health` endpoint status

## 🎯 Next Steps

1. **Set up PostgreSQL** (recommended for production)
2. **Configure custom domain** (optional)
3. **Set up monitoring alerts**
4. **Optimize models** for production use
5. **Add authentication** if needed

---

**Deployment Complete!** 🎉

Your surveillance system is now live on Render. Access it via the provided URL and start uploading videos for processing.
