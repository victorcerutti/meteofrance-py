# -*- coding: utf-8 -*-
from meteofrance.client import meteofranceClient, meteofranceError
import time
import unittest

class TestLocation(unittest.TestCase):
  def test_oslo(self):
    client = meteofranceClient('oslo, norvege', True)
    data = client.get_data()
    self.assertEqual(data['name'], 'Oslo')
    self.assertEqual(data['printName'], u'Oslo (Norvège)')

  def test_luxembourg(self):
    client = meteofranceClient('luxembourg', True)
    data = client.get_data()
    self.assertEqual(data['name'], 'Luxembourg')
    self.assertEqual(data['printName'], u'Luxembourg (Luxembourg )')

  def test_postal_code(self):
    client = meteofranceClient('80000', True)
    data = client.get_data()
    self.assertEqual(data['name'], 'Amiens')
    self.assertEqual(data['dept'], '80')
    self.assertEqual(data['printName'], 'Amiens (80000)')

  def test_city_name(self):
    client = meteofranceClient('Brest', True)
    data = client.get_data()
    self.assertEqual(data['name'], 'Brest')
    self.assertEqual(data['printName'], u'Brest (Biélorussie)')

  #postal code is not correct : should return the first result which is "Ableiges"
  def test_department(self):
    client = meteofranceClient('95', True)
    data = client.get_data()
    self.assertEqual(data['name'], 'Ableiges')
    self.assertEqual(data['printName'], 'Ableiges (95450)')

  def f_test_invalid(self):
    meteofranceClient('foobar')

  def test_invalid(self):
    self.assertRaises(meteofranceError, self.f_test_invalid)

class TestClientData(unittest.TestCase):
  def test_beynost(self):
    client = meteofranceClient('01700')
    client.need_rain_forecast = False
    client.update()
    data = client.get_data()
    self.assertIn('name', data)
    self.assertIn('dept', data)
    self.assertIn('fetched_at', data)
    self.assertIn('forecast', data)
    self.assertIn('freeze_chance', data)
    self.assertIn('rain_chance', data)
    self.assertIn('snow_chance', data)
    self.assertIn('temperature', data)
    self.assertIn('thunder_chance', data)
    self.assertIn('uv', data)
    self.assertIn('weather_class', data)
    self.assertIn('weather', data)
    self.assertIn('wind_bearing', data)
    self.assertIn('wind_speed', data)
    self.assertNotIn('next_rain_intervals', data)
    self.assertNotIn('next_rain', data)
    self.assertNotIn('rain_forecast_text', data)
    self.assertNotIn('rain_forecast', data)

  # pointe-a-pitre : result from meteo-france is different and it returns less data
  def test_pointe_a_pitre(self):
    client = meteofranceClient('97110')
    client.need_rain_forecast = False
    client.update()
    data = client.get_data()
    self.assertIn('name', data)
    self.assertNotIn('dept', data)
    self.assertIn('fetched_at', data)
    self.assertIn('forecast', data)
    self.assertNotIn('freeze_chance', data)
    self.assertNotIn('rain_chance', data)
    self.assertNotIn('snow_chance', data)
    self.assertIn('temperature', data)
    self.assertNotIn('thunder_chance', data)
    self.assertIn('uv', data)
    self.assertIn('weather_class', data)
    self.assertIn('weather', data)
    self.assertIn('wind_bearing', data)
    self.assertIn('wind_speed', data)
    self.assertNotIn('next_rain_intervals', data)
    self.assertNotIn('next_rain', data)
    self.assertNotIn('rain_forecast_text', data)
    self.assertNotIn('rain_forecast', data)

class TestRainForecast(unittest.TestCase):
  def test_rain_forecast_is_updated(self):
    client = meteofranceClient('01700')
    client.need_rain_forecast = False
    client.update()
    self.assertEqual(client.need_rain_forecast, False)
    data = client.get_data()
    self.assertNotIn('next_rain_intervals', data)
    self.assertNotIn('next_rain', data)
    self.assertNotIn('rain_forecast_text', data)
    self.assertNotIn('rain_forecast', data)
    client.need_rain_forecast = True
    client.update()
    self.assertEqual(client.need_rain_forecast, True)
    data = client.get_data()
    self.assertIn('next_rain_intervals', data)
    self.assertIn('next_rain', data)
    self.assertIn('rain_forecast_text', data)
    self.assertIn('rain_forecast', data)

  #marseille : no rain forecast
  def test_marseille(self):
    client = meteofranceClient(13000, True)
    data = client.get_data()
    self.assertNotIn('next_rain_intervals', data)
    self.assertNotIn('next_rain', data)
    self.assertNotIn('rain_forecast_text', data)
    self.assertNotIn('rain_forecast', data)

  #Rouen : rain forecast available
  def test_rouen(self):
    client = meteofranceClient(76000, True)
    data = client.get_data()
    self.assertIn('next_rain_intervals', data)
    self.assertIn('next_rain', data)
    self.assertIn('rain_forecast_text', data)
    self.assertIn('rain_forecast', data)

if __name__ == '__main__':
    unittest.main()
