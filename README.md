# Portfolio

![Python](https://img.shields.io/badge/Python-Flask-3776AB?logo=python&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-06B6D4?logo=tailwindcss&logoColor=white)
![Docker](https://img.shields.io/badge/Container-Docker-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Hosted%20on-Kubernetes-326CE5?logo=kubernetes&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

My personal portfolio website: a small, single-page Flask app that shows my skills,
experience, certificates and projects.

It runs on my own Kubernetes cluster at home, deployed with Flux from my
[homelab repository](https://github.com/Slux567/homelab).

## Features

- **Single page:** intro, highlights, skills, experience, certificates, projects and contact.
- **Content in one place:** everything on the page comes from the `PROFILE` dictionary in `app.py`.
- **Certificates from Credly:** badges are fetched from my public
  [Credly profile](https://www.credly.com/users/stijn-luijkx), so new certificates show up
  automatically. The result is cached for an hour, so Credly gets at most one request per
  hour. If Credly is unreachable, the last known certificates stay on the page.
- **No frontend build step:** Tailwind CSS is loaded from a CDN, pinned to an exact version
  with an integrity hash.
- **Container-ready:** a small Docker image that runs gunicorn as a non-root user and works
  with a read-only filesystem.
- **Secure by default:** see [Security](#security).

## Tech stack

| Part | Technology |
|---|---|
| Backend | [Flask](https://flask.palletsprojects.com/) with Jinja templates |
| Styling | [Tailwind CSS](https://tailwindcss.com/) (browser build via CDN) |
| Web server | [gunicorn](https://gunicorn.org/) |
| Container | Docker |
| Hosting | Talos Kubernetes cluster, managed with Flux |

## Project structure

```
.
├── app.py              # Flask app, settings, page content (PROFILE) and Credly integration
├── templates/
│   ├── base.html       # Shared layout: <head>, Tailwind, footer
│   └── index.html      # The page itself
├── static/
│   └── certificates.js # Switching between certificate pages
├── requirements.in     # Direct Python dependencies (edit this one)
├── requirements.txt    # All dependencies, pinned with hashes (generated)
└── Dockerfile          # Container image
```

## How it works

1. A visitor opens `/`.
2. Flask runs `index()` in `app.py`, which gets the certificates (from the cache or from Credly).
3. `templates/index.html` is rendered with the `PROFILE` data and the certificates.
4. Tailwind classes in the HTML style the page in the browser.

## Running locally

Requires Python 3.13+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://localhost:5000>. This uses Flask's development server, which only listens on
localhost. For automatic reloading and error pages while developing, run
`FLASK_DEBUG=true python app.py` instead. Never enable debug mode in production.

## Running with Docker

```bash
docker build -t portfolio .
docker run -p 8000:8000 portfolio
```

Open <http://localhost:8000>. With Podman, replace `docker` with `podman`.

The container also runs with a read-only filesystem and all Linux capabilities dropped:

```bash
docker run -p 8000:8000 --read-only --cap-drop=ALL portfolio
```

## Configuration

Settings are read from environment variables:

| Variable | Default | Description |
|---|---|---|
| `TRUSTED_PROXY_COUNT` | `0` | Number of reverse proxies in front of the app that set `X-Forwarded-*` headers. Set it to the real number of proxies, never higher, or visitors can spoof their IP address. |
| `CREDLY_USERNAME` | `stijn-luijkx` | Credly profile to load certificates from |
| `CREDLY_CACHE_SECONDS` | `3600` | How long certificates are cached |
| `CREDLY_TIMEOUT_SECONDS` | `5` | Timeout for requests to Credly |
| `FLASK_DEBUG` | `false` | Debug mode, only for local development with `python app.py` |

The `/healthz` endpoint returns `ok` and can be used for Kubernetes liveness and readiness
probes.

## Security

- **Debug mode is off** unless explicitly enabled.
- **Security headers** on every response: a strict Content Security Policy (scripts only from
  this site and the pinned Tailwind file, images only from Credly), HSTS,
  `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`
  and `Cross-Origin-Opener-Policy`.
- **Reverse proxy support:** `ProxyFix` uses the client IP and protocol from `X-Forwarded-*`
  headers, but only when `TRUSTED_PROXY_COUNT` is set.
- **Supply chain:** all Python dependencies (including indirect ones) are pinned with hashes,
  the base image is pinned by digest, and Tailwind is loaded with an integrity hash.
- **Container:** runs as non-root user `10001`, contains only the files the app needs, and
  supports a read-only filesystem.

## Updating the content

| What | Where |
|---|---|
| Bio, skills, experience, projects, contact | `PROFILE` in `app.py` |
| Certificates | My Credly profile (appears on the site within an hour) |
| Layout and styling | `templates/index.html` and `templates/base.html` |

## Updating dependencies

Direct dependencies are listed in `requirements.in`. After changing it, regenerate the pinned
`requirements.txt` inside the same Python image the Dockerfile uses:

```bash
docker run --rm -v "$PWD":/src -w /src python:3.13-slim sh -c \
  "pip install -q pip-tools && pip-compile --generate-hashes --strip-extras --allow-unsafe --no-header -o requirements.txt requirements.in"
```

## License

[MIT](LICENSE)
