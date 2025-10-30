# AI Chat Feature - Complete Setup & Running Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- SQLite/PostgreSQL
- Optional: Weaviate (for Vector DB)
- Optional: Mem0 API credentials

### Backend Setup

#### 1. Install Dependencies
```bash
cd language-learning-platform

# Using pip
pip install -r requirements.txt

# OR Using UV (recommended)
uv sync
```

#### 2. Configure Environment Variables
Create a `.env` file in the project root:
```
# Database
DATABASE_URL=sqlite:///telugu_english_learning.db
# or for PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost/db_name

# JWT
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# AI/LLM (Google Generative AI)
GOOGLE_API_KEY=your_google_api_key

# Mem0 (Optional - for memory management)
CLUSTER_URL=https://your-cluster.weaviate.network
AUTH_CLIENT_SECRET=your_weaviate_secret

# Flask
FLASK_ENV=development
FLASK_DEBUG=1
```

#### 3. Initialize Database
```bash
# Create tables
flask db upgrade

# Or if first time
flask db init
flask db migrate
flask db upgrade
```

#### 4. Verify Models
```bash
# Check if chat models exist
flask shell
>>> from app.models import ChatConversation, ChatMessage
>>> db.create_all()
>>> exit()
```

#### 5. Start Backend Server
```bash
# Option 1: Direct
python app.py

# Option 2: With Flask CLI
flask run

# Option 3: With Gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Backend will be available at: `http://localhost:5000`

### Frontend Setup

#### 1. Install Dependencies
```bash
cd ConvAI_frontV1
npm install
```

#### 2. Configure API Endpoint
Check `src/config/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
```

#### 3. Start Development Server
```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 📋 Architecture Overview

```
┌─────────────────────────────────────────┐
│     Frontend (React + Vite)             │
│  ┌──────────────────────────────────┐   │
│  │  Chat.jsx (Main Page)            │   │
│  │  ChatContext.jsx (State)         │   │
│  │  ChatHistorySidebar.jsx          │   │
│  │  MemoryInsights.jsx              │   │
│  │  WebSearchResults.jsx            │   │
│  └──────────────────────────────────┘   │
└──────────────────┬──────────────────────┘
                   │ HTTP/REST
                   ▼
┌─────────────────────────────────────────┐
│     Backend (Flask + SQLAlchemy)        │
│  ┌──────────────────────────────────┐   │
│  │  chat_routes.py (Endpoints)      │   │
│  │  enhanced_chat_service_v2.py     │   │
│  │  chat_history_service.py         │   │
│  │  vector_db_service.py            │   │
│  │  mem0_service.py                 │   │
│  └──────────────────────────────────┘   │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
    Database   DuckDuckGo   Vector DB
    (SQLite)   (Web Search) (Weaviate)
                             │
                             ▼
                          Mem0 API
                       (Memory Store)
```

## 🔌 API Endpoints Reference

### Conversations
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/conversations` | Create conversation |
| GET | `/api/chat/conversations` | List conversations |
| GET | `/api/chat/conversations/:id` | Get specific conversation |
| PUT | `/api/chat/conversations/:id` | Update conversation |
| DELETE | `/api/chat/conversations/:id` | Delete conversation |

### Messages
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/conversations/:id/messages` | Send message |
| GET | `/api/chat/conversations/:id/messages` | Get messages |

### Search & Learning
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/web-search` | Web search |
| GET | `/api/chat/user-learning-context` | Learning context |
| GET | `/api/chat/user-memories` | User memories |
| POST | `/api/chat/search-memories` | Search memories |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chat/analytics/conversations/:id` | Analytics |
| GET | `/api/chat/analytics/learning-statistics` | Statistics |
| GET | `/api/chat/analytics/learning-insights` | Insights |

## 🧪 Testing

### Run Comprehensive Tests
```bash
cd language-learning-platform
python test_chat_features.py
```

Output shows:
- ✓ Create Conversation
- ✓ Send Messages (with web search)
- ✓ Get Messages
- ✓ Get Conversations
- ✓ Web Search
- ✓ Learning Context
- ✓ User Memories
- ✓ Analytics
- ✓ Statistics

Results saved to: `chat_test_results.json`

### Manual Testing with cURL

#### Create Conversation
```bash
curl -X POST http://localhost:5000/api/chat/conversations \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "title": "English Grammar",
    "topic": "grammar"
  }'
```

#### Send Message
```bash
curl -X POST http://localhost:5000/api/chat/conversations/1/messages \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "message": "What is present perfect tense?",
    "use_web_search": true,
    "topic": "grammar"
  }'
```

## 🔍 Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'duckduckgo_search'`
```bash
pip install duckduckgo-search
```

**Issue**: `No such table: chat_conversations`
```bash
flask db upgrade
flask shell
>>> from app.models import db; db.create_all()
>>> exit()
```

**Issue**: CORS errors
```python
# Check app/__init__.py has CORS enabled:
from flask_cors import CORS
CORS(app)
```

### Frontend Issues

**Issue**: Chat context undefined
- Ensure `ChatProvider` wraps app in `main.jsx`
- Verify `useChat()` is only called within ChatProvider

**Issue**: Messages not updating
- Check browser console for API errors
- Verify backend is running on port 5000
- Check `src/config/api.js` for correct API URL

**Issue**: Web search not working
- Verify `duckduckgo-search` is installed
- Check internet connection
- May be rate-limited by DuckDuckGo

## 📊 Feature Verification Checklist

- [ ] Backend server running (http://localhost:5000)
- [ ] Frontend server running (http://localhost:5173)
- [ ] Database migrations completed
- [ ] Chat tables exist in database
- [ ] Can create new conversation
- [ ] Can send and receive messages
- [ ] Web search returns results
- [ ] Chat history displays correctly
- [ ] Memory insights visible
- [ ] Analytics show statistics

## 🚀 Production Deployment

### Backend
```bash
# Install gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or use systemd service
sudo systemctl start chat-backend
```

### Frontend
```bash
# Build for production
npm run build

# Serve with production server
npm run preview

# Or deploy to hosting (Vercel, Netlify, etc.)
```

## 📚 Additional Resources

- [Enhanced Chat Service Documentation](../CHAT_FEATURE_COMPLETE.md)
- [Setup Mem0 Integration](../setup_mem0.py)
- [API Test Suite](test_chat_features.py)
- [Database Models](app/models/chat.py)
- [Chat Routes](app/routes/chat_routes.py)

## 🎯 Key Features

✅ Real-time chat messaging
✅ DuckDuckGo web search integration
✅ Mem0 memory management
✅ Vector database semantic search
✅ Chat history tracking
✅ Learning analytics
✅ Conversation export
✅ Multi-topic support
✅ Grammar explanations
✅ Learning insights

## 📞 Support

For help:
1. Check logs: `flask --log-level=DEBUG app.py`
2. Run tests: `python test_chat_features.py`
3. Review environment: verify all `.env` variables
4. Check database: `flask shell`

---

**Version**: 1.0.0
**Status**: ✅ Production Ready
**Last Updated**: October 22, 2025
