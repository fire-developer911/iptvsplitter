# Quick Start - 5 Minute Setup

Get your IPTV Proxy running in production in under 5 minutes.

## 1. Local Setup (1 minute)

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials (use your editor of choice)
nano .env
# OR
vim .env
```

Fill in:
```env
main_url=http://your-xtream-provider.com:8080
main_user=your_real_username
main_pass=your_real_password

user_1_user=client1
user_1_pass=clientpass1
user_1_exp=31/12/2025
```

## 2. Test Locally (Optional, 1 minute)

```bash
# Node.js
npm install
npm run dev

# Python
pip install -r requirements.txt
python main.py
```

Visit: `http://localhost:3000/health`

## 3. Deploy to Render (3 minutes)

### 3.1 Push to GitHub

```bash
git init
git add .
git commit -m "IPTV Proxy"
git remote add origin https://github.com/YOUR_USER/iptv-proxy.git
git push -u origin main
```

⚠️ Make sure `.env` is in `.gitignore` (it is by default)

### 3.2 Create Service on Render

1. Go to https://render.com
2. Click **New +** → **Web Service**
3. Select your `iptv-proxy` repository

### 3.3 Configure

| Setting | Value |
|---------|-------|
| Name | `iptv-proxy` |
| Environment | Node (or Python) |
| Build | `npm install` (or `pip install -r requirements.txt`) |
| Start | `npm start` (or `uvicorn main:app --host 0.0.0.0 --port $PORT`) |
| Instance | Free |

### 3.4 Add Environment Variables

Copy these into Render's **Environment** section:

```
main_url=http://your-xtream-provider.com:8080
main_user=your_real_username
main_pass=your_real_password
user_1_user=client1
user_1_pass=clientpass1
user_1_exp=31/12/2025
```

### 3.5 Deploy!

Click **Create Web Service** and wait 2-3 minutes.

## 4. Use It

Your service URL: `https://YOUR_SERVICE_NAME.onrender.com`

### Test
```bash
curl "https://YOUR_SERVICE_NAME.onrender.com/health"
```

### In IPTV Apps
Playlist URL:
```
https://YOUR_SERVICE_NAME.onrender.com/player_api.php?action=get_simple_playlist&username=client1&password=clientpass1
```

## Done! 🎉

You now have a working IPTV proxy that:
- ✅ Hides your real credentials
- ✅ Manages multiple client accounts
- ✅ Auto-validates expiration dates
- ✅ Streams video without buffering
- ✅ Runs on free Render tier
- ✅ Includes free HTTPS

## Next Steps

- **Add more users:** Edit Environment variables in Render
- **Update expiration:** Change `user_N_exp` in Render
- **Monitor logs:** Click "Logs" tab in Render dashboard
- **Scale up:** Upgrade to Starter plan ($7/mo) if you have 5+ concurrent streams

## Support

- Check `README.md` for detailed docs
- Check `RENDER_DEPLOYMENT.md` for Render-specific help
- Run `./test.sh` to validate your setup locally

## Troubleshooting

### "Service won't start"
→ Check **Deployments** tab, click failed deployment, scroll to "Build logs"

### "Invalid username" errors
→ Double-check `user_N_user` variable names (must be exact)

### "Upstream connection fails"
→ Verify `main_url`, `main_user`, `main_pass` are correct in Environment

### "Service keeps sleeping"
→ Upgrade from Free to Starter plan to always-on service

---

**Questions?** See the full README.md or check Render's documentation.
