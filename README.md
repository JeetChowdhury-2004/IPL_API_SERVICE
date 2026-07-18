# IPL API Service

A production-ready Flask REST API for Indian Premier League analytics, powered by PostgreSQL and ball-by-ball Cricsheet data.

The project exposes clean API endpoints for IPL matches, batting records, bowling records, teams, players, venues, seasons, and matchup analysis. It also includes a browser-based documentation UI with an interactive API tester.

## Live Demo

- API Platform: `https://ipl-api-service-lkbv.onrender.com`
- Documentation: `https://ipl-api-service-lkbv.onrender.com/documentation`
- Available Data: `https://ipl-api-service-lkbv.onrender.com/available-data`
- Health Check: `https://ipl-api-service-lkbv.onrender.com/health`

## Features

- REST APIs for IPL statistics and analytics.
- PostgreSQL-backed storage for matches, deliveries, and wickets.
- ETL pipeline to download and load the latest IPL JSON data from Cricsheet.
- Interactive documentation page with categorized APIs and live testing.
- Machine-readable API metadata through `/api-docs`.
- Search endpoints for teams and players.
- CORS configuration for external frontend clients.
- Render-ready deployment using Gunicorn and `Procfile`.

## Tech Stack

- Python
- Flask
- PostgreSQL
- psycopg2
- pandas
- requests
- Jinja2
- Bootstrap
- Vanilla JavaScript
- Gunicorn

## Project Structure

```text
IPL_API_Service/
|-- app.py                  # Flask application factory and page routes
|-- wsgi.py                 # WSGI entry point for production
|-- config.py               # Environment-based app configuration
|-- Procfile                # Render/Railway web process command
|-- requirements.txt        # Python dependencies
|-- database/               # Database connection and insert helpers
|-- etl/                    # Cricsheet download and data loading pipeline
|-- routes/                 # API route modules
|-- sql/                    # PostgreSQL schema
|-- static/                 # CSS, JavaScript, and assets
|-- templates/              # Jinja2 pages and partials
|-- tests/                  # Lightweight tests
`-- utils/                  # API docs metadata and shared helpers
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/JeetChowdhury-2004/IPL_API_SERVICE.git
cd IPL_API_SERVICE
```

### 2. Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a local `.env` file:

```powershell
Copy-Item .env.example .env
```

Update `.env` with your own values:

```env
FLASK_ENV=development
SECRET_KEY=replace-with-a-long-random-secret
CORS_ORIGINS=

DB_HOST=localhost
DB_NAME=ipl_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_PORT=5432
```

`CORS_ORIGINS` can be left blank when the API and documentation UI are served from the same Flask app.

### 5. Create the Database Schema

Create a PostgreSQL database, then run:

```bash
psql -U postgres -d ipl_db -f sql/schema.sql
```

If `psql` is not available, run the schema using any PostgreSQL client and the SQL in `sql/schema.sql`.

### 6. Load IPL Data

```bash
python etl/update_data.py
```

This command:

1. Downloads the latest IPL JSON ZIP from Cricsheet.
2. Extracts match files into `raw_data/json_matches`.
3. Loads match metadata into `matches`.
4. Loads ball-by-ball data into `deliveries`.
5. Loads wicket information into `wickets`.

### 7. Run Locally

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## API Endpoints

### Core Pages

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Homepage |
| `GET` | `/documentation` | Interactive API documentation |
| `GET` | `/api-docs` | Machine-readable API metadata |
| `GET` | `/available-data` | Database-supported teams, seasons, venues, and players |
| `GET` | `/about` | About page |
| `GET` | `/health` | Service health check |

### Matches

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/matches` | List IPL matches |
| `GET` | `/matches/season/<season>` | Matches from a specific season |
| `GET` | `/matches/filter` | Filter matches by supported query parameters |
| `GET` | `/matches/head-to-head` | Team head-to-head record |
| `GET` | `/matches/title-winners` | IPL title winners |
| `GET` | `/matches/title-counts` | Title counts by team |
| `GET` | `/matches/most-successful-team` | Most successful IPL teams |
| `GET` | `/matches/highest-run-chases` | Highest run chases |
| `GET` | `/matches/highest-team-totals` | Highest team totals |
| `GET` | `/matches/lowest-defended-scores` | Lowest defended scores |
| `GET` | `/matches/lowest-team-totals` | Lowest team totals |
| `GET` | `/matches/closest-finishes` | Closest IPL finishes |
| `GET` | `/matches/super-over-matches` | Super over matches |
| `GET` | `/matches/highest-successful-chases` | Highest successful chases |

