# Onboarding Flow - Quick Start Testing Guide

## Prerequisites
- Backend server running on `http://localhost:5000`
- Frontend development server running
- PostgreSQL database configured

## Quick Test Steps

### 1. Test New User Registration Flow

```bash
# 1. Clear browser localStorage
localStorage.clear()

# 2. Navigate to registration
http://localhost:3000/register

# 3. Register new user
Username: testuser_001
Email: test001@example.com
Password: Test@123

# Expected: Redirect to /assessment
# Expected: NO navbar visible
```

### 2. Test Initial Assessment Flow

```bash
# Should be at /assessment
# Expected: Clean interface without navbar
# Expected: Assessment questions displayed

# Complete the assessment
# Expected: Redirect to /assessment-results
# Expected: Still no navbar
```

### 3. Test Onboarding Flow

```bash
# From /assessment-results, continue to onboarding
# Expected: Redirect to /onboarding
# Expected: Still no navbar

# Complete onboarding steps
# Expected: Redirect to /dashboard
# Expected: NAVBAR NOW VISIBLE
```

### 4. Test Protected Route Access

```bash
# Before completing onboarding, manually navigate to:
http://localhost:3000/dashboard

# Expected: Automatic redirect to /assessment

# Try accessing other protected routes:
http://localhost:3000/learning-paths
http://localhost:3000/vocabulary

# Expected: All redirect to /assessment
```

### 5. Test Returning User

```bash
# Logout
# Login with same user (who completed onboarding)

# Expected: Redirect to /dashboard
# Expected: Navbar visible immediately
# Expected: All routes accessible
```

## API Testing

### Check User Status
```bash
# Get JWT token from login
curl -X GET http://localhost:5000/api/user/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected Response (before onboarding):
{
  "user_status": {
    "onboarding_completed": false,
    "needs_initial_assessment": true,
    "current_learning_phase": "assessment",
    "navigation": {
      "show_navbar": false,
      "redirect_to": "/assessment",
      "required_action": "complete_assessment"
    }
  }
}

# Expected Response (after onboarding):
{
  "user_status": {
    "onboarding_completed": true,
    "needs_initial_assessment": false,
    "current_learning_phase": "learning",
    "navigation": {
      "show_navbar": true,
      "redirect_to": null,
      "required_action": null
    }
  }
}
```

### Check Route Access
```bash
curl -X GET http://localhost:5000/api/user/can-access/dashboard \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Before onboarding:
{
  "can_access": false,
  "reason": "Onboarding not completed",
  "redirect_to": "/assessment"
}

# After onboarding:
{
  "can_access": true,
  "reason": "User has completed onboarding",
  "redirect_to": null
}
```

## Browser DevTools Checks

### 1. Network Tab
- Check `/api/user/status` calls on route changes
- Verify JWT token in Authorization header
- Check response status: 200 OK

### 2. Console
- No JavaScript errors
- Check status logs from OnboardingGuard
- Verify redirect messages

### 3. Application → LocalStorage
```javascript
// Should contain:
{
  "access_token": "eyJ...",
  "user": {
    "id": 1,
    "username": "testuser_001",
    "onboarding_completed": false,
    "needs_initial_assessment": true,
    "current_learning_phase": "assessment"
  }
}
```

## Visual Checks

### During Onboarding (Navbar Hidden)
- ✅ Clean full-width layout
- ✅ No sidebar navigation
- ✅ No top app bar with menu items
- ✅ Focus on assessment/onboarding content only

### After Onboarding (Navbar Visible)
- ✅ Left sidebar with navigation menu
- ✅ Top app bar with notifications, theme toggle, user menu
- ✅ All menu items clickable
- ✅ Current page highlighted in menu
- ✅ User profile section at bottom of sidebar

## Common Issues & Solutions

### Issue: Navbar Not Hiding During Onboarding
**Solution:**
1. Check `/api/user/status` response
2. Verify `show_navbar` is `false`
3. Check MainLayoutEnhanced conditional rendering
4. Clear browser cache and localStorage

### Issue: Infinite Redirect Loop
**Solution:**
1. Check OnboardingGuard `allowedPhases` prop
2. Verify user's `current_learning_phase` matches route requirement
3. Check status API response structure
4. Ensure no conflicting redirects in multiple guards

### Issue: Can Access Protected Routes Before Onboarding
**Solution:**
1. Verify OnboardingGuard wraps the route in App.jsx
2. Check `requireOnboarding` prop is set
3. Verify backend returns correct status
4. Check JWT token validity

### Issue: Status Not Updating After Onboarding
**Solution:**
1. Check backend updates `onboarding_completed` field
2. Verify `fetchUserStatus()` called after completion
3. Check AuthContext state update
4. Refresh page to force status refetch

### Issue: Navbar Showing During Assessment
**Solution:**
1. Verify route is `/assessment` or `/onboarding`
2. Check status API returns `show_navbar: false`
3. Verify MainLayoutEnhanced receives correct status
4. Check for caching issues in status fetch

## Database Verification

### Check User Onboarding Status
```sql
-- Check specific user
SELECT 
  id, 
  username, 
  onboarding_completed, 
  needs_initial_assessment, 
  current_learning_phase,
  initial_assessment_id,
  assessment_taken_at
FROM users 
WHERE username = 'testuser_001';

-- Expected before onboarding:
-- onboarding_completed: false
-- needs_initial_assessment: true
-- current_learning_phase: 'onboarding' or 'assessment'

-- Expected after onboarding:
-- onboarding_completed: true
-- needs_initial_assessment: false
-- current_learning_phase: 'learning'
```

## Component State Verification

### React DevTools

1. **MainLayoutEnhanced Component:**
   - Check `userStatus` state
   - Check `showNavbar` state
   - Verify updates on route change

2. **OnboardingGuard Component:**
   - Check `status` state
   - Check `loading` state
   - Verify redirect logic

3. **AuthContext:**
   - Check `user` object has onboarding fields
   - Check `userStatus` state
   - Check `isAuthenticated` is true

## Performance Checks

### API Call Frequency
- Status API should be called:
  - On component mount
  - On route change
  - After login/register
  - NOT on every render

### Loading States
- Show loading spinner during initial status fetch
- No flash of wrong content
- Smooth transitions between layouts

## Security Verification

### Frontend Guards
- Try bypassing guard by modifying React DevTools state
- Verify backend still blocks access
- Check JWT token required for all status endpoints

### Backend Protection
- Try accessing protected routes without JWT
- Verify 401 Unauthorized response
- Try accessing another user's status
- Verify 403 Forbidden response

## Success Criteria

✅ New user registration redirects to assessment  
✅ Navbar hidden during onboarding flow  
✅ Assessment completion progresses to onboarding  
✅ Onboarding completion shows navbar  
✅ Protected routes inaccessible before onboarding  
✅ All routes accessible after onboarding  
✅ Direct URL access properly redirects  
✅ Returning users see correct state  
✅ Status API returns accurate data  
✅ No infinite redirect loops  
✅ No console errors  
✅ Smooth UI transitions  

## Next Steps After Testing

1. **If all tests pass:**
   - Document any edge cases discovered
   - Update user documentation
   - Deploy to staging environment

2. **If tests fail:**
   - Check troubleshooting section above
   - Review implementation guide
   - Check backend logs for errors
   - Verify database schema matches expectations

## Support

For issues not covered in this guide:
1. Check `guides/ONBOARDING_STATUS_IMPLEMENTATION.md`
2. Review backend logs: `tail -f app.log`
3. Check browser console for errors
4. Verify all files were updated correctly
5. Restart both frontend and backend servers
