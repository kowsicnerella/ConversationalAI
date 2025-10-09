# Learning Paths 422 Error - Troubleshooting Guide

## Issue

The `/api/courses/learning-paths` endpoint is returning a **422 UNPROCESSABLE ENTITY** error.

## Root Cause

The 422 error from Flask-JWT-Extended indicates one of the following:

1. **Missing JWT Token** - User is not logged in or token was not sent
2. **Invalid JWT Token** - Token format is incorrect or corrupted
3. **Expired JWT Token** - Token has expired (configured for 24 hours)
4. **JWT Secret Mismatch** - Token was created with a different secret key

## What We've Done

### 1. Added Authentication Checks

**File**: `src/services/learningPathService.js`

```javascript
async getLearningPaths(params = {}) {
  try {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.warn('No access token found. User may not be logged in.');
      throw new Error('Authentication required. Please log in.');
    }

    const response = await axiosInstance.get(API_ENDPOINTS.COURSES.LEARNING_PATHS, { params });
    return response.data;
  } catch (error) {
    console.error("Error fetching learning paths:", error);
    console.error("Error response:", error.response?.data);
    console.error("Error status:", error.response?.status);
    throw error;
  }
}
```

### 2. Added Error Display

**File**: `src/pages/LearningPaths.jsx`

- Added error state to track and display errors
- Added user-friendly error messages for authentication issues
- Added Alert component to show errors to users

### 3. Enhanced Error Messages

The page now shows specific messages for:

- 401/422 errors → "Please log in to view learning paths."
- Network errors → "Failed to load learning paths. Please try again later."
- Missing authentication → "Please log in to access learning paths."

## How to Fix

### Option 1: Ensure User is Logged In (Most Likely Solution)

1. **Navigate to the Login page**: `/login`
2. **Log in with valid credentials**
3. **Verify token is saved**:
   ```javascript
   // Open browser console and check:
   console.log(localStorage.getItem("access_token"));
   // Should return a long JWT token string
   ```
4. **Navigate back to Learning Paths page**

### Option 2: Check JWT Configuration

If users ARE logged in but still getting 422 errors, check:

**File**: `language-learning-platform/config.py`

```python
# Ensure these match
SECRET_KEY = 'telugu-english-learning-platform-secret-key'
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
```

### Option 3: Clear and Re-login

If the token might be corrupted:

```javascript
// In browser console:
localStorage.removeItem("access_token");
localStorage.removeItem("user");
// Then log in again
```

### Option 4: Check Backend Logs

The Flask backend should show the actual error. Look for:

```
127.0.0.1 - - [01/Oct/2025 XX:XX:XX] "GET /api/courses/learning-paths HTTP/1.1" 422 -
```

And check what error is being logged before this line.

## Testing the Fix

### 1. Check Authentication Status

```javascript
// In browser console
const token = localStorage.getItem("access_token");
console.log("Token exists:", !!token);
console.log("Token length:", token?.length);
```

### 2. Check Network Tab

- Open Browser DevTools → Network tab
- Try to access Learning Paths page
- Look for the request to `/api/courses/learning-paths`
- Check the **Headers** tab:
  - Request Headers should include: `Authorization: Bearer <token>`
  - Response should show the actual error message

### 3. Check Console Logs

The enhanced error logging will now show:

- Token presence
- Exact error response from backend
- HTTP status code

## Expected Behavior

### When User is NOT Logged In

- Error alert displays: "Please log in to view learning paths."
- Page shows empty state
- Console shows: "No access token found"

### When User IS Logged In

- Learning paths load successfully
- No error alert displayed
- Console shows successful data retrieval

## API Endpoints Reference

| Endpoint                                  | Method | Auth Required | Purpose                          |
| ----------------------------------------- | ------ | ------------- | -------------------------------- |
| `/api/courses/learning-paths`             | GET    | ✅ Yes        | Get all available learning paths |
| `/api/courses/my-learning-paths`          | GET    | ✅ Yes        | Get user's enrolled paths        |
| `/api/courses/learning-paths/{id}/enroll` | POST   | ✅ Yes        | Enroll in a learning path        |

## Next Steps

1. **Verify user is logged in** - This is the most common cause
2. **Check browser console for detailed error logs**
3. **Check Flask terminal for backend error details**
4. **If still failing, check JWT secret key configuration**

## Additional Notes

- JWT tokens expire after 24 hours (configurable in `config.py`)
- Tokens are automatically attached to requests via axios interceptor in `config/api.js`
- The `@jwt_required()` decorator on the backend validates the token
- A 422 error specifically means the JWT couldn't be parsed/validated
