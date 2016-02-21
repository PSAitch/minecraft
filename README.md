# Minecraft
Minecraft server code
This project is about ensuring that Minecraft can be configured and run as a service from a web interface
### mc
script file for installing and testing minecraft
* will create user and root folder
* copies files to appropriate places
* test execution

### minecraft
shell script which runs the service and responds to service commands
* basic service commands of start, stop and status via the minecraft_server.py script
* other test commands such as parameter information (source file location etc), install check and mods information

### minecraft_server.py
python file which runs the service
* uses a separate process for the Java Minecraft code
* webserver interface which can 
  * receive sent commands and pipe them to the server console
  * retrieve the server parameters and change them
  * manage service configuration

### TODO
* index.htm which enables access to the web admin tool
  * shows the server properties and allows for their management using the form provided by the web service
  * shows the service properties and allows for that configuration, e.g. server version, auto-start
  * has form for sending commands and frame for console responses
