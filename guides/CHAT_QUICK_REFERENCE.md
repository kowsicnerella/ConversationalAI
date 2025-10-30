# 🚀 AI Chat Feature - Quick Reference Card

## Start the App

### Backend (Terminal 1)
```bash
cd language-learning-platform
python app.py
# Available at: http://localhost:5000/api/chat
```

### Frontend (Terminal 2)
```bash
cd ConvAI_frontV1
npm run dev
# Available at: http://localhost:5173
```

## Access Chat

1. Open browser: http://localhost:5173
2. Go to `/chat` route
3. Start chatting!

## Key Features

| Feature | How to Use | Location |
|---------|-----------|----------|
| Send Message | Type and press Enter | Chat input box |
| Web Search | Toggle `use_web_search` in send | Message options |
| Chat History | Click menu icon → History | Left sidebar |
| View Insights | Scroll right panel | Memory section |
| Search Results | Auto-displayed after web search | Below message |

## API Endpoints (Quick Ref)

### Create Chat
```
POST /api/chat/conversations
Body: {"title": "...", "topic": "..."}
```

### Send Message
```
POST /api/chat/conversations/1/messages
Body: {"message": "...", "use_web_search": true}
```

### Get History
```
GET /api/chat/conversations/1/messages
```

### Web Search
```
POST /api/chat/web-search
Body: {"query": "..."}
```

## Test It

```bash
# Run full test suite
cd language-learning-platform
python test_chat_features.py
```

## File Structure

```
Frontend:
├── src/pages/Chat.jsx                    # Main page
├── src/context/ChatContext.jsx           # State management
└── src/components/chat/
    ├── ChatHistorySidebar.jsx            # History panel
    ├── MemoryInsights.jsx                # Memory display
    └── WebSearchResults.jsx              # Search results

Backend:
├── app/routes/chat_routes.py             # API endpoints
├── app/services/
│   ├── enhanced_chat_service_v2.py       # Chat logic
│   ├── chat_history_service.py           # History logic
│   ├── vector_db_service.py              # Vector search
│   └── mem0_service.py                   # Memory logic
└── app/models/chat.py                    # Database models
```

## Environment Variables (.env)

```
DATABASE_URL=sqlite:///db.db
SECRET_KEY=your_key
GOOGLE_API_KEY=your_key
FLASK_ENV=development
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Chat not loading | Check backend is running on :5000 |
| Messages not sending | Verify API endpoint in config/api.js |
| Web search not working | Check internet, may be rate-limited |
| Memory insights empty | Mem0 service may not be configured |
| Database error | Run `flask db upgrade` |

## Common Tasks

### Add New Conversation Topic
Edit `enhanced_chat_service_v2.py` SYSTEM_PROMPTS dict

### Change Web Search Provider
Edit `search_web()` method in enhanced_chat_service_v2.py

### Customize Chat UI
Edit `src/pages/Chat.jsx` component

### Add New Analytics
Edit `chat_history_service.py` analytics methods

## Important Files

- `CHAT_FEATURE_COMPLETE.md` - Full documentation
- `CHAT_SETUP_GUIDE.md` - Setup instructions
- `test_chat_features.py` - Test suite
- `.env` - Environment configuration

## Debug Mode

```bash
# Backend
FLASK_ENV=development FLASK_DEBUG=1 python app.py

# Frontend
npm run dev # Already in debug mode
```

Check logs at:
- Backend: Terminal output
- Frontend: Browser DevTools (F12)

---

✅ **Everything is ready to use!**

For detailed info, see `CHAT_SETUP_GUIDE.md`
