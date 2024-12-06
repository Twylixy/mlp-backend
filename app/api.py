from datetime import datetime
from app.metrics import get_metrics
from app.parser import get_weather_data, WeatherData
from app.redis import redis_conn
from pydantic import BaseModel
import pandas as pd
import numpy as np
from app.globals import loaded_model  
from fastapi import APIRouter # импортирую APIRouter


router = APIRouter() # импортирую APIRouter

class PredictionForDay(BaseModel):
    day: datetime
    predicted_number: float
    accuracy: float


class PredictionReport(BaseModel):
    predictions: list[PredictionForDay]


@router.get("/predict", response_model=PredictionReport) #добавил декоратор
async def predict() -> PredictionReport:
    weather_data = redis_conn.get("weather_data")

    if weather_data:
        weather_data = []
        for wd in weather_data:
            weather_data.append(WeatherData.model_validate_json(wd))
    else:
        weather_data = get_weather_data()

    metrics = get_metrics(weather_data)

    metrics['day'] = pd.to_datetime(metrics['day'])
    metrics['Day_of_Week'] = metrics['day'].dt.dayofweek  # 0 - понедельник, 6 - воскресенье
    metrics['Month'] = metrics['day'].dt.month
    metrics['Year'] = metrics['day'].dt.year
    

    metrics.rename(columns={
        'temp_mean': 'T_mean',
        'temp_max': 'T_max',
        'temp_min': 'T_min',
        'pressure_mean': 'P_mean',
        'humidity_mean': 'U_mean',
        'wind_speed_mean': 'Ff_mean',
        'temp_mean_lag1': 'T_mean_lag1',
        'temp_max_lag1': 'T_max_lag1',
        'temp_min_lag1': 'T_min_lag1',
        'pressure_mean_lag1': 'P_mean_lag1',
        'humidity_mean_lag1': 'U_mean_lag1',
        'wind_speed_mean_lag1': 'Ff_mean_lag1',
        'temp_mean_lag2': 'T_mean_lag2',
        'temp_max_lag2': 'T_max_lag2',
        'temp_min_lag2': 'T_min_lag2',
        'pressure_mean_lag2': 'P_mean_lag2',
        'humidity_mean_lag2': 'U_mean_lag2',
        'wind_speed_mean_lag2': 'Ff_mean_lag2',
        'temp_mean_lag3': 'T_mean_lag3',
        'temp_max_lag3': 'T_max_lag3',
        'temp_min_lag3': 'T_min_lag3',
        'pressure_mean_lag3': 'P_mean_lag3',
        'humidity_mean_lag3': 'U_mean_lag3',
        'wind_speed_mean_lag3': 'Ff_mean_lag3'
    }, inplace=True)

    X_test = metrics[[
    'T_mean', 'T_max', 'T_min',
    'P_mean', 
    'U_mean', 
    'Ff_mean', 
    'T_mean_lag1', 'T_max_lag1', 'T_min_lag1', 
    'P_mean_lag1', 
    'U_mean_lag1', 
    'Ff_mean_lag1', 
    'T_mean_lag2', 'T_max_lag2', 'T_min_lag2', 
    'P_mean_lag2', 
    'U_mean_lag2', 
    'Ff_mean_lag2', 
    'T_mean_lag3', 'T_max_lag3', 'T_min_lag3', 
    'P_mean_lag3', 
    'U_mean_lag3', 
    'Ff_mean_lag3', 
    'Day_of_Week', 'Month', 'Year'
    ]]

    # Здесь передаем всё в модель, она предсказывает
    # Её результат нужно подогнать под ответ бека "PredictionReport",
    # а точнее под PredictionForDay

    # В результате возврат будет такой:
    # return PredictionReport(predictions=[PredictionForDay(), ...])
    
    y_new_pred = np.clip(loaded_model.predict(X_test), a_min=0, a_max=None) #массив numpy

    # print("Предсказанные значения:", y_new_pred)

    # Формирую список предсказаний
    predictions = []
    for i, pred in enumerate(y_new_pred):
        predictions.append(PredictionForDay(day=metrics['day'].iloc[i], predicted_number=pred))

    return PredictionReport(predictions=predictions)

