CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    season INTEGER NOT NULL,
    match_date DATE,
    city TEXT,
    venue TEXT,
    team1 TEXT,
    team2 TEXT,
    toss_winner TEXT,
    toss_decision TEXT,
    winner TEXT,
    player_of_match TEXT,
    result_type TEXT,
    result_margin INTEGER,
    target_runs INTEGER,
    target_overs NUMERIC,
    super_over BOOLEAN DEFAULT FALSE,
    match_stage TEXT,
    is_playoff BOOLEAN DEFAULT FALSE,
    umpire1 TEXT,
    umpire2 TEXT
);

CREATE TABLE IF NOT EXISTS deliveries (
    delivery_key TEXT PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    innings INTEGER NOT NULL,
    over_no INTEGER NOT NULL,
    ball_no INTEGER NOT NULL,
    batter TEXT,
    bowler TEXT,
    non_striker TEXT,
    batting_team TEXT,
    bowling_team TEXT,
    batsman_run INTEGER DEFAULT 0,
    extras_run INTEGER DEFAULT 0,
    total_run INTEGER DEFAULT 0,
    extra_type TEXT,
    phase TEXT,
    is_boundary BOOLEAN DEFAULT FALSE,
    is_dot_ball BOOLEAN DEFAULT FALSE,
    non_boundary BOOLEAN DEFAULT FALSE,
    is_super_over BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS wickets (
    delivery_key TEXT NOT NULL REFERENCES deliveries(delivery_key) ON DELETE CASCADE,
    player_out TEXT NOT NULL,
    dismissal_kind TEXT NOT NULL,
    fielders_involved TEXT,
    PRIMARY KEY (delivery_key, player_out, dismissal_kind)
);

CREATE INDEX IF NOT EXISTS idx_matches_season ON matches(season);
CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches(team1, team2);
CREATE INDEX IF NOT EXISTS idx_matches_winner ON matches(winner);
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_deliveries_match_id ON deliveries(match_id);
CREATE INDEX IF NOT EXISTS idx_deliveries_batter ON deliveries(batter);
CREATE INDEX IF NOT EXISTS idx_deliveries_bowler ON deliveries(bowler);
CREATE INDEX IF NOT EXISTS idx_deliveries_batting_team ON deliveries(batting_team);
CREATE INDEX IF NOT EXISTS idx_deliveries_bowling_team ON deliveries(bowling_team);
CREATE INDEX IF NOT EXISTS idx_wickets_delivery_key ON wickets(delivery_key);
CREATE INDEX IF NOT EXISTS idx_wickets_player_out ON wickets(player_out);
