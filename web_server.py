import os, threading, datetime, logging, time, xml.etree.ElementTree as ET
from http.server import HTTPServer, BaseHTTPRequestHandler
from os import path
from socketserver import ThreadingMixIn
from io import BytesIO
from urllib.parse import urlparse 

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

class Server(BaseHTTPRequestHandler):
    types_handler = XML_Handler('mimetypes.xml')
    
    def check_file(self, file_path):
        if path.exists(file_path):
            return True
        self.send_error(404,"File not found")
        return False    

    def check_accept(self,file_path):


        file_Open = file_path 

        if file_Open == '/':
            file_Open = '/index.html'
 
        file_type_buffer = file_Open.split(".")#
        file_type = file_type_buffer[1] #html o extension


        if file_type.find('?') != -1: 
            file_trueType = file_type.split("?")
            file_type = file_trueType[0]
        accept_buffer = self.headers['Accept'].split("/")#accept_clause.split("/")
        accept_type = accept_buffer[1] #gif de image/gif o el * de */*

        if accept_type == "*":
            return True
        else:
            if accept_type != file_type:
                self.send_error(406,"Not Acceptable")
            else: 
                return True

    def set_headers(self, content_type, content_length = None):
        self.send_response(200)

        if content_length:
            self.send_header('Content-Length', content_length)
        self.send_header('Content-Type', content_type)
        self.end_headers()  

    def log_info(self, command, server, referer='', url='', data=''):
        logging.info(" {} > {} > {} > {} > /{} > {}".format(command, int(time.time()), server, referer, url, data))    

    def get_args(self, url):
        long_url = urlparse(self.path)
        path = long_url[2] #path index
        query = long_url[4] #query index

        return path[1:], query
        
    def do_HEAD(self):
        self.path, query = self.get_args(self.path)
        self.log_info(self.command , 'localhost', '', self.path, query)

        if self.check_file(self.path) and self.check_accept(self.path):
            file_to_open = open(self.path,'rb').read() # rb lo abre como binario para que las imagenes funcionen

            _, suffix = path.splitext(self.path)
            
            content_type = self.types_handler.get_type(suffix[1:])
            content_length = len(file_to_open)

            self.set_headers(content_type, content_length)
        
    def do_GET(self):
        query = ''
        if self.path == '/':
            self.path = 'index.html'
        else:
            self.path, query = self.get_args(self.path)

        self.log_info(self.command, 'localhost', '', self.path, query)

        if self.check_file(self.path) and self.check_accept(self.path):
            file_to_open = open(self.path,'rb').read() # rb lo abre como binario para que las imagenes funcionen

            _, suffix = path.splitext(self.path)
            
            content_type = self.types_handler.get_type(suffix[1:])
            content_length = len(file_to_open)

            self.set_headers(content_type, content_length)
            self.wfile.write(bytes(file_to_open))
    
    def do_POST(self):
        
        self.path, query = self.get_args(self.path)
        self.log_info(self.command, 'localhost', '', self.path, query)
        try:
            
            file_to_open = open(self.path,'rb').read()
            
            _prefix, suffix = path.splitext(self.path)
            
            content_type = self.types_handler.get_type(suffix[1:])
            content_length = len(file_to_open)

            self.set_headers(content_type, content_length)
            self.wfile.write(bytes(file_to_open))
        except:
            self.send_error(404,"File not found")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Se crea un thread cada que hay un request"""

def main():
    port = 80
    date_tag = datetime.datetime.now().strftime("%Y-%b-%d_%H-%M-%S")
    cwd = os.getcwd()
    directory = os.path.join(cwd,"logs")
    
    if not os.path.exists(directory):
        os.mkdir(directory)
    
    file_name = '{}/logs/bitacora_{}.log'.format(cwd, date_tag)

    logging.basicConfig(filename=file_name, level=logging.INFO)

    try:
        logging.info('\n---------\nLog started on %s.\n---------' % time.asctime())

        server = ThreadedHTTPServer(('localhost', port), Server)
        print("Server running on port %s" % port)
        server.serve_forever()
    
    except KeyboardInterrupt:
        print ("Closing web server")
        logging.info('\n---------\nLog closed on %s.\n---------\n' % time.asctime())
        server.socket.close()

if __name__ == '__main__':
    main()    


