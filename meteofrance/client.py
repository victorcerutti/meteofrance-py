"""
Meteo France raining forecast.
"""

import re
import requests
from bs4 import BeautifulSoup

SEARCH_API = 'http://www.meteofrance.com/mf3-rpc-portlet/rest/lieu/facet/previsions/search/{}'
RAIN_FORECAST_API = 'http://www.meteofrance.com/mf3-rpc-portlet/rest/pluie/{}/'
WEATHER_FORECAST_URL = 'http://www.meteofrance.com/previsions-meteo-france/{}/{}'


class meteofranceError(Exception):
    """Raise when errors occur while fetching or parsing MeteoFrance data"""


class meteofranceClient():
    """Client to fetch and parse data from Meteo-France"""
    def __init__(self, postal_code):
        """Initialize the client object."""
        self.postal_code = postal_code
        self._city_slug = False
        self._insee_code = False
        self._rain_forecast = False
        self._rain_available = False
        self._weather_html_soup = False
        self._data = {}
        self._init_codes()
        self.update()

    def update(self):
        """Fetch new data and format it"""
        self._fetch_foreacast_data()
        if self._rain_available is True:
            self._fetch_rain_forecast()
        self._format_data()

    def _init_codes(self):
        """Search and set city slug and insee code."""
        url = SEARCH_API.format(self.postal_code)
        try:
            results = requests.get(url, timeout=10).json()
            for result in results:
                if result["id"] and result["type"] == "VILLE_FRANCE":
                    self._insee_code = result["id"]
                    self._city_slug = result["slug"]
                    self._rain_available = result["pluieAvalaible"]
                    self._data["name"] = result["slug"].title()
                    self.postal_code = result["codePostal"]
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

    def _format_data(self):
        """Format data from JSON and HTML returned by Meteo-France."""
        try:
            rain_forecast = self._rain_forecast
            if rain_forecast is not False:
                self._data["rain_forecast"] = rain_forecast["niveauPluieText"][0]
                self._data["next_rain"] = self._get_next_rain_time()
                self._data["next_rain_intervals"] = {}
                for interval in range(0, len(rain_forecast["dataCadran"])):
                    self._data["next_rain_intervals"]["rain_level_"+str(interval*5)+"min"] = rain_forecast["dataCadran"][interval]["niveauPluie"]
            soup = self._weather_html_soup
            if soup is not False:
                self._data["weather"] = soup.find(class_="day-summary-label").string
                self._data["temperature"] = soup.find(class_="day-summary-temperature").string.replace('°C', '')
                self._data["wind_speed"] = next(soup.find(class_="day-summary-wind").stripped_strings).replace(' km/h', '')
                day_probabilities = soup.find(class_="day-probabilities")
                if day_probabilities:
                    day_probabilities = day_probabilities.find_all("li")
                    self._data["rain_chance"] = day_probabilities[0].strong.string.split()[0]
                    self._data["thunder_chance"] = day_probabilities[1].strong.string.split()[0]
                    self._data["freeze_chance"] = day_probabilities[2].strong.string.split()[0]
                    self._data["snow_chance"] = day_probabilities[3].strong.string.split()[0]
                self._data["uv"] = soup.find(class_="day-summary-uv").string.split()[1]

        except Exception as err:
            raise meteofranceError("Error while formatting datas: "+err)

    def get_data(self):
        """Return formatted data of current forecast"""
        return self._data
