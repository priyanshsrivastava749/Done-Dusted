# Done-Dusted 🎯

**Done-Dusted** is a productivity and video tracking application designed to help users manage their study goals, track video progress, and maintain consistency through analytics and streaks. It allows users to create goals, mark videos as completed, and stay focused using a built-in timer.

---

## 🚀 Project Overview

This project helps students and learners:
- **Track Progress**: Monitor completion status of video courses.
- **Set Goals**: Create daily study targets and track hours.
- **Analyze Performance**: View detailed analytics and study streaks.
- **Stay Focused**: Use a built-in focus timer (Pomodoro-style) to log deep work sessions.
- **Smart Notes**: Generate AI-powered notes for videos (integrated with Google Gemini).

---

## 🛠️ Tech Stack

- **Backend**: Django (Python)
- **Database**: SQLite (Default)
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript
- **API Integration**: Google API Client (YouTube/Gemini)

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Python** (v3.8 or higher)
- **pip** (Python package installer)
- **Git** (for version control)

---

## ⚡ Installation Steps

Follow these steps to set up the project locally.

### 1. Clone the Repository
Open your terminal and run:
```bash
git clone <repository-url>
cd Done-Dusted
```

### 2. Create Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
Create a `.env` file in the root directory (where `manage.py` is located) to store sensitive keys:

```ini
# .env file
SECRET_KEY=your_django_secret_key
DEBUG=True
GOOGLE_API_KEY=your_google_api_key
```
> **Note**: You need a Google API Key for video tracking and AI features.

### 5. Database Setup
Initialize the database tables:
```bash
python manage.py migrate
```

(Optional) Create an admin user to access the Django Admin panel:
```bash
python manage.py createsuperuser
```

### 6. Run the Server
Start the local development server:
```bash
python manage.py runserver
```

Open your browser and navigate to:
`http://127.0.0.1:8000/`

---

## 📖 Usage

1. **Dashboard**: Upon logging in, you will see your daily streaks and active goals.
2. **Add Goals/Exams**: Use the "+ New Goal" button to create a new subject or exam to track.
3. **Track Videos**: Go to a subject page and paste a YouTube playlist URL (if supported) or manually add videos.
4. **Mark as Done**: Click the checkbox next to a video to mark it as completed. Your progress bar will update automatically.
5. **Focus Timer**: Use the timer widget at the bottom right to track your study sessions.

---

## 📂 Folder Structure

Here is a quick overview of the main folders:

```
Done-Dusted/
├── core/                 # Main application logic (views, models, urls)
├── done_dusted/          # Project configuration (settings.py, wsgi.py)
├── static/               # Static assets (CSS, JS, Images)
├── templates/            # HTML Templates
├── db.sqlite3            # Database file
├── manage.py             # Django command-line utility
└── requirements.txt      # Project dependencies
```

---

## 🔧 Common Errors & Fixes

**1. `ModuleNotFoundError`**
- **Cause**: Dependencies are not installed or virtual environment is not active.
- **Fix**: Activate venv and run `pip install -r requirements.txt`.

**2. `TemplateSyntaxError`**
- **Cause**: Issues with HTML template tags.
- **Fix**: Check recent changes in `templates/` folder or ensure all `{% block %}` tags are closed.

**3. Database Issues (no tables)**
- **Cause**: Migrations not applied.
- **Fix**: Run `python manage.py migrate`.

---

## 🔮 Future Improvements

- [ ] Add dark mode toggle.
- [ ] Integration with more video platforms.
- [ ] Mobile-responsive app version.
- [ ] Advanced graphical analytics.

---
*Happy Coding!* 🚀
