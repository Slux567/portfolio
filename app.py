"""
Portfolio website of Stijn Luijkx, built with Flask.

All content of the site lives in the PROFILE dictionary below. To add a skill,
job or project, add it to the right list - no HTML changes needed.
Certificates are loaded automatically from Credly.
"""

import os
import time

import requests
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

# --- Settings -----------------------------------------------------------------
# Everything that can differ per environment is read from environment variables.

# Debug mode shows code and lets you run Python from the browser on errors.
# It must never be on in production, so it's off unless explicitly enabled.
DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

# Credly profile to load certificates from, and how long to cache them.
CREDLY_USERNAME = os.environ.get("CREDLY_USERNAME", "stijn-luijkx")
CREDLY_CACHE_SECONDS = int(os.environ.get("CREDLY_CACHE_SECONDS", "3600"))
CREDLY_TIMEOUT_SECONDS = int(os.environ.get("CREDLY_TIMEOUT_SECONDS", "5"))

# Number of reverse proxies in front of the app that add X-Forwarded-* headers
# (e.g. 1 for Envoy). 0 means: don't trust these headers at all.
# Never set this higher than the real number of proxies, or visitors can spoof
# their IP address by sending their own X-Forwarded-For header.
TRUSTED_PROXY_COUNT = int(os.environ.get("TRUSTED_PROXY_COUNT", "0"))

# Tailwind CSS is loaded from this exact URL (see templates/base.html).
TAILWIND_URL = "https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.3.5/dist/index.global.js"

# --- App ----------------------------------------------------------------------

app = Flask(__name__)

if TRUSTED_PROXY_COUNT > 0:
    # Use the client IP and protocol (http/https) from the proxy headers,
    # instead of the IP and protocol of the proxy itself.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=TRUSTED_PROXY_COUNT, x_proto=TRUSTED_PROXY_COUNT)


PROFILE = {
    "name": "Stijn Luijkx",
    "title": "Cloud Engineer",
    "location": "The Netherlands",
    "email": "contact@stijnluijkx.com",
    "bio": (
        "Cloud Engineer with a passion for Kubernetes and the cloud-native way "
        "of building and running software. I enjoy designing platforms that are "
        "reliable, secure, and easy to operate. Always learning, and excited to "
        "keep growing."
    ),
    # Shown bigger at the top of the Skills section.
    "core_skills": [
        "Kubernetes",
        "AWS",
        "Linux",
    ],
    "skills": [
        "Python",
        "Terraform",
        "Ansible",
        "Prometheus",
        "Grafana",
        "Vector",
        "PostgreSQL",
        "Thanos",
        "VictoriaMetrics",
        "Networking",
        "Envoy",
        "cert-manager",
        "Loki",
        "Gateway API",
        "GitHub Actions",
        "CI/CD",
        "Helm",
        "Flux",
        "GitOps",
        "Kustomize",
        "Talos Linux",
        "Cilium",
        "ExternalDNS",
        "Cloudflare",
        "SOPS",
        "External Secrets",
        "Alertmanager",
        "Renovate",
        "Bash",
    ],
    # "logo" is a file in static/logos/.
    "experience": [
        {
            "role": "Cloud/DevOps Engineer",
            "company": "KPN Developer Portal",
            "period": "January 2025 - Present",
            "logo": "kpn.svg",
        },
        {
            "role": "AWS Cloud Engineer",
            "company": "Sogeti",
            "period": "February 2024 - Present",
            "logo": "sogeti.svg",
        },
    ],
    "projects": [
        {
            "name": "Kubernetes Homelab",
            "description": (
                "My personal Kubernetes cluster at home, managed the GitOps way "
                "with Flux."
            ),
            "url": "https://github.com/Slux567/homelab",
        },
    ],
}


def fetch_certificates_from_credly(username):
    """Fetch public badges from Credly and return a simple list of certificates."""
    url = f"https://www.credly.com/users/{username}/badges.json"
    try:
        response = requests.get(url, timeout=CREDLY_TIMEOUT_SECONDS)
        response.raise_for_status()
        certificates = []
        for badge in response.json()["data"]:
            certificates.append({
                "name": badge["badge_template"]["name"],
                "image": badge["badge_template"]["image_url"],
                "issuer": badge["issuer"]["entities"][0]["entity"]["name"],
                "date": badge["issued_at_date"],
                "url": f"https://www.credly.com/badges/{badge['id']}",
            })
        return certificates
    except Exception:
        # Credly is down, slow or changed its format.
        # Return None so we know the fetch failed.
        app.logger.warning("Could not fetch certificates from Credly", exc_info=True)
        return None


# A simple cache: we remember the certificates and when we fetched them,
# so we only ask Credly once per hour instead of on every page visit.
cache = {"certificates": [], "fetched_at": 0}


def get_certificates(username):
    """Return certificates from the cache, refreshing it when it's too old."""
    cache_age = time.time() - cache["fetched_at"]
    if cache_age > CREDLY_CACHE_SECONDS:
        certificates = fetch_certificates_from_credly(username)
        if certificates is not None:
            # Only replace the cache when the fetch worked, so we keep
            # showing the old certificates if Credly is having problems.
            cache["certificates"] = certificates
        cache["fetched_at"] = time.time()
    return cache["certificates"]


@app.route("/")
def index():
    certificates = get_certificates(CREDLY_USERNAME)
    # render_template looks inside the "templates" folder.
    # Everything we pass in can be used in the HTML.
    return render_template(
        "index.html",
        profile=PROFILE,
        certificates=certificates,
        tailwind_url=TAILWIND_URL,
    )


@app.route("/healthz")
def healthz():
    """Health check for Kubernetes probes. Doesn't call Credly, so it's always fast."""
    return "ok"


@app.after_request
def add_security_headers(response):
    """Add security headers to every response."""
    # Content Security Policy: the browser only loads scripts, styles and images
    # from the sources listed here. This blocks most injected-code (XSS) attacks.
    # Tailwind adds <style> tags while the page loads, so inline styles are allowed.
    response.headers["Content-Security-Policy"] = "; ".join([
        "default-src 'none'",
        f"script-src 'self' {TAILWIND_URL}",
        "style-src 'unsafe-inline'",
        "img-src 'self' https://images.credly.com",
        "base-uri 'none'",
        "form-action 'none'",
        "frame-ancestors 'none'",
    ])
    # Always use HTTPS for this site from now on (browsers ignore this over plain HTTP).
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    return response


if __name__ == "__main__":
    # Only used when you run "python app.py" locally (localhost only).
    # In Docker we use gunicorn instead (see the Dockerfile).
    app.run(port=5000, debug=DEBUG)
