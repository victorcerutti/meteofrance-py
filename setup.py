from setuptools import setup

setup(
    name='meteofrance',
    version='0.2.1',
    description = 'Extract Meteo-France weather forecast',
    author = 'victorcerutti',
    author_email = 'victorcerutti+meteofrance@gmail.com',
    url = 'https://github.com/victorcerutti/meteofrance-py',
    packages=['meteofrance',],
    install_requires=[
       'requests',
       'beautifulsoup4'
    ],
    license='MIT',
    long_description='Extract Meteo-France current weather and 1 hour rain forecast',
)
