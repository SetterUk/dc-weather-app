# 🚀 DC Weather App Deployment Guide

## Overview
This guide will help you deploy your DC Weather App to production:
- **Frontend**: Next.js app deployed on Vercel
- **Backend**: FastAPI app deployed on Railway/Render

## 📋 Prerequisites
1. **GitHub Account** with your code repository
2. **Vercel Account** (free tier available)
3. **Railway Account** (free tier available) or **Render Account**
4. **OpenAI API Key** (for chat and TTS features)

## 🔧 Step 1: Prepare Your Repository

### 1.1 Update Environment Variables
Create `.env.local` in your frontend directory:
```env
NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.railway.app
```

### 1.2 Commit and Push Your Code
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

## 🌐 Step 2: Deploy Backend (Railway)

### 2.1 Deploy to Railway
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Set the **Root Directory** to `backend`
6. Click "Deploy"

### 2.2 Configure Environment Variables
In Railway dashboard, add these environment variables:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 2.3 Get Your Backend URL
- Railway will provide a URL like: `https://your-app-name.railway.app`
- Copy this URL for the next step

## 🎨 Step 3: Deploy Frontend (Vercel)

### 3.1 Deploy to Vercel
1. Go to [Vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project"
4. Import your GitHub repository
5. Set the **Root Directory** to `frontend`
6. Click "Deploy"

### 3.2 Configure Environment Variables
In Vercel dashboard, go to Settings → Environment Variables:
```
NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.railway.app
```

### 3.3 Update CORS in Backend
Replace `https://frontend-d30imq72n-setteruks-projects.vercel.app` in `backend/main.py` with your actual Vercel domain.

## 🔄 Step 4: Connect Frontend to Backend

### 4.1 Update API Routes
Your frontend API routes already use `process.env.BACKEND_URL`, so they should work automatically.

### 4.2 Test the Connection
1. Visit your Vercel app URL
2. Try the weather functionality
3. Test the chat feature

## 🛠️ Alternative Backend Hosting

### Option A: Render
1. Go to [Render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repo
4. Set **Root Directory** to `backend`
5. Set **Build Command**: `pip install -r requirements.txt`
6. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Option B: Heroku
1. Install Heroku CLI
2. Create `Procfile` (already created)
3. Deploy using Heroku CLI

## 🔍 Troubleshooting

### Common Issues:
1. **CORS Errors**: Update the `allow_origins` in `backend/main.py`
2. **Environment Variables**: Ensure all variables are set in both platforms
3. **Build Errors**: Check the build logs in Vercel/Railway
4. **API Timeouts**: Increase function timeout in `vercel.json`

### Debug Steps:
1. Check Railway logs for backend errors
2. Check Vercel logs for frontend errors
3. Test API endpoints directly using Postman
4. Verify environment variables are loaded correctly

## 📊 Monitoring

### Vercel Analytics
- Built-in analytics for frontend performance
- Function execution times
- Error tracking

### Railway Monitoring
- Application logs
- Resource usage
- Health checks

## 🔐 Security Notes

1. **Never commit API keys** to your repository
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** (automatic on Vercel/Railway)
4. **Regularly update dependencies**

## 🎉 Success!
Your DC Weather App should now be live with:
- ✅ Interactive 3D hero models
- ✅ Real-time weather data
- ✅ AI-powered chat with voice
- ✅ Hero-specific personalities and responses

## 🔗 Useful Links
- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/) 