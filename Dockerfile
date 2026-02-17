FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . /app/

# Create directory for static files and media
RUN mkdir -p /app/staticfiles /app/media /app/data

# Expose port
EXPOSE 8000

# Run server using Gunicorn
CMD ["gunicorn", "done_dusted.wsgi:application", "--bind", "0.0.0.0:8000"]
