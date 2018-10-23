from setuptools import setup
import twine

setup(
    name='meteofrance',
    version='0.1dev',
    description = 'Extract Meteo-France weather forecast',
    author = 'victorcerutti',
    author_email = 'victorcerutti+meteofrance@gmail.com',
    url = 'https://github.com/victorcerutti/meteofrance-py',
    packages=['meteofrance',],
    install_requires=[
       'requests',
    ],
    license='MIT',
    long_description='Extract Meteo-France 1hour raining forecast',
)
