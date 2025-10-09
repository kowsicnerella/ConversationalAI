# JWT Authentication Debugging Guide

## Changes Made

### 1. Enhanced Frontend Logging (api.js)

- Added detailed console logs to track JWT token
- Logs show token presence, length, and preview
- Enhanced error logging for 422 errors

### 2. Backend JWT Error Handlers (app/**init**.py)

- Added custom error handlers for JWT validation issues
- Now returns specific error messages for:
  - Invalid token (422)
  - Missing Authorization header (401)
  - Expired token (401)
  - Revoked token (401)

### 3. Test Endpoints (test_auth_routes.py)

- `/api/test-no-auth` - Works without authentication
- `/api/test-auth` - Requires JWT token

## How to Debug

### Step 1: Check Browser Console

Open your browser console and look for these logs when you try to access Learning Paths:

```
🔑 Request interceptor - Token present: true/false
🔑 Token length: XXX
🔑 Token preview: eyJhbGciOiJIUzI1NiIs...
📡 Request URL: /courses/my-learning-paths
📡 Request Method: get
✅ Authorization header set (or ⚠️ No token found)
```

### Step 2: Test Without Auth

Try accessing the no-auth endpoint to verify the backend is working:

```javascript
// In browser console:
fetch("http://localhost:5000/api/test-no-auth")
  .then((r) => r.json())
  .then((data) => console.log("No auth test:", data));

// Expected: { message: 'No auth required - this works!', status: 'success' }
```

### Step 3: Test With Auth

Try the authenticated endpoint:

```javascript
// In browser console:
const token = localStorage.getItem("access_token");
fetch("http://localhost:5000/api/test-auth", {
  headers: { Authorization: `Bearer ${token}` },
})
  .then((r) => r.json())
  .then((data) => console.log("Auth test:", data))
  .catch((err) => console.error("Auth test error:", err));

// Expected if working: { message: 'JWT authentication working!', user_id: '1', user_id_type: 'str' }
// Expected if broken: { error: 'Missing Authorization Header', message: '...' }
```

### Step 4: Check Flask Logs

**IMPORTANT**: Restart your Flask server to apply the new changes!

```bash
# In your Flask terminal (D:\ConversationalAI\language-learning-platform)
# Stop the server (Ctrl+C) and restart:
py app.py
```

Then check the Flask console for any errors when you make requests.

### Step 5: Verify Token Format

Check if the token is a valid JWT:

```javascript
// In browser console:
const token = localStorage.getItem("access_token");
console.log("Token:", token);

// A valid JWT has 3 parts separated by dots
const parts = token?.split(".");
console.log("Token parts:", parts?.length); // Should be 3

// Try to decode the header and payload (not the signature)
if (parts && parts.length === 3) {
  try {
    const header = JSON.parse(atob(parts[0]));
    const payload = JSON.parse(atob(parts[1]));
    console.log("Token header:", header);
    console.log("Token payload:", payload);
    console.log("Token expires:", new Date(payload.exp * 1000));
  } catch (e) {
    console.error("Failed to decode token:", e);
  }
}
```

## Common Issues and Solutions

### Issue 1: "No token found in localStorage"

**Solution**: You need to log in first

```javascript
// Check if you're logged in:
console.log("User:", localStorage.getItem("user"));
console.log("Token:", localStorage.getItem("access_token"));

// If not logged in, navigate to /login
window.location.href = "/login";
```

### Issue 2: "Invalid token" (422)

**Causes**:

- Token was created with a different JWT_SECRET_KEY
- Token format is corrupted
- Token doesn't have the expected structure

**Solution**:

```javascript
// Clear and re-login:
localStorage.clear();
window.location.href = "/login";
```

### Issue 3: "Token has expired" (401)

**Solution**: Just log in again. Tokens expire after 24 hours.

### Issue 4: "Missing Authorization Header" (401)

**Causes**:

- Token is not in localStorage
- Axios interceptor is not working
- Token is null/undefined

**Solution**: Check the browser console logs - they will show if the interceptor is adding the header.

## Expected Console Output

### When Everything Works:

```
🔑 Request interceptor - Token present: true
🔑 Token length: 234
🔑 Token preview: eyJhbGciOiJIUzI1NiIs...
📡 Request URL: /courses/my-learning-paths
📡 Request Method: get
✅ Authorization header set
✅ Response received: /courses/my-learning-paths 200
```

### When Token is Missing:

```
🔑 Request interceptor - Token present: false
🔑 Token length: undefined
🔑 Token preview: undefined...
📡 Request URL: /courses/my-learning-paths
📡 Request Method: get
⚠️ No token found in localStorage
❌ Response error: { status: 401, ... }
🔒 401 Unauthorized - Clearing auth and redirecting to login
```

### When Token is Invalid:

```
🔑 Request interceptor - Token present: true
🔑 Token length: 234
🔑 Token preview: eyJhbGciOiJIUzI1NiIs...
📡 Request URL: /courses/my-learning-paths
📡 Request Method: get
✅ Authorization header set
❌ Response error: { status: 422, data: { error: 'Invalid token', message: '...' } }
⚠️ 422 Unprocessable Entity - Likely JWT validation issue
```

## Next Steps

1. **Restart Flask server** (MUST DO!)
2. **Open browser DevTools Console**
3. **Try to access Learning Paths page**
4. **Copy the console output and share it**
5. **Try the test endpoints to isolate the issue**

The enhanced logging will tell us exactly what's happening!
