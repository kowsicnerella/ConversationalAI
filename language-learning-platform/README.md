# 🇮🇳 Telugu-English Learning Platform

A comprehensive AI-powered language learning platform specifically designed for Telugu speakers learning English. Built with Flask, SQLAlchemy, and Google's Gemini AI.

## 🌟 Features

### 🎯 Personalized Learning Journey (NEW!)

**4-Phase Intelligent Learning System:**

1. **Goal Setting & Onboarding**: Set daily time goals and learning focus areas
2. **AI Proficiency Assessment**: Conversational assessment that evaluates English level through natural dialogue
3. **Personalized Dashboard**: Daily streaks, contextual challenges, vocabulary discovery, and adaptive recommendations
4. **Smart Session Management**: AI-powered learning sessions with real-time vocabulary tracking and progress analytics

**Key Personalization Features:**

- **Intelligent Tutoring**: AI adapts conversations based on user proficiency and mistakes
- **Contextual Vocabulary Learning**: Automatically discovers and tracks new words from conversations with Telugu translations
- **Mistake Pattern Analysis**: AI identifies common errors and generates targeted practice activities
- **Daily Challenges**: Personalized conversation starters and activities based on learning goals
- **Adaptive Content**: Difficulty and content type adjust based on assessment results and ongoing performance

### 🤖 AI-Powered Activity Generation

- **Quiz Generation**: Multiple-choice questions with Telugu explanations
- **Flashcards**: English words with Telugu translations
- **Reading Comprehension**: English texts with vocabulary explanations
- **Writing Practice**: Prompts with AI feedback and corrections
- **Role-Playing Scenarios**: Conversational practice in real-world contexts
- **Image Recognition**: Vocabulary learning through camera/uploaded images
- **AI Tutor Chat**: Interactive conversations for practice

### 📊 Advanced Progress Tracking

- **Learning Sessions**: Detailed session tracking with time spent, words learned, and AI-generated summaries
- **Vocabulary Mastery**: Track word discovery, practice frequency, and mastery levels (new → learning → mastered)
- **Proficiency Progression**: Monitor improvement across grammar, vocabulary, fluency, and confidence
- **Goal Achievement**: Daily and weekly goal tracking with streak maintenance
- **Performance Analytics**: Average scores, time spent, improvement trends

### 🎮 Gamification System

- **Badge System**: Earn badges for milestones and achievements
- **Points & Leaderboards**: Compete with other learners
- **Daily Challenges**: Complete activities to maintain streaks
- **Achievement Tracking**: Progress towards learning goals

### 👤 User Management

- **User Registration/Login**: Secure authentication system
- **Profile Management**: Track native language, proficiency level
- **Dashboard**: Comprehensive overview of progress and achievements

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with PostgreSQL/SQLite support
- **AI Integration**: Google Gemini API
- **Cloud Database**: Supabase (optional)
- **Image Processing**: Pillow (PIL)
- **Authentication**: Werkzeug security

## 📁 Project Structure

```
language-learning-platform/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models
│   │   ├── user.py             # User & Profile models
│   │   ├── activity.py         # Activity & UserActivityLog models
│   │   ├── course.py           # LearningPath & Course models
│   │   ├── gamification.py     # Badge & Achievement models
│   │   └── personalization.py  # Personalization models (NEW!)
│   ├── services/               # Business logic
│   │   ├── activity_generator_service.py  # AI activity generation
│   │   ├── progress_service.py           # Progress tracking
│   │   ├── gamification_service.py       # Badges & achievements
│   │   └── personalization_service.py    # Personalization features (NEW!)
│   └── api/                    # REST API endpoints
│       ├── auth_routes.py      # Authentication endpoints
│       ├── user_routes.py      # User management endpoints
│       ├── activity_routes.py  # Activity generation endpoints
│       ├── gamification_routes.py # Gamification endpoints
│       └── personalization_routes.py # Personalization API (NEW!)
├── config.py                   # Configuration settings
├── app.py                      # Application entry point
├── init_db.py                  # Database initialization
├── test_activity_generator.py  # Activity testing script
├── test_personalization.py     # Personalization testing script (NEW!)
├── requirements.txt            # Python dependencies
├── PERSONALIZATION_API.md      # Personalization API documentation (NEW!)
└── .env.example               # Environment variables template
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd language-learning-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration:
# - GEMINI_API_KEY: Your Google Gemini API key
# - SECRET_KEY: A secure secret key for Flask
# - Database configuration (SQLite for development)
```

