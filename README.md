# Where-Is-Weather-Bot-for-Telegram

Telegram bot @WhereIsWeatherBot accepts the number of month and day, 
as well as preferrable range of mean daily temperature and number of days with any kind of 
precipitation per week, searches for all places in the world with chosen parameters during the week
of the chosen day and returns an image of the world map with all found places marked on it and
links to Google Maps for 5 randomly selected points.

Plan to add several features to the bot:
- ask for acceptable kinds of precipitation and filter results according to it;
- ask about extreme weather conditions (as tornado, storm wind, shower, extreme heat or cold,
and extreme daily temperature range) and filter results according to it;
- give the full list of countries with selected points on request.

Weather data was taken from The Integrated Surface Hourly (ISH) dataset published by 
[National Climatic Data Center, NESDIS, NOAA, U.S. Department of Commerce]
(https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc%3AC00516/html).
Data for all weather stations for 2016-2020 were selected and pre-processed to obtain weekly
average temperature, number of days with precipitation and extreme weather conditions for 
every station. 
Using geocoder library for Python and station's coordinates all information about its location
was obtained (country, region, settlement).
Weekly weather data and location for every station are stored as weather_data.csv.

Requirements:
- Python 3.8.6
- pyTelegramBotAPI 3.7.4
- pandas 1.1.5
- numpy 1.19.4
- scipy 1.5.4
- vedis 0.7.1
- matplotlib 3.3.3
- basemap 1.2.2
- pyproj 3.0.0

The most difficult part is to install Basemap. For Windows you could do it by installing
two compiled Python libraries:
- pyproj: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyproj (choose the suitable version
of your OS and Python) 
- basemap: https://www.lfd.uci.edu/~gohlke/pythonlibs/#basemap (choose the suitable version
of your OS and Python)
Eventually, you should be able to use Basemap in your Python scripts.