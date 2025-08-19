# MailApp Deployment Guide - Render + Neon PostgreSQL

This guide will help you deploy your MailApp to Render using Neon PostgreSQL as the database.

## Prerequisites

1. **GitHub Repository**: Ensure your code is in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Neon Account**: Sign up at [neon.tech](https://neon.tech)

## Step 1: Set up Neon PostgreSQL Database

1. **Create a Neon Account** and log in
2. **Create a new project** in Neon
3. **Create a database** (you can use the default one)
4. **Get your connection string**:
   - Go to your project dashboard
   - Click on "Connection Details"
   - Copy the connection string (it looks like: `postgresql://username:password@host/database?sslmode=require`)

## Step 2: Prepare Your Repository

1. **Update your local `.env` file** with your Neon database URL:
   ```
   DATABASE_URL=postgresql://username:password@host/database?sslmode=require
   SECRET_KEY=your-production-secret-key
   DEBUG=False
   GEMINI_API_KEY=your-gemini-api-key
   ```

2. **Test locally with PostgreSQL** (optional but recommended):
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic
   python manage.py runserver
   ```

3. **Commit and push all changes** to your GitHub repository

## Step 3: Deploy to Render

### Option A: Using the Render Dashboard

1. **Connect your GitHub repository**:
   - Go to [render.com](https://render.com) and log in
   - Click "New +" → "Web Service"
   - Connect your GitHub account and select your repository

2. **Configure the web service**:
   - **Name**: `mailapp` (or your preferred name)
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn MailProject.wsgi:application`

3. **Set environment variables**:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string
   - `SECRET_KEY`: A secure secret key for production
   - `DEBUG`: `False`
   - `GEMINI_API_KEY`: Your Gemini API key (if using AI features)

### Option B: Using render.yaml (Infrastructure as Code)

1. **Use the included render.yaml** file in your repository
2. **Deploy from GitHub** by connecting your repository
3. **Set environment variables** in the Render dashboard

## Step 4: Configure Environment Variables in Render

In your Render web service dashboard, add these environment variables:

| Key | Value | Description |
|-----|-------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@host/db` | Your Neon PostgreSQL connection string |
| `SECRET_KEY` | `your-secret-key-here` | Django secret key (generate a new one) |
| `DEBUG` | `False` | Always False in production |
| `GEMINI_API_KEY` | `your-api-key` | Your Gemini AI API key |

## Step 5: Deploy and Test

1. **Deploy**: Render will automatically build and deploy your app
2. **Check logs**: Monitor the deployment logs for any errors
3. **Test your app**: Visit your Render URL and test all functionality

## Step 6: Run Migrations and Create Superuser

After successful deployment, you may need to:

1. **Run migrations** (should be automatic via build.sh):
   ```bash
   python manage.py migrate
   ```

2. **Create a superuser** via Render shell:
   - Go to your service dashboard in Render
   - Open "Shell" tab
   - Run: `python manage.py createsuperuser`

## Important Notes

### Security
- ✅ Debug is disabled in production
- ✅ SSL redirects are enabled
- ✅ Security headers are configured
- ✅ Static files are served via WhiteNoise

### Database
- ✅ PostgreSQL is used in production
- ✅ SQLite is used for local development
- ✅ Connection pooling is handled by Neon

### Static Files
- ✅ Static files are collected during build
- ✅ WhiteNoise serves static files efficiently
- ✅ CSS/JS files are compressed

## Troubleshooting

### Common Issues

1. **Build fails**: Check the build logs in Render dashboard
2. **Database connection fails**: Verify your DATABASE_URL
3. **Static files not loading**: Ensure `collectstatic` runs in build.sh
4. **500 errors**: Check the application logs in Render

### Useful Commands

```bash
# Test locally with production settings
export DEBUG=False
python manage.py check --deploy

# Collect static files locally
python manage.py collectstatic --no-input

# Test database connection
python manage.py dbshell
```

## Environment Variables Reference

Create these environment variables in Render:

```bash
# Required
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-here
DEBUG=False

# Optional
GEMINI_API_KEY=your-gemini-api-key
ALLOWED_HOST=your-custom-domain.com
```

## Next Steps

1. **Set up custom domain** (if needed)
2. **Configure email backend** (for password resets, etc.)
3. **Set up monitoring** and logging
4. **Add SSL certificate** (automatic with Render)
5. **Configure backups** for your Neon database

Your MailApp should now be successfully deployed and running on Render with Neon PostgreSQL! 🚀
