# Start from a small official Python image
FROM python:3.13-slim

# All following commands run inside /app in the container
WORKDIR /app

# Install the Python dependencies first (this layer is cached between builds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Don't run as root inside the container
RUN useradd --create-home appuser
USER appuser

# The port our app listens on
EXPOSE 8000

# gunicorn is a production-ready web server for Flask apps.
# "app:app" means: the "app" object inside app.py
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
