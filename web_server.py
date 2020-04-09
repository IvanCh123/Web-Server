import os, re, socket, threading, datetime, time, xml.etree.ElementTree as ET
from io import BytesIO
from urllib.parse import urlparse 

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
        file_type = self.types_handler.get_type(suffix[1:])

        if file_type in accept_buffer:
            return True
        else:
            for item in accept_buffer:
                if item.startswith("*/*"):
                    return True
        return False

    def send_headers(self, client_socket, protocol, error_code, content_type=None, content_length = None, file_content=None):
        error_html = "<html><body><h1>Error response</h1><p>Error code: {}</p><p>Message: {}.</p></body></html>\n"
        server = "MyCoolServer/1.0"
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
            
    def do_HEAD(self, data_vector, client_socket):
        file_name = data_vector[1]
        protocol = data_vector[4]

        if self.check_file(file_name): 
            if self.check_accept(data_vector):
                file_content = open(file_name,'rb').read() # rb lo abre como binario para que las imagenes funcionen
                _, suffix = os.path.splitext(file_name)
                
                content_type = self.types_handler.get_type(suffix[1:])
                content_length = len(file_content)

                self.send_headers(client_socket,protocol, "200 OK", content_type, content_length,None)
                time.sleep(1)
            else:
                self.send_headers(client_socket, protocol, "406 Not Acceptable",None,None,None)	
        else:
            self.send_headers(client_socket, protocol, "404 Not Found",None,None,None)
    
    def do_GET(self, data_vector, client_socket):
        file_name = data_vector[1]
        protocol = data_vector[4]

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
        file_name = data_vector[1]
        protocol = data_vector[4]
                
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

    def get_args(self, url):
        long_url = urlparse(url)
        file_name = long_url[2] #2: path index
        query = long_url[4] #4: query index

        return file_name[1:], query

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

    def parse_request(self, worker_id, data, client_socket, log_file):
        buffer_vector = data.split()#la request como vector 

        command = buffer_vector[0].decode("utf-8")# GET, POST, HEAD
        file_name = buffer_vector[1].decode("utf-8") # url/archivo
        protocol = buffer_vector[2].decode("utf-8") # HTTP/1.1
        accept_types = buffer_vector[self.look_for(buffer_vector, 'Accept')+1].decode("utf-8")
        host_name = buffer_vector[self.look_for(buffer_vector, 'Host')+1].decode("utf-8")
        
        buffer_vector = None
        query = ''

        if file_name == '/':
            file_name = 'index.html'
        else:
            file_name, query = self.get_args(file_name)

        data_vector = [command, file_name, host_name, accept_types, protocol]
        print("    [{}] {} request on {} @ {}".format(worker_id, command, host_name, file_name))
        
        request_meesage =  "{}, {}, {}, {}, {}, {}\n".format(command, int(time.time()), host_name, '', file_name, query)
        
        file = open(log_file, "a")
        file.write(request_meesage)
        file.close()
        
        return data_vector
	
def file_setup():
    date_tag = datetime.datetime.now().strftime("%Y-%b-%d_%H-%M-%S")
    cwd = os.getcwd()
    directory = os.path.join(cwd,"logs")

    if not os.path.exists(directory):
        os.mkdir(directory)

    file_name = '{}/logs/bitacora_{}.csv'.format(cwd, date_tag)
    log_file = open(file_name, "w")
    log_file.write("Metodo, Estampilla de Tiempo, Servidor, Refiere, URL, Datos\n")
    log_file.close()

    return file_name

def main():
    port = 80
    thread_count = 8

    request = Request_Handler()
    server_socket = socket.socket()
    
    server_socket.bind(('localhost',port))
    server_socket.listen(5)

    print("Server running on port %s" % port)

    file_name = file_setup()
    
    def thread_gen():
        for worker_id in range(thread_count):
            thread = threading.Thread(target=run, args=(worker_id, server_socket, file_name, request,))
            thread.daemon = True
            yield thread # use yield when we want to iterate over a sequence, but don’t want to store the entire sequence in memory.

    threads = list(thread_gen())

    for thread in threads:
        thread.start() 

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print ("Closing web server")
        server_socket.close()
        threads.clear()
        os.sys.exit(0) 

def run(worker_id, server_socket, file_name, request):
    client_socket, _addr = server_socket.accept()
    _continue = True
    try:
        while _continue:
            data = client_socket.recv(1024)
            if data:
                clean_data  = request.parse_request(worker_id,data, client_socket, file_name)
                request.call_server(clean_data, client_socket)
    except:
        _continue = False
        

if __name__ == '__main__':
    main()  