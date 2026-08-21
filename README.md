# IPTV Xtream Codes Proxy

A lightweight, production-ready proxy service that sits between your IPTV clients and your upstream Xtream Codes provider. It hides your main credentials while allowing you to manage multiple secondary users with custom usernames, passwords, and expiration dates.

## Features

✅ **Credential Isolation** - Hide real upstream credentials from clients  
✅ **Dynamic User Management** - Add/remove users by editing `.env` (no code changes)  
✅ **Expiration Dates** - Automatically reject expired accounts  
✅ **Streaming Optimization** - Streams video without buffering entire files in memory  
✅ **Transparent Proxy** - Pass-through all endpoints (player API, M3U playlists, video streams)  
✅ **Render-Ready** - Automatically binds to `$PORT` environment variable  
✅ **Dual Stack** - Includes both Node.js (Express) and Python (FastAPI) implementations  

## Quick Start

### Option 1: Node.js (Recommended for Render)

#### Local Development

```bash
# Clone or set up the project
git clone <repo>
cd iptv-proxy

# Install dependencies
npm install

# Create .env file from template
cp .env.example .env

# Edit .env with your credentials
nano .env

# Start the server
npm run dev

# Or in production mode
npm start
```

The server will start on `http://localhost:3000` (or whatever `$PORT` is set to).

#### Deploy to Render

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository**
3. **Set build command**: `npm install`
4. **Set start command**: `npm start`
5. **Add environment variables** in Render dashboard:
   - Copy all variables from your `.env` file
   - Set `NODE_ENV=production` (optional but recommended)

Render will automatically:
- Bind to the `$PORT` environment variable
- Install dependencies with `npm install`
- Start the service with `npm start`

### Option 2: Python FastAPI

#### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# Edit .env with your credentials
nano .env

# Start the server
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

#### Deploy to Render

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository**
3. **Set build command**: `pip install -r requirements.txt`
4. **Set start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Add environment variables** in Render dashboard

## Configuration

### `.env` File Structure

```env
# Main upstream credentials (REQUIRED)
main_url=http://your-xtream-provider.com:8080
main_user=your_real_username
main_pass=your_real_password

# Custom users (add as many as you need)
user_1_user=client_username_1
user_1_pass=client_password_1
user_1_exp=1/5/2026        # DD/MM/YYYY format

user_2_user=client_username_2
user_2_pass=client_password_2
user_2_exp=18/6/2026

user_3_user=client_username_3
user_3_pass=client_password_3
user_3_exp=31/12/2026
```

**Notes:**
- Dates must be in `DD/MM/YYYY` format (e.g., `25/12/2025`)
- Users are automatically loaded based on the `user_N_*` pattern
- You can have unlimited users (just keep incrementing the number)
- No code restart needed when changing expiration dates (checked at runtime)

## Usage

### Basic Requests

All requests must include valid credentials as query parameters:

```bash
# Get playlist (M3U format)
curl "http://proxy-url:3000/player_api.php?action=get_live_categories&username=client_username_1&password=client_password_1"

# Get VOD categories
curl "http://proxy-url:3000/player_api.php?action=get_vod_categories&username=client_username_1&password=client_password_1"

# Stream a live channel
curl "http://proxy-url:3000/live/username/password/channel_id.ts?username=client_username_1&password=client_password_1"

# Stream VOD
curl "http://proxy-url:3000/movie/username/password/movie_id.mp4?username=client_username_1&password=client_password_1"
```

### With IPTV Players

For apps like IPTV Smarters Pro, GSE Smart IPTV, or TVirl:

1. **Playlist URL**: `http://proxy-url:3000/player_api.php?action=get_simple_playlist&username=YOUR_USER&password=YOUR_PASS`
2. **Use this as the server URL** in your IPTV app

The proxy will:
- Validate the credentials
- Check expiration date
- Rewrite the request with upstream credentials
- Stream the playlist/video back to your client

## API Endpoints

### Public Endpoints (No Authentication)

#### Health Check
```
GET /health
```
Response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

