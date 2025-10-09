# Vocabulary Management - Quick Test Guide

## 🧪 Step-by-Step Testing Instructions

### Prerequisites
- Backend server running: `python app.py`
- Frontend server running: `npm run dev`
- User logged in with valid JWT token

---

## Test 1: Auto-Save from Quiz ✅

**Steps:**
1. Navigate to Activities page
2. Click on Quiz activity
3. Generate a quiz (any topic, any level)
4. Complete the quiz by answering all questions
5. Submit quiz
6. Navigate to Vocabulary page (once created)
7. **Expected:** Words from quiz questions appear in vocabulary list
8. **Verify:** Words have `source_activity = "quiz"` (check in database or API response)

**API Check:**
```bash
GET /api/vocabulary/words
# Should return words from the completed quiz
```

---

## Test 2: Auto-Save from Flashcards ✅

**Steps:**
1. Navigate to Activities page
2. Click on Flashcard activity
3. Generate flashcards
4. Practice the flashcards (flip at least 3 cards)
5. Complete the flashcard session
6. Navigate to Vocabulary page
7. **Expected:** Words from flashcards appear in vocabulary list
8. **Verify:** Words have Telugu translations from flashcard backs

---

## Test 3: Auto-Save from Writing Practice ✅

**Steps:**
1. Navigate to Activities page
2. Click on Writing Practice activity
3. Generate a writing prompt
4. Write a paragraph (use at least 5-10 different English words)
5. Submit writing for evaluation
6. Navigate to Vocabulary page
7. **Expected:** Keywords from your writing appear in vocabulary
8. **Verify:** Words extracted from user text, not from prompt

---

## Test 4: Auto-Save from Role-Playing ✅

**Steps:**
1. Navigate to Activities page
2. Click on Role-Play activity
3. Start a conversation scenario
4. Send at least 3 messages with varied vocabulary
5. Complete the scenario
6. Navigate to Vocabulary page
7. **Expected:** Words from your conversation messages appear
8. **Verify:** Words saved with `source_activity = "roleplay_<topic>"`

---

## Test 5: Vocabulary Statistics ✅

**API Test:**
```bash
GET /api/vocabulary/stats
```

**Expected Response:**
```json
{
  "stats": {
    "total_words": 25,
    "review_needed": 8,
    "mastery_distribution": {
      "learning": 15,
      "familiar": 7,
      "mastered": 3
    },
    "difficulty_distribution": {
      "beginner": 18,
      "intermediate": 5,
      "advanced": 2
    },
    "mastery_percentage": {
      "learning": 60.0,
      "familiar": 28.0,
      "mastered": 12.0
    }
  }
}
```

**Verify:**
- [ ] total_words = sum of all vocabulary words
- [ ] review_needed = words not practiced in 7+ days (excluding mastered)
- [ ] mastery_distribution counts match actual data
- [ ] mastery_percentage adds up to ~100%

---

## Test 6: Search Functionality ✅

**API Tests:**

**Search by English word:**
```bash
GET /api/vocabulary/words?search=hello
# Should return words containing "hello"
```

**Search by Telugu word:**
```bash
GET /api/vocabulary/words?search=హలో
# Should return words with Telugu translation containing "హలో"
```

**Search by definition:**
```bash
GET /api/vocabulary/words?search=greeting
# Should return words with "greeting" in definition
```

**Verify:**
- [ ] Search is case-insensitive
- [ ] Partial matches work
- [ ] Telugu search works
- [ ] Returns empty array if no matches

---

## Test 7: Filter by Difficulty ✅

**API Tests:**
```bash
# Beginner words only
GET /api/vocabulary/words?difficulty=beginner

# Intermediate words only
GET /api/vocabulary/words?difficulty=intermediate

# Advanced words only
GET /api/vocabulary/words?difficulty=advanced
```

**Verify:**
- [ ] Only words with matching difficulty returned
- [ ] Filter works with search combined
- [ ] Empty filter returns all words

---

## Test 8: Filter by Mastery Level ✅

**API Tests:**
```bash
# Learning words only
GET /api/vocabulary/words?mastery_level=learning

# Familiar words only
GET /api/vocabulary/words?mastery_level=familiar

# Mastered words only
GET /api/vocabulary/words?mastery_level=mastered
```

**Verify:**
- [ ] Only words with matching mastery returned
- [ ] Filter works with difficulty filter combined
- [ ] Words cycle through mastery levels correctly

---

## Test 9: Add Word Manually ✅

