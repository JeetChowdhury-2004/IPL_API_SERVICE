try:
    from flask import Flask, render_template, request
    from werkzeug.exceptions import HTTPException

    from config import get_config
    from utils.api_docs import API_DOCS
    from utils.api_response import success_response, error_response

except ModuleNotFoundError as exc:
    if exc.name != "flask":
        raise

    raise SystemExit(
        "Flask is not installed for this Python interpreter.\n"
        "Run this app with the project virtual environment:\n"
        "  .\\.venv\\Scripts\\python.exe app.py\n"
        "Or install dependencies first:\n"
        "  python -m pip install -r requirements.txt"
    ) from exc


from routes.matches import matches_bp
from routes.players import players_bp
from routes.batting import batting_bp
from routes.bowling import bowling_bp
from routes.matchups import matchups_bp
from routes.teams import teams_bp
from routes.seasons import seasons_bp
from routes.venues import venues_bp


API_PREFIXES = (
    "/api",
    "/matches",
    "/batting",
    "/bowling",
    "/players",
    "/matchups",
    "/teams",
    "/seasons",
    "/venues"
)


def register_extensions(app):
    try:
        from flask_cors import CORS
    except ModuleNotFoundError:
        return

    origins = app.config.get("CORS_ORIGINS")

    if not origins:
        return

    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    origin.strip()
                    for origin in origins.split(",")
                    if origin.strip()
                ]
            }
        }
    )


def wants_json_response():
    return (
        request.path.startswith(API_PREFIXES)
        or request.accept_mimetypes.best == "application/json"
    )


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    register_extensions(app)

    app.register_blueprint(matches_bp)
    app.register_blueprint(players_bp)
    app.register_blueprint(batting_bp)
    app.register_blueprint(bowling_bp)
    app.register_blueprint(matchups_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(seasons_bp)
    app.register_blueprint(venues_bp)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/documentation")
    def documentation():
        return render_template(
            "documentation.html",
            api_docs=API_DOCS
        )

    @app.route("/api-docs")
    def get_api_docs():
        return success_response(API_DOCS)

    @app.route("/available-data")
    def available_data():
        from utils.available_data import load_available_data

        data = load_available_data()

        return render_template(
            "available_data.html",
            database_available=data["database_available"],
            error_message=data["error_message"],
            teams=data["teams"],
            seasons=data["seasons"],
            cities=data["cities"],
            venues=data["venues"],
            batters=data["batters"],
            bowlers=data["bowlers"]
        )

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/health")
    def health():
        return success_response({"status": "ok"})

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        if wants_json_response():
            return error_response(error.description, error.code)

        return error

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled application error")

        if wants_json_response():
            return error_response("Internal server error", 500)

        return render_template("500.html"), 500

    return app

# print(">>> APP.PY LOADED <<<")
app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
    # app.run(debug=True)
