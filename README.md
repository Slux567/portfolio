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
- **Container-ready:** a small Docker image that runs gunicorn as a non-root user.

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
├── app.py              # Flask app, page content (PROFILE) and Credly integration
├── templates/
│   ├── base.html       # Shared layout: <head>, Tailwind, footer
│   └── index.html      # The page itself
├── requirements.txt    # Python dependencies
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

Open <http://localhost:5000>. This uses Flask's debug server, which reloads on code changes
and only listens on localhost.

## Running with Docker

```bash
docker build -t portfolio .
docker run -p 8000:8000 portfolio
```

Open <http://localhost:8000>. With Podman, replace `docker` with `podman`.

## Updating the content

| What | Where |
|---|---|
| Bio, skills, experience, projects, contact | `PROFILE` in `app.py` |
| Certificates | My Credly profile (appears on the site within an hour) |
| Layout and styling | `templates/index.html` and `templates/base.html` |

## License

[MIT](LICENSE)
