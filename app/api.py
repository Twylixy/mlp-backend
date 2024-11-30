from datetime import datetime
from app.metrics import get_metrics
from app.parser import get_weather_data, WeatherData
from app.redis import redis_conn
from pydantic import BaseModel


class PredictionForDay(BaseModel):
    day: datetime
    predicted_number: float
    accuracy: float


class PredictionReport(BaseModel):
    predictions: list[PredictionForDay]


async def predict() -> PredictionReport:
    weather_data = redis_conn.get("weather_data")

    if weather_data:
        weather_data = []
        for wd in weather_data:
            weather_data.append(WeatherData.model_validate_json(wd))
    else:
        weather_data = get_weather_data()

    metrics = get_metrics(weather_data)

    # Здесь передаем всё в модель, она предсказывает
    # Её результат нужно подогнать под ответ бека "PredictionReport",
    # а точнее под PredictionForDay

    # В результате возврат будет такой:
    # return PredictionReport(predictions=[PredictionForDay(), ...])
