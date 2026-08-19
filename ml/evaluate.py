import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.preprocessing import FEATURE_COLUMNS

def evaluate_saved_model(models_dir: str = os.path.join("ml", "models"), test_data_path: str = os.path.join("data", "ml_safety_dataset.csv")):
    model_path = os.path.join(models_dir, "safety_model.joblib")
    prep_path = os.path.join(models_dir, "preprocessor.joblib")

    if not os.path.exists(model_path) or not os.path.exists(prep_path):
        print("Model or preprocessor artifact missing. Please run ml/train.py first.")
        return

    rf_model = joblib.load(model_path)
    preprocessor = joblib.load(prep_path)

    df = pd.read_csv(test_data_path)
    X = df[FEATURE_COLUMNS]
    y = df["risk_score"]

    X_scaled = preprocessor.transform(X)
    y_pred = rf_model.predict(X_scaled)

    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)

    print("=== Saved Model Evaluation Report ===")
    print(f"Total Samples Evaluated: {len(y)}")
    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²:   {r2:.4f}")
    return {"mae": mae, "rmse": rmse, "r2": r2}

if __name__ == "__main__":
    evaluate_saved_model()
