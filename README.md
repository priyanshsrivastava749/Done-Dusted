# 🎯 Done-Dusted

> **"Master Your Study Goals with Precision."**

**Done-Dusted** is your ultimate productivity companion designed to streamline video course tracking and study sessions. Whether you're preparing for exams or mastering a new skill, Done-Dusted keeps you accountable with smart analytics, focus timers, and goal management.

---

## 🚀 Key Features

- **📊 Smart Analytics**: Visualize your daily streaks, study hours, and completion rates.
- **🎯 Goal Management**: Set custom study goals and track progress against deadlines.
- **🎥 Video Tracking**: Seamlessly track video courses (YouTube integration) and mark progress.
- **⏱️ Focus Mode & Persistence**: Built-in Pomodoro-style timer to maximize deep work sessions. Accurately persists across reloads via `localStorage` with a minimize/hide toggle mechanism.
- **📱 True Responsiveness**: An explicitly fixed, scroll-independent Sidebar that collapses smoothly with dedicated toggle buttons for both Desktop and Mobile environments. 
- **📝 AI-Powered Notes**: Generate smart summaries and notes for your videos using Google Gemini.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | ![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white) | Robust Python web framework. |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white) | Lightweight default database. |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white) | Clean, responsive UI. |
| **AI** | ![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=flat&logo=google&logoColor=white) | Intelligent note generation. |

---

## 📋 Prerequisites

To run this project, you need:

- **Python 3.10+**
- **Git**

---

## ⚡ Quick Start

The easiest way to run the application on Windows is to use the provided setup script.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/priyanshsrivastava749/Done-Dusted.git
    cd Done-Dusted
    ```

2.  **Add your API Keys**
    Create a `.env` file in the root directory:
    ```ini
    SECRET_KEY=your_secret_key
    DEBUG=True
    GOOGLE_API_KEY=your_google_api_key
    ```

3.  **Run with the Setup Script**
    ```bash
    .\run_server.bat
    ```
    This script automatically creates a virtual environment, installs the dependencies from `requirements.txt`, applies database migrations, and starts the Django development server on `http://127.0.0.1:8000/`.

> **Note**: Your database and media files are persisted locally on your machine, so your data is safe even between restarts.

---

## 🐢 Manual Setup

If you prefer running it manually:

1.  **Create Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```ini
    SECRET_KEY=your_secret_key
    DEBUG=True
    GOOGLE_API_KEY=your_google_api_key
    ```

4.  **Run Migrations & Server**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

---

## � Project Structure

```
Done-Dusted/
├── core/                 # 🧠 Application Logic (Views, Models, Serializers)
├── done_dusted/          # ⚙️ Project Settings & Config
├── static/               # 🎨 CSS, JS, Images
├── templates/            # 📄 HTML Templates
├── run_server.bat        # 🚀 Windows Auto-Start Script
└── requirements.txt      # 📦 Python Dependencies
```

---

## 🤝 Contributing

Contributions are welcome!
1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
    Made with ❤️ by <b>Priyansh Srivastava</b>
</div>
