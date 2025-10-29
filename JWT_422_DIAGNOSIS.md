# 422 Error on Learning Path Endpoints - Diagnosis

## 🔍 What We Know

✅ **Fixed:** Blueprint name conflict
- Changed `Blueprint('enhanced_activity')` to `Blueprint('enhanced_activity_v2')`
- Backend now starts successfully

❌ **Still Failing:** Two endpoints return 422
- `GET /api/learning-path/spaced-repetition/due` → 422
- `GET /api/learning-path/activities/incomplete` → 422

✅ **Working:** Other endpoints
- `GET /api/personalization/dashboard` → 200 OK
- All other endpoints working normally

---

## 🔎 Root Cause Analysis

The 422 error with "Invalid token" message means:

1. **Token signature verification failed** - OR -
2. **Token format is invalid** - OR -
3. **Token is using different secret than app expects**

Both endpoints use `@jwt_required()` decorator (same as working endpoints), so the issue isn't the decorator itself.

---

## 🧪 What to Check

### 1. Frontend Token Sending
When you make a request to these endpoints, ensure:

```javascript
// Correct way
const token = localStorage.getItem('token'); // or wherever you store it
fetch('/api/learning-path/spaced-repetition/due', {
  headers: {
    'Authorization': `Bearer ${token}`  // ← Must be "Bearer TOKEN"
  }
})
```

### 2. Browser DevTools Check
1. Open Browser DevTools (F12)
2. Go to Network tab
3. Make a request to `/api/learning-path/spaced-repetition/due`
4. Check the request headers - look for `Authorization` header
5. Check the response - what exact error message?

### 3. Token Inspection
If you have the token, decode it at [jwt.io](https://jwt.io):
- Check the `exp` field - is it expired?
- Check the `iat` field - when was it issued?
- Check algorithm - should be HS256

### 4. Server Side Debugging
Add logging to see what's happening:

```python
# In app/__init__.py, add this before jwt.init_app(app):

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    print(f"DEBUG: Invalid token error: {error_string}")  # Add this
    return (
        jsonify({
            "error": "Invalid token",
            "message": error_string,
            "telugu_message": "చెల్లని టోకెన్",
        }),
        422,
    )
```

---

## 🎯 Solutions to Try (in order)

### Solution 1: Re-login (Most Common)
1. Log out from the frontend
2. Clear browser cache/localStorage
3. Log back in
4. Try the endpoints again

This regenerates the token and often fixes 422 errors.

### Solution 2: Check Token Expiration
1. Check if your JWT tokens expire (likely 24 hours)
2. If the test token is old, it will fail
3. Generate a fresh token by logging in again

### Solution 3: Verify Authorization Header
In your frontend, make sure you're sending:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs... (your token)
```

NOT:
```
Authorization: eyJhbGciOiJIUzI1NiIs...  (missing "Bearer")
```

### Solution 4: Check JWT Configuration
The existing JWT setup should work. Verify:
```python
# In config.py
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or SECRET_KEY
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
```

---

## 📊 Comparison: Working vs Failing

| Aspect | Working (`/personalization/dashboard`) | Failing (`/learning-path/...`) |
|--------|----------------------------------------|-------------------------------|
| Decorator | `@jwt_required()` | `@jwt_required()` |
| Blueprint | `personalization_bp` | `learning_path_bp` |
| Status | 200 OK | 422 Invalid token |
| Token needed | Yes | Yes |
| Difference | ??? | ??? |

If both use same JWT decorator and you're sending token to both, the issue might be:
- Different JWT secret being used somewhere
- Token validation order
- Timing issue (token expires between requests)

---

## 🚀 Quick Test

From your browser console:

```javascript
// Test 1: Working endpoint
fetch('http://localhost:5000/api/personalization/dashboard', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
}).then(r => r.json()).then(console.log)

// Test 2: Failing endpoint
fetch('http://localhost:5000/api/learning-path/spaced-repetition/due', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
}).then(r => r.json()).then(console.log)
```

If both fail with 422, token is invalid or expired.
If first works but second fails, there might be a blueprint/routing issue.

---

## Next Steps

1. **Log out and back in** - Simplest fix that solves most JWT issues
2. **Check browser console** - See exact error response
3. **Add server logging** - See what error the JWT handler is receiving
4. **Compare with working endpoint** - Check for subtle differences
5. **Test with curl** - Eliminate frontend as a variable

Let me know what you find!
