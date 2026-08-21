import express from 'express';
import dotenv from 'dotenv';
import axios from 'axios';
import { URL } from 'url';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Parse upstream credentials from .env
const mainUrl = process.env.main_url;
const mainUser = process.env.main_user;
const mainPass = process.env.main_pass;

if (!mainUrl || !mainUser || !mainPass) {
  throw new Error('Missing required environment variables: main_url, main_user, main_pass');
}

// Parse custom users from .env dynamically
const users = {};
const envKeys = Object.keys(process.env);

envKeys.forEach((key) => {
  const userMatch = key.match(/^user_(\d+)_user$/);
  if (userMatch) {
    const userId = userMatch[1];
    const userKey = `user_${userId}_user`;
    const passKey = `user_${userId}_pass`;
    const expKey = `user_${userId}_exp`;

    if (process.env[userKey] && process.env[passKey] && process.env[expKey]) {
      users[process.env[userKey]] = {
        password: process.env[passKey],
        expiration: process.env[expKey],
      };
    }
  }
});

console.log(`✓ Loaded ${Object.keys(users).length} custom user(s)`);
console.log(`✓ Upstream: ${mainUrl}`);

/**
 * Validate if an account has expired
 * @param {string} expDate - Date string in DD/MM/YYYY format
 * @returns {boolean} - true if expired, false if still valid
 */
function isExpired(expDate) {
  const [day, month, year] = expDate.split('/').map(Number);
  const expirationDate = new Date(year, month - 1, day); // month is 0-indexed
  expirationDate.setHours(23, 59, 59, 999); // end of day
  return new Date() > expirationDate;
}

/**
 * Authentication middleware
 */
function authenticateUser(req, res, next) {
  const { username, password } = req.query;

  if (!username || !password) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Missing username or password',
    });
  }

  const user = users[username];

  if (!user) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid username',
    });
  }

  if (user.password !== password) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid password',
    });
  }

  if (isExpired(user.expiration)) {
    return res.status(403).json({
      error: 'Forbidden',
      message: 'Account expired',
    });
  }

  // Attach main credentials to request for later use
  req.mainUser = mainUser;
  req.mainPass = mainPass;

  next();
}

/**
 * Rewrite URL to replace custom credentials with upstream credentials
 */
function rewriteUrl(urlString) {
  try {
    const url = new URL(urlString, mainUrl);
    url.searchParams.set('username', mainUser);
    url.searchParams.set('password', mainPass);
    return url.toString();
  } catch (err) {
    console.error('Error rewriting URL:', err);
    throw err;
  }
}

/**
 * Generic proxy handler for all routes
 */
async function proxyHandler(req, res) {
  try {
    // Reconstruct the full path with query parameters (excluding auth credentials we'll replace)
    const pathWithQuery = req.originalUrl;

    // Build the upstream URL
    const upstreamUrl = mainUrl + pathWithQuery.split('?')[0];
    
    // Rewrite credentials
    const rewrittenUrl = rewriteUrl(upstreamUrl);

    console.log(`[${new Date().toISOString()}] ${req.method} ${req.originalUrl} → ${rewrittenUrl}`);

    // Make the request to upstream server
    const response = await axios({
      method: req.method.toLowerCase(),
      url: rewrittenUrl,
      headers: {
        ...req.headers,
        host: new URL(mainUrl).host,
      },
      validateStatus: () => true, // Don't throw on any status code
      responseType: 'stream',
      timeout: 30000,
    });

    // Copy response headers
    Object.keys(response.headers).forEach((key) => {
      if (key.toLowerCase() !== 'transfer-encoding') {
        res.setHeader(key, response.headers[key]);
      }
    });

    res.status(response.status);

    // Pipe the stream directly to the response (no buffering)
    response.data.pipe(res);

    // Handle stream errors
    response.data.on('error', (err) => {
      console.error('Upstream stream error:', err);
      if (!res.headersSent) {
        res.status(502).json({ error: 'Bad Gateway', message: 'Upstream server error' });
      } else {
        res.end();
      }
    });
  } catch (error) {
    console.error('Proxy error:', error.message);
    if (!res.headersSent) {
      res.status(502).json({
        error: 'Bad Gateway',
        message: 'Failed to connect to upstream server',
      });
    }
  }
}

// Health check endpoint (no auth required)
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
  });
});

// API info endpoint (no auth required)
app.get('/info', (req, res) => {
  res.json({
    service: 'IPTV Proxy',
    version: '1.0.0',
    activeUsers: Object.keys(users).length,
  });
});

// All other routes go through authentication and proxy
app.all('*', authenticateUser, proxyHandler);

// Global error handler
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: 'An unexpected error occurred',
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`\n🚀 IPTV Proxy Server running on port ${PORT}`);
  console.log(`📍 Upstream: ${mainUrl}`);
  console.log(`👥 Users configured: ${Object.keys(users).length}`);
  console.log(`\n✓ Ready to accept connections\n`);
});
