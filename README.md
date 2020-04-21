# CC-mini-project-ECS781P
by Wu Yucong

This project implement a flask application using the MetaWeather API and the VM of AWS in cloud, which can get the nearest weather condition conveniently and rapidly. It provide the function of:
1. Searching the weather of the nearest day for a specific city according to the city name.
1. Searching both the min and max temperature in the nearest day for a specific city according to the city name.

This weather application simply uses city name as input for searching (which is new compared with original API), instead of city IDs. GET requests are used to obtain the information and the functions hold JSON-format responses.

PREPARATION
1. Create a EC2 cloud instance (e.g. in AWS) and connected to it.
2. Download the WeatherApp1-final.py file from repository.
3. Upload codes in terminal and run it use:
```
sudo python  WeatherApp1-final.py
```

.
