#!/usr/bin/env python
import socket
import SocketServer
import subprocess
import threading
import sys
import io
import os

import time
# fied strings
FREE_MEM_CMD="""free -t -m | grep Mem | awk '{print $4}'"""
INI_FILE='/etc/minecraft.conf'
LOG_FILE='/var/log/minecraft.log'
KILL_SIGNAL='/api/send?command=/stop'
KILL_RESP_OK='OK'
KILL_RESP_BAD='BD'
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
        print "{} wrote:".format(self.client_address[0])
        print self.data
        try:
#            print "Service the request"
            
            p=self.data.rfind("?")+1
            sp=self.data.find(" ")+1
            if p>0: # Not a parametered request
                sPage=self.data[sp:p-1]
                end=self.data.rfind(' ')
                params=self.data[p:end].split("&")
            else:
                sPage=self.data[sp:p-1]
            if sPage =="/api/setval" and p>0:
                param_key=_getStrParam("key",params)
                param_value=_getStrParam("value",params)
                Set_MC_Value(param_key,param_value)
            elif sPage =="/api/getval" and p>0:
                param_key=_getStrParam("key",params)
                param_value=Get_MC_Value(param_key)
                self.request.sendall(param_value)
            elif sPage =="/api/send" and p>0:
                send_text=_getStrParam("command",params)
                print send_text
                self.server.MC_Process.MC_Input.writeline(send_text)
                resp=self.server.MC_Process.MC_Output.readline()
#                self.server.MC_Process.proc.stdin.writeline(send_text)
#                resp=self.server.MC_Process.proc.stdout.readline()
		if send_text=='/stop':
	                self.request.sendall(KILL_RESP_OK)
		else:
			self.request.sendall(resp)
            elif sPage =="/api/get":
                resp=self.server.MC_Process.proc.stdout.readline()
                self.request.sendall(resp)
            elif sPage =="/api/params":
                # send the contents of the config file
                resp=self.server.MC_Process.proc.stdout.read(1000)
                self.request.sendall(resp)
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
		mem_param='1G'
        elif mem_tot>1000:
                mem_param='1G'
	else:
		mem_param='512M'
	mc_version=_getIniValue('server_version')
	mc_path='minecraft_server.'+mc_version+'.jar'
        return ['sudo','java','-Xms'+mem_param,'-Xmx'+mem_param,'-jar',mc_path,'nogui']
    def run(self):
	try:
		self.cmd=self.MC_CmdLine()
        	os.chdir('/srv/minecraft')
	        self.proc=subprocess.Popen(self.cmd,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
#        self.proc=subprocess.Popen(self.cmd,stdin=subprocess.PIPE)
	        self.MC_Input=self.proc.stdin
        	self.MC_Output=self.proc.stdout
		self.MC_Log=io.open(LOG_FILE,'a')
		while self.Live():
			outLine=self.MC_Output.readline()
			self.MC_Log.writeline(outLine)
	finally:
		self.MC_Log.close()
        
class MC_Server:
    """
    This is the base class for the instance's data
    it includes properties for the TCP server for the RPC calls
    and stream handlers for the I/O of the minecraft process
    both of these elements need to be contained in a separate thread
    
    """
    def __init__(self):
	PORT=_getIntParam('port',sys.argv,8000)
	HOST =_getStrParam('host',sys.argv,"*")
        self.MC_Process=MC_Thread()
        self.RPC_Server=SocketServer.TCPServer((HOST, PORT), MinecraftTCPHandler())
        self.RPC_Server.MC_Process=self.MC_Process

    def keep_running(self):
        return self.MC_Process.is_alive()
#	return 1

    def serve_forever(self):
        self.MC_Process.start()
        while self.keep_running() :
            self.RPC_Server.handle_request()
#	    time.sleep(10)
            
if __name__ == "__main__":    
    PORT=_getIntParam('port',sys.argv,8000)
    HOST =_getStrParam('host',sys.argv,"*")
    if _getSwitch('help',sys.argv)==0:
        print """
Usage
    minecraft_server.py --help
        display this message
    minecraft_server.py [ port=<port> ] [ host=<host> ]
        start the Minecraft service rununing
            """
    elif 'start' in sys.argv:
        mc_Server=MC_Server()
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        mc_Server.serve_forever()
    elif 'stop' in sys.argv:
#        print "Please connect to the server instance and issue the /stop command"
        # or construct an HTTP request to localhost to stop the service
	stop_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	stop_sock.connect(('localhost',PORT))
	try:
		stop_sock.sendall(KILL_SIGNAL)
		amt_rcv=0
		amt_exp=2
		while amt_rcv<amt_exp:
			resp=stop_sock.recv(2)
			amt_rcv=len(resp)
		if resp==KILL_RESP_OK:
			print "Process Killed"
			reslt=0
		elif resp==KILL_RESP_BAD:
			print "Unable to kill process"
			reslt=1
		else:
			print "Bad Response Received"
			reslt=1
	finally:
		stop_sock.close()
	exit(reslt)
    else:
        print "Unknown Command"
