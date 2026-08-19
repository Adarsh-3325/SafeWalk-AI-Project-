import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.preprocessing import SafetyFeaturePreprocessor, FEATURE_COLUMNS

def train_safety_model(
    data_path: str = os.path.join("data", "ml_safety_dataset.csv"),
    models_dir: str = os.path.join("ml", "models")
):
    print(f"Loading safety dataset from {data_path}...")
    if not os.path.exists(data_path):
        from ml.generate_dataset import generate_synthetic_safety_dataset
        df = generate_synthetic_safety_dataset(num_samples=10000)
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        df.to_csv(data_path, index=False)
    else:
        df = pd.read_csv(data_path)

    X = df[FEATURE_COLUMNS]
    y = df["risk_score"]

    print(f"Dataset shape: {df.shape}")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Fit Preprocessor
    print("Fitting preprocessor pipeline...")
    preprocessor = SafetyFeaturePreprocessor()
    X_train_scaled = preprocessor.fit_transform(X_train)
    X_test_scaled = preprocessor.transform(X_test)

    # Train Random Forest Regressor
    print("Training RandomForestRegressor model...")
    rf_model = RandomForestRegressor(
        n_estimators=150,
        max_depth=15,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train_scaled, y_train)

    # Predictions & Evaluation
    y_pred = rf_model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("\n--- Model Evaluation Results ---")
    print(f"Mean Absolute Error (MAE):  {mae:.4f}")
    print(f"Root Mean Sq Error (RMSE): {rmse:.4f}")
    print(f"R-squared (R²):            {r2:.4f}")

    # Feature Importance Breakdown
    importances = rf_model.feature_importances_
    feature_importance_dict = dict(zip(FEATURE_COLUMNS, importances))
    sorted_importances = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)

    print("\n--- Feature Importances ---")
    for feat, imp in sorted_importances:
        print(f"  {feat:30s}: {imp:.4f}")

    # Save Model Artifacts
    os.makedirs(models_dir, exist_ok=True)
    
    # Also save to backend/app/ml/models/ if exists or create
    backend_models_dir = os.path.join("backend", "app", "ml", "models")
    os.makedirs(backend_models_dir, exist_ok=True)

    model_path = os.path.join(models_dir, "safety_model.joblib")
    prep_path = os.path.join(models_dir, "preprocessor.joblib")
    meta_path = os.path.join(models_dir, "feature_metadata.json")

    joblib.dump(rf_model, model_path)
    joblib.dump(preprocessor, prep_path)

    # Mirror to backend dir
    joblib.dump(rf_model, os.path.join(backend_models_dir, "safety_model.joblib"))
    joblib.dump(preprocessor, os.path.join(backend_models_dir, "preprocessor.joblib"))

    metadata = {
        "model_type": "RandomForestRegressor",
        "n_estimators": 150,
        "metrics": {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2)
        },
        "feature_names": FEATURE_COLUMNS,
        "feature_importances": {k: float(v) for k, v in feature_importance_dict.items()}
    }

    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    with open(os.path.join(backend_models_dir, "feature_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nModel artifacts successfully saved to {models_dir} and {backend_models_dir}")
    return rf_model, preprocessor, metadata

if __name__ == "__main__":
    train_safety_model()
