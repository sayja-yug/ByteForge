# SmartShiksha - AI-Powered Personalized Learning Platform

🎓 A comprehensive AI-powered learning recommendation system with multi-role support, intelligent recommendations, gamification, and advanced analytics.

## ✨ Features

### For Students
- AI-powered personalized recommendations with explanations
- Browse subjects, topics, and learning resources
- **Unified Diagnostic Assessment** to identify initial knowledge gaps
- Interactive quiz system with instant feedback
- Progress tracking with XP and achievements
- Gamification (levels, badges, streaks)
- Learning path generation
- Performance analytics and **Formal Report Cards**

### For Teachers
- AI quiz generator
- **Manual Mark Entry** for offline assessments
- **Formal Report Card generation**
- Class performance analytics
- Student performance tracking
- Struggling student identification
- AI-suggested teaching materials
- Intervention tracking system
- Assessment management

### For Parents
- Children progress monitoring
- **View Formal Report Cards**
- Weekly summary reports
- Early warning alerts
- Notification system (email/SMS)
- Performance insights

### For Admins
- Complete platform management
- System analytics dashboard
- User management
- Content moderation
- Audit logging

## 🚀 Quick Start

### Prerequisites
- Python 3.14+
- pip
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/sayja-yug/ByteForge.git
cd ByteForge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install django

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Generate sample data
python manage.py generate_sample_data

# Run development server
python manage.py runserver
```

### Access Points
- **Main Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Browse Subjects**: http://127.0.0.1:8000/learning/subjects/

### Demo Accounts
- **Student**: demo_student / demo123
- **Teacher**: demo_teacher / demo123
- **Admin**: admin / admin123

## 📊 Technology Stack

- **Backend**: Django 6.0, Python 3.14
- **Database**: SQLite (PostgreSQL for production)
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **AI Engine**: Rule-based recommendation system

## 🏗️ Architecture

### Database Models (23 Total)

- **accounts** (4): User, StudentProfile, TeacherProfile, ParentProfile
- **learning** (5): Subject, Topic, LearningResource, LearningActivity, StudentPerformance
- **recommendations** (4): Recommendation, LearningPath, LearningPathStep, Feedback
- **assessments** (4): Assessment, Question, QuizAttempt, QuestionResponse
- **analytics** (6): GamificationProfile, Badge, AuditLog, TeacherIntervention, TeacherMark, ReportCard

## 🎯 Key Innovations

1. **Explainable AI** - Every recommendation shows WHY with data points
2. **Multi-dimensional Personalization** - Combines performance + learning style + behavior
3. **Gamification** - XP, badges, streaks for engagement
4. **Parent Transparency** - Non-intrusive monitoring with alerts
5. **Teacher Support** - Automated analytics and intervention tracking

## 📚 Documentation

See [DOCUMENTATION.md](DOCUMENTATION.md) for complete documentation including:
- Feature details
- User guides
- API reference
- Deployment guide

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

Built with ❤️ for personalized education

---

**Ready to transform education with AI!** 🚀
