import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin

FEATURE_COLUMNS = [
    "crime_incident_count",
    "crime_density",
    "weighted_crime_severity",
    "min_dist_recent_crime_m",
    "lighting_score_avg",
    "dark_segment_pct",
    "crowd_density_avg",
    "isolated_segment_pct",
    "temp_celsius",
    "visibility_km",
    "precipitation_mm",
    "weather_severity",
    "hour_of_day",
    "is_weekend",
    "is_night",
    "is_peak_hour",
    "user_report_count",
    "weighted_user_reports",
    "report_density"
]

class SafetyFeaturePreprocessor(BaseEstimator, TransformerMixin):
    """
    Reproducible feature preprocessor pipeline for the route safety model.
    Handles missing value imputation, outlier clipping, and feature scaling.
    """
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names = FEATURE_COLUMNS
        self.is_fitted = False

    def fit(self, X: pd.DataFrame, y=None):
        X_clean = self._clean_data(X)
        self.scaler.fit(X_clean[self.feature_names])
        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("SafetyFeaturePreprocessor must be fitted before transforming data.")
        X_clean = self._clean_data(X)
        return self.scaler.transform(X_clean[self.feature_names])

    def fit_transform(self, X: pd.DataFrame, y=None) -> np.ndarray:
        return self.fit(X, y).transform(X)

    def _clean_data(self, X: pd.DataFrame) -> pd.DataFrame:
        df = X.copy()
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0.0
        
        # Fill missing values with domain defaults
        df["crime_incident_count"] = df["crime_incident_count"].fillna(0)
        df["crime_density"] = df["crime_density"].fillna(0.0)
        df["weighted_crime_severity"] = df["weighted_crime_severity"].fillna(0.0)
        df["min_dist_recent_crime_m"] = df["min_dist_recent_crime_m"].fillna(1000.0)
        df["lighting_score_avg"] = df["lighting_score_avg"].fillna(75.0)
        df["dark_segment_pct"] = df["dark_segment_pct"].fillna(10.0)
        df["crowd_density_avg"] = df["crowd_density_avg"].fillna(50.0)
        df["isolated_segment_pct"] = df["isolated_segment_pct"].fillna(10.0)
        df["temp_celsius"] = df["temp_celsius"].fillna(20.0)
        df["visibility_km"] = df["visibility_km"].fillna(10.0)
        df["precipitation_mm"] = df["precipitation_mm"].fillna(0.0)
        df["weather_severity"] = df["weather_severity"].fillna(0.0)
        df["hour_of_day"] = df["hour_of_day"].fillna(12)
        df["is_weekend"] = df["is_weekend"].fillna(0)
        df["is_night"] = df["is_night"].fillna(0)
        df["is_peak_hour"] = df["is_peak_hour"].fillna(0)
        df["user_report_count"] = df["user_report_count"].fillna(0)
        df["weighted_user_reports"] = df["weighted_user_reports"].fillna(0.0)
        df["report_density"] = df["report_density"].fillna(0.0)

        # Clip values to valid domains
        df["min_dist_recent_crime_m"] = np.clip(df["min_dist_recent_crime_m"], 0, 10000)
        df["lighting_score_avg"] = np.clip(df["lighting_score_avg"], 0, 100)
        df["crowd_density_avg"] = np.clip(df["crowd_density_avg"], 0, 100)

        return df
