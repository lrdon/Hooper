"""
model.py
Module for training and using a simple ML model to predict NBA game outcomes.
"""
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from typing import Tuple

class NBAPredictor:
    """
    A simple NBA game outcome predictor using linear regression.
    """
    def __init__(self):
        self.model = LinearRegression()
        self.team_id_map = {}

    def prepare_features(self, games_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target for model training.
        Features: one-hot encoding of home and away team IDs.
        Target: point differential (home_score - away_score).
        """
        # One-hot encode team IDs
        X = pd.get_dummies(games_df[['home_team_id', 'away_team_id']].astype(str), columns=['home_team_id', 'away_team_id'])
        y = games_df['home_score'] - games_df['away_score']
        return X, y

    def fit(self, games_df: pd.DataFrame):
        """
        Train the model on historical games data.
        """
        X, y = self.prepare_features(games_df)
        self.model.fit(X, y)
        self.feature_columns = X.columns  # Save for prediction

    def predict(self, home_team_id: int, away_team_id: int) -> float:
        """
        Predict the point differential for a given matchup.
        Returns the predicted (home_score - away_score).
        """
        # Create a single-row DataFrame with the same columns as training
        data = {col: 0 for col in self.feature_columns}
        data[f'home_team_id_{home_team_id}'] = 1
        data[f'away_team_id_{away_team_id}'] = 1
        X_pred = pd.DataFrame([data])
        return self.model.predict(X_pred)[0]

    def predict_scores(self, home_team_id: int, away_team_id: int, avg_total: float = 200.0) -> Tuple[float, float]:
        """
        Predict the likely final scores for a matchup, given average total points.
        Returns (home_score, away_score).
        """
        diff = self.predict(home_team_id, away_team_id)
        # Split avg_total based on predicted differential
        home_score = (avg_total + diff) / 2
        away_score = (avg_total - diff) / 2
        return home_score, away_score