### Batting

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/batting/most-runs` | Highest run scorers |
| `GET` | `/batting/highest-score` | Highest individual scores |
| `GET` | `/batting/strike-rate` | Batting strike-rate leaderboard |
| `GET` | `/batting/batting-average` | Batting average leaderboard |
| `GET` | `/batting/most-sixes` | Most sixes |
| `GET` | `/batting/most-fours` | Most fours |
| `GET` | `/batting/orange-cap-by-season` | Orange Cap winners by season |
| `GET` | `/batting/most-50s` | Most half-centuries |
| `GET` | `/batting/most-100s` | Most centuries |

### Bowling

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/bowling/most-wickets` | Highest wicket takers |
| `GET` | `/bowling/economy` | Bowling economy leaderboard |
| `GET` | `/bowling/strike-rate` | Bowling strike-rate leaderboard |
| `GET` | `/bowling/average` | Bowling average leaderboard |
| `GET` | `/bowling/best-figures` | Best bowling figures |
| `GET` | `/bowling/purple-cap-by-season` | Purple Cap winners by season |

### Teams

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/teams` | List IPL teams |
| `GET` | `/teams/search` | Search teams |
| `GET` | `/teams/most-wins` | Teams with most wins |
| `GET` | `/teams/win-percentage` | Team win percentage |
| `GET` | `/teams/playoff-record` | Team playoff records |
| `GET` | `/teams/finals-record` | Team finals records |
| `GET` | `/teams/chasing-record` | Team chasing records |
| `GET` | `/teams/defending-record` | Team defending records |

### Players

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/players/search` | Search players |
| `GET` | `/players/player-summary` | Player batting, bowling, and match summary |
| `GET` | `/players/player-of-the-match` | Player of the Match records |
| `GET` | `/players/player-career-span` | Player career span |
| `GET` | `/players/best-all-rounders` | All-rounder leaderboard |

### Matchups, Seasons, and Venues

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/matchups/batter-vs-bowler` | Batter vs bowler matchup |
| `GET` | `/matchups/batter-vs-team` | Batter vs team matchup |
| `GET` | `/matchups/bowler-vs-team` | Bowler vs team matchup |
| `GET` | `/seasons/<season>/summary` | Season summary |
| `GET` | `/venues/stats` | Venue statistics |

## Example Requests

```bash
curl "http://127.0.0.1:5000/health"
```

```bash
curl "http://127.0.0.1:5000/matches?limit=5"
```

```bash
curl "http://127.0.0.1:5000/batting/most-runs?season=2024&limit=10"
```

```bash
curl "http://127.0.0.1:5000/players/player-summary?player=MS%20Dhoni"
```

```bash
curl "http://127.0.0.1:5000/matchups/batter-vs-bowler?batter=Virat%20Kohli&bowler=Jasprit%20Bumrah"
```

## Query Parameters

Many endpoints support common filters:

| Parameter | Description | Example |
| --- | --- | --- |
| `season` | Filter by IPL season | `season=2024` |
| `team` | Filter by team name | `team=Mumbai Indians` |
| `player` | Filter by player name | `player=Virat Kohli` |
| `venue_name` | Filter by venue | `venue_name=Wankhede Stadium` |
| `limit` | Limit number of records | `limit=10` |

Use `/available-data` to view exact database-supported values.

## Data Updates

Run the ETL whenever new Cricsheet IPL data is available:

```bash
python etl/update_data.py
```

The loader is designed to upsert or ignore duplicate records where appropriate, so rerunning it is safe for refreshing the database.

For production, schedule this command using a cron service or Render Cron Job during IPL season.

## Deployment on Render

### Web Service

Use these settings:

```text
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn wsgi:app --bind 0.0.0.0:$PORT
```

The repository includes a `Procfile` with the same production start command.

### Environment Variables

```env
FLASK_ENV=production
SECRET_KEY=replace-with-a-secure-random-secret
CORS_ORIGINS=
DB_HOST=your-render-internal-db-host
DB_NAME=your-render-db-name
DB_USER=your-render-db-user
DB_PASSWORD=your-render-db-password
DB_PORT=5432
```

When the web service and database are both on Render, use the internal database hostname for `DB_HOST`.

### Database Setup

Run the schema once against your production PostgreSQL database:

```bash
psql "YOUR_RENDER_EXTERNAL_DATABASE_URL" -f sql/schema.sql
```

Then load the IPL data:

```bash
python etl/update_data.py
```

## Tests

Run the test suite:

```bash
pytest
```

## Security Notes

- Do not commit `.env` or database credentials.
- Use a strong random `SECRET_KEY` in production.
- Restrict `CORS_ORIGINS` when connecting from external frontend domains.
- Rotate credentials if they are accidentally shared.

## Data Source and Attribution

This project uses IPL data from [Cricsheet](https://cricsheet.org/).

Please review and follow Cricsheet's license and attribution requirements before using the data in a public or commercial product.

## Author

Created by [Jeet Chowdhury](https://github.com/JeetChowdhury-2004).
