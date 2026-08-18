from __future__ import annotations

from flask import Flask, Response, jsonify, redirect, render_template

from .catalog import resources
from .ecosystem import ecosystem


def create_landing_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    @app.get("/")
    def index():
        catalog = resources()
        featured = [item for item in catalog if item["featured"]]
        ecosystem_resources = [item for item in catalog if not item["featured"]]
        return render_template(
            "index.html", featured=featured, ecosystem=ecosystem_resources
        )

    @app.get("/ecosystem/")
    def ecosystem_page():
        return render_template("ecosystem.html", catalog=ecosystem())

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "services": {
                    "landing": "ok",
                    "ecosystem": "ok",
                    "scenarios": "ok",
                    "workshop": "ok",
                },
            }
        )

    @app.get("/dashboard/")
    @app.get("/dashboard")
    def dashboard_alias():
        return redirect("/scenarios/", code=308)

    @app.get("/robots.txt")
    def robots():
        return Response("User-agent: *\nAllow: /\n", mimetype="text/plain")

    @app.errorhandler(404)
    def not_found(error):
        del error
        return render_template("404.html"), 404

    return app
