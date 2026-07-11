from app import create_app
import routes.players as players_module
import routes.teams as teams_module
import routes.seasons as seasons_module
import routes.venues as venues_module
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
