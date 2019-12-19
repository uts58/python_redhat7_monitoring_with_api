import time
import os
import glob
import sys
import json
import md5
import sqlite3
from datetime import datetime
import pickle
from urllib import urlopen
import platform
import re
import sys
import multiprocessing
from urllib import urlopen

PAYLOAD = dict()
BASEPATH = "/etc/zabbix/zabbix_agentd.d"
IMGFILE = BASEPATH + os.path.sep + "state.img"
DBFILE = BASEPATH + os.path.sep + "state.db"
CONN = None
CURSOR = None
class Config:
	def __init__(self):
		global BASEPATH
		if not os.path.exists(BASEPATH):
			ret = dict()
			ret["error"] = "Basepath " + BASEPATH + " doesn't exist"
			print(json.dumps(ret))
			exit(1)
		return None

	####RETURNS CURRENT FILE SYSTEM DATA AS A DICTIONARY####
	def getCurrentFS(self):
		FS = dict()
		DATA = dict()
		PAYLOAD=dict()
		mounts = os.popen('mount -v').readlines()
		for line in mounts:
			line = line.split(' ')
			if (line[4] not in ["nfs","nfs3","nfs4","fuse.gvfsd-fuse"]):
				if(line[2] in DATA.keys()):
					DATA[line[2]]={
						"size":list(set(DATA[line[2]]["size"]+[os.popen('df -kPa ' + line[2]).readlines()[1].split()[1]])),
						"perm":list(set(DATA[line[2]]["perm"]+line[5].strip('\n').strip('(').strip(')').split(','))),
						"dev":list(set(DATA[line[2]]["dev"]+[line[0]])),
						"fstype":list(set(DATA[line[2]]["fstype"]+[line[4]])),
						"hash":{
								"total":(md5.new(str(DATA[line[2]])).hexdigest()),
								"perm":(md5.new(str(DATA[line[2]]["perm"])).hexdigest()),
								"dev":(md5.new(str(DATA[line[2]]["dev"])).hexdigest()),
								"fstype":(md5.new(str(DATA[line[2]]["fstype"])).hexdigest()),
								"size":(md5.new(str(DATA[line[2]]["size"])).hexdigest())
								}
					}
				else:
					DATA[line[2]]={
						"size":[os.popen('df -kPa ' + line[2]).readlines()[1].split()[1]],
						"perm":line[5].strip('\n').strip('(').strip(')').split(','),
						"dev":[line[0]],
						"fstype":[line[4]]
					}
					DATA[line[2]]["hash"]={
								"total":(md5.new(str(DATA[line[2]])).hexdigest()),
								"perm":(md5.new(str(DATA[line[2]]["perm"])).hexdigest()),
								"dev":(md5.new(str(DATA[line[2]]["dev"])).hexdigest()),
								"fstype":(md5.new(str(DATA[line[2]]["fstype"])).hexdigest()),
								"size":(md5.new(str(DATA[line[2]]["size"])).hexdigest())
								}
		FS["DATA"]=DATA
		FS["hash"]=md5.new(str(FS["DATA"])).hexdigest()
		FS["GENERATION_TIME"]=int(time.time())
		return FS
	####RETURNS CURRENT FILE SYSTEM DATA AS A DICTIONARY####
	def getCurrentNET(self):
		DATA=dict()
		NET=dict()
		PAYLOAD=dict()
		for line in open('/proc/net/dev').readlines()[2:]:
			interface=line.split(':')[0].strip()
			path="/sys/class/net/"+interface
			tempDict=dict()
			with open((path+"/address"),"r") as f:
				try:
					tempDict["mac"]=[f.read().strip("\n")]
				except IOError as ioe:
					tempDict["mac"]=[]
			with open((path+"/mtu"),"r") as f:
				try:
					tempDict["mtu"]=[f.read().strip("\n")]
				except IOError as ioe:
					tempDict["mtu"]=[]
			with open((path+"/carrier"),"r") as f:
				try:
					tempDict["linkstate"]=[f.read().strip("\n")]
				except IOError as ioe:
					tempDict["linkstate"]=[]
			with open((path+"/operstate"),"r") as f:
				try:
					tempDict["state"]=[f.read().strip("\n")]
				except IOError as ioe:
					tempDict["state"]=[]		
			with open((path+"/speed"),"r") as f:
				try:
					tempDict["speed"]=[f.read().strip("\n")]
				except IOError as ioe:
					tempDict["speed"]=[]
			temp=os.popen('ip add show dev '+interface).read().splitlines()
			tempDict["ip"]=[x.split()[1] for x in temp if "inet" in x]			
			DATA[interface]=tempDict
		dev=os.popen("ls -l /sys/class/net").readlines()[1:]
		for line in dev:
			interface=line.strip("\n").split(" ")[-3]
			DATA[interface]["dev"]=["/sys/"+line.strip("\n").split(" ")[-1].strip("../../")]
			DATA[interface]["hash"]={
				"total":(md5.new(str(DATA[interface])).hexdigest()),
				"mac":(md5.new(str(DATA[interface]["mac"])).hexdigest()),
				"ip":(md5.new(str(DATA[interface]["ip"])).hexdigest()),
				"state":(md5.new(str(DATA[interface]["state"])).hexdigest()),
				"linkstate":(md5.new(str(DATA[interface]["linkstate"])).hexdigest()),
				"dev":(md5.new(str(DATA[interface]["dev"])).hexdigest()),
				"mtu":(md5.new(str(DATA[interface]["mtu"])).hexdigest()),
				"speed":(md5.new(str(DATA[interface]["speed"])).hexdigest()),
			}
		NET["DATA"]=DATA
		NET["hash"]=(md5.new(str(NET["DATA"])).hexdigest())
		NET["GENERATION_TIME"]=int(time.time())
		return NET
	####RETURNS CURRENT SYSTEM INFO AS A DICTIONARY####
	def getSysInfo(self):
		SYSTEM=dict()
		SYS=dict()
		SYSTEM={
			"hostname":[platform.node()],
			"arch":[platform.machine()],
			"platform": [platform.platform()],
			"kernel":[platform.uname()[2]],
			"dist_name":[platform.dist()[0]],
			"dist_ver":[platform.dist()[1]],
			"dist_code_name":[platform.dist()[2]],
			"cpus":[multiprocessing.cpu_count()],
			"total_mem":[(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES'))],
		}
		if os.path.exists('/sys/class/fc_host/'):
			SYSTEM["fc"]=[True]
		else:
			SYSTEM["fc"]=[False]
		SYSTEM["hash"]={
			"total":(md5.new(str(SYSTEM)).hexdigest()),
			"arch":(md5.new(str(SYSTEM["arch"])).hexdigest()),
			"platform":(md5.new(str(SYSTEM["platform"])).hexdigest()),
			"kernel":(md5.new(str(SYSTEM["kernel"])).hexdigest()),
			"dist_name":(md5.new(str(SYSTEM["dist_name"])).hexdigest()),
			"dist_ver":(md5.new(str(SYSTEM["dist_ver"])).hexdigest()),
			"dist_code_name":(md5.new(str(SYSTEM["dist_code_name"])).hexdigest()),
			"cpus":(md5.new(str(SYSTEM["cpus"])).hexdigest()),
			"total_mem":(md5.new(str(SYSTEM["total_mem"])).hexdigest()),
			"fc":(md5.new(str(SYSTEM["fc"])).hexdigest()),
		}
		SYS["DATA"]=SYSTEM
		SYS["hash"]=(md5.new(str(SYS["DATA"])).hexdigest())
		SYS["GENERATION_TIME"]=int(time.time())
		return SYS
	####CALLS BOTH getCurrentFS() and getCurrentNET(), PUTS THEM IN A DICT AND RETURNS IT####
	####ALSO GENERATES A CURRENT TIMESTAMP####
	def getCurrentSTAT(self):
		PAYLOAD=dict()
		PAYLOAD={
			"NET": self.getCurrentNET(),
			"FS": self.getCurrentFS(),
			"USER": self.getUserInfo(),
			"SYSTEM": self.getSysInfo(),
			"GENERATION_TIME":int(time.time())
			}
		return PAYLOAD
	####THIS METHOD COMPARES OLD AND NEW DICTIONARIES####
	def compareDict(self,selector):
		NEWCONFIG = self.getCurrentSTAT()
		OLDCONFIG = self.getOldSTAT()
		CHANGEDDICT=dict()
		# print(selector)
		################THIS SHOULD BE EQUAL##############
		if(NEWCONFIG[selector]["hash"]==OLDCONFIG[1][selector]["hash"]):
			return CHANGEDDICT
		else:
			for NEW in NEWCONFIG[selector]["DATA"]:
				if NEW in OLDCONFIG[1][selector]["DATA"].keys():
					##########THIS SHOULD BE NOT EQUAL###############
					if(NEWCONFIG[selector]["DATA"][NEW]["hash"]["total"]!=OLDCONFIG[1][selector]["DATA"][NEW]["hash"]["total"]):
						CHANGEDDICT[NEW]=dict()
						CHANGEDDICT[NEW]["old"]=dict()
						CHANGEDDICT[NEW]["new"]=dict()
						del(NEWCONFIG[selector]["DATA"][NEW]["hash"]["total"])
						del(OLDCONFIG[1][selector]["DATA"][NEW]["hash"]["total"])
						for keys in NEWCONFIG[selector]["DATA"][NEW]["hash"]:
							if NEWCONFIG[selector]["DATA"][NEW]["hash"][keys]!=OLDCONFIG[1][selector]["DATA"][NEW]["hash"][keys]:
								CHANGEDDICT[NEW]["old"][keys]=list(set(OLDCONFIG[1][selector]["DATA"][NEW][keys])-set(NEWCONFIG[selector]["DATA"][NEW][keys]))
								CHANGEDDICT[NEW]["new"][keys]=list(set(NEWCONFIG[selector]["DATA"][NEW][keys])-set(OLDCONFIG[1][selector]["DATA"][NEW][keys]))
			for NEW in NEWCONFIG[selector]["DATA"]:
				if NEW not in OLDCONFIG[1][selector]["DATA"].keys():
					del(NEWCONFIG[selector]["DATA"][NEW]["hash"])
					CHANGEDDICT[NEW]={
						"new": NEWCONFIG[selector]["DATA"][NEW],
						"old":{}
					}
			for OLD in OLDCONFIG[1][selector]["DATA"]:
				if OLD not in NEWCONFIG[selector]["DATA"].keys(): 
					del(OLDCONFIG[1][selector]["DATA"][OLD]["hash"])
					CHANGEDDICT[OLD]={
						"new":{},
						"old": OLDCONFIG[1][selector]["DATA"][OLD]
					}

			return CHANGEDDICT
	####THIS METHOD CALLS compareDict(), FEEDS THEM "FS" AND "NET" PARAMETER####
	def compareSTAT(self):
		CHANGED={
			"FS":self.compareDict("FS"),
			"NET":self.compareDict("NET"),
			"USER":self.compareDict("USER"),
			"SYSTEM":self.compareDict("SYSTEM"),
			"CHECKING_TIME":int(time.time())
		}
		return CHANGED

	def loadOldData(self, selector=None):
		if not os.path.exists(IMGFILE):                                 
			return False
		else:                                                           
			DICT = pickle.load(open(IMGFILE,"rb"))                      
			if selector in DICT.keys():                    
				return DICT[selector]
			elif selector is None:                                      
				return DICT
			elif selector not in DICT.keys():                           
				return None

	def getOldSTAT(self):
		DATA = self.loadOldData()                                
		if not DATA:                                                  
			if DATA is False:
				pickle.dump(self.getCurrentSTAT(),open(IMGFILE,"wb"))     
			return DATA, self.getCurrentSTAT()                          
		else:
			return True, DATA

	def initDB(self):
		global CONN
		global CURSOR
		CONN = sqlite3.connect(DBFILE, isolation_level=None)
		CONN.text_factory = str
		CURSOR = CONN.cursor()
		CURSOR.execute('''CREATE TABLE if not exists 
		fs(
		ID TEXT PRIMARY KEY, 
		MOUNTPOINT TEXT, 
		PERM TEXT, 
		DEV TEXT,
		FSTYPE TEXT,
		DT TIMESTAMP
		)''')

	def storeFSDataToDB(self, FSDATA):
		if type(FSDATA)!=list:
			return False
		global CURSOR
		for fsdata in FSDATA:
			for mount in fsdata.keys():
				MOUNTPOINT = mount
				PERMISSION = str(",".join(fsdata[MOUNTPOINT]["perm"]))
				DEV = fsdata[MOUNTPOINT]["dev"]
				FSTYPE = fsdata[MOUNTPOINT]["fstype"]
				ID = md5.new(MOUNTPOINT+DEV).hexdigest().upper()
				DT = datetime.now()
				query = "INSERT INTO fs(ID,MOUNTPOINT,PERM,DEV,FSTYPE,DT) VALUES('{}','{}','{}','{}','{}','{}')".format(ID,MOUNTPOINT,PERMISSION,DEV,FSTYPE,DT)
				try:
					CURSOR.execute(query)
				except sqlite3.IntegrityError as primarykeyerror:
					return False
		return CURSOR.lastrowid == len(FSDATA)
	def getUserInfo(self):
	    USERSINFO=dict()
	    with open('/etc/passwd','r') as passwd:
	        GIDS = list()
	        USERS=dict()
	        with open('/etc/group','r') as group:
	            for lines in group.readlines():
	                temp = list()
	                lines = lines.strip('\n')
	                for entry in lines.split(':'):
	                    temp.append(entry)
	                GIDS.append(temp)
	        entries = ([[line for line in lines.split(':')] for lines in passwd.readlines()])
	        SUDOERS = list()
	        with open('/etc/sudoers','r') as sudoers:
	            regex = re.compile(r'(^$)|(^#)|(^Defaults\s+)')
	            for line in sudoers.read().splitlines():
	                if regex.match(line) is None:
	                    SUDOERS.append(line)
	        for entry in entries:
	            temp = dict()
	            # temp["username"] = entry[0]
	            temp["uid"] = [entry[2]]
	            temp["gid"] = set()
	            temp["gid"].add(entry[3])
	            temp["sudo"] = list()
	            for sudos in ([sudo.split('\t') for sudo in SUDOERS]):
	                if (entry[0] in sudos):
	                    temp["sudo"].append(sudos[:])
	            for gid in GIDS:
	                if entry[0] in gid:
	                    temp["gid"].add(gid[2])
	            temp["gid"] = list(temp["gid"])
	            temp["remarks"] = [entry[4]]
	            temp["home"] = [entry[5]]
	            temp["shell"] = [entry[6].strip('\n')]
	            with os.popen('chage -l ' + str(entry[0])) as line:
	                for line in (line.read().splitlines()):
	                    ent = line.split(':')
	                    temp[(str(ent[0].strip('\t')).lower().replace(" ",'_')).strip()] = [str(ent[1].strip())]
	            with os.popen('lastlog -u ' + str(entry[0]) + " | grep -v 'Username'") as lastlog:
	                for line in lastlog:
	                    # temp["lastlogin"] = dict()
	                    line = line.split()
	                    #print("Never logged" in line[-1])
	                    if ("Never" in line[-3]):
	                    	temp["lastlogin"]=[
		                    	"terminal = null",
		                    	"from = null",
		                    	"dt = **Never logged in**"
	                    	]
	                    else:
	                    	if line[1].strip()==":0":
	                    		temp["lastlogin"]=[
		                    		"terminal = local terminal",
		                    		"from = "+line[2].strip(),
		                    		"dt = "+' '.join(line[-6:]).strip().strip('\n')
		                    	]
	                    	else:
		                    	temp["lastlogin"]=[
		                    		"terminal = "+line[1].strip(),
		                    		"from = "+line[2].strip(),
		                    		"dt = "+' '.join(line[-6:]).strip().strip('\n')
		                    	]

	                temp["hash"]={
	                	"total":(md5.new(str(temp)).hexdigest()),
	                	"shell":(md5.new(str(temp["shell"])).hexdigest()),
	                	"number_of_days_of_warning_before_password_expires":(md5.new(str(temp["number_of_days_of_warning_before_password_expires"])).hexdigest()),
	                	"uid":(md5.new(str(temp["uid"])).hexdigest()),
	                	"password_expires":(md5.new(str(temp["password_expires"])).hexdigest()),
	                	"sudo":(md5.new(str(temp["sudo"])).hexdigest()),
	                	"account_expires":(md5.new(str(temp["account_expires"])).hexdigest()),
	                	"gid":(md5.new(str(temp["gid"])).hexdigest()),
	                	"last_password_change":(md5.new(str(temp["last_password_change"])).hexdigest()),
	                	"remarks":(md5.new(str(temp["remarks"])).hexdigest()),
	                	"home":(md5.new(str(temp["home"])).hexdigest()),
	                	"minimum_number_of_days_between_password_change":(md5.new(str(temp["minimum_number_of_days_between_password_change"])).hexdigest()),
	                	"lastlogin":(md5.new(str(temp["lastlogin"])).hexdigest()),
	                }
	                USERS[entry[0]]=temp
	        
	        USERSINFO["DATA"]=USERS
	        USERSINFO["hash"]=(md5.new(str(USERS)).hexdigest())
	    	USERSINFO["GENERATION_TIME"]=int(time.time())
	    return USERSINFO



