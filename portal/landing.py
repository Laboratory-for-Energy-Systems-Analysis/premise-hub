from __future__ import annotations

from flask import Flask, Response, jsonify, redirect, render_template

from .catalog import resources
from .ecosystem import ecosystem
from .presentations import presentations
from .publications import publications


def create_landing_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    @app.get("/")
    def index():
        catalog = resources()
        publication_catalog = publications()
        publication_entries = [
            item for item in publication_catalog if item["kind"] == "application"
        ]
        foundational_publication = next(
            item for item in publication_catalog if item["kind"] == "foundational"
        )
        featured_resources = [item for item in catalog if item["featured"]]
        interactive_ecosystem = next(
            (
                item
                for item in featured_resources
                if item["id"] == "interactive-ecosystem"
            ),
            None,
        )
        featured = [
            item
            for item in featured_resources
            if item["id"] != "interactive-ecosystem"
        ]
        ecosystem_resources = [item for item in catalog if not item["featured"]]
        return render_template(
            "index.html",
            featured=featured,
            interactive_ecosystem=interactive_ecosystem,
            presentations=presentations(),
            ecosystem=ecosystem_resources,
            publications=publication_entries,
            foundational_publication=foundational_publication,
            publication_years=sorted(
                {item["year"] for item in publication_entries}, reverse=True
            ),
            publication_topics=sorted(
                {
                    topic
                    for item in publication_entries
                    for topic in item["topics"]
                },
                key=str.casefold,
            ),
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
                    "lca_time": "ok",
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
