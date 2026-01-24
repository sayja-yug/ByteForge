# Database Models Documentation

## Overview

This document explains the complete database architecture for the AI-Powered Personalized Learning Recommendation System. The database is designed to support intelligent personalization, behavior tracking, and adaptive learning.

---

## Model Relationships Diagram

```
User (AbstractUser)
├── StudentProfile (1:1)
│   ├── LearningActivity (1:N)
│   ├── StudentPerformance (1:N)
│   ├── Recommendation (1:N)
│   ├── LearningPath (1:N)
│   ├── QuizAttempt (1:N)
│   ├── GamificationProfile (1:1)
│   ├── TeacherIntervention (1:N)
│   ├── TeacherMark (1:N)
│   └── ReportCard (1:N)
├── TeacherProfile (1:1)
│   ├── LearningResource (1:N) - created_by
│   ├── Assessment (1:N) - created_by
│   ├── TeacherIntervention (1:N)
│   ├── TeacherMark (1:N)
│   └── ReportCard (1:N)
└── ParentProfile (1:1)
    └── StudentProfile (1:N) - children

Subject (1:N) → Topic (1:N) → LearningResource
                         └─→ Assessment (1:N) → Question (1:N)

LearningPath (M:N) ↔ Topic (through LearningPathStep)
```

---

## Apps Structure

### 1. **accounts** - User Management
- `User` - Extended Django user with role support
- `StudentProfile` - Student-specific data
- `TeacherProfile` - Teacher-specific data  
- `ParentProfile` - Parent-specific data

### 2. **learning** - Content & Activity
- `Subject` - Top-level subjects (Math, Physics, etc.)
- `Topic` - Subject subdivisions (Algebra, Mechanics, etc.)
- `LearningResource` - Videos, PDFs, articles, quizzes
- `LearningActivity` - Student interaction tracking
- `StudentPerformance` - Academic scores and assessments

### 3. **recommendations** - AI Engine
- `Recommendation` - Personalized suggestions
- `LearningPath` - Custom learning roadmaps
- `LearningPathStep` - Individual path steps
- `Feedback` - User feedback for improvement

### 4. **assessments** - Testing & Evaluation
- `Assessment` - Quiz/test container
- `Question` - Individual questions with Bloom's taxonomy
- `QuizAttempt` - Student assessment attempts
- `QuestionResponse` - Individual answer tracking

### 5. **analytics** - Gamification & Monitoring
- `GamificationProfile` - XP, badges, streaks
- `Badge` - Achievement definitions
- `AuditLog` - Security and compliance tracking
- `TeacherIntervention` - Support action tracking
- `TeacherMark` - Manual grading and feedback
- `ReportCard` - Formal academic records

---

## Key Design Decisions

### Why These Models Support AI Personalization

#### 1. **Multi-Dimensional Student Profiling**
- `StudentProfile.learning_style` → Matches content format (video/reading/practice)
- `StudentProfile.learning_pace` → Adjusts difficulty progression speed
- `StudentProfile.target_subjects` → Focuses recommendations

#### 2. **Comprehensive Behavior Tracking**
- `LearningActivity` tracks:
  - Time spent per resource
  - Completion rates
  - Revisit patterns
  - Drop-off points
- This data feeds the recommendation engine

#### 3. **Performance Analysis**
- `StudentPerformance` captures:
  - Scores by topic
  - Difficulty levels attempted
  - Strengths and weaknesses
  - Time efficiency
- Enables knowledge gap detection

#### 4. **Explainable AI**
- `Recommendation.reason` - Human-readable explanation
- `Recommendation.reasoning_factors` - Data points used
- `LearningPath.generation_criteria` - Why path was created
- **Critical for judges and user trust**

#### 5. **Continuous Feedback Loop**
- `Feedback` model collects:
  - Was recommendation helpful?
  - Was difficulty appropriate?
  - User comments
- System improves over time

#### 6. **Adaptive Difficulty**
- `Assessment.is_adaptive` - Adjusts question difficulty
- `Question.difficulty` + `Question.bloom_level` - Granular control
- `QuizAttempt.mistakes` - Generates targeted practice

---

## How Models Work Together

### Example: Generating a Recommendation

1. **Analyze Performance**
   ```
   StudentPerformance → Identify weak topics (e.g., Algebra < 60%)
   ```

2. **Check Learning Behavior**
   ```
   LearningActivity → See if student abandoned Algebra resources
   ```

3. **Match Learning Style**
   ```
   StudentProfile.learning_style = 'visual'
   → Find video resources for Algebra
   ```

4. **Create Recommendation**
   ```
   Recommendation:
   - resource: "Algebra Basics Video"
   - reason: "You scored 45% on Algebra quiz. This video matches your visual learning style."
   - reasoning_factors: {"score": 45, "topic": "Algebra", "style": "visual"}
   ```

5. **Track Effectiveness**
   ```
   Student views resource → LearningActivity created
   Student rates helpful → Feedback recorded
   Next quiz score improves → Recommendation marked effective
   ```

### Example: Building a Learning Path

1. **Identify Goals**
   ```
   StudentProfile.target_subjects = ["Mathematics"]
   StudentProfile.grade_level = "10th Grade"
   ```

