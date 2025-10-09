# 🧪 Initial Assessment - Quick Test Guide

## Prerequisites
1. Backend server running on `http://localhost:5000`
2. Frontend server running on `http://localhost:5173` (or your port)
3. User account registered and logged in

---

## 🎯 Quick Test Steps

### Test 1: Complete Assessment Flow (5-10 minutes)

#### Step 1: Start Assessment
1. Navigate to `/assessment` in browser
2. **Expected**: Assessment page loads with "Loading Assessment..."
3. **Expected**: First question appears with:
   - Question text
   - Telugu hint (if available)
   - Skill area chip (vocabulary, grammar, etc.)
   - Difficulty level chip (beginner, intermediate, advanced)
   - Answer options (multiple choice or text input)

#### Step 2: Answer Questions
1. Select/enter an answer for the first question
2. Click "Next Question"
3. **Expected**: 
   - Progress bar updates (e.g., "Question 2 of 15")
   - Next question appears
   - Previous button becomes enabled
4. Repeat for several questions

#### Step 3: Test Navigation
1. Click "Previous" button
2. **Expected**: Returns to previous question
3. **Expected**: Previous answer is still selected
4. Click "Next" again to continue

#### Step 4: Complete Assessment
1. Answer all questions until the last one
2. **Expected**: "Complete Assessment" button appears (green, with checkmark icon)
3. Click "Complete Assessment"
4. **Expected**: "Submitting..." state shows briefly
5. **Expected**: Redirects to `/assessment-results`

#### Step 5: View Results
**Expected Results Page displays:**
- 🎉 Header: "Assessment Complete!"
- 📊 Overall score as percentage (e.g., "75%")
- 🏆 Proficiency level badge (Beginner/Intermediate/Advanced)
- 📈 Radar chart showing skill breakdown
- 📋 Detailed scores for each skill with progress bars
- 💪 Strengths section (skills with >75% score)
- 📝 Weaknesses section (skills with <50% score)
- 🎯 "View Personalized Learning Paths" button

#### Step 6: Verify Profile Update
1. Navigate to `/profile` or check dashboard
2. **Expected**: Proficiency level updated
3. **Database Check** (optional):
   ```sql
   SELECT proficiency_level, needs_initial_assessment, 
          assessment_taken_at, current_learning_phase 
   FROM users WHERE id = <user_id>;
   ```
   Expected values:
   - `proficiency_level`: "beginner"/"intermediate"/"advanced"
   - `needs_initial_assessment`: 0 (False)
   - `assessment_taken_at`: Recent timestamp
   - `current_learning_phase`: "learning"

---

## 🔍 Detailed Test Cases

### Test Case 1: Multiple Choice Question
**Steps:**
1. Start assessment
2. Find a multiple choice question
3. Select an option
4. **Expected**: Radio button selected, option highlighted
5. Click "Next"
6. **Expected**: Answer submitted, next question loads

**Pass Criteria:** ✅ Selection works, answer submits, progresses to next

---

### Test Case 2: Text Input Question
**Steps:**
1. Continue assessment until text input question
2. Type answer in text area
3. **Expected**: Text appears as typed
4. Click "Next"
5. **Expected**: Answer submitted, next question loads

**Pass Criteria:** ✅ Text input works, answer submits, progresses

---

### Test Case 3: Empty Answer Validation
**Steps:**
1. On any question, don't select/enter an answer
2. Click "Next"
3. **Expected**: Error alert appears: "Please provide an answer before proceeding."
4. Select/enter an answer
5. Click "Next"
6. **Expected**: Error disappears, question submits

**Pass Criteria:** ✅ Validation prevents empty submission

---

### Test Case 4: Progress Tracking
**Steps:**
1. Note the progress indicator at top
2. Answer each question, observe progress
3. **Expected**: 
   - "Question X of Y" updates correctly
   - Progress bar percentage increases
   - Percentage matches question number

**Pass Criteria:** ✅ Progress updates accurately

---

### Test Case 5: Cannot Complete Twice
**Steps:**
1. Complete an assessment
2. Note the `assessment_id` from URL or network tab
3. Try to POST to `/api/assessment/{id}/complete` again
4. **Expected**: Error response: "Assessment is already completed"

**Pass Criteria:** ✅ Prevents duplicate completion

---

### Test Case 6: Results Visualization
**Steps:**
1. View assessment results
2. Check radar chart
3. **Expected**: Chart displays with proper axes and data points
4. Check skill progress bars
5. **Expected**: Bars show correct percentages
6. Check strengths/weaknesses
7. **Expected**: Skills categorized correctly based on scores