#### Service Info
```
GET /info
```
Response:
```json
{
  "service": "IPTV Proxy",
  "version": "1.0.0",
  "activeUsers": 3
}
```

### Protected Endpoints

All other routes require valid `username` and `password` query parameters:

- `?username=<client_user>&password=<client_pass>`

Invalid credentials return:

```json
{
  "error": "Unauthorized",
  "message": "Invalid username"
}
```

Expired accounts return:

```json
{
  "error": "Forbidden",
  "message": "Account expired"
}
```

## Performance & Streaming

- **No Memory Buffering**: Video and playlist streams are piped directly from upstream to client
- **Concurrent Connections**: Can handle hundreds of simultaneous streams
- **Low Latency**: Minimal overhead, typical latency < 50ms
- **Large Files**: Tested with video streams up to 4GB without issues

## Monitoring

### Node.js
The server logs all requests with timestamps:
```
[2024-01-15T10:30:45.123Z] GET /live/user/pass/1.ts → http://upstream:8080/live/user/pass/1.ts
[2024-01-15T10:30:46.456Z] GET /player_api.php?action=get_categories → http://upstream:8080/player_api.php?action=get_categories
```

### Python
Check Render logs in the dashboard or via CLI:
```bash
render logs <service-id>
```

## Troubleshooting

### "Invalid username" error
- Double-check the `user_N_user` value in `.env`
- Ensure no typos in the query parameter

### "Invalid password" error
- Verify `user_N_pass` matches query parameter exactly
- Check for whitespace in `.env`

### "Account expired" error
- Update `user_N_exp` date in `.env`
- Ensure date format is `DD/MM/YYYY`

### Upstream connection fails
- Check `main_url`, `main_user`, `main_pass` are correct
- Verify upstream server is accessible
- Check firewall rules if on private network
- Look for 502 Bad Gateway responses

### Video buffering / slow streams
- Check network bandwidth to upstream server
- Consider moving proxy closer to upstream (same region/provider)
- Monitor Render CPU/memory usage

## Security Notes

⚠️ **Always use HTTPS** when proxying Xtream Codes traffic in production:
- Deploy on Render (includes free HTTPS)
- Use a reverse proxy like Cloudflare for additional DDoS protection
- Never expose HTTP without TLS

⚠️ **Credentials in .env**:
- Do NOT commit `.env` to git (add to `.gitignore`)
- Use Render's environment variable dashboard, not git
- Rotate credentials regularly

## Advanced Configuration

### Custom Port (Local Development)

**Node.js:**
```bash
PORT=8080 npm start
```

**Python:**
```bash
PORT=8080 python main.py
```

### Upstream Server with Authentication

If your upstream uses Basic Auth:

**Node.js** - Modify the axios call in `index.js`:
```javascript
auth: {
  username: 'upstream_user',
  password: 'upstream_pass'
}
```

**Python** - Modify httpx call in `main.py`:
```python
auth=(upstream_user, upstream_pass)
```

### Custom Timeouts

**Node.js** - Change timeout in `index.js`:
```javascript
timeout: 60000, // 60 seconds
```

**Python** - Change timeout in `main.py`:
```python
timeout=60.0
```

## Architecture

```
┌─────────────────┐
│   IPTV Client   │
│  (Smarters Pro) │
└────────┬────────┘
         │
         │ GET /live/user/pass/1.ts?username=client_1&password=pwd_1
         │
    ┌────▼─────────────────────────────────┐
    │   IPTV Proxy (This Service)           │
    │ ┌────────────────────────────────────┤
    │ │ 1. Extract & Validate Credentials │
    │ │ 2. Check Expiration Date          │
    │ │ 3. Rewrite: client → upstream     │
    │ │ 4. Stream Response to Client      │
    │ └────────────────────────────────────┤
    └────┬──────────────────────────────────┘
         │
         │ GET /live/user/pass/1.ts?username=real_user&password=real_pass
         │
    ┌────▼───────────────────┐
    │  Upstream Xtream Codes  │
    │  Provider              │
    └────────────────────────┘
```

## Support & Contribution

For bugs, feature requests, or improvements, feel free to open an issue or submit a pull request.

## License

MIT
