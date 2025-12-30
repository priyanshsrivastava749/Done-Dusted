# Done-Dusted

Done-Dusted is a Django-based application for managing notes and educational video content. This project allows users to organize subjects, chapters, and topics, linking them with relevant video resources and personal notes.

## Features
- **Subject & Chapter Management**: Organize educational content hierarchically.
- **Video Integration**: Link and manage YouTube videos for topics.
- **Note Taking**: Rich text support for creating and saving notes locally.
- **Simulation Hub**: Interactive physics simulations.

## Prerequisites
Before you begin, ensure you have the following installed on your system:
- **Python 3.8+**
- **Git**

## Installation

Follow these steps to set up the project locally.

### 1. Clone the Repository
Open your terminal or command prompt and run:
```bash
git clone https://github.com/priyanshsrivastava749/Done-Dusted.git
cd Done-Dusted
```

### 2. Create and Activate Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Database Setup
Apply the database migrations to set up the database schema:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)
To access the Django admin panel, creating a superuser is recommended:
```bash
python manage.py createsuperuser
```
Follow the prompts to set a username, email, and password.

### 6. Run the Development Server
Start the server to use the application:
```bash
python manage.py runserver
```

Once the server is running, open your browser and access the application at:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

To access the Admin Panel, go to:
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Troubleshooting
- **Port already in use**: If port 8000 is taken, run on a different port:
  ```bash
  python manage.py runserver 8080
  ```
- **Virtual Environment**: Ensure your virtual environment is activated (you should see `(venv)` in your terminal prompt) before running `pip install` or `python manage.py` commands.

## Contributing
1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.
