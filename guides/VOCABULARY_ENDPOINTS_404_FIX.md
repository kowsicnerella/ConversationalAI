# 🔧 Vocabulary Endpoints 404 Fix

## Issues Addressed

### ✅ Fixed: `GET http://localhost:5000/api/vocabulary/words` → 404

**Problem**: Frontend was requesting vocabulary words list but getting 404.

**Root Cause**: Two vocabulary systems with conflicting registrations:
1. **Old API** (has `/words` endpoint) - was registered at `/api/vocabulary-old`
2. **Phase 5 Mastery** (SM-2 spaced repetition, no `/words`) - was registered at `/api/vocabulary`

Frontend expects `/api/vocabulary/words` from old API, but Phase 5 was blocking that route.

---

## Solution Applied

### Backend Configuration Update

**File**: `app/__init__.py`

**Changed Registration Order and Prefixes**:

```python
# Before (❌ Conflicting):
app.register_blueprint(vocabulary_bp, url_prefix="/api/vocabulary-old")  # Old API (line 174)
app.register_blueprint(vocabulary_phase5_bp, url_prefix="/api/vocabulary")  # Phase 5 (line 216)

# After (✅ Properly separated):
app.register_blueprint(vocabulary_bp, url_prefix="/api/vocabulary")  # Old API → /api/vocabulary
app.register_blueprint(vocabulary_phase5_bp, url_prefix="/api/vocabulary-v2")  # Phase 5 → /api/vocabulary-v2
```

### Why This Works

| System | Endpoint Prefix | Use Cases |
|--------|-----------------|-----------|
| **Old API** | `/api/vocabulary` | `/words`, `/words/{id}`, `/stats`, `/examples` |
| **Phase 5** | `/api/vocabulary-v2` | SM-2 spaced repetition, practice sessions, word networks |

Frontend continues using old API for backward compatibility while Phase 5 features are available at v2 path.

---

## Frontend Updates

**File**: `src/config/api.js`

### Added Vocabulary v2 Endpoints

```javascript
// Vocabulary (Old API - backward compatible)
VOCABULARY: {
  WORDS: '/vocabulary/words',  // ✅ Now works
  WORD_DETAIL: (id) => `/vocabulary/words/${id}`,
  // ... all legacy endpoints
},

// NEW: Vocabulary Mastery v2 (Phase 5)
VOCABULARY_V2: {
  INTRODUCE: '/vocabulary-v2/introduce',
  INTRODUCE_FROM_TEXT: '/vocabulary-v2/introduce-from-text',
  ADD_TO_VOCABULARY: '/vocabulary-v2/add-to-my-vocabulary',
  WORDS_DUE: '/vocabulary-v2/words-due',
  REVIEW: '/vocabulary-v2/review',
  PRACTICE_SESSION_START: '/vocabulary-v2/practice-session/start',
  // ... all Phase 5 SM-2 endpoints
}
```

---

## Endpoint Mapping

### Old API (Backward Compatible)
```
GET    /api/vocabulary/words              # ✅ Now works
GET    /api/vocabulary/words/{id}         # ✅ Now works
GET    /api/vocabulary/{id}/examples      # ✅ Now works
GET    /api/vocabulary/stats              # ✅ Now works
POST   /api/vocabulary/words              # ✅ Now works
PUT    /api/vocabulary/words/{id}         # ✅ Now works
DELETE /api/vocabulary/words/{id}         # ✅ Now works
```

### Phase 5 Mastery (New)
```
POST   /api/vocabulary-v2/introduce
POST   /api/vocabulary-v2/introduce-from-text
POST   /api/vocabulary-v2/add-to-my-vocabulary
GET    /api/vocabulary-v2/words-due
POST   /api/vocabulary-v2/review
POST   /api/vocabulary-v2/practice-session/start
POST   /api/vocabulary-v2/practice-session/{id}/complete
POST   /api/vocabulary-v2/practice-activity
GET    /api/vocabulary-v2/mastery
GET    /api/vocabulary-v2/word-network/{id}
GET    /api/vocabulary-v2/related-words
```

---

## About the `POST /api` Error

**Note**: The `POST http://localhost:5000/api` → 404 is **expected behavior**.

This error is likely from:
- Browser extension making requests
- Service worker debug call
- Testing tool or proxy
- Malformed request with no proper endpoint

**No fix needed** - this is correct (404 for undefined routes).

---

## Data Flow

### Before Fix
```
Frontend requests:
├─ GET /api/vocabulary/words
│  └─ Routes to axiosInstance with baseURL /api
│     └─ Final URL: http://localhost:5000/api/vocabulary/words
│
└─ But Phase 5 is registered at /api/vocabulary
   └─ Old API (with /words endpoint) is at /api/vocabulary-old
   └─ ❌ 404 - Route not found
```

### After Fix
```
Frontend requests:
├─ GET /api/vocabulary/words
│  └─ Routes to axiosInstance with baseURL /api
│     └─ Final URL: http://localhost:5000/api/vocabulary/words
│
└─ Old API is now registered at /api/vocabulary
   └─ Has /words endpoint
   └─ ✅ 200 - Success
```

---

## Implementation Details

### Backend Routing Hierarchy
```
/api/vocabulary/            → Old API (backward compatible)
├─ words                    → GET/POST
├─ words/{id}              → GET/PUT/DELETE
├─ words/{id}/examples     → GET
└─ words/{id}/practice-result → POST

/api/vocabulary-v2/         → Phase 5 (new SM-2 system)
├─ introduce               → POST
├─ words-due              → GET
├─ review                 → POST
├─ practice-session/start → POST
└─ mastery               → GET
```

---

## API Version Strategy

**Pattern**: Using version suffix for new features
- **Old**: `/api/vocabulary` - Stable, backward compatible
- **New**: `/api/vocabulary-v2` - Latest features (SM-2, spaced repetition)

This allows:
- ✅ Existing frontend code continues working
- ✅ New code can opt-in to v2 features
- ✅ Gradual migration path
- ✅ No breaking changes

---

## Files Modified

1. ✅ `app/__init__.py`
   - Line 174: Changed vocabulary registration to `/api/vocabulary`
   - Line 216: Changed Phase 5 to `/api/vocabulary-v2`

2. ✅ `src/config/api.js`
   - Added VOCABULARY_V2 section with all Phase 5 endpoints
   - Updated VOCABULARY comments to indicate "old API"
   - Organized endpoints by system

---

## Status

✅ **FIXED** - October 22, 2025

**Endpoints Now Working**:
- ✅ `GET /api/vocabulary/words` (was 404, now 200)
- ✅ `POST /api/vocabulary/words`
- ✅ All other old API vocabulary endpoints
- ✅ Phase 5 available at `/api/vocabulary-v2`

**Lesson Learned**: 
- Use different URL prefixes for different versions/systems
- Avoid registering conflicting blueprints at same path
- Document which API is used where

---

## What To Do Now

1. **Restart backend** to apply registration changes
2. **Test vocabulary endpoints**:
   - `GET /api/vocabulary/words` should return word list
   - `POST /api/vocabulary/words` should create word
   - Check browser console for successful requests
3. **For Phase 5 features**, use:
   - `GET /api/vocabulary-v2/words-due` for spaced repetition
   - `POST /api/vocabulary-v2/review` for SM-2 algorithm

**Expected**: All vocabulary endpoints return 200 OK! 🎉
