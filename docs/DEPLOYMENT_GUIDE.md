# Deployment Guide

Comprehensive guide for deploying the Vortex 2026 Accommodation System to production.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Google Cloud Setup](#google-cloud-setup)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

Before deploying to production, ensure you have:

- [ ] Google Cloud project with Sheets API enabled
- [ ] Service account credentials (JSON file)
- [ ] Google Sheet created and shared with service account
- [ ] Registration data prepared (JSON format)
- [ ] Strong API secret key generated
- [ ] Domain names configured (optional but recommended)
- [ ] SSL certificates (automatic with Vercel/Netlify/Render)
- [ ] All tests passing locally
- [ ] Environment variables documented

---

## Google Cloud Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: `vortex-2026-accommodation`
3. Enable billing (required for API access)

### Step 2: Enable Google Sheets API

1. Navigate to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click "Enable"

### Step 3: Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Name: `vortex-accommodation-service`
4. Create and download JSON key
5. **IMPORTANT**: Store this key securely!

### Step 4: Set Up Google Sheet

1. Create a new Google Sheet
2. Name it: `Vortex 2026 Accommodation`
3. Run the setup script:

```bash
cd backend
python scripts/setup_google_sheets.py
```

4. Share the sheet with your service account email (found in JSON key)
5. Grant "Editor" permission

**Detailed instructions**: See [Google Sheets Setup Guide](GOOGLE_SHEETS_SETUP.md)

---

## Backend Deployment

### Option 1: Render (Recommended)

Render provides easy deployment with automatic HTTPS and scaling.

#### Step 1: Prepare Repository

1. Push your code to GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

#### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

#### Step 3: Create Web Service

1. Click "New +" > "Web Service"
2. Connect your repository
3. Configure the service:
   - **Name**: `vortex-2026-backend`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4`

#### Step 4: Set Environment Variables

In Render dashboard, add these environment variables:

```
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
SHEET_NAME=Vortex 2026 Accommodation
API_SECRET_KEY=<generate-strong-random-key>
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
REGISTRATION_DATA_PATH=data/registration_data.json
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Important**:

- Copy the entire service account JSON as one line
- Generate a strong API secret key (use a password generator)
- Update ALLOWED_ORIGINS with your actual frontend URL

#### Step 5: Add Disk Storage (for registration data)

1. In Render dashboard, go to your service
2. Click "Disks" tab
3. Add disk:
   - **Name**: `data`
   - **Mount Path**: `/app/data`
   - **Size**: 1 GB

4. Upload registration data:
   - Use Render Shell or deploy with data in repository

#### Step 6: Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy
3. Wait for deployment to complete (5-10 minutes)
4. Note your service URL: `https://vortex-2026-backend.onrender.com`

#### Step 7: Verify Deployment

```bash
curl https://vortex-2026-backend.onrender.com/api/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2026-03-06T10:00:00Z",
  "services": {
    "googleSheets": "connected",
    "registrationData": "loaded"
  }
}
```

---

### Option 2: Railway

Railway offers simple deployment with automatic scaling.

#### Step 1: Install Railway CLI

```bash
npm i -g @railway/cli
```

#### Step 2: Login and Initialize

```bash
railway login
cd backend
railway init
```

#### Step 3: Set Environment Variables

```bash
railway variables set GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
railway variables set SHEET_NAME="Vortex 2026 Accommodation"
railway variables set API_SECRET_KEY="your-strong-secret-key"
railway variables set ALLOWED_ORIGINS="https://your-frontend.vercel.app"
railway variables set REGISTRATION_DATA_PATH="data/registration_data.json"
railway variables set ENVIRONMENT="production"
railway variables set LOG_LEVEL="INFO"
```

#### Step 4: Deploy

```bash
railway up
```

Railway will:

- Detect Python and install dependencies
- Use configuration from `railway.json`
- Deploy and provide a public URL

#### Step 5: Get Service URL

```bash
railway domain
```

---

### Option 3: Docker + Any Cloud Provider

Deploy using Docker to AWS, Azure, GCP, or any container platform.

#### Step 1: Build Docker Image

```bash
cd backend
docker build -t vortex-2026-backend .
```

#### Step 2: Test Locally

```bash
docker run -p 8000:8000 \
  -e GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}' \
  -e SHEET_NAME="Vortex 2026 Accommodation" \
  -e API_SECRET_KEY="your-secret-key" \
  -e ALLOWED_ORIGINS="http://localhost:5173" \
  -e REGISTRATION_DATA_PATH="data/registration_data.json" \
  -v $(pwd)/data:/app/data \
  vortex-2026-backend
```

#### Step 3: Push to Container Registry

**Docker Hub:**

```bash
docker tag vortex-2026-backend your-username/vortex-2026-backend
docker push your-username/vortex-2026-backend
```

**AWS ECR:**

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag vortex-2026-backend <account-id>.dkr.ecr.us-east-1.amazonaws.com/vortex-2026-backend
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/vortex-2026-backend
```

#### Step 4: Deploy to Cloud Platform

Follow your cloud provider's documentation for deploying containers:

- **AWS**: ECS, Fargate, or App Runner
- **Azure**: Container Instances or App Service
- **GCP**: Cloud Run or GKE
- **DigitalOcean**: App Platform

---

## Frontend Deployment

### Option 1: Vercel (Recommended)

Vercel provides the best experience for React/Vite applications.

#### Step 1: Install Vercel CLI (Optional)

```bash
npm i -g vercel
```

#### Step 2: Deploy via GitHub (Recommended)

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your repository
5. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

#### Step 3: Set Environment Variables

In Vercel dashboard, add:

```
VITE_API_URL=https://vortex-2026-backend.onrender.com
VITE_API_SECRET_KEY=<same-as-backend-api-secret-key>
```

**Important**: The API secret key must match the backend!

#### Step 4: Deploy

1. Click "Deploy"
2. Vercel will build and deploy automatically
3. Your site will be live at: `https://your-project.vercel.app`

#### Step 5: Configure Custom Domain (Optional)

1. In Vercel dashboard, go to "Settings" > "Domains"
2. Add your custom domain
3. Follow DNS configuration instructions
4. Wait for SSL certificate to be issued (automatic)

#### Step 6: Update Backend CORS

Update backend `ALLOWED_ORIGINS` to include your Vercel URL:

```bash
# In Render dashboard
ALLOWED_ORIGINS=https://your-project.vercel.app,https://your-custom-domain.com
```

---

### Option 2: Netlify

Netlify is another excellent option for static sites.

#### Step 1: Install Netlify CLI (Optional)

```bash
npm i -g netlify-cli
```

#### Step 2: Deploy via GitHub (Recommended)

1. Push your code to GitHub
2. Go to [netlify.com](https://netlify.com)
3. Click "New site from Git"
4. Connect your repository
5. Configure build:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`

#### Step 3: Set Environment Variables

In Netlify dashboard, go to "Site settings" > "Environment variables":

```
VITE_API_URL=https://vortex-2026-backend.onrender.com
VITE_API_SECRET_KEY=<same-as-backend-api-secret-key>
```

#### Step 4: Deploy

1. Click "Deploy site"
2. Netlify will build and deploy
3. Your site will be live at: `https://random-name.netlify.app`

#### Step 5: Configure Custom Domain (Optional)

1. Go to "Domain settings"
2. Add custom domain
3. Follow DNS configuration instructions

---

### Option 3: Static Hosting (S3, Azure, etc.)

Deploy the built files to any static hosting service.

#### Step 1: Build for Production

```bash
cd frontend
npm run build
```

This creates a `dist/` directory with optimized files.

#### Step 2: Upload to Hosting

**AWS S3 + CloudFront:**

```bash
# Upload to S3
aws s3 sync dist/ s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

**Azure Static Web Apps:**

```bash
# Install Azure CLI
az login
az staticwebapp create --name vortex-2026 --resource-group your-rg --source dist/
```

#### Step 3: Configure Environment Variables

For static hosting, you need to inject environment variables at build time:

```bash
VITE_API_URL=https://your-backend.com npm run build
```

Or use a `.env.production` file:

```
VITE_API_URL=https://your-backend.com
VITE_API_SECRET_KEY=your-secret-key
```

---

## Post-Deployment Verification

### Backend Verification

1. **Health Check**:

```bash
curl https://your-backend.com/api/health
```

2. **Search Endpoint**:

```bash
curl -X POST https://your-backend.com/api/search \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

3. **Check Logs**:
   - Render: Dashboard > Logs
   - Railway: `railway logs`
   - Docker: `docker logs <container-id>`

### Frontend Verification

1. **Load the Application**:
   - Open your frontend URL in a browser
   - Check for console errors (F12)

2. **Test Search**:
   - Enter a test email
   - Verify results display correctly

3. **Test Accommodation Form**:
   - Fill in the form
   - Submit and verify success message

4. **Test Error Handling**:
   - Try invalid inputs
   - Verify error messages display

### Integration Testing

1. **End-to-End Flow**:
   - Search for a participant
   - Add accommodation entry
   - Verify entry appears in Google Sheet

2. **CORS Verification**:
   - Ensure frontend can call backend
   - Check browser console for CORS errors

3. **Authentication**:
   - Verify API calls include auth header
   - Test with invalid token (should fail)

---

## Monitoring and Maintenance

### Health Monitoring

Set up uptime monitoring:

**UptimeRobot** (Free):

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Add monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://your-backend.com/api/health`
   - **Interval**: 5 minutes
3. Set up email alerts

**Render Built-in**:

- Render automatically monitors health checks
- Alerts sent to your email

### Log Monitoring

**Backend Logs**:

- Render: Dashboard > Logs (real-time)
- Railway: `railway logs --follow`
- Docker: `docker logs -f <container-id>`

**What to Monitor**:

- Error rates
- Response times
- Google Sheets API errors
- Authentication failures
- Rate limit hits

### Performance Monitoring

**Key Metrics**:

- Search endpoint response time (target: < 1s)
- Accommodation creation time (target: < 2s)
- Error rate (target: < 1%)
- Concurrent users (target: 50+)

**Tools**:

- Render: Built-in metrics dashboard
- Railway: Metrics tab
- Custom: Application Performance Monitoring (APM) tools

### Backup Strategy

**Google Sheets**:

1. Set up automatic exports:
   - File > Download > CSV
   - Schedule daily exports

2. Version history:
   - Google Sheets automatically tracks changes
   - File > Version history

**Registration Data**:

- Keep backups of registration JSON file
- Store in multiple locations
- Version control in Git

### Scaling

**Backend Scaling**:

Render:

- Upgrade to higher plan for more resources
- Enable auto-scaling (Professional plan)

Railway:

- Automatically scales based on load
- Upgrade plan for more resources

**Frontend Scaling**:

- Vercel/Netlify automatically scale
- Global CDN handles traffic spikes
- No configuration needed

### Security Updates

**Regular Maintenance**:

1. Update dependencies monthly:

```bash
# Backend
pip list --outdated
pip install --upgrade <package>

# Frontend
npm outdated
npm update
```

2. Rotate API keys quarterly
3. Review access logs for suspicious activity
4. Update service account keys annually

---

## Troubleshooting

### Backend Issues

**Issue**: Backend won't start

**Solutions**:

- Check all environment variables are set
- Verify Google credentials JSON is valid
- Ensure registration data file exists
- Check logs for specific error messages

**Issue**: Google Sheets connection fails

**Solutions**:

- Verify sheet is shared with service account
- Check Google Sheets API is enabled
- Ensure credentials have correct permissions
- Test credentials locally first

**Issue**: High response times

**Solutions**:

- Check Google Sheets API quota
- Verify registration data is cached
- Increase worker count
- Upgrade server resources

### Frontend Issues

**Issue**: Can't connect to backend

**Solutions**:

- Verify `VITE_API_URL` is correct
- Check backend CORS configuration
- Ensure backend is running
- Check browser console for errors

**Issue**: Authentication errors

**Solutions**:

- Verify `VITE_API_SECRET_KEY` matches backend
- Check auth header is being sent
- Ensure token is not expired

**Issue**: Build fails

**Solutions**:

- Check Node.js version (18+)
- Clear node_modules and reinstall
- Verify all dependencies are installed
- Check for TypeScript errors

### Common Deployment Issues

**Issue**: Environment variables not working

**Solutions**:

- Verify variables are set in deployment platform
- Check variable names (case-sensitive)
- Rebuild/redeploy after setting variables
- For frontend, ensure VITE\_ prefix

**Issue**: CORS errors

**Solutions**:

- Add frontend URL to backend `ALLOWED_ORIGINS`
- Include protocol (https://)
- Redeploy backend after changes
- Check for trailing slashes

**Issue**: Rate limiting too aggressive

**Solutions**:

- Adjust rate limits in backend code
- Implement exponential backoff in frontend
- Consider upgrading to higher tier

---

## Rollback Procedure

If deployment fails or issues arise:

### Render

1. Go to dashboard > Deployments
2. Click on previous successful deployment
3. Click "Redeploy"

### Railway

```bash
railway rollback
```

### Vercel

1. Go to dashboard > Deployments
2. Find previous deployment
3. Click "Promote to Production"

### Manual Rollback

```bash
git revert HEAD
git push origin main
```

---

## Production Checklist

Before going live:

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Google Sheets connected and tested
- [ ] CORS configured correctly
- [ ] HTTPS enabled
- [ ] Health monitoring set up
- [ ] Backup strategy in place
- [ ] Error logging configured
- [ ] Rate limiting tested
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Team trained on system
- [ ] Rollback procedure tested
- [ ] Support contacts documented

---

## Support Contacts

During the event:

- **Technical Lead**: [contact info]
- **Backend Issues**: [contact info]
- **Frontend Issues**: [contact info]
- **Google Cloud**: [contact info]

---

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [Netlify Documentation](https://docs.netlify.com)
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)

---

## Conclusion

This guide covers the complete deployment process for the Vortex 2026 Accommodation System. Follow the steps carefully, verify each stage, and maintain good monitoring practices.

For issues not covered here, consult the platform-specific documentation or contact the technical team.

Good luck with your deployment! 🚀
