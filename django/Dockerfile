# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock /app/

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# uvicorn worker를 위한 추가 패키지 설치
RUN poetry add uvicorn[standard]

# Install Python dependencies
RUN poetry install --no-interaction --no-ansi

# Copy the Django project
COPY django/ /app/

# Set environment variable for Django settings
ENV DJANGO_SETTINGS_MODULE=a_core.settings.product_asgi

# Create directory for static files
RUN mkdir -p /app/static

# Run migrations and collect static files
RUN python manage.py makemigrations --noinput --settings=a_core.settings.product_asgi && \
    python manage.py migrate --noinput --settings=a_core.settings.product_asgi && \
    python manage.py collectstatic --noinput --settings=a_core.settings.product_asgi

# Expose port 8000
EXPOSE 8000

# Define the default command to run the application
CMD ["gunicorn", "a_core.asgi:application", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--worker-connections", "1000", \
     "--timeout", "300", \
     "--bind", "0.0.0.0:8000", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50"] 