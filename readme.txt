#RedHat7 Server Monitoring tool 
Project Overview: 
	1. Server automation
	2. Pull server status (FS status, net status, system status etc.)
	3. Compare old and new server status to identify problems
	4. Save info as JSON/ binary stream
#Monitoring Tool REST API
Project Overview: 
	1. REST api using Flask
	2. Return JSON data via api
	3. Authentication using Firebase
	4. User ACL

id={
	"test" : { 
		"ip" : "172.16.23.213", 
		"auth_token" : "null" 
	}, 
	"uts" : { 
		"ip" : "127.0.0.1", 
		"auth_token" : "32540709fc5bd1b0478a6bfc2ecdc55b.1572952677" 
	} 
}

python setup-tools
create a rpm package for zabbix_client, python 2.7


zabbix_aggentd.conf

regex:
uts

# Server= 172.16.7.221

# ServerActive= 172.16.7.221

systemctl restart zabbix_agent.service

systemctl enable zabbix_agent.service

configuration>hosts>create host>


zabbix agent version 349
