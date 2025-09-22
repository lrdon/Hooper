"""
data_loader.py
Module to load and preprocess NBA data from the SQLite database into pandas DataFrames.
"""
import sqlite3
import pandas as pd
from typing import Tuple

DB_NAME = 'nba.db'

def load_data(db_name: str = DB_NAME) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load Teams, Players, and Games tables from the SQLite database into pandas DataFrames.
    Returns:
        teams_df, players_df, games_df: DataFrames for each table.
    """
    conn = sqlite3.connect(db_name)
    teams_df = pd.read_sql_query('SELECT * FROM Teams', conn)
    players_df = pd.read_sql_query('SELECT * FROM Players', conn)
    games_df = pd.read_sql_query('SELECT * FROM Games', conn)
    conn.close()
    return teams_df, players_df, games_df

def preprocess_data(teams_df: pd.DataFrame, players_df: pd.DataFrame, games_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Perform basic data cleaning and preprocessing.
    For this fictional dataset, just ensure no missing values and correct types.
    """
    teams_df = teams_df.drop_duplicates().fillna('Unknown')
    players_df = players_df.drop_duplicates().fillna('Unknown')
    games_df = games_df.drop_duplicates().fillna(0)
    # Convert scores to int
    games_df['home_score'] = games_df['home_score'].astype(int)
    games_df['away_score'] = games_df['away_score'].astype(int)
    return teams_df, players_df, games_df
