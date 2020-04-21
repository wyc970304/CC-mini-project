from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates")

## This application uses MetaWeather API to provide functions of:
## searching the weather or temperature (min and max) of the nearest day for a specific city.
## It uses city name as input for searching (which is new compared with original API), instead of city IDs.

id_url_template = 'https://www.metaweather.com/api/location/search/?query={query}'
location_url_template = 'https://www.metaweather.com/api/location/{woeid}'


## Input a city name, and get the next day's weather of it (GET)
## Return: Date, weather

@app.route('/api/get_weather_by_city', methods=['GET'])
def get_weather_by_city():
    # Get the city
    my_query = request.args.get('query')
    # Robust
    if (my_query is None):
        return jsonify({'Failure':'No input'}), 400  # if input failure, return 400
    # put the content of parameter into url
    id_url = id_url_template.format(query=my_query)
    # get the file which contains id of city
    resp = requests.get(id_url)
    if resp.ok:
        locate = resp.json()
        # Get the first id as the input city to check weather
        woeid = locate[0]['woeid']
        # Use woeid to get the weather of city
        if woeid is None:
            return jsonify({'error': 'No id'}), 400
        location_url = location_url_template.format(woeid=woeid)
        resp1 = requests.get(location_url)
        if resp1.ok:
            weather1 = resp1.json()
            # Date of next day
            date = weather1['consolidated_weather'][0]['created']
            # Weather of next day
            weather = weather1['consolidated_weather'][0]['weather_state_name']
            date_dict = {'date': date}
            weather_dict = {'weather': weather}
            # Create a new dictionary to save weather of nextday
            weaData = dict(date_dict, **weather_dict)
            return jsonify({'city_weather': weaData}), 200  # if succeed, return 200
        else:
            return jsonify({'error': resp.reason}), 404  # if failure in requests, return 404
    else:
        return jsonify({'error': resp.reason}), 404  # if failure in requests, return 404



## Input a city name, and get the next day's mix and max temperature of it (GET)
## Return: Date, min_temp, max_temp

@app.route('/api/get_temp_by_city', methods=['GET'])
def get_minmaxTemp_by_city():
    # Get the city
    my_query = request.args.get('query')
    # Robust
    if (my_query is None):
        return jsonify({'Failure':'No input'}), 400  # if input failure, return 400
    # put the content of parameter into url
    id_url = id_url_template.format(query=my_query)
    # get the file which contains id of city
    resp = requests.get(id_url)
    if resp.ok:
        locate = resp.json()
        # Get the first id as the input city to check weather
        woeid = locate[0]['woeid']
        # Use woeid to get the mix and max temperature of city
        if woeid is None:
            return jsonify({'error': 'No id'}), 400
        location_url = location_url_template.format(woeid=woeid)
        resp1 = requests.get(location_url)
        if resp1.ok:
            temp1 = resp1.json()
            # Date of next day
            date = temp1['consolidated_weather'][0]['created']
            # Minimum temperature of next day
            min = temp1['consolidated_weather'][0]['min_temp']
            # Max temperature of next day
            max = temp1['consolidated_weather'][0]['max_temp']
            date_dict = {'date': date}
            min_dict = {'min_temp': min_temp}
            max_dict = {'max_temp': max_temp}
            # Create a new dictionary to save temperatures of nextday
            data1 = dict(date_dict, **min_dict)
            data2 = dict(data1t, **max_dict)
            return jsonify({'city_temperature': data2}), 200  # if succeed, return 200
        else:
            return jsonify({'error': resp.reason}), 404  # if failure in requests, return 404
    else:
        return jsonify({'error': resp.reason}), 404  # if failure in requests, return 404

if __name__=="__main__":
    app.run(host='0.0.0.0')
