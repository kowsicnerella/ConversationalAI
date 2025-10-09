# 🚀 ConvAI Frontend - Quick Start Guide

## 📋 Table of Contents

1. [First Time Setup](#first-time-setup)
2. [Running the Application](#running-the-application)
3. [Project Structure](#project-structure)
4. [Common Tasks](#common-tasks)
5. [Troubleshooting](#troubleshooting)
6. [Backend Integration](#backend-integration)

---

## 🎬 First Time Setup

### Prerequisites

Ensure you have the following installed:

- **Node.js**: v16 or higher ([Download](https://nodejs.org/))
- **npm**: Comes with Node.js
- **Git**: For version control ([Download](https://git-scm.com/))

### Installation Steps

1. **Navigate to the project directory**

```bash
cd d:\ConversationalAI\ConvAI_frontV1
```

2. **Install dependencies**

```bash
npm install
```

3. **Create environment file**
   Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

4. **Verify installation**

```bash
npm run dev
```

You should see:

```
VITE v6.3.6  ready in 252 ms
➜  Local:   http://localhost:5173/
```

---

## 🏃 Running the Application

### Development Mode

```bash
npm run dev
```

- Opens at `http://localhost:5173` (or next available port)
- Hot Module Replacement (HMR) enabled
- Changes reflect instantly

### Production Build

```bash
npm run build
```

- Creates optimized build in `dist/` folder
- Minified and tree-shaken
- Ready for deployment

### Preview Production Build

```bash
npm run preview
```

- Test the production build locally
- Runs on `http://localhost:4173`

### Linting

```bash
npm run lint
```

- Checks code quality
- Reports errors and warnings

---

## 📁 Project Structure

### Key Directories

```
src/
├── components/common/     # Reusable UI components
├── config/               # Configuration files
├── context/              # React Context providers
├── layouts/              # Page layouts
├── pages/                # Application pages
│   ├── auth/            # Authentication pages
│   └── activities/      # Activity type pages
├── assets/              # Static assets
├── App.jsx              # Root component
├── main.jsx             # Entry point
└── index.css            # Global styles
```

### Important Files

| File                           | Purpose                               |
| ------------------------------ | ------------------------------------- |
| `src/config/api.js`            | API endpoints and Axios configuration |
| `src/config/theme.js`          | MUI theme customization               |
| `src/context/AuthContext.jsx`  | Authentication state management       |
| `src/context/ThemeContext.jsx` | Dark/Light mode management            |
| `src/App.jsx`                  | Route definitions                     |
| `.env`                         | Environment variables                 |

---

## 🛠️ Common Tasks

### Adding a New Page

1. Create page component in `src/pages/`

```jsx
// src/pages/NewPage.jsx
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";

const NewPage = () => {
  return (
    <PageTransition>
      <GradientText variant="h4">New Page</GradientText>
      {/* Your content */}
    </PageTransition>
  );
};

export default NewPage;
```

2. Add route in `src/App.jsx`

```jsx
import NewPage from "./pages/NewPage";

// Inside protected routes
<Route path="/new-page" element={<NewPage />} />;
```

3. Add to sidebar navigation in `src/layouts/MainLayout.jsx`

```jsx
{
  text: 'New Page',
  icon: <YourIcon />,
  path: '/new-page',
}
```

### Changing Theme Colors

Edit `src/config/theme.js`:

```javascript
palette: {
  primary: {
    main: '#YOUR_COLOR',
  },
  secondary: {
    main: '#YOUR_COLOR',
  },
}
```

### Adding a New API Endpoint

Edit `src/config/api.js`:

```javascript
export const API_ENDPOINTS = {
  // ... existing endpoints
  NEW_ENDPOINT: "/your-endpoint",
};
```

Use in component:

```jsx
import axiosInstance, { API_ENDPOINTS } from "../config/api";

const response = await axiosInstance.get(API_ENDPOINTS.NEW_ENDPOINT);
```

### Creating Custom Animations

Add to `src/index.css`:

```css
@keyframes your-animation {
  0% {
    /* start state */
  }
  100% {
    /* end state */
  }
}

.your-class {
  animation: your-animation 1s ease-in-out;
}
```

Or use Framer Motion:

```jsx
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.5 }}
>
  Content
</motion.div>
```

---

## 🐛 Troubleshooting

### Port Already in Use

**Problem**: "Port 5173 is in use"
**Solution**: Vite automatically finds next available port, or specify custom port:

```bash
# In package.json or vite.config.js
server: {
  port: 3000,
  strictPort: false,
}
```

### Dependencies Not Installing

**Problem**: npm install fails
**Solution**:

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### API Connection Errors

**Problem**: Cannot connect to backend
**Solution**:

1. Check `.env` file has correct `VITE_API_BASE_URL`
2. Ensure backend is running on specified port
3. Check browser console for CORS errors
4. Mock data will display automatically if API fails

### Dark Mode Not Working

**Problem**: Theme toggle doesn't work
**Solution**:

1. Check `ThemeContext` is wrapping App in `main.jsx`
2. Clear browser localStorage:

```javascript
localStorage.removeItem("themeMode");
```

### Build Errors

**Problem**: Production build fails
**Solution**:

```bash
# Check for linting errors
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix

# Check for unused imports
```

### Animations Not Smooth

**Problem**: Laggy animations
**Solution**:

1. Check browser hardware acceleration is enabled
2. Reduce number of animated elements
3. Use `will-change` CSS property sparingly
4. Check browser console for performance warnings

---

## 🔌 Backend Integration

### Environment Setup

1. **Development**

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

2. **Production**

```env
VITE_API_BASE_URL=https://your-api-domain.com/api
```

### API Request Flow

```
Component → axiosInstance → Interceptor → Backend
                ↓
            Add JWT Token
                ↓
            Handle Response
                ↓
         Return Data or Error
```

### Authentication Flow

1. **Login**

```javascript
// User logs in
const response = await axiosInstance.post(API_ENDPOINTS.AUTH.LOGIN, {
  username,
  password,
});

// Token stored in localStorage
localStorage.setItem("token", response.data.access_token);

// AuthContext updates user state
setUser(response.data.user);
```

2. **Authenticated Requests**

```javascript
// Interceptor automatically adds token
config.headers.Authorization = `Bearer ${token}`;
```

3. **Logout**

```javascript
// Clear token
localStorage.removeItem("token");

// Clear user state
setUser(null);
```

### Mock Data Fallback

All pages include mock data that displays if API is unavailable:

```javascript
try {
  const response = await axiosInstance.get(endpoint);
  setData(response.data);
} catch (error) {
  console.error("API error:", error);
  // Fall back to mock data
  setData(mockData);
}
```

### CORS Configuration

Ensure your Flask backend has CORS enabled:

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

## 🎨 Customization Guide

### Changing Logo

Replace files in:

- `public/vite.svg` - Favicon
- `src/assets/` - Logo images

Update in `MainLayout.jsx` and `LandingPage.jsx`

### Modifying Colors

1. Edit `src/config/theme.js` for MUI components
2. Edit CSS variables in `src/index.css` for custom styles
3. Update gradient colors in components

### Adding New Fonts

1. Import in `src/index.css`:

```css
@import url("https://fonts.googleapis.com/css2?family=Your+Font&display=swap");
```

2. Update theme in `src/config/theme.js`:

```javascript
typography: {
  fontFamily: 'Your Font, sans-serif',
}
```

### Customizing Sidebar

Edit `menuItems` array in `src/layouts/MainLayout.jsx`:

```javascript
const menuItems = [
  { text: "Your Item", icon: <Icon />, path: "/path" },
  // Add more items
];
```

---

## 📊 Performance Tips

1. **Code Splitting**: Already implemented with React.lazy
2. **Image Optimization**: Use WebP format, lazy loading
3. **Bundle Analysis**:

```bash
npm run build -- --analyze
```

4. **Lighthouse Audit**: Check Chrome DevTools
5. **Memoization**: Use `useMemo` and `useCallback` for expensive computations

---

## 🚀 Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Netlify

```bash
npm run build
# Upload dist/ folder to Netlify
```

### Traditional Hosting

```bash
npm run build
# Upload contents of dist/ folder to your web server
```

### Environment Variables in Production

Set in your hosting platform dashboard:

- `VITE_API_BASE_URL`

---

## 📚 Additional Resources

- **React Docs**: https://react.dev/
- **MUI Docs**: https://mui.com/
- **Framer Motion**: https://www.framer.com/motion/
- **Vite Docs**: https://vitejs.dev/
- **Recharts**: https://recharts.org/

---

## 💡 Best Practices

1. **Component Organization**: Keep components small and focused
2. **State Management**: Use Context for global state, local state for component-specific
3. **Error Handling**: Always wrap API calls in try-catch
4. **Accessibility**: Use semantic HTML, ARIA labels
5. **Performance**: Avoid unnecessary re-renders with memo/useMemo
6. **Code Style**: Follow ESLint rules, use Prettier for formatting

---

## 🎉 You're All Set!

Your ConvAI frontend is ready to go. Start the development server and begin exploring the features:

```bash
npm run dev
```

Visit `http://localhost:5173` and enjoy your modern, animated language learning platform!

For questions or issues, check the troubleshooting section or refer to the comprehensive documentation in README.md and FEATURES_SUMMARY.md.

**Happy Coding! 🚀✨**
