"""
Portfolio website of Stijn Luijkx, built with Flask.

All content of the site lives in the PROFILE dictionary below. To add a skill,
job or project, add it to the right list - no HTML changes needed.
Certificates are loaded automatically from Credly.
"""

import time

import requests
from flask import Flask, render_template

app = Flask(__name__)


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
    # Credly username (https://www.credly.com/users/stijn-luijkx).
    # Certificates are loaded from there automatically, see get_certificates().
    "credly_username": "stijn-luijkx",
    # Special titles/achievements shown at the top of the page.
    "highlights": [
        {
            "emoji": "🚀",
            "title": "Kubestronaut",
            "text": "Holds all five CNCF Kubernetes certifications: CKA, CKAD, CKS, KCNA and KCSA.",
        },
        {
            "emoji": "🏠",
            "title": "Homelab Enthusiast",
            "text": "Runs a Kubernetes cluster at home (and you are currently being served by it).",
        },
    ],
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
    "experience": [
        {
            "role": "Cloud Engineer",
            "company": "KPN Developer Portal",
            "period": "January 2024 - Present",
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
        response = requests.get(url, timeout=5)
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
CACHE_SECONDS = 60 * 60  # 1 hour
cache = {"certificates": [], "fetched_at": 0}


def get_certificates(username):
    """Return certificates from the cache, refreshing it if it's older than an hour."""
    cache_age = time.time() - cache["fetched_at"]
    if cache_age > CACHE_SECONDS:
        certificates = fetch_certificates_from_credly(username)
        if certificates is not None:
            # Only replace the cache when the fetch worked, so we keep
            # showing the old certificates if Credly is having problems.
            cache["certificates"] = certificates
        cache["fetched_at"] = time.time()
    return cache["certificates"]


@app.route("/")
def index():
    certificates = get_certificates(PROFILE["credly_username"])
    # render_template looks inside the "templates" folder.
    # Everything we pass in can be used in the HTML.
    return render_template("index.html", profile=PROFILE, certificates=certificates)


@app.after_request
def add_security_headers(response):
    """Add basic security headers to every response."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


if __name__ == "__main__":
    # Only used when you run "python app.py" locally (debug mode, localhost only).
    # In Docker we use gunicorn instead (see the Dockerfile).
    app.run(port=5000, debug=True)
