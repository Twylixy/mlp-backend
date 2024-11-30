import pandas as pd
from parser import WeatherData


def get_metrics(data: list[WeatherData]) -> pd.DataFrame:
    df = pd.DataFrame([item.model_dump() for item in data])

    df["temp_mean"] = (df["temperature_day"] + df["temperature_night"]) / 2
    df["temp_max"] = df["temperature_day"]
    df["temp_min"] = df["temperature_night"]

    df["pressure_mean"] = df["pressure"]
    df["humidity_mean"] = df["humidity"]
    df["wind_speed_mean"] = df["wind_speed"]

    lags = [1, 2, 3]
    for lag in lags:
        for col in [
            "temp_mean",
            "temp_max",
            "temp_min",
            "pressure_mean",
            "humidity_mean",
            "wind_speed_mean",
        ]:
            df[f"{col}_lag{lag}"] = df[col].shift(lag)

    df["Day"] = df["day"].dt.day
    df["Month"] = df["day"].dt.month
    df["Year"] = df["day"].dt.year

    df.dropna(inplace=True)
    return df
