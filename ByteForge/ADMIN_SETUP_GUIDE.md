# Admin Panel Setup Guide

## 🎯 Admin Panel Access

**URL**: http://127.0.0.1:8000/admin/

**Credentials**:
- Username: `admin`
- Password: `admin123`

---

## 📊 Available Admin Sections

### 1. **User Accounts & Profiles**
- **Users**: Manage all platform users (Student/Teacher/Parent/Admin)
- **Student Profiles**: Learning preferences, streaks, parent connections
- **Teacher Profiles**: Specializations, verification status
- **Parent Profiles**: Notification preferences

### 2. **Learning Content & Activities**
- **Subjects**: Top-level subjects (Math, Physics, etc.)
- **Topics**: Subject subdivisions with prerequisites
- **Learning Resources**: Videos, PDFs, articles, quizzes
- **Learning Activities**: Student interaction tracking
- **Student Performances**: Academic scores and assessments

### 3. **AI Recommendations & Learning Paths**
- **Recommendations**: AI-generated suggestions with explainability
- **Learning Paths**: Personalized roadmaps
- **Learning Path Steps**: Individual path components
- **Feedback**: User feedback for continuous improvement

### 4. **Assessments & Quizzes**
- **Assessments**: Quiz/test containers
- **Questions**: Individual questions with Bloom's taxonomy
- **Quiz Attempts**: Student assessment tracking
- **Question Responses**: Granular answer analytics

### 5. **Analytics & Gamification**
- **Gamification Profiles**: XP, levels, badges, streaks
- **Badges**: Achievement definitions
- **Audit Logs**: Security and compliance (read-only)
- **Teacher Interventions**: Support action tracking

---

## 🎨 Admin Features

### Custom List Displays
- Sortable columns for easy data management
- Quick filters for common queries
- Search functionality across relevant fields

### Inline Editing
- **Assessments**: Add questions directly within assessment
- **Learning Paths**: Manage steps inline
- **Quiz Attempts**: View responses inline

### Bulk Actions
- Verify teachers/resources in bulk
- Publish assessments
- Mark feedback as reviewed
- Flag suspicious quiz attempts

### Read-Only Protection
- **Audit Logs**: Cannot be edited or deleted (security)
- **Calculated Fields**: Auto-computed values (percentages, success rates)

---

## 🚀 Quick Start: Adding Sample Data

### Step 1: Create Subjects
1. Go to **Learning Content & Activities** → **Subjects**
2. Click **Add Subject**
3. Example:
   - Name: Mathematics
   - Description: Core mathematical concepts
   - Icon: fas fa-calculator
   - Color Code: #3498db

### Step 2: Create Topics
1. Go to **Topics** → **Add Topic**
2. Example:
   - Subject: Mathematics
   - Name: Algebra
   - Difficulty: Beginner
   - Estimated Hours: 10

### Step 3: Create Learning Resources
1. Go to **Learning Resources** → **Add Learning Resource**
2. Example:
   - Topic: Algebra
   - Title: Introduction to Algebra
   - Resource Type: Video Tutorial
   - URL: https://youtube.com/...
   - Difficulty: Easy

### Step 4: Create Users
1. Go to **User Accounts** → **Users** → **Add User**
2. Create a student:
   - Username: student1
   - Role: Student
   - Email: student1@example.com
3. Then create their profile in **Student Profiles**

### Step 5: Create Assessments
1. Go to **Assessments** → **Add Assessment**
2. Add questions inline
3. Publish when ready

---

## 🔍 Key Admin Workflows

### For Testing AI Recommendations

1. **Create Student Profile** with learning preferences
2. **Add Student Performance** records (low scores in specific topics)
3. **Create Learning Activities** (track resource usage)
4. **Generate Recommendations** manually or via AI engine
5. **Track Feedback** to improve recommendations

### For Testing Gamification

1. **Create Student Profile**
2. **Create Gamification Profile** (auto-created via signals later)
3. **Award XP** for activities
4. **Create Badges** for achievements
5. **Track Streaks** via daily activity

### For Testing Assessments

1. **Create Assessment** with questions
2. **Publish Assessment**
3. **Create Quiz Attempt** for a student
4. **Add Question Responses**
5. **Review Performance** and mistakes

---

## 🎓 Admin Panel Best Practices

### Data Entry Order
1. Subjects → Topics → Resources
2. Users → Profiles
3. Assessments → Questions
4. Learning Paths → Steps

### Quality Control
- Use **is_verified** flags for content curation
- Review **suspicious_activity** flags in quiz attempts
- Monitor **audit logs** for security

### Performance Monitoring
- Check **view_count** on resources
- Review **success_rate** on questions
- Track **was_helpful** on recommendations

---

## 🔐 Security Features

### Audit Logging
- All important actions are logged
- IP address and user agent tracking
- Read-only to prevent tampering

### Academic Integrity
- Suspicious activity detection in quiz attempts
- Activity log timestamps for pattern analysis
- Confidence level tracking

### Access Control
- Role-based permissions (configured in views later)
- Parent read-only access (enforced in views)
- Teacher verification system

---

## 📈 Next Steps After Admin Setup

1. **Populate Sample Data** for testing
2. **Build Authentication Views** (login/register)
3. **Create Student Dashboard** with AI recommendations
4. **Implement Recommendation Engine** logic
5. **Design UI/UX** for all user roles

---

## 🎯 For Hackathon Demo

### Recommended Sample Data
- 3-5 Subjects (Math, Physics, Chemistry, etc.)
- 10-15 Topics across subjects
- 20-30 Learning Resources (mix of videos, PDFs, quizzes)
- 5-10 Students with varied profiles
- 2-3 Teachers
- 1-2 Parents
- 10-15 Assessments with questions
- Sample quiz attempts with performance data
- AI-generated recommendations with explanations

This will showcase:
- ✅ Multi-role system
- ✅ Content diversity
- ✅ AI personalization
- ✅ Gamification
- ✅ Academic integrity
- ✅ Parent transparency

---

**Admin panel is ready for data entry and testing!** 🚀
