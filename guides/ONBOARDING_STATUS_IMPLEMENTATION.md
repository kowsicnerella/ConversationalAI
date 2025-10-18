# Onboarding Status & Navigation Implementation Guide

## Overview
Complete implementation of user onboarding status tracking and conditional navigation/UI rendering based on user progress through the onboarding workflow.

## Architecture

### Backend Components

#### 1. User Model (`app/models/user.py`)
**Onboarding Fields:**
```python
onboarding_completed = db.Column(db.Boolean, default=False)
needs_initial_assessment = db.Column(db.Boolean, default=True)
current_learning_phase = db.Column(db.String(20), default="onboarding")
initial_assessment_id = db.Column(db.Integer)
assessment_taken_at = db.Column(db.DateTime)
```

**Learning Phases:**
- `onboarding` - User in initial onboarding
- `assessment` - User taking initial assessment
- `learning` - User actively learning
- `mastery` - User in mastery phase

#### 2. User Status API (`app/api/user_status_routes.py`)
**New Blueprint:** `user_status_bp`

**Endpoints:**

##### GET `/api/user/status`
Returns comprehensive user status for navigation decisions.

**Response Structure:**
```json
{
  "user_status": {
    "user_id": 1,
    "username": "john_doe",
    "onboarding_completed": false,
    "needs_initial_assessment": true,
    "current_learning_phase": "assessment",
    "initial_assessment_id": 1,
    "assessment_taken_at": "2024-01-15T10:30:00Z",
    "profile": {
      "points": 150,
      "level": 2,
      "proficiency_level": "Beginner"
    },
    "navigation": {
      "show_navbar": false,
      "redirect_to": "/assessment",
      "required_action": "complete_assessment"
    }
  }
}
```

**Navigation Logic:**
- `show_navbar: false` - During onboarding/assessment
- `show_navbar: true` - After onboarding completion
- `redirect_to` - Suggested redirect path
- `required_action` - What user needs to do next

##### GET `/api/user/can-access/<route_path>`
Checks if user can access specific route.

**Response:**
```json
{
  "can_access": true,
  "reason": "User has completed onboarding",
  "redirect_to": null
}
```

### Frontend Components

#### 1. OnboardingGuard (`src/components/guards/OnboardingGuard.jsx`)
Route protection component that enforces onboarding flow.

**Props:**
- `requireOnboarding` (boolean) - Route requires completed onboarding
- `allowedPhases` (array) - Specific phases allowed to access route
- `children` - Protected component

**Behavior:**
```jsx
// Protect route requiring completed onboarding
<OnboardingGuard requireOnboarding>
  <Dashboard />
</OnboardingGuard>

// Allow only during specific phases
<OnboardingGuard allowedPhases={["assessment", "onboarding"]}>
  <InitialAssessment />
</OnboardingGuard>
```

**Flow:**
1. Fetches `/api/user/status` on mount
2. Checks onboarding status
3. Redirects based on requirements:
   - Not onboarded + requires onboarding → `/assessment`
   - Onboarded + accessing onboarding route → `/dashboard`
   - Phase mismatch → Appropriate phase route

#### 2. Enhanced MainLayout (`src/layouts/MainLayoutEnhanced.jsx`)
Layout with conditional navbar rendering.

**Key Features:**
- Fetches user status on mount and route change
- Conditionally shows/hides entire navbar
- Displays simplified layout during onboarding
- Shows full navigation after completion

**Status-Driven UI:**
```jsx
// No navbar - clean onboarding experience
if (!showNavbar) {
  return (
    <Box sx={{ minHeight: "100vh" }}>
      <Outlet />
    </Box>
  );
}

// Full layout with navbar
return <Box sx={{ display: "flex" }}>...</Box>;
```

#### 3. Updated AuthContext (`src/context/AuthContext.jsx`)
Enhanced authentication context with status management.

**New Features:**
- `userStatus` state - Current user status object
- `fetchUserStatus()` - Refresh user status from API
- Auto-fetch status after login/register
- Update user object with latest onboarding fields

**Usage:**
```jsx
const { user, userStatus, fetchUserStatus } = useAuth();

// Refresh status after important actions
await fetchUserStatus();

// Check navigation requirements
if (userStatus?.navigation.show_navbar) {
  // Show navbar
}
```

