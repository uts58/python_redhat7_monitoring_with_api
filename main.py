import json
import libconfig
import datetime
import pickle
import md5
import sys
import requests

BASEPATH = "/etc/zabbix/zabbix_agentd.d"
CONFIG = libconfig.Config()

#####AVAILABLE METHODS######
# getCurrentFS() ###RETURNS CURRENT FILE SYSTEM
# getCurrentNET() ###RETURNS CURRENT NET
# getSysInfo() ###RETURNS CURRENT SYSTEM INFO
# getUserInfo() ###RETURNS CURRENT USER INFO
# getCurrentSTAT() ###RETUNRS CURRENT ALL STATS
# getOldSTAT() ###RETURNS SAVED OLD INFO AS DICT
# compareDict(selector) ###SELECTOR IS USED TO COMPARE SPECIFIC DICT (EX: FS, NET, USER, SYSTEM)
# compareSTAT() ###COMPARES WHOLE SYSTEM STATS
#############################


# IF DEFAULT COMPARES WHOLE SYSTEM AND MAKES A JSON DUMP
if (len(sys.argv) is 1):
	with open('COMPAREDSTAT.json', 'w') as f:
		json.dump(CONFIG.compareSTAT(),f,indent=4)
#HELP INFO	
elif (sys.argv[1] in ["-h","-help","help","--help"]):
	print("Usage: \n1. python main.py (default: compares whole system)\n2. python main.py <new|old|compare> SELECTOR \nSELECTOR availabe: NET, FS, USER, SYSTEM ")
#LESS THAN TWO ARGUMENTS
elif (len(sys.argv)<3):
	print("Please use good arguments, use -h for help")
#WRONG ARGUMETNS CHECKING
elif ((sys.argv[1] not in ["old", "new", "compare"])) or ((sys.argv[2] not in ["NET", "FS", "USER", "SYSTEM"])):
	print("Please use good arguments, use -h for help")
#EVERY ARGUMENTS ARE FINE
else:
	desicion=sys.argv[1]
	selector=sys.argv[2]
	#########COMPARING WITH SELECTOR#########
	if(desicion=="compare"):
		with open('compared'+selector+'.json', 'w') as f:
			json.dump(CONFIG.compareDict(selector),f,indent=4)	
	#########GETTING OLD DATA FROM STATE.IMG WITH SELECTOR#########
	elif(desicion=="old"):
		if(selector=="NET"):
			with open('old'+selector+'.json', 'w') as f:
				json.dump(CONFIG.getOldSTAT()[1]["NET"],f,indent=4)
		if(selector=="FS"):
			with open('old'+selector+'.json', 'w') as f:
				json.dump(CONFIG.getOldSTAT()[1]["FS"],f,indent=4)
		if(selector=="USER"):
			with open('old'+selector+'.json', 'w') as f:
				json.dump(CONFIG.getOldSTAT()[1]["USER"],f,indent=4)
		if(selector=="SYSTEM"):
			with open('old'+selector+'.json', 'w') as f:
				json.dump(CONFIG.getOldSTAT()[1]["SYSTEM"],f,indent=4)
	#########PULLING NEW DATA FROM SYSTEM#########
	elif(desicion=="new"):
			if(selector=="NET"):
				with open('new'+selector+'.json', 'w') as f:
					json.dump(CONFIG.getCurrentNET(),f,indent=4)
			if(selector=="FS"):
				with open('new'+selector+'.json', 'w') as f:
					json.dump(CONFIG.getCurrentFS(),f,indent=4)
			if(selector=="USER"):
				with open('new'+selector+'.json', 'w') as f:
					json.dump(CONFIG.getUserInfo(),f,indent=4)
			if(selector=="SYSTEM"):
				with open('new'+selector+'.json', 'w') as f:
					json.dump(CONFIG.getSysInfo(),f,indent=4)
###########################################################################
###########################################################################

# headers = {'Content-Type': 'application/json'}

# data = '{\n"host_name":"uts",\n"auth_token":"7b6ff4a5fb4a4a83062e0836004de898.1573477941",\n"PAYLOAD":CONFIG.getCurrentFS()\n}'
# data1={
# 	"host_name":"uts",
# 	"auth_token":"7b6ff4a5fb4a4a83062e0836004de898.1573477941",
# 	"PAYLOAD": str(CONFIG.getCurrentNET()),
# }

# response = requests.post('http://127.0.0.1:5000/', headers=headers, data=json.dumps(data1))

# print(response.content)