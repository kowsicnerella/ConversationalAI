# Role-Playing Scenarios - Implementation Guide

## 🎭 Overview
The Role-Playing Scenarios feature allows users to practice conversational English in realistic situations through interactive AI-powered conversations. Users engage in real-time dialogues where the AI acts as a conversation partner (waiter, doctor, shop assistant, etc.).

---

## ✅ Features Implemented

### 1. **AI-Powered Scenario Generation**
- Creates realistic conversation scenarios based on topic and difficulty level
- Generates setting, roles, goals, and initial dialogue
- Provides suggested responses to help users start
- Includes key vocabulary relevant to the scenario
- All content is AI-generated (no mock data)

### 2. **Interactive Chat Interface**
- Real-time conversation with AI
- Message history with timestamps
- User and AI messages visually distinguished
- Auto-scroll to latest message
- Send messages via Enter key or button

### 3. **Context-Aware AI Responses**
- AI maintains conversation context across turns
- Natural progression toward scenario goal
- Appropriate responses based on user's role
- Signals when conversation goal is achieved

### 4. **Grammar Feedback**
- Real-time grammar correction during conversation
- Errors shown with original → corrected format
- Detailed explanations in English + Telugu
- Non-intrusive feedback (doesn't break conversation flow)

### 5. **Comprehensive Evaluation**
- AI evaluates overall performance at completion
- Scores: Grammar, Fluency, Overall (0-100)
- Goal achievement status
- Strengths and improvements lists
- Vocabulary usage analysis
- Encouragement messages in English + Telugu

### 6. **Points System**
- Base points: 30 for completion
- Quality bonus: 0-20 (based on overall score)
- Turn bonus: 2 points per turn (max 10)
- Total range: 30-60 points

---

## 🏗️ Architecture

### Backend Components

#### 1. **Service Layer** (`app/services/activity_service.py`)

**Method: `generate_role_playing_scenario(user_id, topic, level)`**
- Generates AI-powered conversation scenario
- Supports 8 topics: restaurant, shopping, interview, doctor, hotel, airport, bank, phone
- Returns scenario with setting, roles, goal, initial line, suggested responses, vocabulary

**Method: `generate_conversation_response(user_id, scenario_data, conversation_history, user_message)`**
- Generates contextual AI response in conversation
- Maintains last 10 messages for context
- Provides grammar correction for user's message
- Returns AI response, feedback, and progress status

**Method: `complete_role_play_session(user_id, scenario_data, conversation_history)`**
- Evaluates completed conversation
- Calculates grammar, fluency, and overall scores
- Determines goal achievement
- Awards points to user profile

**Helper: `_save_vocabulary_from_conversation(user_id, text, topic)`**
- Extracts keywords from user's messages
- Saves new vocabulary to VocabularyWord table
- Tracks source as `roleplay_{topic}`

#### 2. **API Routes** (`app/api/activities_routes.py`)

**POST `/api/activities/generate-role-play`**
- Request: `{topic, level}`
- Creates LearningSession with activity_type='roleplay'
- Returns: `{success, session_id, scenario_data, message}`

**POST `/api/activities/conversation`**
- Request: `{session_id, scenario_data, conversation_history, user_message}`
- Updates conversation history with user + AI messages
- Saves history to LearningSession.user_input
- Returns: `{success, response_data, conversation_history, message}`

**POST `/api/activities/complete-roleplay`**
- Request: `{session_id, scenario_data, conversation_history}`
- Completes LearningSession (status, score, points, time)
- Awards points to user profile
- Returns: `{success, evaluation, message}`

### Frontend Components

#### 1. **RolePlayActivity Component** (`RolePlayActivity.jsx`)

**Features:**
- Scenario header with setting, roles, and goal
- Real-time chat interface (scrollable messages)
- Message input with send button
- Grammar feedback dialog (on errors)
- Evaluation dialog (on completion)
- Suggested responses (initial guidance)

**States:**
- `scenarioData`: Scenario setup from AI
- `conversationHistory`: Array of messages {role, content, timestamp}
- `userMessage`: Current message being typed
- `evaluation`: Final evaluation results
- `showGrammarFeedback`: Grammar correction data

**Key Functions:**
- `loadScenario()`: Fetches scenario from API
- `handleSendMessage()`: Sends user message and gets AI response
- `handleCompleteScenario()`: Finishes conversation and gets evaluation
- `scrollToBottom()`: Auto-scrolls to latest message

#### 2. **ActivitiesHub Integration**

**Activity Card:**
```javascript
{
  id: 'roleplay',
  title: 'Role-Play Scenarios',
  title_telugu: 'రోల్-ప్లే దృశ్యాలు',
  description: 'Practice real conversations in realistic situations',
  description_telugu: 'వాస్తవ పరిస్థితులలో నిజమైన సంభాషణలను ప్రాక్టీస్ చేయండి',
  icon: RolePlayIcon,
  color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  points: '30-60 points',
  duration: '5-15 min'
}
```

---

## 📊 Example Flow

### **Scenario: Order at Restaurant**

**1. User Action:**
- Selects "Role-Play" from Activities Hub
- Chooses topic "restaurant", level "beginner"
- Clicks "Start Activity"

**2. AI Generates Scenario:**
```json
{
  "title": "Order at a Restaurant",
  "title_telugu": "రెస్టారెంట్లో ఆర్డర్ చేయండి",
  "setting": "You are at a local restaurant.",
  "setting_telugu": "మీరు స్థానిక రెస్టారెంట్లో ఉన్నారు.",
  "user_role": "Customer",
  "user_role_telugu": "కస్టమర్",
  "ai_role": "Waiter",
  "ai_role_telugu": "వెయిటర్",
  "user_goal": "Order food and drinks.",
  "user_goal_telugu": "ఆహారం మరియు పానీయాలు ఆర్డర్ చేయండి.",
  "initial_line": "Good evening! Welcome to our restaurant. May I take your order?",
  "suggested_responses": [
    "I want chicken biryani please",
    "Can I see the menu?",
    "What do you recommend?"
  ],
  "key_vocabulary": [
    {"english": "order", "telugu": "ఆర్డర్"},
    {"english": "menu", "telugu": "మెను"},
    {"english": "bill", "telugu": "బిల్లు"}
  ]
}
```

**3. Conversation:**

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | AI | "Good evening! Welcome to our restaurant. May I take your order?" |
| 2 | User | "I want chicken biryani please" |
| 3 | AI | "Great choice! Would you like anything to drink with that?" |
| 4 | User | "Yes, one water bottle" |
| 5 | AI | "Perfect! One chicken biryani and one water bottle. Anything else?" |
| 6 | User | "No, that's all" |
| 7 | AI | "Excellent! Your order will be ready in 15 minutes. Thank you!" |

**4. Grammar Feedback (if errors):**
If user writes: "I want two biryani please"
```json
{
  "has_errors": true,
  "corrected_version": "I want two biryanis please",
  "errors": [
    {
      "original": "two biryani",
      "correction": "two biryanis",
      "explanation": "Plural form needed after number 'two'",
      "explanation_telugu": "'two' తర్వాత బహువచన రూపం అవసరం"
    }
  ]
}
```

**5. Evaluation:**
```json
{
  "goal_achieved": true,
  "conversation_quality": "good",
  "strengths": [
    "Clear and polite requests",
    "Appropriate responses to questions",
    "Good use of restaurant vocabulary"
  ],
  "improvements": [
    "Practice plural forms with numbers",
    "Try using more varied expressions"
  ],
  "vocabulary_used": ["chicken", "biryani", "water", "bottle", "order"],
  "grammar_score": 80,
  "fluency_score": 85,
  "overall_score": 82,
  "num_turns": 4,
  "points_earned": 46,
  "encouragement": "Great job! You successfully ordered at the restaurant!",
  "encouragement_telugu": "అద్భుతం! మీరు రెస్టారెంట్లో విజయవంతంగా ఆర్డర్ చేసారు!"
}
```

**Points Calculation:**
- Base: 30 points
- Quality bonus: (82/100) * 20 = 16 points
- Turn bonus: 4 turns * 2 = 8 points (capped at 10)
- **Total: 30 + 16 + 8 = 54 points**

---

## 🎯 Supported Topics

| Topic | Scenario Description | Key Vocabulary |
|-------|---------------------|----------------|
| **restaurant** | Ordering food and drinks | menu, order, bill, waiter, chef |
| **shopping** | Buying items at a store | price, discount, size, color, payment |
| **interview** | Job interview conversation | experience, skills, salary, position |
| **doctor** | Medical consultation | symptoms, medicine, appointment, health |
| **hotel** | Checking in/out of hotel | room, reservation, checkout, luggage |
| **airport** | Airport procedures | boarding, gate, luggage, passport |
| **bank** | Banking transactions | account, deposit, withdraw, balance |
| **phone** | Making a phone call | call, message, number, speak |

---

## 💡 Testing Checklist

### Scenario Generation
- [ ] Click Role-Play activity card
- [ ] Select topic (restaurant/shopping/etc.)
- [ ] Select difficulty level
- [ ] Verify scenario displays with:
  - Title (English + Telugu)
  - Setting description
  - User role and AI role
  - Goal statement
  - Initial AI message appears in chat
  - Suggested responses shown

### Conversation Flow
- [ ] Type user message in input field
- [ ] Press Enter or click Send button
- [ ] Verify user message appears in chat (right side, blue bubble)
- [ ] Verify AI response appears (left side, white bubble)
- [ ] Verify conversation scrolls to bottom automatically
- [ ] Send 3-5 messages to build conversation
- [ ] Verify context maintained across turns
- [ ] Verify AI responses are relevant to topic

### Grammar Feedback
- [ ] Type message with intentional error (e.g., "I want two apple")
- [ ] Verify grammar feedback dialog appears
- [ ] Check corrected version displayed
- [ ] Verify errors listed with:
  - Original phrase
  - Correction
  - Explanation (English)
  - Explanation (Telugu)
- [ ] Close feedback dialog
- [ ] Continue conversation

### Completion & Evaluation
- [ ] Click "Complete Scenario" button
- [ ] Verify evaluation dialog displays with:
  - Overall score (percentage)
  - Grammar score
  - Fluency score
  - Number of conversation turns
  - Points earned (30-60 range)
  - Goal achievement status
  - Strengths list (2-3 items)
  - Improvements list (2-3 items)
  - Vocabulary used (chips)
  - Encouragement message (English + Telugu)
- [ ] Click "Finish" button
- [ ] Verify returns to Activities Hub
- [ ] Check points added to user profile

### Edge Cases
- [ ] Try sending empty message → should be disabled
- [ ] Try completing with < 3 messages → button disabled
- [ ] Test with very long messages (200+ chars)
- [ ] Test rapid-fire messages (send quickly)
- [ ] Test network error handling
- [ ] Test AI generation failure (shows error message)

---

## 🔧 Configuration

### AI Prompt Engineering

**Scenario Generation Prompt:**
- Specifies scenario topic and difficulty level
- Requests specific JSON structure
- Emphasizes realistic, practical scenarios
- Requires Telugu translations for all fields
- Includes suggested responses for user guidance

**Conversation Response Prompt:**
- Provides full scenario context
- Includes last 10 messages for context awareness
- Requests natural response as AI's role
- Includes grammar correction in response
- Tracks conversation progress (beginning/middle/end/complete)

**Evaluation Prompt:**
- Analyzes all user messages
- Counts conversation turns
- Evaluates grammar, fluency, overall quality
- Determines goal achievement
- Provides constructive feedback

### Retry Logic
- 3 attempts for AI generation
- Exponential backoff: 1s, 2s, 4s
- Detailed logging for debugging
- Error messages returned if all attempts fail

---

## 📝 Database Schema

### LearningSession (Role-Play)

```python
activity_type = 'roleplay'
topic = 'restaurant'  # or shopping, interview, etc.
level = 'beginner'  # or intermediate, advanced
status = 'completed'
started_at = datetime
completed_at = datetime
time_spent_minutes = 8

activity_data = {
  "title": "Order at a Restaurant",
  "setting": "...",
  "user_role": "Customer",
  "ai_role": "Waiter",
  "user_goal": "...",
  "initial_line": "...",
  ...
}

user_input = [
  {"role": "ai", "content": "...", "timestamp": "..."},
  {"role": "user", "content": "...", "timestamp": "..."},
  {"role": "ai", "content": "...", "timestamp": "..."},
  ...
]

ai_feedback = {
  "goal_achieved": true,
  "conversation_quality": "good",
  "strengths": [...],
  "improvements": [...],
  "grammar_score": 80,
  "fluency_score": 85,
  "overall_score": 82,
  "num_turns": 4,
  "points_earned": 46,
  ...
}

score = 82  # overall_score
points_earned = 46
```

---

## 🚀 API Endpoints Summary

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/api/activities/generate-role-play` | POST | Generate scenario | `{topic, level}` | `{session_id, scenario_data}` |
| `/api/activities/conversation` | POST | Continue conversation | `{session_id, scenario_data, conversation_history, user_message}` | `{response_data, conversation_history}` |
| `/api/activities/complete-roleplay` | POST | Complete & evaluate | `{session_id, scenario_data, conversation_history}` | `{evaluation, points_earned}` |

---

## 📊 Performance Metrics

### Time Investment
- **Setup**: 30 seconds (load scenario)
- **Conversation**: 5-10 minutes (varies by user)
- **Evaluation**: 10 seconds (AI evaluation)
- **Total**: ~5-15 minutes per scenario

### Points Distribution
| Performance | Grammar | Fluency | Turns | Points |
|-------------|---------|---------|-------|--------|
| Excellent | 90-100 | 90-100 | 8+ | 54-60 |
| Good | 75-89 | 75-89 | 5-7 | 45-53 |
| Fair | 60-74 | 60-74 | 3-4 | 38-44 |
| Needs Work | <60 | <60 | 1-2 | 30-37 |

---

## 🎓 Learning Objectives

### Skills Practiced
- **Conversational English**: Real-time dialogue practice
- **Context Understanding**: Following conversation flow
- **Vocabulary Usage**: Topic-specific words
- **Grammar Application**: Correct sentence construction
- **Role Awareness**: Understanding social contexts

### Progression Path
1. **Beginner**: Restaurant, Shopping (simple requests)
2. **Intermediate**: Hotel, Phone (more complex interactions)
3. **Advanced**: Interview, Doctor, Bank (professional/formal conversations)

---

## 🐛 Troubleshooting

### Common Issues

**Issue: Scenario doesn't load**
- **Solution**: Check AI API key in environment
- Verify network connection
- Check backend logs for AI generation errors

**Issue: AI responses are generic**
- **Solution**: Ensure conversation_history is passed correctly
- Check context window (last 10 messages)
- Verify scenario_data contains role information

**Issue: Grammar feedback not showing**
- **Solution**: Check if user message actually has errors
- Verify AI response includes `grammar_correction` field
- Ensure feedback dialog state management works

**Issue: Points not awarded**
- **Solution**: Verify user profile exists
- Check database transaction commits
- Ensure complete_role_play_session runs successfully

---

## 📚 Future Enhancements

### Planned Features
- [ ] **Voice Input**: Speak instead of typing
- [ ] **Voice Output**: AI speaks responses aloud
- [ ] **Branching Scenarios**: Multiple paths based on choices
- [ ] **Cultural Tips**: Context-specific cultural notes
- [ ] **Conversation Templates**: Pre-built conversation starters
- [ ] **Replay Feature**: Review past conversations
- [ ] **Difficulty Progression**: Auto-adjust based on performance
- [ ] **Multi-turn Goals**: Complex scenarios requiring 10+ turns

---

## ✅ Summary

The Role-Playing Scenarios feature provides:
- ✅ **8 realistic scenarios** (restaurant, shopping, interview, etc.)
- ✅ **AI-powered conversations** with context awareness
- ✅ **Real-time grammar feedback** with Telugu explanations
- ✅ **Comprehensive evaluation** (grammar, fluency, overall scores)
- ✅ **Points system** (30-60 points based on performance)
- ✅ **Full conversation logging** for review
- ✅ **100% AI-generated content** (no mock data)
- ✅ **Responsive chat interface** with auto-scroll
- ✅ **Bilingual support** (English + Telugu throughout)

**Time Investment:** 5-15 minutes per scenario  
**Points Range:** 30-60 points  
**Difficulty Levels:** Beginner, Intermediate, Advanced  
**Topics:** 8 practical scenarios

---

**Last Updated:** January 9, 2025  
**Version:** 1.0  
**Status:** ✅ Fully Implemented and Ready for Testing
