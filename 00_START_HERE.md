# 🚀 IPTV Proxy - Start Here

Your **production-ready IPTV Xtream Codes proxy** is ready to deploy. This document tells you exactly where to start.

## What You Have

A complete proxy service that:
- ✅ Hides your real Xtream Codes credentials from clients
- ✅ Manages unlimited custom users with passwords + expiration dates
- ✅ Validates credentials & dates automatically
- ✅ Streams video without buffering large files
- ✅ Deploys on Render in 5 minutes (with free HTTPS)
- ✅ Written in Node.js (Express) OR Python (FastAPI)

## Pick Your Path

### Path A: "Just Deploy It Fast" ⚡ (5 minutes)

1. Read: **QUICKSTART.md** (you'll be live in 5 mins)
2. Follow the 4 steps
3. Done!

### Path B: "I Want to Understand Everything" 📚 (20 minutes)

1. Read: **IMPLEMENTATION_SUMMARY.md** (how it works, architecture, examples)
2. Read: **README.md** (complete reference)
3. Read: **RENDER_DEPLOYMENT.md** (step-by-step Render guide)
4. Deploy

### Path C: "I'll Test Locally First" 🧪 (10 minutes)

1. Read: **QUICKSTART.md** section 1 (local setup)
2. Create `.env` from `.env.example`
3. Run: `npm install && npm run dev` (or `pip install -r requirements.txt && python main.py`)
4. Run: `./test.sh` to validate
5. Then follow QUICKSTART.md section 3 to deploy to Render

## File Guide

| File | Purpose | Read If |
|------|---------|---------|
| **00_START_HERE.md** | This overview | First time |
| **QUICKSTART.md** | 5-minute deployment | Want to deploy ASAP |
| **IMPLEMENTATION_SUMMARY.md** | How it works + architecture | Want to understand the system |
| **README.md** | Complete reference docs | Need full documentation |
| **RENDER_DEPLOYMENT.md** | Render-specific guide | Deploying to Render |
| **index.js** | Main Node.js server | Using Node.js version |
| **main.py** | Main Python server | Using Python version |
| **package.json** | Node.js dependencies | Using Node.js |
| **.env.example** | Configuration template | Setting up your credentials |
| **test.sh** | Test your setup | Validating locally |

## Your First 5 Minutes

```bash
# 1. Copy config template
cp .env.example .env

# 2. Edit with your credentials
nano .env
# main_url = your xtream provider
# main_user = your real username  
# main_pass = your real password
# user_1_user = client 1 username
# etc.

# 3. Deploy to Render (follow QUICKSTART.md section 3)

# 4. Test
curl "https://YOUR_SERVICE.onrender.com/health"

# 5. Use in IPTV app with URL:
# https://YOUR_SERVICE.onrender.com/player_api.php?action=get_simple_playlist&username=client_1&password=client_pass
```

## Key Concepts

### How It Works

```
IPTV Client
    ↓ (sends: username=alice, password=pwd1)
Proxy validates & checks expiration
    ↓ (rewrites to: username=REAL_USER, password=REAL_PASS)
Upstream Xtream Server
    ↓ (returns video stream)
IPTV Client receives video
```

### Configuration (`.env`)

```
# Your real credentials (kept secret)
main_url=http://your-provider.com:8080
main_user=your_username
main_pass=your_password

# Client credentials (shared with IPTV users)
user_1_user=alice
user_1_pass=pwd123
user_1_exp=31/12/2025
```

Just add more `user_N_*` lines to create additional clients.

### Expiration Dates

Format: `DD/MM/YYYY` (e.g., `31/12/2025` = December 31, 2025)

When a client's date passes, the proxy automatically rejects them with 403 Forbidden. No restart needed.

## Choose Your Stack

### Node.js + Express (Recommended)
- Faster startup
- Lower memory
- Excellent streaming
- Use if: You want the fastest setup

### Python + FastAPI (Alternative)
- More readable code
- Built-in async
- Better for CPU workloads
- Use if: You prefer Python

Both have identical features. Pick whichever you're comfortable with.

## Deployment Options

### Render.com (Recommended) ✨
- Free HTTPS
- Free tier available
- Zero DevOps needed
- Auto-deploy on git push
- See **QUICKSTART.md** section 3

### Other Hosting
The code works anywhere:
- Heroku, Railway, Fly.io, AWS, DigitalOcean, etc.
- Just change the start command in their settings
- All implementations bind to `$PORT` automatically

## Monitoring Your Service

Once deployed, check:

**Health Check** (no auth needed):
```bash
curl https://YOUR_SERVICE/health
```

**View Logs** (on Render):
1. Dashboard → Click your service
2. Go to "Logs" tab
3. See all requests in real-time

**Test with Credentials:**
```bash
curl "https://YOUR_SERVICE/player_api.php?action=get_categories&username=alice&password=pwd1"
```

## Managing Users (After Deployment)

### Add a new user
1. Go to Render dashboard
2. Click your service → Environment
3. Add new variables:
   ```
   user_3_user=newclient
   user_3_pass=newpassword
   user_3_exp=31/12/2026
   ```
4. Click "Save Changes"
5. Service auto-redeploys

### Expire a user
1. Update `user_N_exp` to a past date
2. That user is rejected automatically

### Remove a user
1. Delete the `user_N_user`, `user_N_pass`, `user_N_exp` variables
2. Click "Save Changes"

No code changes, no restart needed.

## Security Reminders

✅ Your real Xtream Codes credentials are **never exposed** to clients  
✅ Each client gets unique credentials (easy to revoke)  
⚠️ Use HTTPS (Render provides free SSL)  
⚠️ Never commit `.env` to GitHub (it's in `.gitignore`)  
⚠️ Rotate credentials quarterly  

## What Happens When

### User Logs In
1. Client sends: `?username=alice&password=pwd1`
2. Proxy checks if alice exists in `.env`
3. Proxy checks if password matches
4. Proxy checks if expiration date hasn't passed
5. If all good → Proxy rewrites to real credentials and forwards
6. If bad → Proxy returns 401 or 403

### Streaming Video
1. Client requests: `GET /live/user/pass/1.ts`
2. Proxy validates credentials (< 1ms)
3. Proxy forwards to upstream
4. Video streams directly to client (no buffering, no memory spike)

### Expired Account
1. Expiration date passes
2. Next request is rejected with 403 Forbidden
3. No restart needed, checked every request

## Common Questions

**Q: Can I use this with my own Xtream provider?**  
A: Yes! Set `main_url`, `main_user`, `main_pass` to your provider's credentials.

**Q: Do I need to restart when adding/removing users?**  
A: No! Changes to `user_N_*` variables take effect immediately.

**Q: What if upstream server goes down?**  
A: Proxy returns 502 Bad Gateway. Clients see the error. No data loss.

**Q: Can I limit video quality or bandwidth per user?**  
A: Not in v1.0. See IMPLEMENTATION_SUMMARY.md "Extending the Service" for how to add this.

**Q: How many concurrent streams can it handle?**  
A: Free tier: 1-2 users. Starter tier ($7/mo): 5-10 users. Depends on video bitrate.

**Q: Is HTTPS required?**  
A: For production yes. Render provides free HTTPS automatically.

## Next Steps

### Right Now
1. Choose your reading path above (A, B, or C)
2. Read the appropriate guide
3. Deploy

### After Deployment
1. Test with `curl` or your IPTV app
2. Monitor logs in Render dashboard
3. Add more users by updating Environment variables
4. Consider upgrading from Free to Starter tier if you have 5+ users

## FAQ - Troubleshooting

**"Service won't start on Render"**  
→ Check Deployments tab → Click failed deployment → Scroll to "Build logs" → Fix errors

**"Invalid username error"**  
→ Double-check `user_N_user` variable name in Render Environment (typos matter!)

**"Can't connect to upstream"**  
→ Verify `main_url` is correct and accessible from Render's servers

**"Authentication works but no video streams"**  
→ Your upstream server may be rejecting requests. Check `main_url` directly.

---

## You're Ready! 🎉

**Recommended:** Start with **QUICKSTART.md** for the fastest path to production.

Any questions? Check the relevant guide above or re-read this overview.

**Let's go!** ➜ Read QUICKSTART.md
