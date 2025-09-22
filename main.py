"""
main.py
Main script to run the NBA prediction pipeline and provide a CLI for team matchup prediction.
"""
from database import setup_database
from data_loader import load_data, preprocess_data
from model import NBAPredictor

import numpy as np

def main():
    print("NBA Prediction Program")
    print("Would you like to use real NBA data (from balldontlie API) or fictional data?")
    choice = input("Type 'real' for real NBA data, or anything else for fictional: ").strip().lower()
    use_real = choice == 'real'
    num_games = 100
    api_key = None
    if use_real:
        try:
            num_games = int(input("How many recent games to fetch? (e.g., 100): ").strip())
        except Exception:
            num_games = 100
        api_key = input("If you have a balldontlie API key, enter it here (or press Enter to skip): ").strip()
        if not api_key:
            api_key = None
    print("Setting up database and loading data...")
    setup_database(use_real_data=use_real, num_games=num_games, api_key=api_key)
    teams_df, players_df, games_df = load_data()
    teams_df, players_df, games_df = preprocess_data(teams_df, players_df, games_df)

    # Only allow teams that appear in the games data
    valid_team_ids = set(games_df['home_team_id']).union(set(games_df['away_team_id']))
    valid_teams_df = teams_df[teams_df['id'].isin(valid_team_ids)]

    print("\nTeams (only those present in the games data):")
    for idx, row in valid_teams_df.iterrows():
        print(f"{row['id']}: {row['city']} {row['name']}")

    predictor = NBAPredictor()
    predictor.fit(games_df)

    # Calculate average total points for prediction
    avg_total = np.mean(games_df['home_score'] + games_df['away_score'])

    while True:
        print("\nEnter the IDs of two teams to simulate a matchup (or 'q' to quit):")
        home_id = input("Home team ID: ").strip()
        if home_id.lower() == 'q':
            break
        away_id = input("Away team ID: ").strip()
        if away_id.lower() == 'q':
            break
        try:
            home_id = int(home_id)
            away_id = int(away_id)
            if home_id == away_id:
                print("Teams must be different!")
                continue
            if home_id not in valid_team_ids or away_id not in valid_team_ids:
                print("Invalid team IDs. Please select from the teams listed above.")
                continue
            home_score, away_score = predictor.predict_scores(home_id, away_id, avg_total)
            print(f"\nPredicted Final Score:")
            print(f"{valid_teams_df.loc[valid_teams_df['id'] == home_id, 'name'].values[0]}: {home_score:.1f}")
            print(f"{valid_teams_df.loc[valid_teams_df['id'] == away_id, 'name'].values[0]}: {away_score:.1f}")
        except Exception as e:
            print(f"Error: {e}. Please enter valid numeric team IDs.")

if __name__ == "__main__":
    main()
