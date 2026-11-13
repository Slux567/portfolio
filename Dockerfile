# This Dockerfile has two stages:
#   1. "build": a normal Python image with pip, used to install the dependencies.
#   2. the final image: a "distroless" image that contains only Python itself.
#      No shell, no package manager, no pip - so far less that can be attacked
#      or that security scanners can flag. Only the result of stage 1 is copied in.
#
# Both images are pinned by digest so every build uses the exact same base image
# (a tag like "3.13-slim" can change underneath you). Both are Debian 13 with Python 3.13.

# --- Stage 1: install dependencies ---------------------------------------------
FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90 AS build

# Install the packages into /deps instead of the system Python, so we can copy
# that one folder into the final image.
# --require-hashes makes pip refuse any package whose hash doesn't match requirements.txt.
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore --require-hashes \
    --target /deps -r requirements.txt

# --- Stage 2: the final image ---------------------------------------------------
FROM gcr.io/distroless/python3-debian13:nonroot@sha256:6c4cb3bfa4b555429dd19541796a6ba6b30c84675b460bd0bd5072f7d5bdae71

# Don't write .pyc files (lets the container run with a read-only filesystem),
# print logs straight away instead of buffering them, and tell Python where
# to find the packages from stage 1.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/deps

# All following commands run inside /app in the container
WORKDIR /app

# Copy the installed packages from stage 1, then only the files the app needs
COPY --from=build /deps /app/deps
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Run as the non-root "nonroot" user (65532) that distroless provides.
# A numeric ID lets Kubernetes verify "runAsNonRoot".
# The files above stay owned by root, so the app can't modify its own code.
USER 65532

# The port our app listens on
EXPOSE 8000

# gunicorn is a production-ready web server for Flask apps. There's no shell in
# this image, so it's started through Python: "python3 -m gunicorn".
# "app:app" means: the "app" object inside app.py
# --worker-tmp-dir /dev/shm: gunicorn needs a writable folder, /dev/shm is in memory
# --access-logfile -: log every request to stdout
# --no-control-socket: turn off gunicorn's admin socket, we don't use it
ENTRYPOINT ["/usr/bin/python3", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--worker-tmp-dir", "/dev/shm", "--access-logfile", "-", "--no-control-socket", "app:app"]
