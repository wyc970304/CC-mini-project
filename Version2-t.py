#coding=utf-8
from flask import Flask, render_template, request, jsonify, session, redirect, g
import requests, os, uuid
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from cassandra.cluster import Cluster
from cassandra.query import dict_factory


auth = HTTPBasicAuth()
cluster = Cluster(['cassandra'])
session = cluster.connect()
session.row_factory = dict_factory

app = Flask(__name__)
secret_key = os.urandom(12)

@app.route('/')
def home():
    return jsonify({
                       'data': 'Welcome to the mini project, to see more please visit '}), 200

# Class name User
class User:
    id = ""
    username = ""
    password_hash = ""

    def __init__(self, username, name, email):
        self.username = username
        self.name = name

    def update_id(self, id):
        self.id = id

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    # generates authentication token for the requested used
    def generate_auth_token(self, expiration=10000):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration) #generate a token
        return s.dumps({'id': self.id})

    # verifies the token
    @staticmethod
    def verify_auth_token(token):
        #
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        # token may expired
        except SignatureExpired:
            return None
        print(data['id'])
        prepared_statement = session.prepare('SELECT ID ,Username,Role FROM CCMiniProject.users WHERE ID= ?')
        rows = session.execute(prepared_statement, (uuid.UUID(data['id']),))
        if not rows:
            return None
        else:
            user = User(rows[0][u'username'], "", "")
            return user


## Create a new user into database
## Returns: user details

@app.route('/api/users/createuser', methods=['POST'])
def create_user():
    if request.json is None:
        # none input
        return jsonify({'error': 'missing arguments!'}), 400
    #extract username and password
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        # missing arguments
        return jsonify({'error': 'missing arguments!'}), 400
    prepared_statement = session.prepare("SELECT * FROM CCMiniProject.users WHERE Username = ?;")
    rows = session.execute(prepared_statement, (username,))
    if rows:
        if rows[0][u'username'] == username:
            # user existed already
            return jsonify({'error': 'existing user!'}), 400
    user = User(username=username)
    user.hash_password(password)
    rows = session.execute(
        (uuid.uuid4(), user.username, user.password_hash))
    return jsonify({'username': user.username}), 201

#delete an existed user
@app.route('/api/users/deleteuser/<username>', methods=['DELETE'])
@auth.login_required
def delete_user(username):
    prepared_statement = session.prepare('SELECT ID,Username FROM CCMiniProject.users WHERE Username = ?')
    rows = session.execute(prepared_statement, (username,))

    if (rows is None) or (not rows):
        return jsonify({'error': 'unauthorized delete request!'}), 401
    else:
        if rows[0][u'username'] != g.user.username:
            # existing user
            return jsonify({'error': 'unauthorized delete request!'}), 401
        id_to_delete = rows[0][u'id']
        prepared_statement = session.prepare("DELETE FROM CCMiniProject.users WHERE ID = ?")
        rows = session.execute(prepared_statement, (id_to_delete,))
        return jsonify({'data': 'user deleted'}), 200

#request authentication token
@app.route('/api/token', methods=["GET"])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})

@auth.verify_password
def verify_password(username_or_token, password):
    # verify based on authentication token
    user = User.verify_auth_token(username_or_token)
    # if not verified by token, try to verify using username and password
    if not user:
        prepared_statement = session.prepare(
            "SELECT ID,Username,Password_hash,FROM CCMiniProject.users WHERE Username = ?;")
        rows = session.execute(prepared_statement, (username_or_token,))
        if not rows:
            return False
        else:
            user = User(rows[0][u'username'], "", "")
        if not user.verify_password(password):
            #false password
            return False
    g.user = user
    return True


id_url_template = 'https://www.metaweather.com/api/location/search/?query={query}'
location_url_template = 'https://www.metaweather.com/api/location/{woeid}'

## Input a city name, and get the next day's weather of it (GET)
## Return: Date, weather

@app.route('/api/get_weather_by_city', methods=['GET'])
@auth.login_required
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
@auth.login_required
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
            min_dict = {'min_temp': min}
            max_dict = {'max_temp': max}
            # Create a new dictionary to save temperatures of nextday
            data1 = dict(date_dict, **min_dict)
            data2 = dict(data1, **max_dict)
            return jsonify({'city_temperature': data2}), 200  # if succeed, return 200
        else:
            return jsonify({'error': resp.reason}), 404  # if failure in requests, return 404
    else:
        return jsonify({'error': resp.reason}), 404  # if failure in requests, return 404


@app.before_first_request
def init_database():
    # create keyspace CCMiniProject
    session.execute(
        "CREATE KEYSPACE IF NOT EXISTS CCMiniProject WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 3 };")
    # create table users
    session.execute(
        "CREATE TABLE IF NOT EXISTS CCMiniProject.users ( ID UUID PRIMARY KEY, Username text, Password_hash text);")
    # index Username column
    session.execute("CREATE INDEX IF NOT EXISTS UsernameIndex ON CCMiniProject.users (Username);")
    # insert admin user if not exists
    rows = session.execute("SELECT Username FROM CCMiniProject.users WHERE Username= 'liaoyangqing';")

if __name__ == '__main__':
    app.secret_key = secret_key
    # Loads the SSL certificate
    context = ('cert.pem', 'key.pem')
    app.run(host='0.0.0.0', port=8080, ssl_context=context)
