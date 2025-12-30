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

Follow these steps to set up the project locally:

1.  **Clone the Repository**
    ```bash
    git clone <repository_url>
    cd Done-Dusted
    ```

2.  **Create a Virtual Environment** (Optional but recommended)
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply Database Migrations**
    ```bash
    python manage.py migrate
    ```

5.  **Run the Development Server**
    ```bash
    python manage.py runserver
    ```
    Access the application at `http://127.0.0.1:8000/`.

## Dependencies
The project relies on the following key Python packages (listed in `requirements.txt`):
- `Django>=4.0`: The core web framework.
- `google-api-python-client`: For interacting with YouTube Data API.
- `requests`: For making HTTP requests.

## Contributing
1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.
