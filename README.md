# IPL API Service

IPL API Service is a Flask and PostgreSQL application that exposes Indian Premier League cricket data through REST APIs. It includes endpoints for matches, teams, players, batting, bowling, and matchup analytics, plus a browser documentation UI with a live API tester.

## Features

- REST APIs for IPL batting, bowling, match, team, player, season, venue, and matchup statistics.
- PostgreSQL-backed storage for matches, ball-by-ball deliveries, and wickets.
- ETL script for downloading and loading the latest IPL JSON data from Cricsheet.
- Interactive documentation page at `/documentation`.
- Machine-readable API metadata at `/api-docs`.
- Health check endpoint at `/health`.

## Tech Stack

- Python
- Flask
- PostgreSQL
- psycopg2
- pandas
- requests
- Jinja2 templates
- Bootstrap and vanilla JavaScript

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Update `.env` with your PostgreSQL credentials.

Create the database schema:

```powershell
psql -U postgres -d ipl_db -f sql/schema.sql
```

Load IPL data:

```powershell
python etl/update_data.py
```

Run the app locally:

```powershell
$env:FLASK_ENV="development"
python app.py
```

Open `http://127.0.0.1:5000`.

## Production

Use a real `SECRET_KEY`, keep `FLASK_ENV=production`, and run with a WSGI server:

```bash
gunicorn wsgi:app --bind 0.0.0.0:$PORT
```

The included `Procfile` uses the same command for platforms such as Render or Railway.

For cross-origin browser clients, set `CORS_ORIGINS` to a comma-separated allowlist:

```env
CORS_ORIGINS=https://your-frontend.example.com
```

## Important Endpoints

- `GET /health`
- `GET /api-docs`
- `GET /documentation`
- `GET /available-data`
- `GET /matches`
- `GET /batting/most-runs`
- `GET /bowling/most-wickets`
- `GET /teams/most-wins`
- `GET /teams/search?team_name=delhi`
- `GET /players/search?player_name=pandya`
- `GET /players/player-summary?player=MS%20Dhoni`
- `GET /seasons/2024/summary`
- `GET /venues/stats?venue_name=Wankhede%20Stadium`

## Tests

Run the lightweight test suite:

```powershell
pytest
```

## Data Source

This project uses IPL data from Cricsheet. Review and follow Cricsheet's license and attribution requirements before public launch.
