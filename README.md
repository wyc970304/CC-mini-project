# CC-mini-project-ECS781P
by Wu Yucong

This project implement a flask application using the RickandMothy API (https://rickandmortyapi.com/documentation/) and the VM of AWS in cloud, which can get and process the basic information of characters in RickandMothy conveniently. The application is based on REST API and use the external REST service. It provides REST API which has function of:
1. GET basic information (including ID, name, gender, status and species) of all character in RickandMothy directly from external API and save the information into Cassandra cloud database.
2. GET basic information of one specific character directly using external API (https://rickandmortyapi.com/api/character/{id}) according to ID.
3. GET basic information of one specific character from cloud database according to ID.
4. Create (i.e. POST) a new character in database.
5. DELETE a existed character from database using the ID.

Also, this application is served over HTTPs. The robustness is achieved in a certain extent.

****The lastest version (i.e. Version2-t.py) of application includes creating, deleting users using cassandra and some of trys in build user's identity authentication. Until now, new codes are still not pass the usability test.




1. PREPARATION

(1) Create a EC2 cloud instance (e.g. in AWS) and connected to it.
(2) Download the Version1.py file from repository.
(3) Upload codes in terminal and run it use:
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

(4) After the application is running, open another terminal and using curl to make different operations according to aims.




2. REST API

(1) @app.route('/', methods=['GET'])

GET basic information (including ID, name, gender, status and species) of all character in RickandMothy directly from external API and save the information into Cassandra cloud database.
```
curl -i 'http://172.17.0.2/'
```
If the request is succeed, the output in terminal should be like:
```
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 58
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Wed, 22 Apr 2020 09:52:49 GMT

{"Welcome":"Basic character information of RickandMothy"}
```

(2) @app.route('/person', methods=['GET'])

Get basic information of chosen one character through RickandMothy API using ID.
```
curl -i 'http://172.17.0.2/person?id=123'
```

(3) @app.route('/person/<id>', methods=['GET']) 

Get basic information of one chosen character from Cassandra database using ID.
```
curl -i 'http://172.17.0.2/person/123'
```
   
(4) @app.route('/create',  methods=['POST'])

Create a new character into database.
```
curl -i -H "Content-Type: application/json" -X POST -d '{"id":490, "name":"Fuyuno", "gender":"Female", "status":"Alive", "species":"Human"}' http://172.17.0.2:8080/create
```

(5) @app.route('/delete',  methods=['DELETE'])
Delete a existed character from database using ID.
```
curl -i -H "Content-Type: application/json" -X DELETE -d '{"id":"490"}' http://172.17.0.2:8080/delete
```




3. Using docker to prepare Cassandra

(1) Pull Cassandra docker image
```
sudo docker pull cassandra:latest
```

(2) Run a Cassandra within Docker (e.g. cassandra-test, 9040:9040)
```
sudo docker run --name cassandra-test -p 9040:9040 -d cassandra:latest
```

(3) Interact with Cassandra via its native command line shell client ‘cqlsh’
```
sudo docker exec -it cassandra-test cqlsh
```

(4) Inside of the Cassandra Terminal create a keyspace (e.g. RAMdatabase) for the data to be inserted into.
```
CREATE KEYSPACE RAMdatabase WITH REPLICATION ={'class' : 'SimpleStrategy', 'replication_factor' : 1};
```

(5) Create the table inside of the keyspace.
```
CREATE TABLE RAM.character(id int PRIMARY KEY, name text, gender text, status text, species text);

```




4. HTTPs service

(1) nano requirements.txt
```
pip
Flask
cassandra-driver
requests
requests_cache
```

(2) nano Dockerfile
```
FROM python:3.7-alpine
WORKDIR /myapp
COPY . /myapp
RUN pip install -U -r requirements.txt
EXPOSE 8080
CMD ["python","Version1.py"]
```

(3) Build the image and run it
```
sudo docker build . --tag=cassandrarest:v1
sudo docker run -p 8080:8080 cassandrarest:v1
```
If succuess, the output of terminal is like:
```
 * Serving Flask app "Version1" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
```
