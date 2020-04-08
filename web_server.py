import os, re, socket, threading, datetime, logging, time, xml.etree.ElementTree as ET
from io import BytesIO
from urllib.parse import urlparse 
from socket import SHUT_WR
from multiprocessing import Process

"""
	data_vector:
		# 0: COMMAND
		# 1: PATH
		# 2: HOST
		# 3: ACCEPT_TYPES
		# 4: PROTOCOL
"""

class XML_Handler:
    root = None
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.parse_xml()
        
    def parse_xml(self):
        mytree = ET.parse(self.xml_file)
        self.root = mytree.getroot()
        # TODO: parse to dictionary for direct access (keys)

    def get_type(self, ext):    
        mime_types = self.root.findall('mime-mapping')  
        
        for mime in mime_types:
            extension = mime.find('extension').text
            if (extension == ext):
                return mime.find('mime-type').text

class Server_Handler:
	types_handler = XML_Handler('mimetypes.xml')
	def check_file(self, file_path):
		if os.path.exists(file_path):
			return True
		return False    

	def look_for(self, looking, array):
		index = 0
		for item in array:
			if looking in item:
				return index
			index+=1
		return -1
	def check_accept(self,data_vector):

		file_name = data_vector[1]
		accept_types = data_vector[3]

		if file_name == '/':
			file_name = '/index.html'


		_, suffix = os.path.splitext(file_name)

		if suffix.find('?') != -1: 
			file_true_type = suffix.split("?")
			suffix = file_true_type[0]

		accept_buffer = accept_types.split(",")
		print("asd",suffix)

		return True

		if accept_types == "*":
			return True
		elif accept_types != suffix:
			return False
		else: 
			return True

	def send_headers(self, client_socket, protocol, error_code, content_type=None, content_length = None, file_content=None):
		error_html = "<html><body><h1>Error response</h1><p>Error code: {}</p><p>Message: {}.</p></body></html>\n"
		server = "MyServer/1.0"
		if not error_code.startswith('200'):
			message = ""
			if error_code.startswith('404'):
				message = "File not found."
			elif error_code.startswith('406'):
				message = "File not acceptable"
			else: #501
				message = "The request method is not supported."
			
			content_type = "text/html"
			file_content = error_html.format(error_code, message).encode("utf-8")
			content_length = len(file_content)	
		
		output = "%s %s\nDate: %s\nServer: %s\nContent-Length: %d\nContent-Type: %s\n\n" % (protocol, error_code, time.asctime(), server, content_length, content_type) 
		
		if file_content:
			client_socket.send(output.encode("utf-8")+file_content) 
		else:
			client_socket.send(output.encode("utf-8"))
			
	def log_info(self, command, server, referer='', url='', data=''):
		logging.info(" {} > {} > {} > {} > /{} > {}".format(command, int(time.time()), server, referer, url, data))    

	def get_args(self, url):
		long_url = urlparse(url)
		file_name = long_url[2] #2: path index
		query = long_url[4] #4: query index

		return file_name[1:], query
		
	def do_HEAD(self, data_vector, client_socket):
		command = data_vector[0]
		file_name = data_vector[1]
		host_name = data_vector[2]
		protocol = data_vector[4]

		file_name, query = self.get_args(file_name)
		self.log_info(command , host_name, '', file_name, query)

		if self.check_file(file_name): 
			if self.check_accept(data_vector):
				file_content = open(file_name,'rb').read() # rb lo abre como binario para que las imagenes funcionen
				_, suffix = os.path.splitext(file_name)
				
				content_type = self.types_handler.get_type(suffix[1:])
				content_length = len(file_content)

				self.send_headers(client_socket,protocol, "200 OK", content_type, content_length,None)
			else:
				self.send_headers(client_socket, protocol, "406 Not Acceptable",None,None,None)	
		else:
			self.send_headers(client_socket, protocol, "404 Not Found",None,None,None)
	
	def do_GET(self, data_vector, client_socket):
		query = ''
		command = data_vector[0]
		file_name = data_vector[1]
		host_name = data_vector[2]
		protocol = data_vector[4]

		if file_name == '/':
			file_name = 'index.html'
		else:
			file_name, query = self.get_args(file_name)

		self.log_info(command, host_name, '', file_name, query)

		if self.check_file(file_name):
			if self.check_accept(data_vector):
				file_content = open(file_name,'rb').read() # rb lo abre como binario para que las imagenes funcionen

				_, suffix = os.path.splitext(file_name)
				
				content_type = self.types_handler.get_type(suffix[1:])
				content_length = len(file_content)

				self.send_headers(client_socket, protocol, "200 OK", content_type, content_length, file_content)
			else:
				self.send_headers(client_socket, protocol, "406 Not Acceptable",None,None,None)		
		else:
			self.send_headers(client_socket, protocol, "404 Not Found",None,None,None)
	
	def do_POST(self, data_vector, client_socket):
		command = data_vector[0]
		file_name = data_vector[1]
		host_name = data_vector[2]
		protocol = data_vector[4]
		
		file_name, query = self.get_args(file_name)
		self.log_info(command, host_name, '', file_name, query)
		
		try:
			file_content = open(file_name,'rb').read()
			if self.check_accept(data_vector):
				_prefix, suffix = os.path.splitext(file_name)
				
				content_type = self.types_handler.get_type(suffix[1:])
				content_length = len(file_content)

				self.send_headers(client_socket, protocol, "200 OK", content_type, content_length, file_content)
			else:
				self.send_headers(client_socket, protocol, "406 Not Acceptable",None,None,None)	
		except:
			self.send_headers(client_socket, protocol, "404 Not Found",None,None,None)