### 3. Database Setup

```bash
# Initialize database with default data
python init_db.py
```

### 4. Run the Application

```bash
# Start the Flask development server
python app.py
```

The application will be available at `http://localhost:5000`

### 5. Test Activity Generation

```bash
# Test the AI activity generation (without API key)
python test_activity_generator.py

# Test the new personalization features (with running server)
python test_personalization.py
```

## 📚 API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `PUT /api/auth/profile/<user_id>` - Update profile

### User Management

- `GET /api/user/profile/<user_id>` - Get user profile
- `GET /api/user/dashboard/<user_id>` - Get dashboard data
- `POST /api/user/learning-paths` - Create learning path
- `POST /api/user/activity-completion` - Log activity completion

### Activity Generation

- `POST /api/activity/generate/quiz` - Generate quiz
- `POST /api/activity/generate/flashcards` - Generate flashcards
- `POST /api/activity/generate/reading` - Generate reading exercise
- `POST /api/activity/generate/writing-prompt` - Generate writing prompt
- `POST /api/activity/generate/role-play` - Generate role-play scenario
- `POST /api/activity/analyze-image` - Analyze image for vocabulary
- `POST /api/activity/chat` - Chat with AI tutor
- `POST /api/activity/feedback` - Get writing feedback

### Personalization (NEW!)

- `POST /api/personalization/goals` - Set user learning goals
- `POST /api/personalization/assessment/start` - Start proficiency assessment
- `POST /api/personalization/assessment/{id}/respond` - Submit assessment response
- `POST /api/personalization/assessment/{id}/complete` - Complete assessment
- `GET /api/personalization/dashboard` - Get personalized dashboard
- `POST /api/personalization/session/start` - Start learning session
- `POST /api/personalization/session/{id}/end` - End learning session
- `POST /api/personalization/vocabulary/track` - Track vocabulary learning
- `GET /api/personalization/vocabulary` - Get user vocabulary
- `POST /api/personalization/vocabulary/{id}/practice` - Practice vocabulary

**📖 See [PERSONALIZATION_API.md](PERSONALIZATION_API.md) for detailed documentation.**

### Gamification

- `GET /api/gamification/badges/<user_id>` - Get user badges
- `GET /api/gamification/leaderboard` - Get leaderboard
- `POST /api/gamification/check-achievements/<user_id>` - Check achievements

## 🧪 Testing

### Test Activity Generation (Basic Features)

```bash
python test_activity_generator.py
```

### Test Personalization Features (Full 4-Phase Journey)

```bash
# Start the server first
python app.py

# In another terminal, run the comprehensive test
python test_personalization.py
```

**Personalization Test Coverage:**

- ✅ User authentication and goal setting
- ✅ AI-powered proficiency assessment with conversational evaluation
- ✅ Personalized dashboard with streaks, challenges, and vocabulary
- ✅ Learning session management with vocabulary tracking
- ✅ Vocabulary mastery progression and practice recording

### API Testing

Use tools like Postman or curl to test the API endpoints:

```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "telugu_learner", "email": "user@example.com", "password": "password123"}'

# Set learning goals
curl -X POST http://localhost:5000/api/personalization/goals \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"daily_time_goal": 15, "learning_focus": "conversation"}'

# Generate a quiz
curl -X POST http://localhost:5000/api/activity/generate/quiz \
  -H "Content-Type: application/json" \
  -d '{"topic": "English greetings", "level": "beginner"}'
```

## 🔧 Configuration

### Environment Variables

- `GEMINI_API_KEY`: Google Gemini API key for AI generation
- `SECRET_KEY`: Flask secret key for security
- `DATABASE_URL`: Database connection string
- `SUPABASE_URL` & `SUPABASE_KEY`: Supabase configuration (optional)

### Database Configuration

- **Development**: SQLite database (default)
- **Production**: PostgreSQL via Supabase or other providers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, please open an issue on the GitHub repository or contact the development team.

## 🔮 Future Features

- **Voice Recognition**: Practice pronunciation with speech-to-text
- **Mobile App**: React Native or Flutter mobile application
- **Offline Mode**: Download activities for offline learning
- **Social Features**: Connect with other learners, share progress
- **Advanced Analytics**: Detailed learning analytics and recommendations
- **Custom Courses**: User-generated content and courses
