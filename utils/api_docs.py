# =========================================
# IPL API DOCUMENTATION METADATA
# =========================================

SEASONS = list(range(2008, 2027))

API_DOCS = {

    # =====================================
    # BATTING APIs
    # =====================================

    "batting": [

        {
            "id": "most-runs",
            "title": "Most Runs",
            "route": "/batting/most-runs",
            "method": "GET",
            "description": "Returns batters with highest IPL runs.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "highest-score",
            "title": "Highest Individual Score",
            "route": "/batting/highest-score",
            "method": "GET",
            "description": "Returns highest individual batting scores.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "strike-rate",
            "title": "Batting Strike Rate",
            "route": "/batting/strike-rate",
            "method": "GET",
            "description": "Returns batting strike rates.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "batting-average",
            "title": "Batting Average",
            "route": "/batting/batting-average",
            "method": "GET",
            "description": "Returns batting averages.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "most-sixes",
            "title": "Most Sixes",
            "route": "/batting/most-sixes",
            "method": "GET",
            "description": "Returns players with most sixes.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "most-fours",
            "title": "Most Fours",
            "route": "/batting/most-fours",
            "method": "GET",
            "description": "Returns players with most fours.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "orange-cap-by-season",
            "title": "Orange Cap By Season",
            "route": "/batting/orange-cap-by-season",
            "method": "GET",
            "description": "Returns Orange Cap winners by season.",
            "query_params": []
        },

        {
            "id": "most-50s",
            "title": "Most Fifties",
            "route": "/batting/most-50s",
            "method": "GET",
            "description": "Returns players with most 50s.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "most-100s",
            "title": "Most Hundreds",
            "route": "/batting/most-100s",
            "method": "GET",
            "description": "Returns players with most centuries.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        }
    ],

    # =====================================
    # BOWLING APIs
    # =====================================

    "bowling": [

        {
            "id": "most-wickets",
            "title": "Most Wickets",
            "route": "/bowling/most-wickets",
            "method": "GET",
            "description": "Returns bowlers with most wickets.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "economy",
            "title": "Bowling Economy",
            "route": "/bowling/economy",
            "method": "GET",
            "description": "Returns bowling economy rates.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "strike-rate",
            "title": "Bowling Strike Rate",
            "route": "/bowling/strike-rate",
            "method": "GET",
            "description": "Returns bowling strike rates.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "average",
            "title": "Bowling Average",
            "route": "/bowling/average",
            "method": "GET",
            "description": "Returns bowling averages.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "best-figures",
            "title": "Best Bowling Figures",
            "route": "/bowling/best-figures",
            "method": "GET",
            "description": "Returns best bowling figures.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "purple-cap",
            "title": "Purple Cap",
            "route": "/bowling/purple-cap",
            "method": "GET",
            "description": "Returns Purple Cap winner.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "purple-cap-by-season",
            "title": "Purple Cap By Season",
            "route": "/bowling/purple-cap-by-season",
            "method": "GET",
            "description": "Returns Purple Cap winners by season.",
            "query_params": []
        }
    ],

    # =====================================
    # MATCHUP APIs
    # =====================================

    "matchups": [

        {
            "id": "batter-vs-bowler",
            "title": "Batter vs Bowler",
            "route": "/matchups/batter-vs-bowler",
            "method": "GET",
            "description": "Returns batter vs bowler stats.",
            "query_params": [
                {
                    "name": "batter",
                    "type": "string",
                    "required": True
                },
                {
                    "name": "bowler",
                    "type": "string",
                    "required": True
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "batter-vs-team",
            "title": "Batter vs Team",
            "route": "/matchups/batter-vs-team",
            "method": "GET",
            "description": "Returns batter vs team stats.",
            "query_params": [
                {
                    "name": "batter",
                    "type": "string",
                    "required": True
                },
                {
                    "name": "team",
                    "type": "string",
                    "required": True
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "bowler-vs-team",
            "title": "Bowler vs Team",
            "route": "/matchups/bowler-vs-team",
            "method": "GET",
            "description": "Returns bowler vs team stats.",
            "query_params": [
                {
                    "name": "bowler",
                    "type": "string",
                    "required": True
                },
                {
                    "name": "team",
                    "type": "string",
                    "required": True
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        }
    ],

    # =====================================
    # PLAYER APIs
    # =====================================

    "players": [

        {
            "id": "player-search",
            "title": "Player Search",
            "route": "/players/search",
            "method": "GET",
            "description": "Searches valid player names available in IPL batting and bowling data.",
            "query_params": [
                {
                    "name": "player_name",
                    "type": "string",
                    "required": True
                },
                {
                    "name": "role",
                    "type": "string",
                    "required": False,
                    "allowed_values": [
                        "all",
                        "batter",
                        "bowler"
                    ]
                },
                {
                    "name": "limit",
                    "type": "integer",
                    "required": False,
                    "default": 10,
                    "max": 50
                }
            ]
        },

        {
            "id": "player-summary",
            "title": "Player Summary",
            "route": "/players/player-summary",
            "method": "GET",
            "description": "Returns player summary.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": True
                }
            ]
        },

        {
            "id": "player-of-the-match",
            "title": "Player Of The Match",
            "route": "/players/player-of-the-match",
            "method": "GET",
            "description": "Returns player of match awards.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "player-career-span",
            "title": "Player Career Span",
            "route": "/players/player-career-span",
            "method": "GET",
            "description": "Returns player career span.",
            "query_params": [
                {
                    "name": "player",
                    "type": "string",
                    "required": True
                }
            ]
        },

        {
            "id": "best-all-rounders",
            "title": "Best All Rounders",
            "route": "/players/best-all-rounders",
            "method": "GET",
            "description": "Returns best all rounders.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                },
                {
                    "name": "player",
                    "type": "string",
                    "required": False
                }
            ]
        }
    ],

    # =====================================
    # SEASON APIs
    # =====================================

    "seasons": [

        {
            "id": "season-summary",
            "title": "Season Summary",
            "route": "/seasons/{season}/summary",
            "method": "GET",
            "description": "Returns a season-level overview including final, champion, top batter, top bowler, and highest team total.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": True,
                    "location": "path",
                    "example": 2024,
                    "allowed_values": SEASONS
                }
            ]
        }
    ],

    # =====================================
    # VENUE APIs
    # =====================================

    "venues": [

        {
            "id": "venue-stats",
            "title": "Venue Stats",
            "route": "/venues/stats",
            "method": "GET",
            "description": "Returns venue-level IPL stats including matches, seasons, average first innings score, chasing/defending wins, highest total, and top teams.",
            "query_params": [
                {
                    "name": "venue_name",
                    "type": "string",
                    "required": True,
                    "example": "Wankhede Stadium"
                }
            ]
        }
    ],

    # =====================================
    # TEAM APIs
    # =====================================

    "teams": [

        {
            "id": "team-search",
            "title": "Team Search",
            "route": "/teams/search",
            "method": "GET",
            "description": "Searches valid team names available in IPL match data.",
            "query_params": [
                {
                    "name": "team_name",
                    "type": "string",
                    "required": True
                },
                {
                    "name": "limit",
                    "type": "integer",
                    "required": False,
                    "default": 10,
                    "max": 50
                }
            ]
        },

        {
            "id": "most-wins",
            "title": "Most Wins",
            "route": "/teams/most-wins",
            "method": "GET",
            "description": "Returns teams with most wins.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "win-percentage",
            "title": "Win Percentage",
            "route": "/teams/win-percentage",
            "method": "GET",
            "description": "Returns win percentage.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                },
                {
                    "name": "team",
                    "type": "string",
                    "required": False
                }
            ]
        },

        {
            "id": "playoff-record",
            "title": "Playoff Record",
            "route": "/teams/playoff-record",
            "method": "GET",
            "description": "Returns playoff record.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                },
                {
                    "name": "team",
                    "type": "string",
                    "required": False
                }
            ]
        },

        {
            "id": "finals-record",
            "title": "Finals Record",
            "route": "/teams/finals-record",
            "method": "GET",
            "description": "Returns finals record.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                },
                {
                    "name": "team",
                    "type": "string",
                    "required": False
                }
            ]
        },

        {
            "id": "chasing-record",
            "title": "Chasing Record",
            "route": "/teams/chasing-record",
            "method": "GET",
            "description": "Returns chasing record.",
            "query_params": [
                {
                    "name": "team",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "defending-record",
            "title": "Defending Record",
            "route": "/teams/defending-record",
            "method": "GET",
            "description": "Returns defending record.",
            "query_params": [
                {
                    "name": "team",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        }
    ],

    # =====================================
    # MATCH APIs
    # =====================================

    "matches": [

        {
            "id": "all-matches",
            "title": "All Matches",
            "route": "/matches",
            "method": "GET",
            "description": "Returns all matches.",
            "query_params": [
                {
                    "name": "limit",
                    "type": "integer",
                    "required": False
                }
            ]
        },

        {
            "id": "matches-by-season",
            "title": "Matches By Season",
            "route": "/matches/season/<int:season>",
            "method": "GET",
            "description": "Returns matches by season.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": True,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "filter-matches",
            "title": "Filter Matches",
            "route": "/matches/filter",
            "method": "GET",
            "description": "Filters matches.",
            "query_params": [
                {
                    "name": "team",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "city",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "winner",
                    "type": "string",
                    "required": False
                },
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "head-to-head",
            "title": "Head To Head",
            "route": "/matches/head-to-head",
            "method": "GET",
            "description": "Returns head to head stats.",
            "query_params": [
                {
                    "name": "team1",
                    "type": "string",
                    "required": True
                },
                {
                    "name": "team2",
                    "type": "string",
                    "required": True
                }
            ]
        },

        {
            "id": "title-winners",
            "title": "Title Winners",
            "route": "/matches/title-winners",
            "method": "GET",
            "description": "Returns IPL title winners.",
            "query_params": []
        },

        {
            "id": "title-counts",
            "title": "Title Counts",
            "route": "/matches/title-counts",
            "method": "GET",
            "description": "Returns IPL title counts.",
            "query_params": []
        },

        {
            "id": "most-successful-team",
            "title": "Most Successful Team",
            "route": "/matches/most-successful-team",
            "method": "GET",
            "description": "Returns most successful IPL team.",
            "query_params": []
        },

        {
            "id": "all-teams",
            "title": "All Teams",
            "route": "/teams",
            "method": "GET",
            "description": "Returns all IPL teams.",
            "query_params": []
        },

        {
            "id": "highest-run-chases",
            "title": "Highest Run Chases",
            "route": "/matches/highest-run-chases",
            "method": "GET",
            "description": "Returns highest run chases.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                },
                {
                    "name": "team",
                    "type": "string",
                    "required": False
                }
            ]
        },

        {
            "id": "highest-team-totals",
            "title": "Highest Team Totals",
            "route": "/matches/highest-team-totals",
            "method": "GET",
            "description": "Returns highest team totals.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                },
                {
                    "name": "team",
                    "type": "string",
                    "required": False
                }
            ]
        },

        {
            "id": "lowest-defended-scores",
            "title": "Lowest Defended Scores",
            "route": "/matches/lowest-defended-scores",
            "method": "GET",
            "description": "Returns lowest defended scores.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                },
                {
                    "name": "team",
                    "type": "string",
                    "required": False
                }
            ]
        },

        {
            "id": "lowest-team-totals",
            "title": "Lowest Team Totals",
            "route": "/matches/lowest-team-totals",
            "method": "GET",
            "description": "Returns lowest team totals.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                },
                {
                    "name": "team",
                    "type": "string",
                    "required": False
                }
            ]
        },

        {
            "id": "closest-finishes",
            "title": "Closest Finishes",
            "route": "/matches/closest-finishes",
            "method": "GET",
            "description": "Returns closest IPL finishes.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                }
            ]
        },

        {
            "id": "super-over-matches",
            "title": "Super Over Matches",
            "route": "/matches/super-over-matches",
            "method": "GET",
            "description": "Returns super over matches.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                },
                {
                    "name": "team",
                    "type": "string",
                    "required": False
                }
            ]
        },

        {
            "id": "highest-successful-chases",
            "title": "Highest Successful Chases",
            "route": "/matches/highest-successful-chases",
            "method": "GET",
            "description": "Returns highest successful chases.",
            "query_params": [
                {
                    "name": "season",
                    "type": "integer",
                    "required": False,
                    "allowed_values": SEASONS
                },
                {
                    "name": "team",
                    "type": "string",
                    "required": False
                }
            ]
        }
    ]
}
