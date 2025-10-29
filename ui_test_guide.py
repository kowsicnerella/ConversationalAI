"""
UI Testing Guide - Manual Steps
Follow these steps in the browser at http://localhost:5174
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║               LANGUAGE LEARNING PLATFORM - UI TEST GUIDE                    ║
╔════════════════════════════════════════════════════════════════════════════╗

Frontend: http://localhost:5174
Backend:  http://127.0.0.1:5000

═══════════════════════════════════════════════════════════════════════════

TEST 1: UI REGISTRATION FLOW ⏳
═══════════════════════════════════════════════════════════════════════════

📋 STEPS:

1. Open browser to: http://localhost:5174
   
2. Navigate to Registration:
   - Click "Register" or "Sign Up" button on landing page
   OR
   - Navigate directly to: http://localhost:5174/register

3. Fill Registration Form:
   ┌─────────────────────────────────────────┐
   │ Username:        uitest1                │
   │ Email:           uitest1@test.com       │
   │ Password:        Test123!               │
   │ Confirm Pass:    Test123!               │
   │ Native Lang:     Telugu                 │
   │ Target Lang:     English                │
   └─────────────────────────────────────────┘

4. Submit the form

5. ✅ EXPECTED RESULTS:
   - Success message appears
   - Redirect to assessment/onboarding page
   - OR redirect to dashboard
   - Token stored in localStorage
   - User created in database

6. ⚠️ CHECK BROWSER CONSOLE:
   - Press F12 to open DevTools
   - Look for any errors
   - Check Network tab for API calls

═══════════════════════════════════════════════════════════════════════════

TEST 2: UI LOGIN FLOW ⏸️
═══════════════════════════════════════════════════════════════════════════

📋 STEPS:

1. If already logged in, logout first
   - Look for logout button
   - OR clear localStorage: localStorage.clear()

2. Navigate to: http://localhost:5174/login

3. Enter Credentials:
   ┌─────────────────────────────────────────┐
   │ Username/Email:  uitest1                │
   │ Password:        Test123!               │
   └─────────────────────────────────────────┘

4. Click Login

5. ✅ EXPECTED RESULTS:
   - Login successful message
   - Redirect to dashboard
   - User info displayed
   - Navigation menu appears

═══════════════════════════════════════════════════════════════════════════

TEST 3: UI ASSESSMENT FLOW ⏸️
═══════════════════════════════════════════════════════════════════════════

📋 STEPS:

1. After login, check if redirected to assessment
   OR
   Navigate to: http://localhost:5174/assessment

2. Read assessment instructions

3. Answer Questions:
   - Answer introduction question
   - Answer daily life question
   - Answer goals question

4. Submit assessment

5. ✅ EXPECTED RESULTS:
   - Assessment completed
   - Results displayed
   - Proficiency level shown
   - Recommended learning paths appear

═══════════════════════════════════════════════════════════════════════════

TEST 4: UI DASHBOARD ⏸️
═══════════════════════════════════════════════════════════════════════════

📋 STEPS:

1. Navigate to: http://localhost:5174/dashboard

2. Verify Dashboard Components:
   □ User welcome message
   □ Current level/XP display
   □ Streak counter
   □ Recent activities
   □ Learning progress
   □ Achievements/badges
   □ Quick stats

3. ✅ EXPECTED RESULTS:
   - All stats display correctly
   - No errors in console
   - Data matches backend

═══════════════════════════════════════════════════════════════════════════

TEST 5: UI LEARNING PATHS ⏸️
═══════════════════════════════════════════════════════════════════════════

📋 STEPS:

1. Find Learning Paths section
   - Check navigation menu
   - Look for "Learning Paths" or "Courses"

2. View Available Paths:
   - Should see list of learning paths
   - Each path shows title, level, description

3. Enroll in a Path:
   - Click "Enroll" or "Start Learning"
   - Confirm enrollment

4. ✅ EXPECTED RESULTS:
   - Enrollment successful
   - Path appears in "My Paths"
   - Can access path activities

═══════════════════════════════════════════════════════════════════════════

TEST 6: UI ACTIVITIES ⏸️
═══════════════════════════════════════════════════════════════════════════

📋 STEPS:

1. Navigate to Activities section

2. View Available Activities:
   - Quiz activities
   - Flashcard activities
   - Writing prompts
   - Role-play scenarios

3. Start an Activity:
   - Click on an activity
   - Complete the activity
   - Submit answers

4. ✅ EXPECTED RESULTS:
   - Activity loads correctly
   - Can submit answers
   - Results/feedback shown
   - Progress updated

═══════════════════════════════════════════════════════════════════════════

TEST 7: UI CHAT INTERFACE ⏸️
═══════════════════════════════════════════════════════════════════════════

📋 STEPS:

1. Find Chat/Tutor section
   - Look for chat icon
   - Check navigation menu

2. Open Chat Interface

3. Send Test Messages:
   Message 1: "Hello!"
   Message 2: "Can you help me learn English?"
   Message 3: "Teach me basic greetings"

4. ✅ EXPECTED RESULTS:
   - Chat interface opens
   - Messages send successfully
   - AI responds with helpful answers
   - Conversation history preserved

═══════════════════════════════════════════════════════════════════════════

DEBUGGING TIPS
═══════════════════════════════════════════════════════════════════════════

If something doesn't work:

1. Open Browser DevTools (F12)
   
2. Check Console Tab:
   - Look for JavaScript errors
   - Note API call failures
   
3. Check Network Tab:
   - Look for failed requests (red)
   - Check request/response data
   - Verify API endpoints
   
4. Check Application Tab:
   - localStorage → look for 'access_token'
   - Session Storage
   
5. Backend Logs:
   - Check terminal running Flask
   - Look for error messages
   - Note which endpoints are called

═══════════════════════════════════════════════════════════════════════════

COMMON ISSUES & SOLUTIONS
═══════════════════════════════════════════════════════════════════════════

Issue: Cannot access page after login
→ Check if onboarding is required
→ Clear localStorage and try again

Issue: API calls fail with 401
→ Token might be expired
→ Logout and login again

Issue: API calls fail with 404
→ Endpoint might not exist
→ Check backend routes

Issue: API calls fail with 500
→ Backend error
→ Check Flask terminal for traceback

Issue: Nothing happens on button click
→ Check console for JavaScript errors
→ Verify event handlers are attached

═══════════════════════════════════════════════════════════════════════════

📝 RECORDING YOUR RESULTS
═══════════════════════════════════════════════════════════════════════════

For each test, note:
- ✅ PASS: Everything works as expected
- ⚠️  PARTIAL: Works but with minor issues
- ❌ FAIL: Does not work

Document any errors:
- Screenshot the error
- Copy error message
- Note which step failed

═══════════════════════════════════════════════════════════════════════════

Good luck with testing! 🚀
The browser is already open at http://localhost:5174
Start with TEST 1: UI REGISTRATION FLOW

═══════════════════════════════════════════════════════════════════════════
""")