#### 4. Updated App Routing (`src/App.jsx`)
Routes wrapped with OnboardingGuard for protection.

**Route Categories:**

**Public Routes:**
- `/` - Landing page
- `/login` - Login
- `/register` - Registration
- `/forgot-password` - Password reset

**Onboarding Routes (No navbar):**
```jsx
<OnboardingGuard allowedPhases={["assessment", "onboarding"]}>
  <InitialAssessment />
</OnboardingGuard>
```

**Protected Routes (Require onboarding):**
```jsx
<OnboardingGuard requireOnboarding>
  <Dashboard />
</OnboardingGuard>
```

## User Flow

### New User Registration
1. User registers → JWT token issued
2. AuthContext calls `fetchUserStatus()`
3. Status: `onboarding_completed: false`, `needs_initial_assessment: true`
4. Redirect to `/assessment`
5. Navbar hidden (status.navigation.show_navbar: false)

### Initial Assessment
1. User takes assessment at `/assessment`
2. OnboardingGuard allows access (phase: "assessment")
3. Navbar remains hidden
4. On completion → Update user status
5. Redirect to `/assessment-results`

### Assessment Results → Onboarding
1. User views results at `/assessment-results`
2. Continues to onboarding at `/onboarding`
3. OnboardingGuard allows access (phase: "onboarding")
4. Navbar remains hidden

### Onboarding Completion
1. User completes onboarding
2. Backend updates: `onboarding_completed: true`
3. Backend updates: `current_learning_phase: "learning"`
4. Status updated: `navigation.show_navbar: true`
5. Redirect to `/dashboard`
6. Navbar now visible

### Protected Route Access
1. User attempts to access `/dashboard` before onboarding
2. OnboardingGuard fetches status
3. `onboarding_completed: false` detected
4. Redirect to `/assessment` or `/onboarding`
5. Access denied until completion

### Returning User
1. User logs in
2. AuthContext fetches status
3. `onboarding_completed: true` detected
4. Redirect to `/dashboard`
5. Full navbar visible
6. All routes accessible

## Database Schema

### No Migration Required
User model already contains all necessary fields:

```python
# Existing fields in User model
onboarding_completed = db.Column(db.Boolean, default=False)
needs_initial_assessment = db.Column(db.Boolean, default=True)
current_learning_phase = db.Column(db.String(20), default="onboarding")
initial_assessment_id = db.Column(db.Integer)
assessment_taken_at = db.Column(db.DateTime)
```

**Default Values for New Users:**
- `onboarding_completed`: `False`
- `needs_initial_assessment`: `True`
- `current_learning_phase`: `"onboarding"`
- `initial_assessment_id`: `None`

## API Endpoints Configuration

### Updated `src/config/api.js`
```javascript
USER: {
  PROFILE: '/user/profile',
  UPDATE_PROFILE: '/user/profile',
  ACHIEVEMENTS: '/user/achievements',
  STATS: '/user/stats',
  STATUS: '/user/status',  // NEW
  CAN_ACCESS: (routePath) => `/user/can-access/${routePath}`,  // NEW
},
```

## Testing Checklist

### New User Flow
- [ ] Register new user
- [ ] Verify redirect to `/assessment`
- [ ] Confirm navbar hidden
- [ ] Complete assessment
- [ ] Verify redirect to `/assessment-results`
- [ ] Continue to onboarding
- [ ] Complete onboarding
- [ ] Verify redirect to `/dashboard`
- [ ] Confirm navbar now visible

### Protected Route Access
- [ ] Try accessing `/dashboard` before onboarding
- [ ] Verify redirect to assessment
- [ ] Try accessing `/learning-paths` before onboarding
- [ ] Verify redirect to assessment
- [ ] Complete onboarding
- [ ] Verify all routes now accessible

### Navbar Visibility
- [ ] During registration - No navbar
- [ ] During assessment - No navbar
- [ ] During onboarding - No navbar
- [ ] After onboarding - Navbar visible
- [ ] All menu items functional

### Status API
- [ ] GET `/api/user/status` returns correct data
- [ ] Status updates after onboarding completion
- [ ] Status reflects current learning phase
- [ ] Navigation fields correct for each phase

