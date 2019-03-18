# -*- coding: utf-8 -*-
"""
Meteo France raining forecast.
"""

import re
import requests
import datetime
import string
from bs4 import BeautifulSoup


SEARCH_API = 'http://www.meteofrance.com/mf3-rpc-portlet/rest/lieu/facet/previsions/search/{}'
RAIN_FORECAST_API = 'http://www.meteofrance.com/mf3-rpc-portlet/rest/pluie/{}/'
WEATHER_FORECAST_URL = 'http://www.meteofrance.com/previsions-meteo-france/{}/{}'
WEATHER_FORECAST_WORLD_URL = 'http://www.meteofrance.com/previsions-meteo-monde/{}/{}'


class meteofranceError(Exception):
    """Raise when errors occur while fetching or parsing MeteoFrance data"""


class meteofranceClient():
    """Client to fetch and parse data from Meteo-France"""
    def __init__(self, postal_code, update=False, need_rain_forecast=True):
        """Initialize the client object."""
        self.postal_code = postal_code
        self._city_slug = False
        self._insee_code = False
        self._rain_forecast = False
        self._rain_available = False
        self._weather_html_soup = False
        self.need_rain_forecast = need_rain_forecast
        self._type = None
        self._data = {}
        self._init_codes()
        if update:
            self.update()

    def update(self):
        """Fetch new data and format it"""
        self._fetch_foreacast_data()
        if (self._rain_available is True and self.need_rain_forecast is True):
            self._fetch_rain_forecast()
        self._format_data()

    def _init_codes(self):
        """Search and set city slug and insee code."""
        url = SEARCH_API.format(self.postal_code)
        try:
            results = requests.get(url, timeout=10).json()
            for result in results:
                if result["id"] and (result["type"] == "VILLE_FRANCE" or result["type"] == "VILLE_MONDE"):
                    self._insee_code = result["id"]
                    self._city_slug = result["slug"]
                    self._rain_available = result["pluieAvalaible"]
                    self._data["name"] = result["slug"].title()
                    self.postal_code = result["codePostal"]
                    self._type = result["type"]
                    if result["parent"] and result["parent"] and result["parent"]["type"] == "DEPT_FRANCE":
                        self._data["dept"] = result["parent"]["id"].lower()
                    return
            raise meteofranceError("Error: no forecast for the query `{}`".format(self.postal_code))
        except Exception as err:
            raise meteofranceError(err)

    def _fetch_rain_forecast(self):
        """Get the latest data from Meteo-France."""
        url = RAIN_FORECAST_API.format(self._insee_code)
        try:
            result = requests.get(url, timeout=10).json()
            if result['hasData'] is True:
                self._rain_forecast = result
            else:
                raise meteofranceError("This location has no rain forecast available")
        except Exception as err:
            raise meteofranceError(err)

    def _fetch_foreacast_data(self):
        """Get the forecast and current weather from Meteo-France."""
        if self._type == "VILLE_MONDE":
            url = WEATHER_FORECAST_WORLD_URL.format(self._city_slug, self._insee_code)
        else:
            url = WEATHER_FORECAST_URL.format(self._city_slug, self.postal_code)

        try:
            result = requests.get(url, timeout=10)
            if result.status_code == 200:
                soup = BeautifulSoup(result.text, 'html.parser')
                if soup.find(class_="day-summary-label") is not None:
                    self._weather_html_soup = soup
                    self._parse_insee_code(result.text)
                    return
            raise meteofranceError("Error while fetching weather forecast")
        except Exception as err:
            raise meteofranceError(err)


    def _parse_insee_code(self, html_content):
        insee_code = re.findall('codeInsee:"([^"]*)"', html_content)
        if len(insee_code) is not 0:
            self._insee_code = insee_code[0]

    def _get_next_rain_time(self):
        """Get the minutes to the next rain"""
        time_to_rain = 0
        for interval in self._rain_forecast["dataCadran"]:
            if interval["niveauPluie"] > 1:
                return time_to_rain
            time_to_rain += 5
        return "No rain"

    def _get_next_sun_time(self):
        """Get the minutes to the next sun"""
        time_to_sun = 0
        for interval in self._rain_forecast["dataCadran"]:
            if interval["niveauPluie"] <= 1:
                return time_to_sun
            time_to_sun += 5
        return 60

    def _format_data(self):
        """Format data from JSON and HTML returned by Meteo-France."""
        try:
            self._data["fetched_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rain_forecast = self._rain_forecast
            if rain_forecast is not False:
                self._data["rain_forecast"] = ''#rain_forecast["niveauPluieText"][0]
                self._data["next_rain"] = self._get_next_rain_time()
                emojis = [' ','☀️','🌦','🌧','💦']
                self._data["next_rain_intervals"] = {}
                for interval in range(0, len(rain_forecast["dataCadran"])):
                    self._data["next_rain_intervals"]["rain_level_"+str(interval*5)+"min"] = int(rain_forecast["dataCadran"][interval]["niveauPluie"])
                    self._data["rain_forecast"] += emojis[int(rain_forecast["dataCadran"][interval]["niveauPluie"])]
                if self._data["next_rain"] == 'No rain':
                    self._data["rain_forecast_text"] = "Pas de pluie dans l'heure"
                elif self._data["next_rain"] == 0:
                    self._data["rain_forecast_text"] = "Pluie pendant encore au moins {} min".format(self._get_next_sun_time())
                else:
                    self._data["rain_forecast_text"] = "Risque de pluie dans {} min".format(self._data["next_rain"])
            soup = self._weather_html_soup
            if soup is not False:
                self._data["weather"] = soup.find(class_="day-summary-label").string.strip()

                try: #extract classname
                    self._data["weather_class"] = soup.find(class_="day-summary-image").find("span").attrs['class'][1]
                except:
                    self._data["weather_class"] = None

                try:
                    self._data["temperature"] = int(re.sub("[^0-9\-]","",soup.find(class_="day-summary-temperature").string))
                except: #weird class name of world pages
                    self._data["temperature"] = int(re.sub("[^0-9\-]","",soup.find(class_="day-summary-temperature-outremer").string))

                try:
                    self._data["wind_speed"] = int(next(soup.find(class_="day-summary-wind").stripped_strings).replace(' km/h', ''))
                except: #replace '< 5' by 0
                    self._data["wind_speed"] = 0

                try:
                    self._data["wind_bearing"] = soup.find(class_="day-summary-wind").find("span").attrs['class'][1][2:]
                except: #replace '< 5' by 0
                    self._data["wind_bearing"] = None
                if self._data["wind_bearing"] == "V": #no wind
                    self._data["wind_bearing"] = None

                day_probabilities = soup.find(class_="day-probabilities")
                if day_probabilities:
                    day_probabilities = day_probabilities.find_all("li")
                    self._data["rain_chance"] = int(day_probabilities[0].strong.string.split()[0])
                    self._data["thunder_chance"] = int(day_probabilities[1].strong.string.split()[0])
                    self._data["freeze_chance"] = int(day_probabilities[2].strong.string.split()[0])
                    self._data["snow_chance"] = int(day_probabilities[3].strong.string.split()[0])
                if soup.find(class_="day-summary-uv").string:
                    self._data["uv"] = int(soup.find(class_="day-summary-uv").string.split()[1])

                self._data["forecast"] = {}
                daydatas = soup.find(class_="liste-jours").find_all("li")
                for day in range(0, 5):
                    try:
                        daydata = daydatas[day+1]
                        forecast = {}
                        forecast["date"] = daydata.find("a").string
                        forecast["weather"] = daydata.find("dd").string.strip()
                        forecast["min_temp"] = int(re.sub("[^0-9\-]","",daydata.find(class_="min-temp").string))
                        forecast["max_temp"] = int(re.sub("[^0-9\-]","",daydata.find(class_="max-temp").string))
                        forecast["weather_class"] = daydata.find("dd").attrs['class'][1]
                        self._data["forecast"][day] = forecast
                    except:
                        raise



        except Exception as err:
            raise meteofranceError("Error while formatting datas: {}".format(err))

    def _format_data_for_day(self):
        """ Format data forecast for the next days"""


    def get_data(self):
        """Return formatted data of current forecast"""
        return self._data
