from socket import *
from threading import *
from sys import *
import os
import httplib
import mimetypes

    
host = '127.0.0.1'
port = 9898
headers={'Server' : 'WEBSERVER', 'Content-Type': 'text/html'}
status_codes = httplib.responses
#status_codes = {200:'OK', 404:'Not Found',}

    
def connection(client_socket):
	data = client_socket.recv(1024)
	response = handle_request(data)
	client_socket.send(response)
	client_socket.close()

def response_line(status_code):
        """Returns response line"""
        reason = status_codes[status_code]
        return "HTTP/1.1 %s %s\r\n" % (status_code, reason)
        

def response_header(filename=None):
	content_type = mimetypes.guess_type(filename)[0] or 'text/html'
	return {'Content-Type' : content_type}	
	
        	
def handle_request(data):
	uri, method = parse(data)
	
	if(method == 'GET'):
		filename = uri['GET'].strip('/')
		if os.path.exists(filename):
			res_line = response_line(200)
			res_header = response_header(filename)
			with open(filename) as f:
				res_body = f.read()
		else:
			res_line = response_line(404)
			res_header = response_header()
			
			res_body = "<h1>404 Not Found</h1>"
		
		blank_line = "\r\n"
		
		return "%s%s%s%s"%(res_line,res_header,blank_line ,res_body)

	
def parse(request):
	ret = dict()
	requestlist = request.split('\n')
	for requestelement in requestlist:
		Headers = requestelement.split(' ')
		if Headers[0] == "Content-Type:":
			ret["boundary"] = Headers[2][10:len(Headers[2])]
            		ret["boundary"] = "---" + ret["boundary"]
        	if Headers[0] == "Content-Disposition:":
           		ret["filename"] = Headers[3][10:len(Headers[3])-2]
            		method = "POST"
            		flag = 1
            		return ret,method
        	elif len(Headers) >= 2:
            		ret[Headers[0]] = Headers[1]
            		if Headers[0]=="GET":
                		method = "GET"
                		ret["Version"] = Headers[2]
                		ret["GET"] = ret["GET"][1:]
                		return ret,method




def tcpserver():
	server_socket = socket(AF_INET, SOCK_STREAM)
	server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	server_socket.bind((host,port))
	server_socket.listen(5)
	
	print("Server Started ",server_socket.getsockname())
	
	while True:
		conn, addr = server_socket.accept()
		print("Client connected")
		thread = Thread(target = connection, args = (conn,))
		thread.start()
			
	
	

if __name__ == '__main__':
	tcpserver()
	