### Direct URL Access
- [ ] Paste `/dashboard` URL when not onboarded
- [ ] Verify redirect to assessment
- [ ] Paste `/assessment` URL when onboarded
- [ ] Verify redirect to dashboard
- [ ] Paste `/onboarding` URL when onboarded
- [ ] Verify redirect to dashboard

### Returning Users
- [ ] Login existing onboarded user
- [ ] Verify redirect to dashboard
- [ ] Confirm navbar visible
- [ ] Login user in assessment phase
- [ ] Verify redirect to assessment
- [ ] Confirm navbar hidden

## Error Handling

### Backend
- Returns 401 if not authenticated
- Returns 404 if user not found
- Graceful handling of missing profile data
- Default values for missing onboarding fields

### Frontend
- Loading state during status fetch
- Error state with retry option
- Fallback to showing navbar on error
- LocalStorage fallback for offline checks

## Performance Considerations

### Caching
- Status cached in AuthContext state
- Refreshed on:
  - Login/Register
  - Route changes (in MainLayout)
  - Manual refresh via `fetchUserStatus()`

### API Calls
- Single status endpoint for all navigation logic
- Avoid multiple API calls per route change
- Status included in auth response where possible

### UX Optimizations
- Loading spinner during status fetch
- Smooth transitions between layouts
- No flash of wrong content
- Optimistic UI updates

## Security Considerations

### Backend
- JWT token required for all status endpoints
- User can only access own status
- Phase validation on route access
- Protection against phase manipulation

### Frontend
- Guards enforce backend rules
- No client-side only protection
- Always verify with backend
- Secure token storage in localStorage

## Future Enhancements

### Phase 2 Features
- [ ] Progress indicators during onboarding
- [ ] Skip assessment option for advanced users
- [ ] Re-assessment after X months
- [ ] Custom onboarding paths per language
- [ ] Admin override for onboarding status

### Analytics
- [ ] Track onboarding completion rate
- [ ] Measure time spent in each phase
- [ ] Identify drop-off points
- [ ] A/B test onboarding flows

### UI Enhancements
- [ ] Animated transitions between phases
- [ ] Progress breadcrumbs
- [ ] Phase completion celebrations
- [ ] Personalized welcome messages

## Troubleshooting

### Navbar Not Showing After Onboarding
1. Check user.onboarding_completed in database
2. Verify status API returning show_navbar: true
3. Check MainLayout state update
4. Clear localStorage and re-login

### Infinite Redirect Loop
1. Check OnboardingGuard logic
2. Verify phase matches route requirements
3. Check status API response structure
4. Ensure proper navigation.redirect_to value

### Status Not Updating
1. Verify fetchUserStatus called after updates
2. Check API response in network tab
3. Verify AuthContext state update
4. Check localStorage sync

### Can't Access Protected Routes
1. Verify onboarding_completed is true
2. Check JWT token validity
3. Verify OnboardingGuard props
4. Check backend route protection

## Files Modified/Created

### Backend
- ✅ `app/api/user_status_routes.py` - NEW
- ✅ `app/__init__.py` - Updated (blueprint registration)
- ✅ `app/models/user.py` - Verified (no changes needed)

### Frontend
- ✅ `src/components/guards/OnboardingGuard.jsx` - NEW
- ✅ `src/layouts/MainLayoutEnhanced.jsx` - NEW
- ✅ `src/context/AuthContext.jsx` - Updated
- ✅ `src/App.jsx` - Updated (routing + guards)
- ✅ `src/config/api.js` - Updated (endpoints)

### Documentation
- ✅ `guides/ONBOARDING_STATUS_IMPLEMENTATION.md` - NEW

## Summary

This implementation provides a robust, user-friendly onboarding flow with:
- ✅ Automatic status tracking at every step
- ✅ Conditional navbar rendering based on progress
- ✅ Protected routes with onboarding enforcement
- ✅ Seamless redirects based on user phase
- ✅ Clean, distraction-free onboarding UX
- ✅ Full navigation after completion
- ✅ Backend-enforced security
- ✅ Frontend guard components
- ✅ Comprehensive error handling
- ✅ Performance optimizations

The system ensures users cannot skip required steps and provides a smooth progression from registration through assessment, onboarding, and into the main learning experience.