**Pass Criteria:** ✅ All visualizations render correctly

---

## 🐛 Error Scenarios to Test

### Scenario 1: Network Error
**Steps:**
1. Start assessment
2. Disconnect internet or stop backend
3. Try to submit answer
4. **Expected**: User-friendly error message appears
5. Reconnect/restart backend
6. Try again
7. **Expected**: Works normally

---

### Scenario 2: Invalid Assessment ID
**API Test:**
```bash
curl -X POST http://localhost:5000/api/assessment/99999/submit-answer \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question_id": "q1", "answer": "A"}'
```
**Expected Response:** 404 error with message "Assessment not found or unauthorized"

---

### Scenario 3: Missing Required Fields
**API Test:**
```bash
curl -X POST http://localhost:5000/api/assessment/{id}/submit-answer \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"answer": "A"}'
```
**Expected Response:** 400 error with message "question_id and answer are required"

---

## 📱 Responsive Design Test

### Desktop (1920x1080)
- [ ] Layout is centered and well-proportioned
- [ ] Charts are readable
- [ ] Cards have proper spacing
- [ ] Navigation buttons are accessible

### Tablet (768x1024)
- [ ] Single column layout on narrow screens
- [ ] Touch targets are large enough
- [ ] Charts scale appropriately

### Mobile (375x667)
- [ ] All content is visible without horizontal scroll
- [ ] Text is readable
- [ ] Buttons are easily tappable
- [ ] Progress bar is visible

---

## 🔧 API Testing with curl

### 1. Generate Assessment
```bash
curl -X POST http://localhost:5000/api/assessment/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assessment_type": "comprehensive"}'
```

### 2. Submit Single Answer
```bash
curl -X POST http://localhost:5000/api/assessment/ASSESSMENT_ID/submit-answer \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question_id": "q_vocab_beginner_1", "answer": "A"}'
```

### 3. Complete Assessment
```bash
curl -X POST http://localhost:5000/api/assessment/ASSESSMENT_ID/complete \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"time_spent_seconds": 300}'
```

### 4. Get History
```bash
curl -X GET http://localhost:5000/api/assessment/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Quick Checklist

Use this for rapid testing:

- [ ] Assessment loads with questions
- [ ] Can select multiple choice answers
- [ ] Can type text answers
- [ ] Previous/Next buttons work
- [ ] Progress bar updates
- [ ] Can complete assessment
- [ ] Results page displays
- [ ] Overall score shows as percentage
- [ ] Proficiency level badge appears
- [ ] Radar chart renders
- [ ] Skill bars show percentages
- [ ] Strengths/weaknesses display
- [ ] User profile updates
- [ ] Can't complete twice
- [ ] Error messages appear for validation
- [ ] Responsive on mobile

---

## 🎯 Success Criteria

### ✅ Feature is Working If:
1. User can start assessment without errors
2. All questions display correctly with proper formatting
3. Answers can be submitted one by one
4. Progress tracking works accurately
5. Assessment can be completed successfully
6. Results page displays all information clearly
7. User profile updates with proficiency level
8. No duplicate completions allowed
9. Error handling works for all edge cases
10. UI is responsive and professional

---

## 🚨 Known Issues to Check

### Issue 1: Question IDs
- Ensure `question_id` field is used consistently (not `id`)
- Backend generates `question_id` field
- Frontend uses `question_id` for submission

### Issue 2: Skill Breakdown Format
- Backend returns nested object: `{vocabulary: {percentage: 75, level: 'strong'}}`
- Frontend expects simple object: `{vocabulary: 75}`
- Formatting handled in complete endpoint

### Issue 3: Field Name Consistency
- `skill_area` (not `skill_focus`)
- `difficulty_level` (not `difficulty`)
- `telugu_hint` (not `question_text_telugu`)

---

## 📞 Debugging Tips

### If questions don't load:
1. Check browser console for errors
2. Check network tab for API response
3. Verify backend is running
4. Check authentication token is valid

### If submission fails:
1. Check network tab for error response
2. Verify `question_id` matches backend format
3. Check answer format (string, not empty)
4. Verify assessment_id is correct

### If results don't display:
1. Check if results passed via navigation state
2. Verify response format matches expected structure
3. Check browser console for rendering errors
4. Verify skill_breakdown is formatted correctly

---

## 🎉 Test Completion

When all tests pass, the feature is **READY FOR PRODUCTION**!

**Next Steps:**
1. ✅ Run all test cases
2. ✅ Fix any issues found
3. ✅ Verify on different browsers
4. ✅ Test with real users
5. ✅ Deploy to production

---

**Happy Testing! 🚀**
