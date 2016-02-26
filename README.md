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
  * tabs or table cells for server parameters form, console input / output frame
* need to convert the server to a HTTPServer object which handles put and get requests returning HTML
 * PUT requests to set server parameters and config, and send commands to the server
 * GET requests to return the server parameters form and console output
* need to have a config flag which sets autostart
