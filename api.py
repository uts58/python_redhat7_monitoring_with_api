from flask import Flask, jsonify, request
from pymongo import MongoClient
from random import random
import hashlib
import schedule
import time
import json
import os
import time
#########################GET HASH FROM MONGO###################
userDict=dict()
client=MongoClient('mongodb://localhost:27017/')
db=client['zabbix_api_user']
collection=db['users']
cursor=collection.find()
for doccument in cursor:
	userDict=doccument
del(userDict['_id'])
###############################################################
####################DO JOB AFTER SOMETIMES#####################
def dbDump():
	y=collection.delete_many({})
	x=collection.insert(userDict, manipulate=False)
	# print(x.inserted_ids)
	# print(y.deleted_count)
# schedule.every(1/60).minutes.do(dbDump)

# while True:
# 	schedule.run_pending()
# 	time.sleep(1)
###############################################################
app = Flask(__name__)

@app.route('/', methods = ['POST'])
def postJsonHandler():
	content =request.json
	if content is None:
	 	raise Exception("JSONError")
	ip=request.remote_addr
	if((content["host_name"] in userDict) and (content["auth_token"] in [""," ", "null"]) and (ip == userDict[content["host_name"]]["ip"])):
		auth_token=hashlib.md5(str(random()).split(".")[1]).hexdigest()+"."+str(int(time.time()))
		userDict[content["host_name"]]["auth_token"]=auth_token
		dbDump()
		return {"auth_token":auth_token,"status":"0"}
	elif((content["host_name"] in userDict) and (content["auth_token"]==userDict[content["host_name"]]["auth_token"]) and (ip == userDict[content["host_name"]]["ip"])):
		########AUTH_TOKEN TIMEOUT############
		if(int(time.time())-int(content['auth_token'].split(".")[1])>(90 * 24 * 60 * 60)):
			auth_token=hashlib.md5(str(random()).split(".")[1]).hexdigest()+"."+str(int(time.time()))
			userDict[content["host_name"]]["auth_token"]=auth_token
			return {"auth_token":auth_token,"status":"0"}
		else:
			######### DEAL WITH PAYLOAD HERE #############
			return {"auth_token":content["auth_token"],"status":"1","PAYLOAD":content["PAYLOAD"]}
	elif((content["host_name"] in userDict) and (content["auth_token"]==userDict[content["host_name"]]["auth_token"]) and (ip != userDict[content["host_name"]]["ip"])):
		userDict[content["host_name"]]["ip"]=ip
		dbDump()
		return {"auth_token":content["auth_token"],"status":"0"}
	elif(content["decision"] and content["selector"]):
		terminalString='python main.py '+content["decision"]+" "+content["selector"]
		temp=os.popen(terminalString)
		with open(content["decision"]+content["selector"]+'.json') as json_file:
			data=json.load(json_file)
			return data
	else:
		raise Exception()


@app.errorhandler(Exception)
def handle_unexpected_error(error):
	message = str(error)
	if "JSONError" in error:
		message = "Request must set Content-Type to application/json"
	response = {
		'success': False,
		'error':
		{
			'type':'UnexpectedException',
			'message': message
		}
	}
	return jsonify(response), 500
