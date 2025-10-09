# ConvAI - Telugu-English Language Learning Platform 🚀

A modern, feature-rich language learning platform built with React, Material-UI, and Framer Motion. This application provides an engaging and interactive experience for learning English through Telugu.

![Platform Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![React](https://img.shields.io/badge/React-18.3.1-blue)
![Material--UI](https://img.shields.io/badge/Material--UI-7.3.2-blue)
![Framer Motion](https://img.shields.io/badge/Framer_Motion-12.23.22-purple)

## ✨ Features

### 🎯 Core Features

- **Adaptive Learning Paths** - Personalized learning journeys from beginner to advanced
- **Interactive Activities** - Quizzes, flashcards, reading comprehension, and more
- **AI Chat Assistant** - Practice conversational skills with AI-powered chat
- **Vocabulary Builder** - 3D flip cards with audio pronunciation
- **Progress Analytics** - Detailed charts and insights on your learning journey
- **Gamification** - Points, achievements, streaks, and global leaderboard

### 🎨 UI/UX Highlights

- **Modern Design** - Glass morphism effects and gradient animations
- **Dark Mode Support** - Toggle between light and dark themes
- **Smooth Animations** - Powered by Framer Motion for fluid interactions
- **Responsive Layout** - Optimized for desktop, tablet, and mobile devices
- **Accessible** - Built with accessibility best practices

### 📚 Learning Activities

1. **Quiz Activities** - Timed quizzes with instant feedback and explanations
2. **Flashcard Studies** - Spaced repetition with flip animations
3. **Reading Comprehension** - Long-form passages with comprehension questions
4. **Writing Practice** - AI-powered feedback on writing exercises
5. **Role-Play Scenarios** - Interactive conversation practice

## 🛠️ Tech Stack

### Frontend Framework

- **React 18.3.1** - Modern React with hooks and functional components
- **React Router 7.9.3** - Client-side routing
- **Vite 6.0.5** - Lightning-fast build tool

### UI Components & Styling

- **Material-UI (MUI) 7.3.2** - Comprehensive component library
- **@emotion/react & @emotion/styled** - CSS-in-JS styling
- **@mui/icons-material** - Icon library

### Animation & Interactions

- **Framer Motion 12.23.22** - Production-ready animation library
- **Custom CSS animations** - Float, gradient, shimmer effects

### Data Visualization

- **Recharts 3.2.1** - Composable chart library
- **Line, Bar, Pie, Radar charts** - For analytics dashboard

### State Management & API

- **React Context API** - Global state management
- **Axios 1.12.2** - HTTP client with interceptors
- **PropTypes** - Runtime type checking

## 📁 Project Structure

```
ConvAI_frontV1/
├── public/                  # Static assets
├── src/
│   ├── assets/             # Images, fonts, icons
│   ├── components/
│   │   └── common/         # Reusable components
│   │       ├── AnimatedButton.jsx
│   │       ├── GlassCard.jsx
│   │       ├── GradientText.jsx
│   │       ├── HoverCard.jsx
│   │       ├── LoadingSpinner.jsx
│   │       ├── PageTransition.jsx
│   │       ├── StatCard.jsx
│   │       ├── FloatingParticles.jsx
│   │       └── TypewriterText.jsx
│   ├── config/
│   │   ├── api.js          # API configuration & endpoints
│   │   └── theme.js        # MUI theme configuration
│   ├── context/
│   │   ├── AuthContext.jsx # Authentication state
│   │   └── ThemeContext.jsx # Theme mode state
│   ├── layouts/
│   │   ├── AuthLayout.jsx  # Layout for auth pages
│   │   └── MainLayout.jsx  # Main app layout with sidebar
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   └── ForgotPassword.jsx
│   │   ├── activities/
│   │   │   ├── QuizActivity.jsx
│   │   │   ├── FlashcardsActivity.jsx
│   │   │   └── ReadingActivity.jsx
│   │   ├── LandingPage.jsx
│   │   ├── Dashboard.jsx
│   │   ├── LearningPaths.jsx
│   │   ├── LearningPathDetail.jsx
│   │   ├── Vocabulary.jsx
│   │   ├── Chat.jsx
│   │   ├── Analytics.jsx
│   │   ├── Leaderboard.jsx
│   │   ├── Profile.jsx
│   │   ├── Settings.jsx
│   │   └── Notifications.jsx
│   ├── App.jsx             # Root component with routes
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
├── .env                    # Environment variables
├── package.json
├── vite.config.js
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd ConvAI_frontV1
```

2. **Install dependencies**

```bash
npm install
```

3. **Configure environment variables**
   Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

4. **Start the development server**

```bash
npm run dev
```

The application will open at `http://localhost:5173` (or another port if 5173 is in use)

### Build for Production

```bash
npm run build
```

The optimized build will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## 🎮 Usage Guide

### Authentication Flow

1. **Landing Page** - Introduction to the platform with features overview
2. **Register** - Create an account with learning goals selection
3. **Login** - Sign in to access your personalized dashboard
4. **Forgot Password** - Reset password via email

### Learning Journey

1. **Dashboard** - View your stats, progress, and recommendations
2. **Learning Paths** - Browse and enroll in structured learning paths
3. **Activities** - Complete quizzes, flashcards, reading exercises
4. **Vocabulary** - Study words with flip cards and audio
5. **Chat** - Practice with AI conversational assistant

### Progress Tracking

- **Analytics** - Detailed charts showing your progress over time
- **Leaderboard** - Compete with learners worldwide
- **Profile** - View achievements, skills, and recent activity
- **Notifications** - Stay updated with your learning milestones

## 🎨 Component Library

### AnimatedButton

Button with hover and tap animations using Framer Motion.

### GlassCard

Card component with glass morphism effect and backdrop blur.

### GradientText

Typography with animated gradient text effect.

### HoverCard

Card that lifts on hover with smooth transition.

### LoadingSpinner

Circular loading indicator with gradient colors.

### PageTransition

Wrapper for page entrance animations.

### StatCard

Dashboard card displaying statistics with icon and color.

### FloatingParticles

Animated particle background effect.

### TypewriterText

Text that types out with cursor animation.

## 🌈 Theme Customization

The platform supports light and dark modes with a custom MUI theme:

```javascript
// Primary Colors
primary: "#667eea";
secondary: "#764ba2";

// Gradients
gradient1: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)";
gradient2: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)";

// Typography
fontFamily: "Inter, system-ui, Avenir, Helvetica, Arial, sans-serif";
headingFont: "Poppins, sans-serif";
```

## 📊 API Integration

The platform connects to a Flask backend API with the following endpoints:

### Authentication

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user

### Learning Content

- `GET /learning-paths` - Get all learning paths
- `GET /learning-paths/:id` - Get path details
- `GET /activities` - Get activities
- `POST /activities/:id/complete` - Mark activity complete

### Progress & Analytics

- `GET /progress` - User progress data
- `GET /analytics` - Learning analytics
- `GET /leaderboard` - Global rankings

### Gamification

- `GET /achievements` - User achievements
- `GET /badges` - Available badges
- `POST /points` - Award points

## 🧪 Testing

```bash
# Run linting
npm run lint

# Run type checking (if using TypeScript)
npm run type-check
```

## 🔧 Configuration Files

### vite.config.js

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: false,
  },
});
```

### eslint.config.js

ESLint configuration for code quality

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Code Style

- Use functional components with hooks
- Follow ESLint configuration
- Use PropTypes for component props
- Keep components focused and reusable
- Write descriptive commit messages

## 🐛 Known Issues

- Some lint warnings for unused imports (to be cleaned up)
- Missing dependency warnings in useEffect hooks (intentional for demo)

## 🚀 Future Enhancements

- [ ] Voice recording for speaking practice
- [ ] Offline mode with service workers
- [ ] Social features (friends, study groups)
- [ ] More activity types (listening exercises, grammar drills)
- [ ] Native mobile app (React Native)
- [ ] Multi-language support
- [ ] Advanced analytics with ML insights

## 📄 License

This project is part of a language learning platform. All rights reserved.

## 👥 Team

Built with ❤️ by the ConvAI team

## 📞 Support

For support, email support@convai.com or join our community Discord.

---

**Happy Learning! 🎓✨**
