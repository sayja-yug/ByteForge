# SmartShiksha - AI-Powered Learning Platform - Complete Documentation

## 🎓 System Overview

A comprehensive AI-powered personalized learning recommendation system with multi-role support, intelligent recommendations, gamification, and advanced analytics.

---

## 📚 Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [User Guides](#user-guides)
5. [API Reference](#api-reference)
6. [Deployment](#deployment)

---

## ✨ Features

### For Students
- ✅ AI-powered personalized recommendations with explanations
- ✅ Browse subjects, topics, and learning resources
- ✅ Interactive quiz system with instant feedback
- ✅ Progress tracking with XP and achievements
- ✅ Gamification (levels, badges, streaks)
- ✅ Learning path generation
- ✅ Performance analytics

### For Teachers
- ✅ AI quiz generator
- ✅ Class performance analytics
- ✅ Student performance heatmaps
- ✅ Struggling student identification
- ✅ AI-suggested teaching materials
- ✅ Intervention tracking system
- ✅ Assessment management

### For Parents
- ✅ Children progress monitoring
- ✅ Weekly summary reports
- ✅ Early warning alerts
- ✅ Notification system (email/SMS)
- ✅ Performance insights

### For Admins
- ✅ Complete platform management
- ✅ System analytics dashboard
- ✅ User management
- ✅ Content moderation
- ✅ Audit logging

---

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 6.0, Python 3.14
- **Database**: SQLite (PostgreSQL for production)
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **AI Engine**: Rule-based recommendation system

### Database Models (20 Total)

**accounts** (4 models):
- User (custom user model)
- StudentProfile
- TeacherProfile
- ParentProfile

**learning** (5 models):
- Subject
- Topic
- LearningResource
- LearningActivity
- StudentPerformance

**recommendations** (4 models):
- Recommendation
- LearningPath
- LearningPathStep
- Feedback

**assessments** (4 models):
- Assessment
- Question
- QuizAttempt
- QuestionResponse

**analytics** (4 models):
- GamificationProfile
- Badge
- AuditLog
- TeacherIntervention

---

## 🚀 Installation

### Prerequisites
- Python 3.14+
- pip
- Virtual environment (recommended)

### Setup Steps

```bash
# 1. Clone the repository
cd byteforge

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install django

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Generate sample data
python manage.py generate_sample_data

# 7. Run development server
python manage.py runserver
```

### Access Points
- **Main Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Browse Subjects**: http://127.0.0.1:8000/learning/subjects/

---

## 👥 User Guides

### Student Guide

**Getting Started**:
1. Register at `/accounts/register/student/`
2. Complete your profile with learning preferences
3. Browse subjects and topics
4. Start learning and earn XP

**Taking Quizzes**:
1. Navigate to a topic
2. Click on a quiz resource
3. Answer all questions
4. Submit to see results and earn XP

**Viewing Recommendations**:
1. Go to your dashboard
2. See AI recommendations with explanations
3. Click "Why this recommendation?" to see reasoning
4. Follow suggested learning paths

### Teacher Guide

**Generating Quizzes**:
1. Navigate to a topic
2. Click "Generate Quiz" (or use admin panel)
3. Select difficulty and number of questions
4. Review generated quiz in admin panel
5. Publish when ready

**Viewing Class Analytics**:
1. Go to teacher dashboard
2. See class average and struggling students
3. Review recent quiz attempts
4. Access AI-suggested teaching materials

**Creating Interventions**:
1. Identify struggling students
2. Log intervention in admin panel
3. Track effectiveness over time

### Parent Guide

**Monitoring Children**:
1. Login to parent dashboard
2. View each child's performance
3. Check alerts for issues
4. Review weekly summaries

**Setting Notifications**:
1. Go to profile settings
2. Choose email/SMS preferences
3. Set notification frequency

---

## 🔧 API Reference

### AI Recommendation Engine

```python
from apps.recommendations.services import RecommendationEngine

# Generate recommendations
engine = RecommendationEngine(student_profile)
recommendations = engine.generate_all_recommendations()

# Generate learning path
path = engine.generate_learning_path('Mathematics', 'Master algebra')
```

### Quiz Generator

```python
from apps.assessments.services import QuizGenerator

# Generate quiz
generator = QuizGenerator(topic, difficulty='medium', num_questions=10)
assessment = generator.generate_assessment(teacher_profile)
```

### Notification System

```python
from apps.analytics.notifications import NotificationService

# Send weekly summary
NotificationService.send_parent_weekly_summary(parent_profile)

# Send low score alert
NotificationService.send_low_score_alert(student_profile, topic, score)
```

---

## 🌐 Deployment

### Production Checklist

**Environment**:
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set secure `SECRET_KEY`
- [ ] Use PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Set up Celery for background tasks

**Security**:
- [ ] Enable HTTPS
- [ ] Configure CSRF settings
- [ ] Set up CORS if needed
- [ ] Implement rate limiting
- [ ] Configure file upload limits

**Performance**:
- [ ] Collect static files
- [ ] Configure CDN
- [ ] Enable database indexing
- [ ] Set up caching
- [ ] Optimize queries

**Monitoring**:
- [ ] Set up error tracking (Sentry)
- [ ] Configure logging
- [ ] Set up analytics
- [ ] Monitor performance

### Deployment Commands

```bash
# Collect static files
python manage.py collectstatic

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run with Gunicorn
gunicorn config.wsgi:application
```

---

## 📊 System Features

### AI Recommendation Logic

**Weak Topic Detection**:
- Analyzes performance < 60%
- Matches resources to learning style
- Prioritizes by severity

**Learning Style Matching**:
- Visual → Videos, Interactive demos
- Reading → Articles, PDFs
- Practice → Quizzes, Projects

**Revision Reminders**:
- Identifies topics studied > 7 days ago
- Suggests spaced repetition

**Practice Recommendations**:
- Targets quiz scores < 70%
- Recommends adaptive practice

### Gamification System

**XP Rewards**:
- Complete resource: 10 XP
- Complete quiz: 1 XP per 10% score
- Daily login: 5 XP
- Streak milestones: Bonus XP

**Levels**:
- 100 XP per level
- Unlocks badges and achievements

**Badges**:
- First Quiz (10 XP)
- 7 Day Streak (50 XP)
- Topic Master (100 XP)
- Level milestones

---

## 🔐 Security Features

- Role-based access control
- Audit logging (read-only)
- Academic integrity monitoring
- Password validation
- CSRF protection
- SQL injection prevention

---

## 📞 Support

For issues or questions:
- Check documentation
- Review code comments
- Contact development team

---

**Built with ❤️ for personalized education**
