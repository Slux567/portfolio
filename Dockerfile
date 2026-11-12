# Small official Python image, pinned by digest so every build uses the exact
# same base image (a tag like "3.13-slim" can change underneath you).
FROM python:3.13-slim@sha256:48d884813cf44e927cf64c5529dd630dd3b18338c6dc727991eef9b71e934a20

# Don't write .pyc files (lets the container run with a read-only filesystem)
# and print logs straight away instead of buffering them.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# All following commands run inside /app in the container
WORKDIR /app

# Install the Python dependencies first (this layer is cached between builds).
# --require-hashes makes pip refuse any package whose hash doesn't match requirements.txt.
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore --require-hashes -r requirements.txt

# Copy only the files the app needs
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Run as a non-root user. A numeric ID lets Kubernetes verify "runAsNonRoot".
# The files above stay owned by root, so the app can't modify its own code.
USER 10001

# The port our app listens on
EXPOSE 8000

# gunicorn is a production-ready web server for Flask apps.
# "app:app" means: the "app" object inside app.py
# --worker-tmp-dir /dev/shm: gunicorn needs a writable folder, /dev/shm is in memory
# --access-logfile -: log every request to stdout
# --no-control-socket: turn off gunicorn's admin socket, we don't use it
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-tmp-dir", "/dev/shm", "--access-logfile", "-", "--no-control-socket", "app:app"]
