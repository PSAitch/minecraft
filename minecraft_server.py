#!/usr/bin/env python
import socket
import SocketServer
import subprocess
import threading
import sys
import io
import os

import logging
import sys
import time

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s',
                    )

# String Constants
LOGGER_STREAM="MinecraftServer"
FREE_MEM_CMD="""free -t -m | grep Mem | awk '{print $4}'"""
GET_STATUS_CMD="""sudo ps all | grep java | grep -v grep | tr -d '[[:space:]]'"""
SERVER_ROOT="/srv/minecraft"
INI_FILE='/etc/minecraft.conf'
PROPS_FILE=SERVER_ROOT+'/server.properties'
LOG_FILE='/var/log/minecraft.log'
KILL_CMD='/stop'
KILL_SIGNAL='/api/send?command=/stop'
KILL_RESP_OK='OK'
KILL_RESP_BAD='BD'
GET_PROPS_CMD="sudo ls "+SERVER_ROOT+" | grep '.properties' | grep -v grep"

# code to extract a switch from an argument list 
def _getSwitch(sSwitch,sArray):
    try:
        for sItem in sArray:
            if sItem.find("--")<0:
                pass
            elif sItem[sItem.find("--")+2:] ==sSwitch:
                return 0
                break
        else:
            return 1
    except AttributeError,e:            
        print "Error %s" % (e.args[0])
        sys.exit(1)
    except NameError,e:
        print "Error %s" % (e.args[0])
        sys.exit(1)
    except:
        print "Unhandled Exception" , sys.exc_info()[0]

# code to extract a string value from a parameter list where they are separated by =
def _getStrParam(sParam,sArray, sDefault=""):
    try:
        for sTuple in sArray:
            if sTuple.split("=")[0] == sParam:
                return sTuple.split("=")[1]
                break
        else:
            return sDefault
    except AttributeError,e:            
        print "Error %s" % (e.args[0])
        sys.exit(1)
    except NameError,e:
        print "Error %s" % (e.args[0])
        sys.exit(1)
    except IndexError,e:
        return sDefault
    except:
        print "Unhandled Exception" , sys.exc_info()[0]
# code to extract an integer value from a parameter list where they are separated by =
def _getIntParam(sParam,sArray,iDefault=-1):
    try:
        for sTuple in sArray:
            if sTuple.split("=")[0] != sParam:
                pass
            elif sTuple.rfind("=")==len(sTuple):
                return iDefault
            else:
                return int(sTuple.split("=")[1])
                break
        else:
            return iDefault
    except AttributeError,e:            
        print "Error %s" % (e.args[0])
        sys.exit(1)
    except NameError,e:
        print "Error %s" % (e.args[0])
        sys.exit(1)
    except IndexError,e:
        return iDefault
    except:
        print "Unhandled Exception" , sys.exc_info()[0]

def _getIniValue(sParam):
    fIni=io.open(INI_FILE)
    liIni=fIni.readlines(-1)
    fIni.close()
    vRet=_getStrParam(sParam,liIni,'')
    return vRet.strip()

def _getMC_Value(param_key):
    fConfig=io.open(PROPS_FILE,'r')
    liConfig=fConfig.readlines()
    fConfig.close()
    vRet=_getStrParam(param_key,liConfig,'')
    return vRet.strip()

def _setMC_Value(param_key,param_value):
    # copy the original to .bak
    #TODO
    # open the properties file and put it in a list
    fConfig=io.open(PROPS_FILE,'r')
    liConfig=fConfig.readlines()
    fConfig.close()
    # TODO write the lines out to the new file
    # correcting the new value

class MinecraftTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        self.logger = logging.getLogger(LOGGER_STREAM)
        self.logger.debug("request from {}:".format(self.client_address[0])+self.data)
        try:
            p=self.data.rfind("?")+1
            sp=self.data.find(" ")+1
            if p>0: # Not a parametered request
                sPage=self.data[sp:p-1]
                end=self.data.rfind(' ')
                params=self.data[p:end].split("&")
            else:
                sPage=self.data[sp:p-1]
            if sPage =="/api/set" and p>0:# set server property
                param_key=_getStrParam("key",params)
                param_value=_getStrParam("value",params)
                _setMC_Value(param_key,param_value)
                self.request.sendall(param_value)
                self.logger.debug("property " +param_key+" set to " + param_value)
            elif sPage =="/api/get" and p>0: # get server property
                param_key=_getStrParam("key",params)
                param_value=_getMC_Value(param_key)
                self.request.sendall(param_value)
                self.logger.debug("property " +param_key+" requested")
            elif sPage =="/api/save" and p>0:# save server.properties file
                param_value=_getStrParam("name",params)
                if param_value!='':
                    if _saveMC_PropsFile(param_value)
                        self.request.sendall(KILL_RESP_OK)
                        self.logger.debug("file " +param_value+" saved")
                    else:
                        self.request.sendall(KILL_RESP_BAD)
                        self.logger.debug("file " +param_value+" not saved")
                else:
                    self.request.sendall(KILL_RESP_BAD)
                    self.logger.debug("No name parameter supplied")
            elif sPage =="/api/load" and p>0: # load server.properties file
                param_value=_getStrParam("name",params)
                if param_value!="":
                    _loadMC_PropsFile(param_value)
                    self.request.sendall(KILL_RESP_OK)
                    self.logger.debug("loaded " +param_key+" file")
                else:
                    self.request.sendall(KILL_RESP_BAD)
                    self.logger.debug("Unable to load " +param_key+" file")
            elif sPage =="/api/list" and p>0: # load server.properties list
                liFiles=_getMC_PropsFiles()
                self.request.sendall(liFiles)
                self.logger.debug("properties file list sent")
            elif sPage =="/api/restart" and p>0: # load server.properties list
                try
                    self.server.restart_server()
                    self.request.sendall(KILL_RESP_OK)
                    self.logger.debug("instance restarted")
                except:
                    self.request.sendall(KILL_RESP_BAD)
                    self.logger.debug("Error during restart")
            elif sPage =="/api/send" and p>0:# send command to the console
                send_text=_getStrParam("command",params)
                self.server.MC_Process.MC_Input.writeline(send_text)
#                resp=self.server.MC_Process.MC_Output.readline()
                self.logger.debug("Command " +send_text+" sent")
		if send_text==KILL_CMD:
	                self.request.sendall(KILL_RESP_OK)
		else:# perhaps reform a request
			self.request.sendall(send_text)
            elif sPage =="/api/console":
                fLogfile=io.open(LOG_FILE,'r')
                resp=fLogfile.readall()
                self.request.sendall(resp)
                self.logger.debug("Console requested")
            elif sPage =="/api/params":
                # send the contents of the config file
                # perhaps do this as a form which submits
                fConfig=io.open(INI_FILE)
                resp=fConfig.readall()
                self.request.sendall(resp)
                self.logger.debug("config requested")
            else:
                print "|"+sPage+"|"
                raise TypeError
        except AttributeError,e:            
            print "Atrribute Error {}".format(e.args[0])
            sys.exit(1)
        except TypeError,e:
            print "TypeError {}".format(e)
            sys.exit(1)
        except NameError,e:
            print "Error %s" % (e.args[0])
        except:
            print "Unhandled Exception" , sys.exc_info()[0]
            sys.exit(1)
        finally:            
            # clean up
            print "Clean Up"

def _getMC_PropsFiles():# construct the list of properties files available as an option list
    return subprocess.check_call(GET_PROPS_CMD)

def _loadMC_PropsFile(file_name)
    # back up the existing file
    # copy the new file over server.properties
    return 0

def _saveMC_PropsFile(file_name)
    # save server.properties over new file name
    file_Path=SERVER_ROOT+file_name
    return 0
    
class MC_Thread(threading.Thread):# thread type
    """
    This is the thread that will run the Minecraft proccess
    it declares properties for accessing the I/O streams
    When it finishes, it needs to return control to the parent process
    """
