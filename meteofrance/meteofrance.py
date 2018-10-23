"""
Meteo France raining forecast.
"""

import requests

RAIN_FORECAST_API = 'http://www.meteofrance.com/mf3-rpc-portlet/rest/pluie/{}0/'


class meteofrance(object):
    def __init__(self, insee_code):
        """Initialize the client object."""
        self.insee_code = insee_code
        self._result = False
        self._data = {}
        self.update()

    def update(self):
        self._fetch_data()
        self._format_data()

    def _fetch_data(self):
        """Get the latest data from Meteo-France."""
        url = RAIN_FORECAST_API.format(self.insee_code)
        try:
            result = requests.get(url, timeout=10).json()
            if result['hasData'] is True:
                self._result = result
            else:
                return
        except ValueError as err:
            raise
        return

    def _get_next_rain_time(self):
        """Get the minutes to the next rain"""
        time_to_rain = 0
        for interval in self._result["dataCadran"]:
            if interval["niveauPluie"] > 1:
                return time_to_rain
            time_to_rain += 5
        return "No rain"

    def _format_data(self):
        """Format data from JSON returned by Meteo-France."""
        result = self._result
        if self._result is not False:
            self._data["niveauPluieText"] = result["niveauPluieText"][0]
            self._data["next_rain"] = self._get_next_rain_time()
            for interval in range(0, len(self._result["dataCadran"])):
                self._data["interval"+str(interval+1)] = result["dataCadran"][interval]["niveauPluie"]

    def get_data(self):
        return self._data
