# Deployment to Render.com

This guide walks you through deploying the IPTV Proxy service to Render in 5 minutes.

## Prerequisites

- GitHub account with the IPTV Proxy repository
- Render account (create at https://render.com if needed)
- Your Xtream Codes credentials ready

## Step-by-Step Deployment

### 1. Push to GitHub

```bash
# Initialize git repo if needed
git init

# Add all files
git add .

# Commit
git commit -m "Initial IPTV Proxy setup"

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/iptv-proxy.git
git branch -M main
git push -u origin main
```

**Important:** Make sure `.env` is in `.gitignore` (it is by default). Do NOT push your real credentials to GitHub.

### 2. Create Render Account & Connect GitHub

1. Go to https://render.com
2. Sign up (if needed) or log in
3. Click **Connect GitHub** in your dashboard
4. Authorize Render to access your repositories
5. Select the `iptv-proxy` repository

### 3. Create a New Web Service

1. In Render dashboard, click **New +** → **Web Service**
2. Select the `iptv-proxy` repository
3. Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `iptv-proxy` (or your preferred name) |
| **Environment** | Node (if using Node.js) or Python (if using Python) |
| **Build Command** | See below |
| **Start Command** | See below |
| **Instance Type** | Free (or Starter for better reliability) |

### Build & Start Commands

#### For Node.js (Recommended)

**Build Command:**
```
npm install
```

**Start Command:**
```
npm start
```

#### For Python

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Add Environment Variables

1. Scroll down to **Environment** section
2. Click **Add Environment Variable** for each:

```
main_url=http://your-xtream-provider.com:8080
main_user=your_real_username
main_pass=your_real_password
user_1_user=client_username_1
user_1_pass=client_password_1
user_1_exp=1/5/2026
user_2_user=client_username_2
user_2_pass=client_password_2
user_2_exp=18/6/2026
```

**⚠️ IMPORTANT:** Do NOT use `.env` files in Render. Always add variables through the dashboard.

### 5. Configure Auto-Deploy (Optional)

By default, Render auto-deploys when you push to `main` branch. If you want to disable this:

1. Go to **Settings** → **Auto-Deploy**
2. Toggle **Auto-Deploy** to off

To manually deploy:
- Click **Redeploy** button in the dashboard
- Or push to the `main` branch

### 6. Deploy!

Click **Create Web Service**. Render will:
1. Clone your repository
2. Run the build command (`npm install` or `pip install`)
3. Start the service with your start command
4. Assign a public HTTPS URL

**Deployment typically takes 2-5 minutes.**

## After Deployment

### Verify the Service

```bash
# Health check (no auth required)
curl https://YOUR_SERVICE_NAME.onrender.com/health

# Should return:
# {"status":"ok","timestamp":"2024-01-15T10:30:45.123456"}
```

### Get Your Service URL

Your service is publicly available at:
```
https://YOUR_SERVICE_NAME.onrender.com
```

Example requests:
```bash
# Test with valid credentials
curl "https://YOUR_SERVICE_NAME.onrender.com/player_api.php?action=get_categories&username=client_username_1&password=client_password_1"

# Test health endpoint (no credentials needed)
curl "https://YOUR_SERVICE_NAME.onrender.com/health"
```

### Use in IPTV Apps

For IPTV Smarters Pro, GSE Smart IPTV, or similar apps:

**Playlist URL:**
```
https://YOUR_SERVICE_NAME.onrender.com/player_api.php?action=get_simple_playlist&username=CLIENT_USER&password=CLIENT_PASS
```

**Example:**
```
https://my-iptv-proxy.onrender.com/player_api.php?action=get_simple_playlist&username=client_username_1&password=client_password_1
```

## Monitoring & Logs

### View Logs

1. In Render dashboard, click your service
2. Go to **Logs** tab
3. See real-time server output

Example log entry:
```
✓ Loaded 2 custom user(s)
✓ Upstream: http://my-xtream-provider.com:8080
✓ Ready to accept connections
[2024-01-15T10:30:45.123Z] GET /player_api.php?action=get_categories
```

### Restart Service

If needed:
1. Click **Restart service** button
2. Service will restart in 10-30 seconds

## Updating Credentials

### To Add/Update Users

1. Go to **Environment** section in Render dashboard
2. Update the variable
3. Click **Save Changes**
4. Service auto-redeploys with new credentials

No restart needed for expiration dates (checked at request time).

### To Change Upstream Credentials

1. Update `main_url`, `main_user`, or `main_pass` in Environment
2. Click **Save Changes**
3. Service auto-redeploys

## Troubleshooting

### Service Won't Start

**Check the build logs:**
1. Go to **Deployments** tab
2. Click the failed deployment
3. Scroll to **Build logs** section

**Common issues:**
- `Cannot find module` → Missing `package.json` or `requirements.txt`
- `SyntaxError` → Typo in code
- Missing environment variable → Check **Environment** section

### "Invalid username" errors

1. Verify variable names match exactly:
   - `user_1_user` (not `user_1_username`)
   - `user_1_pass` (not `user_1_password`)
2. Check for trailing whitespace in Environment variables
3. Restart service after adding new users

### Upstream connection fails

1. Verify `main_url` is correct and accessible
2. Check if upstream server is blocking Render's IP range
3. Test locally with `curl` to validate upstream URL
4. Check logs for 502 Bad Gateway errors

### Service is slow

1. Check Render's **CPU** and **Memory** usage in logs
2. If consistently maxed out, upgrade to **Starter** or higher plan
3. Verify upstream server isn't overloaded

## Cost & Performance

### Free Plan (Sufficient for 1-10 users)
- RAM: 512 MB
- CPU: 0.5 shared CPU
- Sleep timeout: 15 minutes inactivity
- Cost: FREE

### Starter Plan (Recommended for production)
- RAM: 2.5 GB
- CPU: 1 dedicated core
- Always running (no sleep)
- Cost: $7/month

If you're running 1-2 client streams, **Free** is fine.
For 5+ concurrent streams, upgrade to **Starter**.

## Security Best Practices

✅ **Always use HTTPS** (Render provides free SSL)
✅ **Rotate credentials** quarterly
✅ **Never commit `.env`** to GitHub
✅ **Use strong passwords** for client accounts
✅ **Monitor logs** for suspicious activity
✅ **Disable unused user accounts** by removing from Environment

## Rolling Back

If a deployment goes wrong:

1. Go to **Deployments** tab
2. Find the previous good deployment
3. Click the **⋯** menu → **Re-deploy**

## Getting Help

- Render Docs: https://render.com/docs
- Check logs in Render dashboard first
- Test locally with `npm start` or `python main.py`
- Verify upstream server is accessible

---

**Your IPTV Proxy is now live and ready to use! 🚀**