#    def __init__(self):
#        self.MC_Input=io.StringIO() #stream variable
#        self.MC_Output=io.StringIO() #stream variable
#        self.=-1
    def Live(self):
        # check the value of the result variable
        return self.proc.poll()
    def MC_CmdLine(self):
        # establish memory capacity
	mem_tot=subprocess.check_call(FREE_MEM_CMD)
        # modify params for memory
	if mem_tot>2000:
		mem_param='2G'
        elif mem_tot>1000:
                mem_param='1G'
	else:
		mem_param='512M'
	mc_version=_getIniValue('server_version')
	mc_path='minecraft_server.'+mc_version+'.jar'
        return ['sudo','java','-Xms'+mem_param,'-Xmx'+mem_param,'-jar',mc_path,'nogui']

    def run(self):
	try:
                self.logger = logging.getLogger(LOGGER_STREAM)
                self.logger.debug("thread starting")
		self.cmd=self.MC_CmdLine()
        	os.chdir(SERVER_ROOT)
	        self.proc=subprocess.Popen(self.cmd,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
                self.logger.debug("Process Started")
	        self.MC_Input=self.proc.stdin
        	self.MC_Output=self.proc.stdout
		self.MC_Log=io.open(LOG_FILE,'a')
		while self.Live():
			outLine=self.MC_Output.readline()
			self.MC_Log.writeline(outLine)
	finally:
                self.logger.debug("thread stopping")
		self.MC_Log.close()
        
class MC_Server(SocketServer.TCPServer):
"""
    This is the base class for the instance's data
    it needs to be multithreaded.    
    """
    def __init__(self,request,client_address,server):
        self.logger = logging.getLogger(LOGGER_STREAM)
        self.logger.debug('__init__')
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        self.MC_Process=MC_Thread()
        self.restarting=0

    def keep_running(self):
        return self.MC_Process.is_alive() or self.restarting==1

    def serve_forever(self):
        self.MC_Process.start()
        while self.keep_running() :
            self.handle_request()

    def restart_server(self):
        self.logger.debug('Restarting')
        self.restarting=1
        Kill_Minecraft()
        while self.MC_Process.is_alive()
            time.sleep(1)
        self.MC_Process=MC_Thread()
        self.MC_Process.start()
        self.restarting=0        
        self.logger.debug('Restarted')

def Detect_Minecraft():
    return subprocess.check_call(GET_STATUS_CMD)

def Kill_Minecraft():
# Connect to the server instance and issue the /stop command
    self.logger = logging.getLogger(LOGGER_STREAM)
    self.logger.debug('Creating Kill socket')
    stop_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    stop_sock.connect(('localhost',PORT))
    try:
        self.logger.debug('sending kill signal to localhost')
	stop_sock.sendall(KILL_SIGNAL)
	amt_rcv=0
	amt_exp=2
	while amt_rcv<amt_exp:
            resp=stop_sock.recv(2)
            amt_rcv=len(resp)
            if resp==KILL_RESP_OK:
                self.logger.debug('Kill Signal processed')
		print "Process Killed"
		reslt=0
	    elif resp==KILL_RESP_BAD:
                self.logger.debug('Kill Signal Failure')
		print "Unable to kill process"
		reslt=1
	    else:
		print "Bad Response Received"
                self.logger.debug('Kill Signal Error')
		reslt=1
    finally:
        self.logger.debug('Closing socket')
	stop_sock.close()
    return reslt
    
if __name__ == "__main__":    
    PORT=_getIntParam('port',sys.argv,8000)
    HOST =_getStrParam('host',sys.argv,"*")
    if _getSwitch('help',sys.argv)==0:
        print """
Usage
    minecraft_server.py --help
        display this message
    minecraft_server.py start [ port=<port> ] [ host=<host> ]
        start the Minecraft service rununing
    minecraft_server.py stop
        Stop the minecraft service
    minecraft_server.py status
        return the status of the service
        """
    elif 'start' in sys.argv:
#        mc_Server=MC_Server()
        mc_Server=MC_Server((HOST,PORT),MinecraftTCPHandler)
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        mc_Server.serve_forever()
    elif 'stop' in sys.argv:
        reslt=Kill_Minecraft() #invoke the process to kill the server
	exit(reslt)
    elif 'status' in sys.argv:
	is_alive=Detect_Minecraft()
        if is_alive==0 :
            print "Minecraft Server is Live"
        exit(is_alive)
    else:
        print "Unknown Command"
        exit(1)
