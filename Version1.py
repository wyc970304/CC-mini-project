from flask import Flask, request, render_template, jsonify
from cassandra.cluster import Cluster
import requests
import json
import requests_cache

requests_cache.install_cache('crime_api_cache', backend='sqlite', expire_after=36000)
cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()
app=Flask(__name__)

RAM_url_template = 'https://rickandmortyapi.com/api/character/?page={page}'
RAM_id_url_template = 'https://rickandmortyapi.com/api/character/{id}'

## Get information and insert them into cassandra
## If success, return a welcome message
@app.route('/', methods=['GET'])
def RAM_database():
	## Initialize lists
	character=[]
    Id=[]
    Name=[]
    Gender=[]
    Status=[]
    Species=[]

	## GET character info of all 25 pages
    for page in range(1,25):
		# put the content of parameter into url
        RAM_url=RAM_url_template.format(page=page)
		# get the file which contains info
        resp=requests.get(RAM_url)
        if resp.ok:
            character.append(resp.json()) # add this page to list

    ## Extract each feature
    for i in range(0,24):
        temp=character[i]['results']
        for j in range(0,20):
            Id.append(temp[j]['id'])
            Name.append(temp[j]['name'])
            Gender.append(temp[j]['gender'])
            Status.append(temp[j]['status'])
            Species.append(temp[j]['species'])

	## Adjust name format
    for i in range(0,479):
        Name[i]=Name[i].replace(".","")
        Name[i]=Name[i].replace("'","")
	## Insert into cassandra database
    for i in range(0,479):
        session.execute("""INSERT INTO RAM.character(id, name, gender, status, species) \ VALUES( {}, '{}', '{}', '{}', '{}')""".format(int(Id[i]), Name[i], Gender[i], Status[i], Species[i])
    return jsonify({'Welcome':'Basic character information of RickandMothy'}), 200 # If success, return welcome and 200


## Get basic information of chosen one character through RickandMothy API
@app.route('/person', methods=['GET'])
def get_person():
	# Get the id of character
	my_id = request.args.get('id')
    # Robust
    if (my_id is None):
        return jsonify({'Failure':'No input'}), 400  # if input failure, return 400
	# put the content of parameter into url
    RAM_id_url=RAM_id_url_template.format(id=my_id)
	resp=requests.get(RAM_id_url)
	if resp1.ok:
		temp=resp.json()
		id=temp['id']
		name=temp['name']
		gender=temp['gender']
		species=temp['species']
		status=temp['status']
		# Create a new dictionary to save basic info of selected character
		t1=dict(id,**name)
		t2=dict(t1,**gender)
		t3=dict(t2,**species)
		t4=dict(t3,**status)
		return jsonify({'Character of searching': t4}), 200  # if succeed, return 200
	else:
		return jsonify({'error': resp.reason}), 404  # if failure in requests, return 404


## Get basic information of one chosen character through cassandra database
@app.route('/person/<id>', methods=['GET'])
def person_by_id(id):
	rows=session.execute("""Select * from RAM.character where id='{}'""".format(id))
	result=[]
	result=({"id": row.id, "name": row.name, "gender": row.gender, "species": row.species, "status": row.status})
	if result!==[]:
		return jsonify(result), 200
	else:
		return jsonify({'Failure':'Character is not existed.'}), 400


## Create a new character into database
@app.route('/create',  methods=['POST'])
def create_character():
	my_id=request.json['id']
	rows=session.execute("""Select * from RAM.character where id='{}'""".format(my_id))
	result=[]
	result=({"id": row.id, "name": row.name, "gender": row.gender, "status": row.status, "species": row.species})
	if result != []:
		return jsonify({'Failure': 'This id is already used'}), 400
	else:
    	session.execute( """INSERT INTO covid19.summary(country,newconfirmed,totalconfirmed,newdeaths,totaldeaths,newrecovered,totalrecovered)\
		VALUES({}, '{}', '{}', '{}', '{}')""".format(int(request.json['id']), request.json['name'], request.json['gender'], request.json['status'], request.json['species']))
		return jsonify({'message': 'Create of character ID {} is done.'.format(my_id)}), 200


## Delete a existed character from database
@app.route('/delete',  methods=['DELETE'])
def delete_character():
	my_id= request.json['id']
	rows=session.execute("""Select * from RAM.character where id='{}'""".format(my_id))
	result=[]
	result = ({"id": row.id, "name": row.name, "gender": row.gender, "species": row.species, "status": row.status})
	if result==[]:
		return jsonify({'Failure': 'Character does not exist'}), 400
	else:
		session.execute("""DELETE FROM RAM.character where id='{}'""".format(my_id))
		return jsonify({'message': 'Delete of character ID {} is done.'.format(my_id)}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)
