# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for compiling mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    default-mysql-client \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install python dependencies and Gunicorn for production server
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Create a startup script that waits for MySQL to be ready before running migrations
RUN echo '#!/bin/sh\n\
echo "Waiting for MySQL to be ready..."\n\
while ! mysqladmin ping -h "$DB_HOST" --port="$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" --silent 2>/dev/null; do\n\
  echo "MySQL is unavailable - sleeping 3s..."\n\
  sleep 3\n\
done\n\
echo "MySQL is up - running migrations..."\n\
python manage.py migrate --noinput\n\
python manage.py collectstatic --noinput\n\
echo "Starting Gunicorn server..."\n\
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
