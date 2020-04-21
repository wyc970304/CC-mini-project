# CC-mini-project-ECS781P
by Wu Yucong

This project implement a flask application using the MetaWeather API and the VM of AWS in cloud, which can get the nearest weather condition conveniently and rapidly. It provide the function of:
1. Searching the weather of the nearest day for a specific city according to the city name.
1. Searching both the min and max temperature in the nearest day for a specific city according to the city name.

This weather application simply uses city name as input for searching (which is new compared with original API), instead of city IDs. GET requests are used to obtain the information and the functions hold JSON-format responses. Also, the robustness is achieved in a certain extent.

****The lastest version (i.e. Version2-t.py) of application includes creating, deleting users using cassandra and some of trys in build user's identity authentication. Until now, new codes are still not pass the usability test.

PREPARATION

1. Create a EC2 cloud instance (e.g. in AWS) and connected to it.
2. Download the Version1.py file from repository.
3. Upload codes in terminal and run it use:
```
sudo python Version1.py
```
If it runs successfully, the output in terminal should be like:
```
 * Serving Flask app "Version1" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

4. After the application is running, open another terminal and send GET request using curl according to different aims:

(1) Getting the weather of the nearest day for a chosen city:
```GET /api/get_weather_by_city/```
```
curl -i 'http://localhost:5000/api/get_weather_by_city?query=london'
```
If the request is succeed, the output in terminal should be like:
```
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 74
Server: Werkzeug/1.0.1 Python/2.7.12
Date: Tue, 21 Apr 2020 02:41:49 GMT

{"city_weather":{"date":"2020-04-21T00:16:03.009829Z","weather":"Clear"}}
```

(2) Getting the min and max temperature of the nearest day for a chosen city:
```GET /api/get_temp_by_city/```
```
curl -i 'http://localhost:5000/api/get_temp_by_city?query=london'
```
If the request is succeed, the output in terminal should be like:
```
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 94
Server: Werkzeug/1.0.1 Python/2.7.12
Date: Tue, 21 Apr 2020 03:59:13 GMT

{"city_temperature":{"date":"2020-04-21T03:16:02.609721Z","max_temp":16.485,"min_temp":9.79}}
```
