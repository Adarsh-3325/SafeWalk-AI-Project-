import os
import numpy as np
import pandas as pd

def generate_synthetic_safety_dataset(num_samples: int = 10000, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic training dataset for route risk estimation.
    Features model domain relationships:
    - Higher crime & severity -> higher risk
    - Low lighting & night time -> multiplied higher risk
    - Isolated segments (low crowd) -> higher risk
    - Adverse weather & visibility -> moderate risk increase
    - Negative user reports -> higher risk
    """
    np.random.seed(random_seed)

    # 1. Crime Features
    crime_incident_count = np.random.poisson(lam=8, size=num_samples)
    crime_density = np.random.gamma(shape=2.0, scale=1.5, size=num_samples) # incidents per km^2
    weighted_crime_severity = np.random.uniform(0, 100, size=num_samples)
    min_dist_recent_crime_m = np.random.exponential(scale=300, size=num_samples) + 10.0

    # 2. Lighting Features
    lighting_score_avg = np.random.beta(a=5, b=2, size=num_samples) * 100 # skewed towards higher lighting in urban areas
    dark_segment_pct = np.random.uniform(0, 80, size=num_samples)

    # 3. Crowd Density Features
    crowd_density_avg = np.random.uniform(10, 95, size=num_samples)
    isolated_segment_pct = np.random.uniform(0, 60, size=num_samples)

    # 4. Weather Features
    temp_celsius = np.random.normal(loc=18, scale=8, size=num_samples)
    visibility_km = np.random.uniform(1.0, 15.0, size=num_samples)
    precipitation_mm = np.random.exponential(scale=2.0, size=num_samples)
    weather_severity = np.clip(precipitation_mm * 1.5 + (15.0 - visibility_km) * 0.5, 0, 10)

    # 5. Time Features
    hour_of_day = np.random.randint(0, 24, size=num_samples)
    is_weekend = np.random.choice([0, 1], p=[0.7, 0.3], size=num_samples)
    is_night = ((hour_of_day >= 21) | (hour_of_day < 6)).astype(int)
    is_peak_hour = (((hour_of_day >= 7) & (hour_of_day <= 9)) | ((hour_of_day >= 17) & (hour_of_day <= 19))).astype(int)

    # 6. User Reports Features
    user_report_count = np.random.poisson(lam=2, size=num_samples)
    weighted_user_reports = user_report_count * np.random.uniform(1.0, 5.0, size=num_samples)
    report_density = user_report_count / (np.random.uniform(1.0, 10.0, size=num_samples))

    # 7. Ground Truth Risk Calculation (0 to 100)
    # Risk interactions: Night + Poor Lighting amplifies risk
    night_lighting_penalty = is_night * (dark_segment_pct / 100.0) * 25.0
    isolated_night_penalty = is_night * (isolated_segment_pct / 100.0) * 20.0

    raw_risk = (
        0.30 * weighted_crime_severity +
        0.20 * (100.0 - lighting_score_avg) +
        0.15 * (100.0 - crowd_density_avg) +
        0.10 * np.clip(weighted_user_reports * 4.0, 0, 100) +
        0.10 * night_lighting_penalty +
        0.05 * isolated_night_penalty +
        0.05 * (weather_severity * 10.0) +
        0.05 * np.clip(1000.0 / (min_dist_recent_crime_m + 1.0), 0, 100)
    )

    # Add controlled Gaussian noise to simulate real-world variability
    noise = np.random.normal(loc=0, scale=3.5, size=num_samples)
    risk_score = np.clip(raw_risk + noise, 0, 100)

    df = pd.DataFrame({
        "crime_incident_count": crime_incident_count,
        "crime_density": crime_density,
        "weighted_crime_severity": weighted_crime_severity,
        "min_dist_recent_crime_m": min_dist_recent_crime_m,
        "lighting_score_avg": lighting_score_avg,
        "dark_segment_pct": dark_segment_pct,
        "crowd_density_avg": crowd_density_avg,
        "isolated_segment_pct": isolated_segment_pct,
        "temp_celsius": temp_celsius,
        "visibility_km": visibility_km,
        "precipitation_mm": precipitation_mm,
        "weather_severity": weather_severity,
        "hour_of_day": hour_of_day,
        "is_weekend": is_weekend,
        "is_night": is_night,
        "is_peak_hour": is_peak_hour,
        "user_report_count": user_report_count,
        "weighted_user_reports": weighted_user_reports,
        "report_density": report_density,
        "risk_score": risk_score
    })

    return df

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate_synthetic_safety_dataset(num_samples=10000)
    output_path = os.path.join("data", "ml_safety_dataset.csv")
    df.to_csv(output_path, index=False)
    print(f"Generated synthetic training dataset with {len(df)} records at {output_path}")
