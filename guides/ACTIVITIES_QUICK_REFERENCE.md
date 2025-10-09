# Activities System - Quick Reference Guide

## 📋 Table of Contents

- [Components](#components)
- [Hooks](#hooks)
- [Services](#services)
- [Utils](#utils)
- [Usage Examples](#usage-examples)

---

## 🧩 Components

### ActivityCard

Displays a single activity card with all relevant information.

```jsx
import ActivityCard from "./components/common/ActivityCard";

<ActivityCard
  activity={{
    id: 1,
    type: "flashcard",
    title: "Daily Vocabulary",
    description: "Practice common English words",
    difficulty: "beginner",
    estimatedTime: 15,
    progress: 60,
    completed: false,
    color: "#1976d2",
    tags: ["vocabulary", "daily"],
  }}
  onClick={() => navigate(`/activities/${activity.id}`)}
  compact={false}
/>;
```

### DifficultyBadge

Displays a difficulty level badge with color coding.

```jsx
import DifficultyBadge from "./components/common/DifficultyBadge";

<DifficultyBadge difficulty="intermediate" size="small" showIcon={true} />;
```

### ActivityStats

Displays activity statistics with progress bars.

```jsx
import ActivityStats from "./components/common/ActivityStats";

<ActivityStats
  stats={{
    averageScore: 85,
    completionRate: 92,
    totalAttempts: 1250,
    averageTimeSpent: 14,
  }}
  showProgress={true}
/>;
```

### LoadingState

Displays a loading spinner with optional message.

```jsx
import LoadingState from "./components/common/LoadingState";

<LoadingState message="Loading activities..." size={60} />;
```

---

## 🪝 Hooks

### useActivities

Manage multiple activities with filtering.

```jsx
import { useActivities } from "./hooks/useActivities";

const MyComponent = () => {
  const {
    activities, // Array of activities
    loading, // Loading state
    error, // Error message
    filters, // Current filters
    fetchActivities, // Fetch with params
    refreshActivities, // Refresh current
    updateFilters, // Update filters
    clearFilters, // Clear all filters
  } = useActivities({
    autoFetch: true,
    filters: { difficulty: "beginner" },
  });

  // Fetch with specific params
  fetchActivities({ type: "quiz" });

  // Update filters
  updateFilters({ difficulty: "intermediate" });
};
```

### useActivity

Manage a single activity.

```jsx
import { useActivity } from "./hooks/useActivities";

const ActivityComponent = ({ activityId }) => {
  const {
    activity, // Activity data
    loading, // Loading state
    error, // Error message
    submitting, // Submission state
    fetchActivity, // Fetch activity
    refreshActivity, // Refresh
    submitActivity, // Submit answers
    startActivity, // Start tracking
    toggleBookmark, // Bookmark toggle
  } = useActivity(activityId, { autoFetch: true });

  // Submit activity
  const handleSubmit = async () => {
    const result = await submitActivity(answers, timeSpent);
    console.log("Score:", result.score);
  };

  // Toggle bookmark
  const handleBookmark = async () => {
    await toggleBookmark(!activity.bookmarked);
  };
};
```

### useActivityGenerator

Generate new activities.

```jsx
import { useActivityGenerator } from "./hooks/useActivities";

const GeneratorComponent = () => {
  const {
    generating, // Generation state
    error, // Error message
    generatedActivity, // Generated activity
    generateActivity, // Generate function
    clearGenerated, // Clear generated
  } = useActivityGenerator();

  const handleGenerate = async () => {
    const activity = await generateActivity({
      activity_type: "flashcard",
      difficulty: "beginner",
      topic: "greetings",
      count: 10,
    });
  };
};
```

### useActivityStatistics

Fetch activity statistics.

```jsx
import { useActivityStatistics } from "./hooks/useActivities";

const StatsComponent = ({ activityId }) => {
  const {
    statistics, // Stats data
    loading, // Loading state
    error, // Error message
    fetchStatistics, // Fetch function
  } = useActivityStatistics(activityId);

  return <ActivityStats stats={statistics} />;
};
```

---

## 🔧 Services

### activityService

Direct API calls for activities.

```javascript
import activityService from "./services/activityService";

// Get activities list
const activities = await activityService.getActivities({
  type: "quiz",
  difficulty: "beginner",
});

// Get single activity
const activity = await activityService.getActivityDetail(activityId);

// Generate activity
const generated = await activityService.generateActivity({
  activity_type: "flashcard",
  difficulty: "intermediate",
  topic: "business",
  count: 20,
});

// Submit activity
const result = await activityService.submitActivity(activityId, {
  answers: [
    { question_id: 1, answer: "A" },
    { question_id: 2, answer: "B" },
  ],
  timeSpent: 300, // seconds
});

// Get recommendations
const recommended = await activityService.getRecommendedActivities(5);

// Toggle bookmark
await activityService.toggleBookmark(activityId, true);

// Get statistics
const stats = await activityService.getActivityStatistics(activityId);

// Get history
const history = await activityService.getActivityHistory({
  page: 1,
  limit: 10,
});
```

---

## 🛠️ Utils

### activityUtils

Helper functions for activity operations.

```javascript
import {
  getActivityIcon,
  getActivityTypeLabel,
  getDifficultyColor,
  formatDuration,
  calculateScore,
  getPerformanceMessage,
  getActivityStatus,
  sortActivities,
  filterActivities,
  getActivityRoute,
} from "./utils/activityUtils";

// Get icon component
const IconComponent = getActivityIcon("flashcard");

// Get type label
const label = getActivityTypeLabel("quiz"); // "Quiz"

// Get difficulty color
const color = getDifficultyColor("beginner"); // "success"

// Format duration
const duration = formatDuration(75); // "1h 15m"

// Calculate score
const score = calculateScore(8, 10); // 80

// Get performance message
const perf = getPerformanceMessage(85);
// { message: "Great Job! 🌟", emoji: "🌟", color: "success", grade: "B" }

// Get activity status
const status = getActivityStatus(activity); // "In Progress"

// Sort activities
const sorted = sortActivities(activities, "difficulty");

// Filter activities
const filtered = filterActivities(activities, {
  search: "vocabulary",
  type: "flashcard",
  difficulty: "beginner",
});

// Get activity route
const route = getActivityRoute("quiz", 123); // "/activities/quiz/123"
```

---

## 💡 Usage Examples

### Example 1: Activities Listing Page

```jsx
import { useActivities } from "./hooks/useActivities";
import ActivityCard from "./components/common/ActivityCard";
import LoadingState from "./components/common/LoadingState";

const ActivitiesPage = () => {
  const { activities, loading, updateFilters } = useActivities();
  const [search, setSearch] = useState("");

  const handleSearch = (e) => {
    setSearch(e.target.value);
    updateFilters({ search: e.target.value });
  };

  if (loading) return <LoadingState />;

  return (
    <div>
      <input
        value={search}
        onChange={handleSearch}
        placeholder="Search activities..."
      />
      <div className="activities-grid">
        {activities.map((activity) => (
          <ActivityCard
            key={activity.id}
            activity={activity}
            onClick={() => navigate(`/activities/${activity.id}`)}
          />
        ))}
      </div>
    </div>
  );
};
```

### Example 2: Activity Detail Page

```jsx
import { useActivity } from "./hooks/useActivities";
import DifficultyBadge from "./components/common/DifficultyBadge";
import ActivityStats from "./components/common/ActivityStats";

const ActivityDetailPage = ({ activityId }) => {
  const { activity, loading, startActivity } = useActivity(activityId);

  const handleStart = async () => {
    await startActivity();
    navigate(`/activities/${activity.type}/${activityId}`);
  };

  if (loading) return <LoadingState />;

  return (
    <div>
      <h1>{activity.title}</h1>
      <DifficultyBadge difficulty={activity.difficulty} />
      <p>{activity.description}</p>
      <ActivityStats stats={activity.statistics} />
      <button onClick={handleStart}>Start Activity</button>
    </div>
  );
};
```

### Example 3: Activity Generator

```jsx
import { useActivityGenerator } from "./hooks/useActivities";

const ActivityGenerator = () => {
  const { generating, generatedActivity, generateActivity } =
    useActivityGenerator();

  const handleGenerate = async () => {
    await generateActivity({
      activity_type: "flashcard",
      difficulty: "beginner",
      topic: "greetings",
      count: 10,
    });
  };

  return (
    <div>
      <button onClick={handleGenerate} disabled={generating}>
        {generating ? "Generating..." : "Generate Activity"}
      </button>
      {generatedActivity && (
        <div>
          <h2>{generatedActivity.title}</h2>
          {/* Display generated activity */}
        </div>
      )}
    </div>
  );
};
```

### Example 4: Submit Activity

```jsx
import { useActivity } from "./hooks/useActivities";

const QuizActivity = ({ activityId }) => {
  const { submitActivity, submitting } = useActivity(activityId);
  const [answers, setAnswers] = useState([]);
  const [startTime] = useState(Date.now());

  const handleSubmit = async () => {
    const timeSpent = Math.floor((Date.now() - startTime) / 1000);
    const result = await submitActivity(answers, timeSpent);

    console.log("Score:", result.score);
    console.log("Feedback:", result.feedback);
  };

  return (
    <div>
      {/* Quiz questions */}
      <button onClick={handleSubmit} disabled={submitting}>
        {submitting ? "Submitting..." : "Submit Answers"}
      </button>
    </div>
  );
};
```

### Example 5: Activity Filtering

```jsx
import { filterActivities, sortActivities } from "./utils/activityUtils";

const FilteredActivities = ({ activities }) => {
  // Apply filters
  const filtered = filterActivities(activities, {
    search: "vocabulary",
    type: "flashcard",
    difficulty: "beginner",
    maxDuration: 30,
  });

  // Sort filtered results
  const sorted = sortActivities(filtered, "difficulty");

  return (
    <div>
      {sorted.map((activity) => (
        <ActivityCard key={activity.id} activity={activity} />
      ))}
    </div>
  );
};
```

---

## 🎯 Best Practices

1. **Always use hooks for state management** - Don't call services directly in components
2. **Handle loading and error states** - Provide good UX feedback
3. **Use ActivityCard component** - Don't recreate activity cards
4. **Leverage utility functions** - Don't duplicate logic
5. **Type validation** - Use PropTypes or TypeScript
6. **Error boundaries** - Wrap activities in error boundaries
7. **Lazy loading** - Use React.lazy for activity components
8. **Memoization** - Use useMemo for expensive computations

---

## 🔗 Related Documentation

- [API Documentation](../language-learning-platform/API_DOCUMENTATION.md)
- [Activities Implementation](./ACTIVITIES_PAGE_IMPLEMENTATION.md)
- [Flashcard Activity Rewrite](./FLASHCARD_ACTIVITY_REWRITE.md)

---

## 🐛 Troubleshooting

### Activities not loading?

- Check network tab for API errors
- Verify JWT token is valid
- Check API_BASE_URL in config

### Mock data showing instead of real data?

- Ensure backend is running
- Check API endpoints match
- Verify authentication

### Filters not working?

- Check filter syntax in updateFilters
- Verify backend supports filter parameters
- Check console for errors

---

## 📞 Support

For issues or questions, please refer to:

- Project README
- API Documentation
- Component documentation
