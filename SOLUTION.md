# Problem & Solution

## Problem

The UpCloud application was experiencing "Failed to fetch" errors when the frontend tried to call the API:

- **Frontend**: Hosted on S3 using HTTP (`http://upcloud-frontend-dev-6402.s3-website-ap-southeast-2.amazonaws.com`)
- **API**: Lambda Function URL using HTTPS (`https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws`)

**Root Cause**: Modern browsers block HTTP pages from calling HTTPS APIs (Mixed Content security policy)

## Solution

Serve both frontend and API from the same Lambda Function URL:

### Architecture Change

**Before:**
```
HTTP (S3) → HTTPS (Lambda)  ❌ Blocked by browser
```

**After:**
```
HTTPS (Lambda) → HTTPS (Lambda)  ✅ Same origin, no mixed content
```

### Implementation

1. **Modified Lambda handler** (`lambda_handlers/api.py`):
   - Added static file serving for `/`, `*.html`, `*.css`, `*.js`
   - Files read from `/var/task/upcloud/static/` in Lambda environment
   - API routes remain at `/api/*`

2. **Updated frontend** (`upcloud/static/config.js`):
   - Changed from absolute API URL to relative paths
   - `window.API_BASE_URL = ''` (same-origin requests)

3. **Lambda package includes static files**:
   ```
   lambda_package.zip
   ├── upcloud/
   │   ├── static/
   │   │   ├── index.html
   │   │   ├── app.css
   │   │   ├── app.js
   │   │   └── config.js
   │   └── service.py
   ├── lambda_handlers/
   │   └── api.py
   └── cleancloud/
       └── ...
   ```

## Result

**Single URL for everything**: https://bq32gaqqawjzx4f7dh3cqivqiy0sctuc.lambda-url.ap-southeast-2.on.aws/

- `/` → Serves index.html
- `/app.css` → Serves CSS
- `/app.js` → Serves JavaScript
- `/config.js` → Serves config
- `/api/health` → API health check
- `/api/dashboard` → Dashboard data
- `/api/findings` → Findings list
- `/api/scan` → Run demo scan

All requests use HTTPS, all from same origin, no browser security issues.

## Benefits

1. **Simplified deployment** - One service instead of two (no S3 website needed)
2. **Security** - Everything over HTTPS
3. **Cost** - Eliminated S3 website hosting costs
4. **No CORS issues** - Same-origin requests
5. **Single URL** - Easier to share and demo
