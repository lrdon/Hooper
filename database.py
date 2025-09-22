"""
database.py
Module to handle SQLite database creation and population for a fictional NBA dataset.
"""
import sqlite3
from typing import Optional
import requests
import time

DB_NAME = 'nba.db'
BALLDONTLIE_API = 'https://api.balldontlie.io/v1/'

def create_connection(db_name: Optional[str] = None):
    """
    Create a database connection to the SQLite database specified by db_name.
    """
    conn = sqlite3.connect(db_name or DB_NAME)
    return conn

def create_tables(conn):
    """
    Create Teams, Players, and Games tables in the database.
    """
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            team_id INTEGER,
            position TEXT,
            FOREIGN KEY (team_id) REFERENCES Teams(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            home_team_id INTEGER,
            away_team_id INTEGER,
            home_score INTEGER,
            away_score INTEGER,
            FOREIGN KEY (home_team_id) REFERENCES Teams(id),
            FOREIGN KEY (away_team_id) REFERENCES Teams(id)
        )
    ''')
    conn.commit()

def populate_tables(conn):
    """
    Populate the Teams, Players, and Games tables with fictional data.
    """
    cursor = conn.cursor()
    # Insert fictional teams
    teams = [
        ('Dragons', 'Atlantis'),
        ('Wolves', 'Moon City'),
        ('Sharks', 'Coral Bay'),
        ('Falcons', 'Skyville')
    ]
    cursor.executemany('INSERT INTO Teams (name, city) VALUES (?, ?)', teams)
    # Insert fictional players
    players = [
        ('Alex Storm', 1, 'Guard'),
        ('Blake Moon', 2, 'Forward'),
        ('Casey Wave', 3, 'Center'),
        ('Drew Sky', 4, 'Guard'),
        ('Eli Blaze', 1, 'Forward'),
        ('Finn Tide', 3, 'Guard'),
        ('Gale Hawk', 4, 'Center'),
        ('Harper Wolf', 2, 'Center')
    ]
    cursor.executemany('INSERT INTO Players (name, team_id, position) VALUES (?, ?, ?)', players)
    # Insert fictional games
    games = [
        ('2023-01-01', 1, 2, 102, 98),
        ('2023-01-02', 3, 4, 110, 105),
        ('2023-01-03', 1, 3, 99, 101),
        ('2023-01-04', 2, 4, 95, 100),
        ('2023-01-05', 4, 1, 108, 112),
        ('2023-01-06', 2, 3, 104, 107)
    ]
    cursor.executemany('INSERT INTO Games (date, home_team_id, away_team_id, home_score, away_score) VALUES (?, ?, ?, ?, ?)', games)
    conn.commit()

def fetch_teams_from_api(api_key=None):
    """
    Fetch NBA teams from the balldontlie API. Optionally use an API key.
    Returns a list of dicts with keys: id, abbreviation, city, conference, division, full_name, name.
    """
    headers = {"Authorization": api_key} if api_key else {}
    resp = requests.get(BALLDONTLIE_API + 'teams', headers=headers)
    resp.raise_for_status()
    return resp.json()['data']

def fetch_games_from_api(num_games=100, api_key=None):
    """
    Fetch recent NBA games from the balldontlie API. Optionally use an API key.
    Returns a list of dicts with game info.
    """
    games = []
    per_page = 100  # max allowed by API
    page = 1
    headers = {"Authorization": api_key} if api_key else {}
    while len(games) < num_games:
        resp = requests.get(BALLDONTLIE_API + f'games', params={'per_page': per_page, 'page': page}, headers=headers)
        resp.raise_for_status()
        data = resp.json()['data']
        if not data:
            break
        games.extend(data)
        page += 1
        time.sleep(0.2)  # be nice to the API
    return games[:num_games]

def populate_tables_from_api(conn, num_games=100, api_key=None):
    """
    Populate Teams and Games tables with real NBA data from the balldontlie API. Optionally use an API key.
    """
    cursor = conn.cursor()
    # Fetch and insert teams
    teams = fetch_teams_from_api(api_key=api_key)
    cursor.execute('DELETE FROM Teams')
    for t in teams:
        cursor.execute('INSERT OR IGNORE INTO Teams (id, name, city) VALUES (?, ?, ?)', (t['id'], t['name'], t['city']))
    # Fetch and insert games
    games = fetch_games_from_api(num_games, api_key=api_key)
    cursor.execute('DELETE FROM Games')
    for g in games:
        if g['home_team_score'] is not None and g['visitor_team_score'] is not None:
            cursor.execute('''INSERT INTO Games (date, home_team_id, away_team_id, home_score, away_score) VALUES (?, ?, ?, ?, ?)''',
                (g['date'][:10], g['home_team']['id'], g['visitor_team']['id'], g['home_team_score'], g['visitor_team_score']))
    conn.commit()

def setup_database(use_real_data=False, num_games=100, api_key=None):
    """
    Create and populate the database. If use_real_data is True, fetch from API. Optionally use an API key.
    """
    conn = create_connection()
    create_tables(conn)
    if use_real_data:
        populate_tables_from_api(conn, num_games=num_games, api_key=api_key)
    else:
        populate_tables(conn)
    conn.close()

if __name__ == "__main__":
    setup_database()