class Request_Handler:
	server = Server_Handler()

	def call_server(self, data_vector, client_socket):
		method_type = data_vector[0]
		protocol = data_vector[4]

		if method_type == "GET":
			self.server.do_GET(data_vector, client_socket)
		elif method_type == "POST":
			self.server.do_POST(data_vector, client_socket)
		elif method_type == "HEAD":
			self.server.do_HEAD(data_vector, client_socket)	
		else:
			return self.server.send_headers(client_socket, protocol, "501 Not supported",None,None,None)
				
	def look_for(self, buffer_vector, var):
		index = 0
		for item in buffer_vector:
			if item.decode("utf-8").startswith(var):
				return index
			index+=1
		return -1
	def parse_request(self, data, client_socket):
		buffer_vector = data.split()#la request como vector 

		command = buffer_vector[0].decode("utf-8")# GET, POST, HEAD
		file_name = buffer_vector[1].decode("utf-8") # url/archivo
		protocol = buffer_vector[2].decode("utf-8") # HTTP/1.1
		accept_types = buffer_vector[self.look_for(buffer_vector, 'Accept')+1].decode("utf-8")
		host_name = buffer_vector[self.look_for(buffer_vector, 'Host')+1].decode("utf-8")
		
		buffer_vector = None
		data_vector = [command, file_name, host_name, accept_types, protocol]

		return data_vector

def run(data, request, client_socket):	
	new_data  = request.parse_request(data, client_socket)
	request.call_server(new_data, client_socket)
	

def main():
	port = 80
	request = Request_Handler()

	server_socket = socket.socket()
	server_socket.bind(('localhost',port))
	server_socket.listen(5)

	print("Server running on port %s" % port)
	
	date_tag = datetime.datetime.now().strftime("%Y-%b-%d_%H-%M-%S")
	cwd = os.getcwd()
	directory = os.path.join(cwd,"logs")

	if not os.path.exists(directory):
		os.mkdir(directory)

	file_name = '{}/logs/bitacora_{}.log'.format(cwd, date_tag)
	logging.basicConfig(filename=file_name, level=logging.INFO)

	client_socket = None
	try:
		while True:
			client_socket, addr = server_socket.accept()
			data = client_socket.recv(1024)
			logging.info('\n---------\nLog started on %s.\n---------' % time.asctime())
			if data:
				process = Process(target=run, args=(data,request,client_socket,))
				print("[%s] Started" % process.name)
				process.start()

			if process.name != "Process-1":
				process.join()			
			
	except KeyboardInterrupt:
		print ("Closing web server")
		logging.info('\n---------\nLog closed on %s.\n---------\n' % time.asctime())
		client_socket.shutdown(SHUT_WR)
		client_socket.close()
	
	

if __name__ == '__main__':
    main()  