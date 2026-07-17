from app import create_app
import routes.players as players_module
import routes.teams as teams_module
import routes.seasons as seasons_module
import routes.venues as venues_module
import routes.batting as batting_module
import routes.bowling as bowling_module
import routes.matchups as matchups_module
import routes.matches as matches_module
from utils.api_docs import API_DOCS


def make_client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_health_endpoint():
    client = make_client()

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "ok"


def test_api_docs_endpoint():
    client = make_client()

    response = client.get("/api-docs")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert "batting" in payload["data"]
    assert "bowling" in payload["data"]


def test_documentation_page_renders():
    client = make_client()

    response = client.get("/documentation")

    assert response.status_code == 200
    html = response.data.decode()
    assert "IPL API Documentation" in html
    assert "/seasons/{season}/summary" in html
    assert "id=\"sidebar-seasons\"" in html


def test_unknown_api_route_returns_json_404():
    client = make_client()

    response = client.get("/api/unknown")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["success"] is False


def test_player_search_returns_exact_available_names(monkeypatch):
    def fake_execute_query(query, values=None):
        return [
            ("MS Dhoni", True, False, 250),
            ("Dhoni Example", True, True, 4)
        ]

    monkeypatch.setattr(
        players_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/players/search?player_name=dhoni")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["player_name"] == "dhoni"
    assert payload["data"]["role"] == "all"
    assert payload["data"]["count"] == 2
    assert payload["data"]["players"][0] == {
        "player": "MS Dhoni",
        "available_as": ["batter"],
        "matches": 250
    }
    assert payload["data"]["players"][1]["available_as"] == [
        "batter",
        "bowler"
    ]


def test_player_search_requires_query():
    client = make_client()

    response = client.get("/players/search")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["message"] == "player_name is required"


def test_player_search_validates_role():
    client = make_client()

    response = client.get("/players/search?player_name=dhoni&role=keeper")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["success"] is False
    assert "role must be one of" in payload["message"]


def test_player_search_uses_default_limit(monkeypatch):
    captured_values = {}

    def fake_execute_query(query, values=None):
        captured_values["values"] = values
        return []

    monkeypatch.setattr(
        players_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/players/search?player_name=pandya")

    assert response.status_code == 200
    assert captured_values["values"][-1] == (
        players_module.DEFAULT_PLAYER_SEARCH_LIMIT
    )


def test_team_search_returns_exact_and_normalized_names(monkeypatch):
    def fake_execute_query(query, values=None):
        return [
            ("Delhi Capitals", 118),
            ("Delhi Daredevils", 161)
        ]

    monkeypatch.setattr(
        teams_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/teams/search?team_name=delhi")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["team_name"] == "delhi"
    assert payload["data"]["count"] == 2
    assert payload["data"]["teams"] == [
        {
            "team": "Delhi Capitals",
            "normalized_team": "Delhi Capitals",
            "matches": 118
        },
        {
            "team": "Delhi Daredevils",
            "normalized_team": "Delhi Capitals",
            "matches": 161
        }
    ]


def test_team_search_requires_query():
    client = make_client()

    response = client.get("/teams/search")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["message"] == "team_name is required"


def test_team_search_uses_default_limit(monkeypatch):
    captured_values = {}

    def fake_execute_query(query, values=None):
        captured_values["values"] = values
        return []

    monkeypatch.setattr(
        teams_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/teams/search?team_name=delhi")

    assert response.status_code == 200
    assert captured_values["values"][-1] == (
        teams_module.DEFAULT_TEAM_SEARCH_LIMIT
    )


def test_season_summary_returns_overview(monkeypatch):
    rows = iter([
        [(74, 10, "2024-03-22", "2024-05-26", 13, 13)],
        [(
            1426312,
            "2024-05-26",
            "Chennai",
            "MA Chidambaram Stadium",
            "Kolkata Knight Riders",
            "Sunrisers Hyderabad",
            "Kolkata Knight Riders",
            "MA Starc"
        )],
        [("V Kohli", 741)],
        [("HV Patel", 24)],
        [(
            1426262,
            1,
            "Sunrisers Hyderabad",
            "Royal Challengers Bangalore",
            287
        )]
    ])

    def fake_execute_query(query, values=None):
        return next(rows)

    monkeypatch.setattr(
        seasons_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/seasons/2024/summary")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["season"] == 2024
    assert payload["data"]["matches"] == 74
    assert payload["data"]["champion"]["team"] == "Kolkata Knight Riders"
    assert payload["data"]["runner_up"]["team"] == "Sunrisers Hyderabad"
    assert payload["data"]["top_batter"] == {
        "player": "V Kohli",
        "runs": 741
    }
    assert payload["data"]["top_bowler"] == {
        "player": "HV Patel",
        "wickets": 24
    }
    assert payload["data"]["highest_team_total"]["runs"] == 287


def test_season_summary_returns_404_for_missing_season(monkeypatch):
    def fake_execute_query(query, values=None):
        return [(0, 0, None, None, 0, 0)]

    monkeypatch.setattr(
        seasons_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/seasons/1999/summary")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["message"] == "Season not found"


def test_venue_stats_returns_overview(monkeypatch):
    rows = iter([
        [(
            132,
            2008,
            2026,
            ["Mumbai"],
            ["Wankhede Stadium", "Wankhede Stadium, Mumbai"]
        )],
        [(171.42,)],
        [(72, 58, 2)],
        [(
            1426268,
            1,
            "Sunrisers Hyderabad",
            "Royal Challengers Bengaluru",
            287
        )],
        [
            ("Mumbai Indians", 82),
            ("Chennai Super Kings", 28)
        ]
    ])

    def fake_execute_query(query, values=None):
        return next(rows)

    monkeypatch.setattr(
        venues_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/venues/stats?venue_name=Wankhede Stadium")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["venue_name"] == "Wankhede Stadium"
    assert payload["data"]["matches"] == 132
    assert payload["data"]["seasons"] == {
        "first": 2008,
        "last": 2026
    }
    assert payload["data"]["average_first_innings_score"] == 171.42
    assert payload["data"]["chasing_wins"] == 72
    assert payload["data"]["defending_wins"] == 58
    assert payload["data"]["highest_team_total"]["runs"] == 287
    assert payload["data"]["top_teams_by_matches"][0]["team"]["team"] == "Mumbai Indians"


def test_venue_stats_returns_404_for_unknown_venue(monkeypatch):
    def fake_execute_query(query, values=None):
        return [(0, None, None, [], [])]

    monkeypatch.setattr(
        venues_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/venues/stats?venue_name=Unknown Venue")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["message"] == "Venue not found"


def test_venue_stats_requires_venue_name():
    client = make_client()

    response = client.get("/venues/stats")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["message"] == "venue_name is required"


def test_orange_cap_by_season_uses_requested_limit(monkeypatch):
    captured_query = []
    captured_values = []

    def fake_execute_query(query, values=None):
        if "COUNT(DISTINCT season)" in query:
            return [(17,)]
        captured_query.append(query)
        captured_values.append(values)
        return [
            (2023, "Shubman Gill", 890),
            (2024, "Virat Kohli", 741),
            (2025, "Sai Sudharsan", 759)
        ]

    monkeypatch.setattr(
        batting_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/batting/orange-cap-by-season?limit=3")

    assert response.status_code == 200
    assert captured_values[-1] == (3, 0)
    assert "ORDER BY season DESC" in captured_query[-1]
    payload = response.get_json()
    assert payload["data"]["count"] == 3


def test_purple_cap_by_season_caps_limit_at_season_count(monkeypatch):
    captured_query = []
    captured_values = []

    def fake_execute_query(query, values=None):
        if "COUNT(DISTINCT season)" in query:
            return [(17,)]
        captured_query.append(query)
        captured_values.append(values)
        return [(2024, "Harshal Patel", 24)]

    monkeypatch.setattr(
        bowling_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/bowling/purple-cap-by-season?limit=999")

    assert response.status_code == 200
    assert captured_values[-1] == (17, 0)
    assert "ORDER BY season DESC" in captured_query[-1]


def test_purple_cap_endpoint_is_removed():
    client = make_client()

    response = client.get("/bowling/purple-cap")

    assert response.status_code == 404


def test_bowling_economy_uses_legal_balls_and_bowler_runs(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Sunil Narine", 300, 240, 7.5)]

    monkeypatch.setattr(
        bowling_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/bowling/economy?player=Sunil%20Narine")

    assert response.status_code == 200
    assert "d.extra_type NOT LIKE '%%wides%%'" in captured_query[-1]
    assert "d.extra_type NOT LIKE '%%noballs%%'" in captured_query[-1]
    assert "d.extra_type LIKE '%%byes%%'" in captured_query[-1]
    assert "d.extra_type LIKE '%%legbyes%%'" in captured_query[-1]


def test_bowling_strike_rate_uses_legal_balls(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Lasith Malinga", 120, 10, 12.0)]

    monkeypatch.setattr(
        bowling_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/bowling/strike-rate?player=Lasith%20Malinga")

    assert response.status_code == 200
    assert "d.extra_type NOT LIKE '%%wides%%'" in captured_query[-1]
    assert "d.extra_type NOT LIKE '%%noballs%%'" in captured_query[-1]


def test_bowling_average_uses_bowler_runs(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Rashid Khan", 250, 10, 25.0)]

    monkeypatch.setattr(
        bowling_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/bowling/average?player=Rashid%20Khan")

    assert response.status_code == 200
    assert "d.extra_type LIKE '%%byes%%'" in captured_query[-1]
    assert "d.extra_type LIKE '%%legbyes%%'" in captured_query[-1]


def test_best_figures_uses_bowler_runs(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Alzarri Joseph", 12345, 2019, 12, 6)]

    monkeypatch.setattr(
        bowling_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/bowling/best-figures?player=Alzarri%20Joseph")

    assert response.status_code == 200
    assert "d.extra_type LIKE '%%byes%%'" in captured_query[-1]
    assert "d.extra_type LIKE '%%legbyes%%'" in captured_query[-1]


def test_batting_strike_rate_uses_legal_balls(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Virat Kohli", 500, 300, 166.67)]

    monkeypatch.setattr(
        batting_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/batting/strike-rate?player=Virat%20Kohli")

    assert response.status_code == 200
    assert "d.extra_type NOT LIKE '%%wides%%'" in captured_query[-1]
    assert "d.extra_type NOT LIKE '%%noballs%%'" in captured_query[-1]


def test_batting_average_qualification_uses_legal_balls(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("MS Dhoni", 5000, 100, 50.0)]

    monkeypatch.setattr(
        batting_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/batting/batting-average")

    assert response.status_code == 200
    assert "d.extra_type NOT LIKE '%%wides%%'" in captured_query[-1]
    assert "d.extra_type NOT LIKE '%%noballs%%'" in captured_query[-1]


def test_most_boundaries_exclude_non_boundary_runs(monkeypatch):
    captured_queries = []

    def fake_execute_query(query, values=None):
        captured_queries.append(query)
        return [("Chris Gayle", 10)]

    monkeypatch.setattr(
        batting_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    sixes_response = client.get("/batting/most-sixes?player=Chris%20Gayle")
    fours_response = client.get("/batting/most-fours?player=Chris%20Gayle")

    assert sixes_response.status_code == 200
    assert fours_response.status_code == 200
    assert all(
        "COALESCE(d.non_boundary, FALSE) = FALSE" in query
        for query in captured_queries
    )


def test_title_counts_groups_normalized_team_names(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Delhi Capitals", 1)]

    monkeypatch.setattr(
        matches_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/matches/title-counts")

    assert response.status_code == 200
    assert "Delhi Daredevils" in captured_query[-1]
    assert "GROUP BY team" in captured_query[-1]


def test_most_successful_team_uses_decided_matches_for_losses(monkeypatch):
    captured_queries = []
    rows = iter([
        [("Delhi Capitals", 100)],
        [(220, 200)]
    ])

    def fake_execute_query(query, values=None):
        captured_queries.append(query)
        return next(rows)

    monkeypatch.setattr(
        matches_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/matches/most-successful-team")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["data"]["losses"] == 100
    assert payload["data"]["win_percentage"] == 50.0
    assert "decided_matches" in captured_queries[-1]


def test_highest_run_chases_uses_second_innings_not_team2(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [(
            2024,
            "Royal Challengers Bangalore",
            "Chennai Super Kings",
            "M Chinnaswamy Stadium",
            "Bengaluru",
            201,
            "Royal Challengers Bangalore",
            4,
            "2024-05-18"
        )]

    monkeypatch.setattr(
        matches_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/matches/highest-run-chases")

    assert response.status_code == 200
    assert "WITH innings_totals AS" in captured_query[-1]
    assert "i2.batting_team AS chasing_team" in captured_query[-1]
    assert "team2 AS chasing_team" not in captured_query[-1]


def test_highest_successful_chases_excludes_retired_wickets(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [(
            1,
            2024,
            "Punjab Kings",
            262,
            262,
            8,
            "Eden Gardens",
            "Kolkata",
            "2024-04-26",
            "Punjab Kings"
        )]

    monkeypatch.setattr(
        matches_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/matches/highest-successful-chases")

    assert response.status_code == 200
    assert "retired hurt" in captured_query[-1]
    assert "retired out" in captured_query[-1]


def test_player_summary_uses_correct_batting_and_bowling_calculations(monkeypatch):
    captured_queries = []
    captured_values = []
    rows = iter([
        [(10,)],
        [(100, 50, 5, 200.0, 20.0)],
        [(24, 30, 2, 7.5, 12.0)]
    ])

    def fake_execute_query(query, values=None):
        captured_queries.append(query)
        captured_values.append(values)
        return next(rows)

    monkeypatch.setattr(
        players_module,
        "normalize_player",
        lambda player: player
    )
    monkeypatch.setattr(
        players_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/players/player-summary?player=Hardik%20Pandya")

    assert response.status_code == 200
    assert captured_values[1][0] == ("retired hurt",)
    assert captured_values[2][0] == players_module.INVALID_DISMISSALS
    assert captured_values[2][1] == players_module.INVALID_DISMISSALS
    assert "d.extra_type NOT LIKE '%%wides%%'" in captured_queries[1]
    assert "d.extra_type NOT LIKE '%%noballs%%'" in captured_queries[1]
    assert "d.extra_type LIKE '%%byes%%'" in captured_queries[2]
    assert "d.extra_type LIKE '%%legbyes%%'" in captured_queries[2]


def test_best_all_rounders_uses_legal_balls_and_bowler_runs(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Hardik Pandya", 1200, 140.0, 30, 8.0, 40.0)]

    monkeypatch.setattr(
        players_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/players/best-all-rounders")

    assert response.status_code == 200
    assert "d.extra_type NOT LIKE '%%wides%%'" in captured_query[-1]
    assert "d.extra_type NOT LIKE '%%noballs%%'" in captured_query[-1]
    assert "d.extra_type LIKE '%%byes%%'" in captured_query[-1]
    assert "d.extra_type LIKE '%%legbyes%%'" in captured_query[-1]


def test_team_most_wins_groups_normalized_names(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Delhi Capitals", 10)]

    monkeypatch.setattr(
        teams_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/teams/most-wins")

    assert response.status_code == 200
    assert "Delhi Daredevils" in captured_query[-1]
    assert "GROUP BY team" in captured_query[-1]


def test_team_win_percentage_groups_normalized_names(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Punjab Kings", 20, 10, 50.0)]

    monkeypatch.setattr(
        teams_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/teams/win-percentage?team=Punjab%20Kings")

    assert response.status_code == 200
    assert "Kings XI Punjab" in captured_query[-1]
    assert "GROUP BY team_name" in captured_query[-1]


def test_chasing_record_uses_second_innings_team(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Royal Challengers Bengaluru", 10, 6, 4, 60.0)]

    monkeypatch.setattr(
        teams_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/teams/chasing-record")

    assert response.status_code == 200
    assert "WITH innings_teams AS" in captured_query[-1]
    assert "i2.batting_team AS chasing_team" in captured_query[-1]
    assert "team2 AS chasing_team" not in captured_query[-1]


def test_defending_record_uses_first_innings_team(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Chennai Super Kings", 10, 6, 4, 60.0)]

    monkeypatch.setattr(
        teams_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get("/teams/defending-record")

    assert response.status_code == 200
    assert "WITH innings_teams AS" in captured_query[-1]
    assert "i1.batting_team AS defending_team" in captured_query[-1]
    assert "team1 AS defending_team" not in captured_query[-1]


def test_batter_vs_bowler_uses_legal_balls(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Virat Kohli", "Jasprit Bumrah", 10, 15, 1, 150.0, 2, 1)]

    monkeypatch.setattr(
        matchups_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get(
        "/matchups/batter-vs-bowler?batter=Virat%20Kohli&bowler=Jasprit%20Bumrah"
    )

    assert response.status_code == 200
    assert "d.extra_type NOT LIKE '%%wides%%'" in captured_query[-1]
    assert "d.extra_type NOT LIKE '%%noballs%%'" in captured_query[-1]


def test_bowler_vs_team_excludes_byes_from_bowler_runs(monkeypatch):
    captured_query = []

    def fake_execute_query(query, values=None):
        captured_query.append(query)
        return [("Jasprit Bumrah", "Chennai Super Kings", 24, 30, 2, 7.5, 12.0, 15.0)]

    monkeypatch.setattr(
        matchups_module,
        "execute_query",
        fake_execute_query
    )

    client = make_client()

    response = client.get(
        "/matchups/bowler-vs-team?bowler=Jasprit%20Bumrah&team=Chennai%20Super%20Kings"
    )

    assert response.status_code == 200
    assert "d.extra_type LIKE '%%byes%%'" in captured_query[-1]
    assert "d.extra_type LIKE '%%legbyes%%'" in captured_query[-1]


def test_public_json_apis_use_standard_response_shape():
    client = make_client()

    for endpoint in (
        "/matches?limit=1",
        "/teams/most-wins?limit=1",
        "/batting/most-runs?limit=1"
    ):
        response = client.get(endpoint)

        assert response.status_code == 200
        payload = response.get_json()
        assert set(("success", "message", "data")).issubset(payload)


def test_documented_example_requests_are_valid():
    client = make_client()

    for category, apis in API_DOCS.items():
        for api in apis:
            response = client.get(api["example_request"])

            assert response.status_code < 400, (
                category,
                api["id"],
                api["example_request"],
                response.status_code
            )
