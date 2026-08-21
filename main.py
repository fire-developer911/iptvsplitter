from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import StreamingResponse
import httpx
import os
from datetime import datetime
from typing import Dict, Tuple
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="IPTV Proxy", version="1.0.0")

# Parse upstream credentials from .env
main_url = os.getenv("main_url")
main_user = os.getenv("main_user")
main_pass = os.getenv("main_pass")

if not all([main_url, main_user, main_pass]):
    raise ValueError("Missing required environment variables: main_url, main_user, main_pass")

# Parse custom users from .env dynamically
users: Dict[str, Dict[str, str]] = {}
env_vars = os.environ

for key in env_vars:
    if key.startswith("user_") and key.endswith("_user"):
        user_id = key.split("_")[1]
        user_key = f"user_{user_id}_user"
        pass_key = f"user_{user_id}_pass"
        exp_key = f"user_{user_id}_exp"

        if all(k in env_vars for k in [user_key, pass_key, exp_key]):
            username = env_vars[user_key]
            users[username] = {
                "password": env_vars[pass_key],
                "expiration": env_vars[exp_key],
            }

logger.info(f"✓ Loaded {len(users)} custom user(s)")
logger.info(f"✓ Upstream: {main_url}")


def is_expired(exp_date: str) -> bool:
    """
    Validate if an account has expired.
    exp_date format: DD/MM/YYYY
    """
    try:
        day, month, year = map(int, exp_date.split("/"))
        expiration_date = datetime(year, month, day, 23, 59, 59)
        return datetime.now() > expiration_date
    except (ValueError, IndexError):
        logger.error(f"Invalid date format: {exp_date}")
        return True


def authenticate_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Authenticate user against credentials and expiration.
    Returns (is_valid, error_message)
    """
    if not username or not password:
        return False, "Missing username or password"

    if username not in users:
        return False, "Invalid username"

    if users[username]["password"] != password:
        return False, "Invalid password"

    if is_expired(users[username]["expiration"]):
        return False, "Account expired"

    return True, ""


@app.get("/health")
async def health_check():
    """Health check endpoint - no auth required"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/info")
async def info():
    """API info endpoint - no auth required"""
    return {
        "service": "IPTV Proxy",
        "version": "1.0.0",
        "activeUsers": len(users),
    }


@app.api_route("/{path:path}", methods=["GET", "POST", "HEAD"])
async def proxy(path: str, request: Request):
    """
    Main proxy endpoint - authenticates request and forwards to upstream.
    Supports all HTTP methods and streams responses without buffering.
    """
    # Extract credentials from query parameters
    username = request.query_params.get("username")
    password = request.query_params.get("password")

    # Authenticate user
    is_valid, error_msg = authenticate_user(username, password)
    if not is_valid:
        status_code = 401 if error_msg != "Account expired" else 403
        raise HTTPException(
            status_code=status_code,
            detail={"error": "Unauthorized" if status_code == 401 else "Forbidden", "message": error_msg},
        )

    # Build upstream URL with rewritten credentials
    upstream_url = f"{main_url}/{path}".rstrip("/")
    
    # Parse existing query parameters and replace/add credentials
    params = dict(request.query_params)
    params["username"] = main_user
    params["password"] = main_pass

    # Build query string
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    if query_string:
        upstream_url = f"{upstream_url}?{query_string}"

    logger.info(f"[{datetime.now().isoformat()}] {request.method} {request.url.path} → {upstream_url}")

    try:
        # Create async HTTP client for streaming
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                request.method,
                upstream_url,
                headers={
                    k: v for k, v in request.headers.items()
                    if k.lower() not in ["host", "connection"]
                },
                follow_redirects=True,
            ) as response:
                # Create an async generator to stream the response
                async def generate():
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        yield chunk

                return StreamingResponse(
                    generate(),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.headers.get("content-type"),
                )

    except httpx.ConnectError as e:
        logger.error(f"Connection error: {e}")
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Bad Gateway",
                "message": "Failed to connect to upstream server",
            },
        )
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error: {e}")
        raise HTTPException(
            status_code=504,
            detail={
                "error": "Gateway Timeout",
                "message": "Upstream server took too long to respond",
            },
        )
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Bad Gateway",
                "message": "An error occurred while proxying the request",
            },
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler to return proper error format"""
    return Response(
        content=str(exc.detail),
        status_code=exc.status_code,
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
