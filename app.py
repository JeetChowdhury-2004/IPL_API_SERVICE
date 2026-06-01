from flask import Flask

from routes.matches import matches_bp
from routes.players import players_bp
from routes.batting import batting_bp
from routes.bowling import bowling_bp
from routes.matchups import matchups_bp
from routes.teams import teams_bp

app = Flask(__name__)

app.register_blueprint(matches_bp)
app.register_blueprint(players_bp)
app.register_blueprint(batting_bp)
app.register_blueprint(bowling_bp)
app.register_blueprint(matchups_bp)
app.register_blueprint(teams_bp)




@app.route("/")
def home():

    return {
        "message": "IPL API Service Running"
    }


if __name__ == "__main__":

    app.run(debug=True)