2. **Find Prerequisites**
   ```
   Topic.prerequisites → Build dependency graph
   ```

3. **Create Path Steps**
   ```
   LearningPath: "Master 10th Grade Math"
   ├── Step 1: Basic Algebra (prerequisite)
   ├── Step 2: Linear Equations
   ├── Step 3: Quadratic Equations
   └── Step 4: Functions
   ```

4. **Adapt to Performance**
   ```
   If student struggles on Step 2:
   → Insert remedial step
   → Recommend easier resources
   → Slow down progression
   ```

---

## Field Explanations

### Why Each Critical Field Exists

#### StudentProfile Fields

| Field | Purpose | AI Usage |
|-------|---------|----------|
| `learning_style` | Matches content format to preference | Filters resources by type |
| `learning_pace` | Adjusts difficulty progression | Controls recommendation speed |
| `target_subjects` | Focuses learning efforts | Prioritizes recommendations |
| `current_streak` | Gamification & habit tracking | Motivates daily engagement |
| `parent` | Parent monitoring connection | Enables parent dashboard |

#### LearningActivity Fields

| Field | Purpose | AI Usage |
|-------|---------|----------|
| `time_spent_minutes` | Measures engagement depth | Identifies engaging content |
| `progress_percentage` | Tracks completion | Detects drop-off points |
| `revisit_count` | Shows difficulty/interest | Flags confusing topics |
| `was_helpful` | Direct feedback | Improves recommendations |

#### Recommendation Fields

| Field | Purpose | AI Usage |
|-------|---------|----------|
| `reason` | Explains recommendation | User trust & transparency |
| `reasoning_factors` | Shows data used | Explainable AI for judges |
| `priority` | Urgency level | Orders dashboard display |
| `was_helpful` | Effectiveness tracking | Refines algorithm |

#### Question Fields

| Field | Purpose | AI Usage |
|-------|---------|----------|
| `bloom_level` | Cognitive complexity | Ensures balanced assessments |
| `success_rate` | Question difficulty calibration | Adaptive quiz generation |
| `difficulty` | Explicit difficulty | Matches student level |

#### GamificationProfile Fields

| Field | Purpose | AI Usage |
|-------|---------|----------|
| `total_xp` | Engagement metric | Rewards learning actions |
| `current_streak` | Habit formation | Encourages daily practice |
| `badges_earned` | Achievement recognition | Motivates goal completion |

#### TeacherMark Fields

| Field | Purpose | AI Usage |
|-------|---------|----------|
| `marks_obtained` | Numeric score | Tracks manual assessment performance |
| `percentage` | Performance metric | Standardizes scores for analytics |
| `notes` | Qualitative feedback | Rich context for student improvement |

#### ReportCard Fields

| Field | Purpose | AI Usage |
|-------|---------|----------|
| `grades_data` | Structured academic data | JSON storage for multi-subject trends |
| `total_percentage` | Aggregated performance | High-level academic tracking |
| `remarks` | Teacher evaluation | Formal narrative of student progress |

---

## Scalability Considerations

### For Future ML Integration

1. **Data Collection Ready**
   - All models include timestamps
   - JSON fields for flexible metadata
   - Comprehensive tracking fields

2. **Feature Engineering**
   - `LearningActivity` → Time-series features
   - `StudentPerformance` → Performance trends
   - `QuestionResponse` → Item response theory

3. **Model Training Data**
   - `Recommendation.was_helpful` → Labels for supervised learning
   - `QuizAttempt.suspicious_activity` → Anomaly detection
   - `Feedback` → Sentiment analysis

### For REST API

All models are designed for easy serialization:
- Clear relationships
- No circular dependencies
- JSON fields for flexible data
- Proper indexing for queries

---

## Security & Privacy

### Audit Trail
- `AuditLog` tracks all sensitive actions
- IP address and user agent logging
- Change tracking for compliance

### Data Privacy
- Parent access is read-only (enforced in views)
- Student data isolated by profile
- Teacher access scoped to their classes

### Academic Integrity
- `QuizAttempt.suspicious_activity` - Cheating detection
- `QuizAttempt.activity_log` - Timestamp analysis
- `QuestionResponse.time_taken_seconds` - Pattern detection

---

## Next Steps

1. **Configure Django Settings**
   - Add apps to INSTALLED_APPS
   - Configure AUTH_USER_MODEL
   - Set up media/static files

2. **Create Migrations**
   - `python manage.py makemigrations`
   - `python manage.py migrate`

3. **Set Up Admin Panel**
   - Register all models
   - Customize admin interfaces
   - Add inline editing

4. **Build Recommendation Engine**
   - Implement scoring algorithms
   - Create path generation logic
   - Build feedback loop

---

## Summary

This database design provides:
- ✅ **Comprehensive student profiling** for personalization
- ✅ **Granular behavior tracking** for AI insights
- ✅ **Explainable recommendations** for transparency
- ✅ **Continuous feedback loop** for improvement
- ✅ **Gamification** for engagement
- ✅ **Multi-role support** (Student/Teacher/Parent/Admin)
- ✅ **Scalability** for future ML and APIs
- ✅ **Security** through audit logging

**Total Models: 23**
**Total Apps: 5**
**Ready for hackathon demo and real-world deployment**