**API Test:**
```bash
POST /api/vocabulary/words
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "english_word": "amazing",
  "telugu_translation": "అద్భుతమైన",
  "phonetic_spelling": "ə-ˈmeɪ-zɪŋ",
  "definition": "Causing great surprise or wonder",
  "example_sentence": "The view from the mountain was amazing!",
  "difficulty_level": "intermediate"
}
```

**Expected Response:**
```json
{
  "message": "Vocabulary word added successfully",
  "word": {
    "id": 26,
    "english_word": "amazing",
    "telugu_translation": "అద్భుతమైన",
    "difficulty_level": "intermediate",
    "mastery_level": "learning"
  }
}
```

**Verify:**
- [ ] Word created with ID
- [ ] english_word converted to lowercase
- [ ] mastery_level defaults to "learning"
- [ ] created_at timestamp set

**Error Cases:**
```bash
# Missing required field
POST /api/vocabulary/words
{
  "english_word": "test"
  # Missing telugu_translation
}
# Should return 400 error

# Duplicate word
POST /api/vocabulary/words
{
  "english_word": "amazing",  # Already exists
  "telugu_translation": "అద్భుతమైన"
}
# Should return 409 error "Word already exists"
```

---

## Test 10: Update Word ✅

**API Test:**
```bash
PUT /api/vocabulary/words/1
Content-Type: application/json

{
  "telugu_translation": "updated translation",
  "definition": "Updated definition",
  "mastery_level": "familiar"
}
```

**Verify:**
- [ ] Only specified fields updated
- [ ] english_word cannot be changed
- [ ] updated_at timestamp updated
- [ ] Returns updated word data

---

## Test 11: Delete Word ✅

**API Test:**
```bash
DELETE /api/vocabulary/words/1
```

**Expected Response:**
```json
{
  "message": "Vocabulary word deleted successfully",
  "telugu_message": "పదజాలం పదం విజయవంతంగా తొలగించబడింది"
}
```

**Verify:**
- [ ] Word removed from database
- [ ] Subsequent GET returns 404
- [ ] User can only delete their own words

---

## Test 12: Practice Flashcard Generation ✅

**API Test:**
```bash
POST /api/vocabulary/practice-flashcards
Content-Type: application/json

{
  "mastery_level": "learning",
  "difficulty_level": "beginner",
  "review_only": true,
  "num_cards": 10
}
```

**Expected Response:**
```json
{
  "session_id": 45,
  "flashcards": [
    {
      "id": 1,
      "front": "hello",
      "back": "హలో",
      "definition": "A greeting",
      "example": "Hello, how are you?",
      "phonetic": "hə-ˈlō",
      "difficulty": "beginner",
      "mastery_level": "learning",
      "practice_count": 2
    }
    // ... more cards
  ],
  "count": 10
}
```

**Verify:**
- [ ] Returns max 10 flashcards (as requested)
- [ ] All cards match filters (mastery=learning, difficulty=beginner)
- [ ] review_only=true returns only words not practiced in 7+ days
- [ ] Creates LearningSession with session_id
- [ ] session.activity_type = "flashcard"
- [ ] session.topic = "vocabulary_practice"

**Edge Cases:**
```bash
# No words match criteria
POST /api/vocabulary/practice-flashcards
{
  "mastery_level": "mastered",
  "difficulty_level": "advanced",
  "num_cards": 50
}
# Should return 404 if no words match
```

---

## Test 13: Practice Result Logging ✅

**API Test:**
```bash
POST /api/vocabulary/words/1/practice-result
Content-Type: application/json

{
  "is_correct": true,
  "practice_type": "flashcard"
}
```

**Verify:**
- [ ] practice_count incremented by 1
- [ ] correct_count incremented if is_correct=true
- [ ] last_practiced timestamp updated
- [ ] mastery_level updated based on accuracy:
  - practice_count ≥ 3 AND accuracy ≥ 80% → "mastered"
  - practice_count ≥ 3 AND accuracy ≥ 60% → "familiar"
  - else → "learning"

**Example Scenario:**
```
Initial: practice_count=0, correct_count=0, mastery_level="learning"

Practice 1 (correct): practice_count=1, correct_count=1, mastery="learning"
Practice 2 (correct): practice_count=2, correct_count=2, mastery="learning"
Practice 3 (correct): practice_count=3, correct_count=3, mastery="mastered" (100%)
Practice 4 (incorrect): practice_count=4, correct_count=3, mastery="familiar" (75%)
Practice 5 (correct): practice_count=5, correct_count=4, mastery="mastered" (80%)
```

