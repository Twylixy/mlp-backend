from datetime import datetime
from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel, field_validator

url = "https://yandex.ru/pogoda/month?lat=57.152986&lon=65.541231&via=ms"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "yandex.ru",
    "Pragma": "no-cache",
    "Priority": "u=0, i",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "TE": "trailers",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
}


class WeatherData(BaseModel):
    day: datetime
    temperature_day: int
    temperature_night: int
    pressure: int
    humidity: int
    wind_speed: float

    @field_validator("pressure", mode="before")
    def parse_pressure(cls, value):
        if isinstance(value, int):
            return value
        return int(value.replace("мм рт. ст.", "").strip())

    @field_validator("humidity", mode="before")
    def parse_humidity(cls, value):
        if isinstance(value, int):
            return value
        return int(value.replace("%", "").strip())

    @field_validator("wind_speed", mode="before")
    def parse_wind_speed(cls, value):
        if isinstance(value, float):
            return value
        return float(value.split("м/с")[0].strip())


def get_weather_data() -> None:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    # Находим таблицу с данными о погоде
    table = soup.find("table", {"class": "climate-calendar"})

    if not table:
        raise ValueError("unable to fetch data, possible bot filtering")

    # Составим список для хранения данных
    weather_data = []

    # Проходим по строкам таблицы, пропуская заголовки
    for row in table.find_all("tr", {"class": "climate-calendar__row"}):
        cells = row.find_all("td", {"class": "climate-calendar__cell"})

        for cell in cells:
            day_link = cell.find("a", {"class": "link"})
            if day_link:
                day = day_link.find(
                    "div", {"class": "climate-calendar-day__day"}
                ).text.strip()
                temp_day = day_link.find(
                    "div", {"class": "climate-calendar-day__temp-day"}
                ).text.strip()
                temp_night = day_link.find(
                    "div", {"class": "climate-calendar-day__temp-night"}
                ).text.strip()

                # Извлекаем дополнительные данные из подробной таблицы
                detailed_table = day_link.find(
                    "table",
                    {"class": "climate-calendar-day__detailed-data-table"},
                )
                pressure = None
                humidity = None
                wind_speed = None

                if detailed_table:
                    # Проходим по строкам в детализированной таблице
                    for row in detailed_table.find_all("tr"):
                        columns = row.find_all("td")
                        for col in columns:
                            # Проверяем наличие тега <i> и извлекаем его класс
                            icon = col.find("i", {"class": True})
                            if not icon:
                                continue

                            icon_classes = icon.get("class", [])
                            if "icon_pressure-black" in icon_classes:
                                pressure = col.find_next("td").text.strip()
                            elif "icon_humidity-black" in icon_classes:
                                humidity = col.find_next("td").text.strip()
                            elif "icon_wind-airflow-black" in icon_classes:
                                wind_speed = col.find_next("td").text.strip()

                # print(
                #     dict(
                #         day=day,
                #         temp_day=int(temp_day.replace("−", "-")),
                #         temp_night=int(temp_night.replace("−", "-")),
                #         pressure=pressure,
                #         humidity=humidity,
                #         wind_speed=wind_speed,
                #     )
                # )
                weather_data.append(
                    dict(
                        day=day,
                        temp_day=int(temp_day.replace("−", "-")),
                        temp_night=int(temp_night.replace("−", "-")),
                        pressure=pressure,
                        humidity=humidity,
                        wind_speed=wind_speed,
                    )
                )

    final = []

    next_month = False
    now = datetime.now()
    for wd in weather_data:
        if len(wd["day"].split()) == 2:
            next_month = True

        dt: datetime
        day = wd["day"].split()[0]

        if next_month:
            dt = datetime(
                year=now.year,
                month=now.month + 1,
                day=int(wd["day"].split()[0]),
            )
        else:
            dt = datetime(
                year=now.year,
                month=now.month,
                day=int(wd["day"].split()[0]),
            )

        final.append(
            WeatherData(
                day=dt,
                temperature_day=wd["temp_day"],
                temperature_night=wd["temp_night"],
                pressure=wd["pressure"],
                humidity=wd["humidity"],
                wind_speed=wd["wind_speed"],
            )
        )

    return final
