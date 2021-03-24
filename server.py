from socket import *
from threading import *
from datetime import *
import os
import sys
from _thread import *
import mimetypes
from urllib.parse import *
from datetime import *
import time
import csv
from server_config import *
import base64


File_Extensions = {'.html':'text/html', '.txt':'text/plain', '.png':'image/png', '.gif': 'image/gif', '.jpg':'image/jpg', '.ico': 'image/x-icon', '.php':'application/x-www-form-urlencoded', '': 'text/plain', '.jpeg':'image/webp', '.pdf': 'application/pdf', '.js': 'application/javascript', '.css': 'text/css', '.mp3' : 'audio/mpeg', '.mp4':'video/mp4'}

File_Types = {'text/html': '.html','text/plain': '.txt', 'image/png': '.png', 'image/gif': '.gif', 'image/jpg': '.jpg','image/x-icon':'.ico', 'image/webp': '.jpeg', 'application/x-www-form-urlencoded':'.php', 'image/jpeg': '.jpeg', 'application/pdf': '.pdf', 'audio/mpeg': '.mp3', 'video/mp4': '.mp4'}


DATE= { 'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12 }


server_socket = socket(AF_INET, SOCK_STREAM)


cget_flag = False    # For Conditional Get
Server= True # Stop Server
CLOSE = True # Close Server
thread_list = []    # To maintain Threads
conn = True
status_code = 0    # Initialize status code as global varibale



# For Cookies
cookie_id = 0
cookie = 'Set-Cookie: id='
cookie_age = '; max-age=1800'

#function to return current date
def date():
	l = time.ctime().split(' ')
	l[0] = l[0] + ','
	string = (' ').join(l)
	string = 'Date: ' + string
	return string

def separate(file_path):
	list_filepath = file_path.split('?')
	file_path = list_filepath[0]
	if(len(list_filepath) > 1):
		query = parse_qs(list_filepath[1])
	else:
		query = {}
	return (file_path, query)



#function to handle status codes
def handle_STATUSCODE(client_socket, s_code):
	global thread_list, status_code
	#set the received status code as global
	status_code = s_code
	
	response = []
	
	
		
		
	
	if status_code == 403:
		response.append('HTTP/1.1 403 Forbidden')
		response.append('Host : 127.0.0.1')
		response.append(date())
		response.append('\r\n')
		response.append('<h1>Forbidden</h1>')
	elif status_code == 403:
		response.append('HTTP/1.1 500 Internal Server Error')
		
		response.append('Host : 127.0.0.1')
		response.append(date())
		response.append('\r\n')
		response.append('<h1>Internal Server Error</h1>')
	elif status_code == 411:
		response.append('HTTP/1.1 411 Length Required')
		
		response.append('Host : 127.0.0.1')
		response.append(date())
		response.append('\r\n')
		response.append('<h1>Length Required</h1>')

	elif status_code == 400:
		response.append('HTTP/1.1 400 Bad Request')
		response.append('Host : 127.0.0.1')
		response.append(date())
		response.append('\r\n')
		response.append('<h1>Bad Request</h1>')

	elif status_code == 404:
		
		response.append('HTTP/1.1 404 PAGE NOT FOUND')
		response.append('Host : 127.0.0.1')
		response.append(date())
		response.append('\r\n')
		response.append('<h1>PAGE NOT FOUND</h1>')

	elif status_code == 415:
		response.append('HTTP/1.1 415 Unsupported Media Type')
		response.append('Host : 127.0.0.1')
		response.append(date())
		response.append('\r\n')
		response.append('<h1>Unsupported Media Type</h1>')
		
	

	if status_code == 505:
		response.append('HTTP/1.1 505 VERSION UNSUPPORTED')
		response.append('Host : 127.0.0.1')
		response.append(date())
		response.append('\r\n')
		response.append('<h1>Version Unsupported</h1>')
	
	if CLOSE:
		msg= '\r\n'.join(response).encode()
		client_socket.send(msg)
	
	try:
		thread_list.remove(client_socket)
		client_socket.close()
	except:
		pass
	manage_server()


def Status_304(client_socket, file_path):
	response=[]
	#print("IN 304")
	global status_code
	status_code = 304
	response.append('HTTP/1.1 304 Not Modified')
		
	response.append(find_last_mdate(file_path))
	response.append('Host : 127.0.0.1')
	response.append(date())
	response.append('\r\n')
	
	
	msg= '\r\n'.join(response).encode()
	client_socket.send(msg)	

# To get last modified date and time of the file		
def find_last_mdate(file_path):
	get_time = time.ctime(os.path.getmtime(file_path))
	list_get_time = get_time.split(' ')
	list_get_time[0] += ','
	l_mtime = 'Last-Modified : '+' '.join(list_get_time)
	return l_mtime


def is_file_modified(file_path, l):
	global cget_flag,DATE
	#print(l)
	list_time = l.split(' ')
	#print(list_time)
	
		
		
	li = find_last_mdate(file_path)
	cmp_li = ''.join(li.split(': ')).split(' ')
	cmp_li.pop(0)
	
	list_time = ''.join(list_time)
	cmp_li = ''.join(cmp_li)
	if(list_time == cmp_li):
		
		cget_flag = True
	else:
		cget_flag = False
			

def handle_DELETE(client_socket, header_dict, file_path, entity_body):
	response = []
	global status_code
	
	IsFile = os.path.isfile(file_path)
	IsDir = os.path.isdir(file_path)
	
	
	# Check if Authorized
	if 'Authorization' in header_dict.keys():
		credentials = header_dict['Authorization'].split(' ')
		#print(credentials)
		credentials = base64.decodebytes(credentials[1].encode())
		credentials = credentials.decode()
		credentials = credentials.split(':')
		#print(credentials[0])
		#print(credentials[1])
		if credentials[0] == username and credentials[1]==password:
			#print("ACKASDF")
			if IsDir:
				status_code = 405
				response.append('HTTP/1.1 405 Method Not Allowed')
			elif IsFile:
				if os.access(file_path, os.W_OK):
					try:
						os.remove(file_path)
					except:
						pass
				else:
					handle_STATUSCODE(client_socket, 403)
			else:
				handle_STATUSCODE(client_socket, 400)
				
			
		else:
			status_code = 401
			response.append('HTTP/1.1 401 Unauthorized')
			response.append('\r\n')
			msg = '\r\n'.join(response).encode()
			client_socket.send(msg)
			return
			
		
	else:
		status_code = 401
		response.append('HTTP/1.1 401 Unauthorized')
		response.append('\r\n')
		msg = '\r\n'.join(response).encode()
		client_socket.send(msg)
		return
		
	response.append('Host : 127.0.0.1')
	response.append(date())
	response.append('\r\n')
	msg = '\r\n'.join(response)
	client_socket.send(msg.encode())





def handle_PUT(client_socket, header_dict, entity_body, addr, file_path, f_data, file_f):
	No_flag = False
	code_201 = False
	
	response = []
	global status_code
	
	# Check for file and dir
	IsFile = os.path.isfile(file_path)
	IsDir = os.path.isdir(file_path)
	
	try:
		Length = int(header_dict['Content-Length'])
		#print('Length : '+ str(Length))
	except KeyError:
		handle_STATUS(client_socket, 411)
	
	
	#Append data to file
	
	try:
		f_data += entity_body
	except TypeError:
		entity_body = entity_body.encode()
		f_data += entity_body
	size = Length - len(entity_body)
	#print("SIZE : " + str(size))
	
	#print(addr)
	 
	#print(f_data)
	
	if IsFile:
		if os.access(file_path, os.W_OK):
			No_flag = True
			
			fp = open(file_path, 'wb')
			fp.write(f_data)
			fp.close()
		else:
			handle_STATUSCODE(client_socket, 403)
	elif IsDir:
	
		pass
	else:
		if DOCUMENTROOT in file_path:
			code_201 = True
			fp = open(file_path,'wb')
			fp.write(f_data)
			fp.close()
		else:
			No_flag = False
	
	if code_201:
		status_code = 201
		response.append('HTTP/1.1 201 Created')
		response.append('Content-Location : ' + file_path)
	elif No_flag:
		status_code = 204
		response.append('HTTP/1.1 204 No Content')
		response.append('Content-Location : ' + file_path)
		
	response.append('\r\n')
	return response
		
			
			
		
			

		

def handle_POST(client_socket, header_dict, entity_body):
	response =[]
	global status_code
	
	info_dict = parse_qs(entity_body)
	file_path = DOCUMENTROOT + '/sample.csv'
	
	#Check for file permissions
	
	
	keys = []
	values = []
	
	for i in info_dict:
		keys.append(i)
		for j in info_dict[i]:
			values.append(j)
	
	#If file already exists
	if_file = os.path.exists(file_path)
	if if_file:
		if os.access(file_path, os.R_OK) and os.access(file_path, os.W_OK):
			fp = open(file_path, 'a')	
			response.append('HTTP/1.1 200 OK')
			status_code = 200
			file_write = csv.writer(fp)
			file_write.writerow(keys)
			file_write.writerow(values)
			fp.close()
			
		else:
			handle_STATUSCODE(client_socket, 403)
		
		
	else:
		fp = open(file_path,'w')
		response.append('HTTP/1.1 201 File Created')
		status_code = 201
		response.append('Path : '+ file_path)
		file_write = csv.writer(fp)
		file_write.writerow(keys)
		file_write.writerow(values)
		fp.close()
	
	response.append(date())
	response.append('Host : 127.0.0.1')
	response.append('Content-Type : text/html')
	
	response.append(find_last_mdate(file_path))
	response.append('\r\n')
	response.append('<h1>INFO RECEIVED</h1>')
	msg = '\r\n'.join(response)
	client_socket.send(msg.encode())
	
		


		
def handle_HEAD(client_socket, header_dict, file_path):
	global conn,server_socket
	global status_code
	response = []
	#print("IN HEAD")
	
	# Use os library to check if file exists 
	# Whether its a dir or file
	# Check file permissions
	IsFile = os.path.isfile(file_path)
	IsDir = os.path.isdir(file_path)
	
	
	if(IsFile):
	#Check is file has readable permissions
		if(os.access(file_path, os.R_OK)):
			pass
		#if not allowed then throw status code 403
		else:
			handle_STATUSCODE(client_socket , 403)
			
		response.append('HTTP/1.1 200 OK')
		status_code = 200
		response.append(date())
		response.append('Server : 127.0.0.1')
		
		response.append(find_last_mdate(file_path))
		
		# Open the file and read contents
		
		try:
			f = open(file_path, "rb")
			size = os.path.getsize(file_path)
			data = f.read(size)
			
			
		except:
			handle_STATUSCODE(client_socket, 500)
		
		
	
	elif(IsDir):
		if(os.access(file_path, os.R_OK)):
			pass
		#if not allowed then throw status code 403
		else:
			handle_STATUSCODE(client_socket, 403)
		
		response.append('HTTP/1.1 200 OK')
		status_code = 200
		
		#List out all files in dir
		list_dir = os.listdir(file_path)
		for name in list_dir:
			if name.startswith('.'):
				list_dir.remove(name)
	
	else:
		handle_STATUSCODE(client_socket, 404)
	
	
	
	for l in header_dict:
		if l == 'Host':
			pass
			
		
		elif l == 'Accept':
			if IsFile:
				try:
					file_ext = os.path.splitext(file_path)
					
					if file_ext[1] in File_Extensions.keys():
						STR = File_Extensions[file_ext[1]]
					else:
						STR = 'text/plain'
					STR = 'Content-Type : '+ STR
					
					response.append(STR)
				except:
					handle_STATUSCODE(client_socket, 415)
		elif l == 'User-Agent':
			pass
		
		elif l == 'If-Modified-Since':
			
			is_file_modified(file_path, header_dict[l])
		
		elif l == 'connection':
			if IsFile:
				conn = True
				response.append('Connection : Keep-Alive')
		elif l == 'Accept-Language':
			lang = 'Content-Language : '+ header_dict[l]
			response.append(lang)
		elif l == 'Accept-Encoding':
			if IsFile:
				response.append('Accpet-Encoding : '+ header_dict[l])
			
		else:
			continue
	#print('\r\n'.join(response))
	
	if IsFile:
		response.append('\r\n')
		
		if cget_flag == True:
			handle_STATUSCODE(file_path, 304)
		elif cget_flag == False:
			
		
			response = '\r\n'.join(response).encode()
			client_socket.send(response)
			
		
		
		
	else:
		handle_STATUSCODE(client_socket, 400)
	
	
	client_socket.close()




def handle_GET(client_socket, header_dict, file_path, query):
	global conn,server_socket
	global status_code
	global cookie_id, cget_flag
	response = []
	
	# Use os library to check if file exists 
	# Whether its a dir or file
	# Check file permissions
	IsFile = os.path.isfile(file_path)
	IsDir = os.path.isdir(file_path)
	
	
	if(IsFile):
	#Check is file has readable permissions
		if(os.access(file_path, os.R_OK)):
			pass
		#if not allowed then throw status code 403
		else:
			handle_STATUSCODE(client_socket , 403)
			
		response.append('HTTP/1.1 200 OK')
		status_code = 200
		response.append(date())
		
		response.append('Server : 127.0.0.1')
		
		response.append(find_last_mdate(file_path))
		# Open the file and read contents
		
		try:
			f = open(file_path, "rb")
			size = os.path.getsize(file_path)
			data = f.read(size)
			response.append('Content-Length : ' + str(size))
			
			
		except:
			handle_STATUSCODE(client_socket, 500)
		
		
	
	elif(IsDir):
		if(os.access(file_path, os.R_OK)):
			pass
		#if not allowed then throw status code 403
		else:
			handle_STATUSCODE(client_socket, 403)
		
		response.append('HTTP/1.1 200 OK')
		status_code = 200
		response.append(date())
		response.append('Server : 127.0.0.1')
		
		response.append(find_last_mdate(file_path))
		
		#List out all files in dir
		list_dir = os.listdir(file_path)
		for name in list_dir:
			if name.startswith('.'):
				list_dir.remove(name)
	
	else:
		handle_STATUSCODE(client_socket, 404)
	
	response.append(cookie + str(cookie_id) + cookie_age)
	cookie_id+=1
	#print("==================")
	#print(header_dict)
	
	for l in header_dict:
		if l == 'Host':
			pass
			
		
		elif l == 'Accept':
			if IsFile:
				try:
					file_ext = os.path.splitext(file_path)
					
					if file_ext[1] in File_Extensions.keys():
						STR = File_Extensions[file_ext[1]]
					else:
						STR = 'text/plain'
					STR = 'Content-Type : '+ STR
					
					response.append(STR)
				except:
					handle_STATUSCODE(client_socket, 415)
		elif l == 'User-Agent':
			pass
		
		elif l == 'If-Modified-Since':
			#print(header_dict[l])
			is_file_modified(file_path, header_dict[l])
		
		
		elif l == 'connection':
			if IsFile:
				conn = True
				response.append('Connection : Keep-Alive')
				
		
				
		elif l == 'Accept-Language':
			lang = 'Content-Language : '+ header_dict[l]
			response.append(lang)
		
		elif l == 'Cookie':
			cookie_id-=1
			response.remove(cookie + str(cookie_id) + cookie_age)	
		else:
			continue
	
	#print(cget_flag)
	if IsFile:
		response.append('\r\n')
		
		if cget_flag == True:
			Status_304(client_socket, file_path)
		elif cget_flag == False:
			
		
			response = '\r\n'.join(response).encode()
			client_socket.send(response)
			client_socket.sendfile(f)
		
	elif IsDir:
		response.append('\r\n')
		response.append('<h1>FILES IN THE DIR</h1>')
		for line in list_dir:
			if file_path == '/':
				link = 'http://' + '127.0.0.1' + ':' + str(port) + '/' + line
				link_l = '<li><a href ="'+link+'">'+line+'</a></li>'
				response.append(link_l)
			else:
				link = 'http://' + '127.0.0.1' + ':' + str(port) +'/'  + line
				link_l = '<li><a href ="'+link+'">'+line+'</a></li>'
				response.append(link_l)
		response.append('</ul></body></html>')
		msg = '\r\n'.join(response).encode()
		client_socket.send(msg)
		client_socket.close()	
	
	elif len(query) > 0 and not IsFile and not IsDir:
		file_path = DOCUMENTROOT + '/sample.txt'
		response = []
		q_dict = parse_qs(query)
		file_path = DOCUMENTROOT + '/sample.csv'
	
		
	
	
		keys = []
		values = []
	
		for i in q_dict:
			keys.append(i)
			for j in q_dict[i]:
				values.append(j)
	
		#If file already exists
		if_file = os.path.exists(file_path)
		if if_file:
			if os.access(file_path, os.R_OK) and os.access(file_path, os.W_OK):
				pass
			else:
				handle_STATUSCODE(client_socket, 403)
		
			fp = open(file_path, 'a')	
			response.append('HTTP/1.1 200 OK')
			status_code = 200
			file_write = csv.writer(fp)
			#file_write.writerow(keys)
			file_write.writerow(values)
			fp.close()
		else:
			fp = open(file_path,'w')
			response.append('HTTP/1.1 201 File Created')
			status_code = 201
			response.append('Path : '+ file_path)
			file_write = csv.writer(fp)
			file_write.writerow(keys)
			file_write.writerow(values)
			fp.close()
	
		response.append(date())
		response.append('Host : 127.0.0.1')
		response.append('Content-Type : text/html')
		response.append(find_last_mdate(file_path))
		response.append('\r\n')
		response.append('<h1>INFO RECEIVED</h1>')
		msg = '\r\n'.join(response)
		client_socket.send(msg.encode())
		
		
	else:
		handle_STATUSCODE(client_socket, 400)
	'''
	if(os.path.exists(file_path)):
		response.append('HTTP/1.1 200 OK')
		file_path=file_path.strip('/')[-1]
		with open(file_path) as f:
			data = f.read()
		client_socket.send(data)
	else:
		client_socket.send('ACK1'.encode('utf-8'))
	
	'''
	
	client_socket.close()


def connection(client_socket, addr, new_thread_start_no):
	global CLOSE, Server, conn
	global server_socket, thread_list, cget_flag
	
	conn = True
	file_f = False
	f_data = b""
	cget_flag = False
	while conn and CLOSE and Server:
		# Accept the data from clients
		
		data = client_socket.recv(1024)
		
		
		#Split the received data
		try:
			data = data.decode('utf-8')
			#print(data)
			#print()
			file_f = True
			
			data_list = data.split('\r\n\r\n')
			
			
		except UnicodeDecodeError:
			data_list = data.split(b'\r\n\r\n')
			file_f = False
			
		
		#Check if there are requests or not
		length_data_list = len(data_list)
		
		if (length_data_list > 1):
			pass
		else:
			#Handle single req line
			header_list = {}
			single_req_line_list = data_list[0].split(' ')
			if(len(single_req_line_list) >=3):
				method = single_req_line_list[0]
				file_path = single_req_line_list[1]
				http_version = single_req_line_list[2] or 'HTTP/1.1'
				file_path = DOCUMENTROOT + file_path
			else:
				handle_STATUSCODE(client_socket, 400)
			query = {}	
			if method == 'GET':
				handle_GET(client_socket,header_list,file_path,query)
			elif method == 'HEAD':
				handle_HEAD(client_socket, header_list, file_path)
			
			
		
				
			
			break
		
		#Separeate the headers and gather all the info from requst made
		
		list_headers = data_list[0].split('\r\n')
		request_made= list_headers[0].split(' ')
		file_path = request_made[1]
		method = request_made[0]
		http_version = request_made[2] or 'HTTP/1.1'
		entity_body = data_list[1]
		
		file_path , query = separate(file_path)
		#print(file_path)
		#print(query)
		#print(entity_body)
		file_path = DOCUMENTROOT + file_path
		
		
		
		try:
			http_version_no = http_version.split('/')[1]
			if not (http_version_no == '1.1'):
				handle_STATUSCODE(client_socket, 505)
				pass
		except IndexError:
			handle_STATUSCODE(client_socket, 505)
			pass
		
		#print(os.path.isfile(file_path))
		#Dictionary for headers from received data
		header_dict = {}
		
		request_made = list_headers.pop(0)
		
		for l in list_headers:
			list_of_lines = l.split(': ')
			header_dict[list_of_lines[0]] = list_of_lines[1]
			
		#print(header_dict)		
		
		if( method == 'GET'):
			handle_GET(client_socket, header_dict, file_path, query)
		elif (method == 'HEAD'):
			handle_HEAD(client_socket, header_dict, file_path)
		elif(method == 'POST'):
			handle_POST(client_socket, header_dict, entity_body)
		elif(method == 'PUT'):
			handle_PUT(client_socket, header_dict, entity_body, addr,  file_path, f_data, file_f)
		elif(method == 'DELETE'):
			handle_DELETE(client_socket, header_dict, file_path, entity_body)
		else:
			break
		
		
		conn = False
	client_socket.close()
	thread_list.remove(client_socket)
		


	
	
	
def httpServer():
	global CLOSE, Server, conn, thread_list
	while CLOSE:
		while Server:
			if not CLOSE:   # If server not started then break
				break
			new_thread_start_no = 0
			client_socket, addr = server_socket.accept()
			thread_list.append(client_socket)
			start_new_thread(connection,(client_socket, addr, new_thread_start_no))
			
			
	server_socket.close()

def manage_server():
	global CLOSE, Server, conn
	
	while True:
		
		str_status = input()
		
		if str_status== 'pause':
			Server = False
		elif str_status == 'start':
			Server = True
		elif str_status == 'stop':
			CLOSE = False
			conn = False
			break

if __name__ == '__main__':
	host = '127.0.0.1'
	port = int(sys.argv[1])
	server_socket.bind((host,port))
	server_socket.listen(5)
	print('Serving HTTP on ' + host + ' port ' + str(port) + ' (http://' + host + ':' + str(port) +'/)')
	start_new_thread(manage_server, ())
	httpServer()
	sys.exit()
	