---

## Test 14: Pagination ✅

**API Test:**
```bash
# Page 1 (first 20 words)
GET /api/vocabulary/words?page=1&per_page=20

# Page 2 (next 20 words)
GET /api/vocabulary/words?page=2&per_page=20
```

**Expected Response:**
```json
{
  "words": [...],  // Max 20 words
  "pagination": {
    "page": 1,
    "pages": 3,
    "per_page": 20,
    "total": 45,
    "has_next": true,
    "has_prev": false
  }
}
```

**Verify:**
- [ ] Returns correct number of words (max per_page)
- [ ] pagination.total matches total word count
- [ ] pagination.pages = ceil(total / per_page)
- [ ] has_next=true if more pages exist
- [ ] has_prev=true if not on first page

---

## Test 15: Sorting ✅

**API Tests:**
```bash
# Sort by date (newest first)
GET /api/vocabulary/words?sort_by=created_at&sort_order=desc

# Sort alphabetically
GET /api/vocabulary/words?sort_by=alphabetical&sort_order=asc

# Sort by difficulty
GET /api/vocabulary/words?sort_by=difficulty

# Sort by mastery
GET /api/vocabulary/words?sort_by=mastery
```

**Verify:**
- [ ] sort_order=asc returns ascending order
- [ ] sort_order=desc returns descending order
- [ ] Default sort is created_at desc (newest first)
- [ ] Alphabetical sorts by english_word

---

## Test 16: Combined Filters ✅

**API Test:**
```bash
GET /api/vocabulary/words?search=hello&difficulty=beginner&mastery_level=learning&page=1&sort_by=alphabetical
```

**Verify:**
- [ ] All filters apply simultaneously
- [ ] Search + difficulty + mastery all work together
- [ ] Sorting applies to filtered results
- [ ] Pagination applies to filtered results

---

## Test 17: Review-Needed Detection ✅

**Setup:**
1. Add a word
2. Practice it once
3. Wait (or manually update last_practiced to 8 days ago)
4. Check stats

**API Test:**
```bash
GET /api/vocabulary/stats
```

**Verify:**
- [ ] review_needed count includes words not practiced in 7+ days
- [ ] Mastered words excluded from review_needed
- [ ] Words never practiced included in review_needed

**SQL Query to Verify:**
```sql
SELECT COUNT(*) FROM vocabulary_word
WHERE user_id = <user_id>
AND (last_practiced IS NULL OR last_practiced < NOW() - INTERVAL '7 days')
AND mastery_level != 'mastered';
```

---

## Test 18: Error Handling ✅

**Test Invalid Data:**
```bash
# Empty word
POST /api/vocabulary/words
{"english_word": "", "telugu_translation": "test"}
# Should return 400

# Invalid mastery level
PUT /api/vocabulary/words/1
{"mastery_level": "invalid"}
# Should return 400

# Non-existent word
GET /api/vocabulary/words/99999
# Should return 404

# Unauthorized access
GET /api/vocabulary/words
# Without JWT token - should return 401
```

---

## 🎯 Success Criteria

### All Tests Pass When:
- [x] Auto-save works from all 4 activity types
- [x] CRUD operations work correctly
- [x] Filtering and search return accurate results
- [x] Pagination works properly
- [x] Sorting applies correctly
- [x] Practice flashcards generate from vocabulary
- [x] Mastery levels update automatically
- [x] Statistics calculate correctly
- [x] Error handling returns proper status codes
- [x] Review-needed detection works

---

## 📊 Database Verification

**Query to check vocabulary:**
```sql
SELECT 
  id,
  english_word,
  telugu_translation,
  difficulty_level,
  mastery_level,
  practice_count,
  correct_count,
  source_activity,
  created_at,
  last_practiced
FROM vocabulary_word
WHERE user_id = <user_id>
ORDER BY created_at DESC
LIMIT 10;
```

**Check mastery distribution:**
```sql
SELECT 
  mastery_level,
  COUNT(*) as count
FROM vocabulary_word
WHERE user_id = <user_id>
GROUP BY mastery_level;
```

**Check review needed:**
```sql
SELECT COUNT(*) as review_needed
FROM vocabulary_word
WHERE user_id = <user_id>
AND (last_practiced IS NULL OR last_practiced < NOW() - INTERVAL '7 days')
AND mastery_level != 'mastered';
```

---

**Last Updated:** January 9, 2025  
**Test Coverage:** 18 comprehensive test scenarios  
**Estimated Testing Time:** 45-60 minutes for complete suite
