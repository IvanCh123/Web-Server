import os, threading, time, xml.etree.ElementTree as ET
from http.server import HTTPServer, BaseHTTPRequestHandler
from os import path
from socketserver import ThreadingMixIn
from io import BytesIO

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

    def set_headers(self, content_type, content_length = None):
        self.send_response(200)

        if content_length:
            self.send_header('Content-Length', content_length)
        self.send_header('Content-Type', content_type)
        self.end_headers()  

    def do_HEAD(self):
        if self.check_file(self.path[1:]):

            print("Path: ", self.path)

            file_to_open = open(self.path[1:],'rb').read() # rb lo abre como binario para que las imagenes funcionen

            _, suffix = path.splitext(self.path)
            
            content_type = self.types_handler.get_type(suffix[1:])
            content_length = len(file_to_open)

            self.set_headers(content_type, content_length)

        
    def do_GET(self):
        print("GET request")

        if self.path == '/':
            self.path = '/index.html'
        else:
            current_path = self.path
            current_path = current_path.split('?')
            """
            if len(current_path)>1:
                link = current_path[1].split('&')
                msg = link[0].split('=')
                msg = msg[1]
            """
            self.path = current_path[0]

        if self.check_file(self.path[1:]):
            file_to_open = open(self.path[1:],'rb').read() # rb lo abre como binario para que las imagenes funcionen

            _, suffix = path.splitext(self.path)
            
            content_type = self.types_handler.get_type(suffix[1:])
            content_length = len(file_to_open)

            self.set_headers(content_type, content_length)
            self.wfile.write(bytes(file_to_open))
    
    def do_POST(self):
        try:
            print("POST request")
            file_to_open = open(self.path[1:],'rb').read()
            
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
    try:
        server = ThreadedHTTPServer(('localhost', port), Server)
        #server = HTTPServer(('localhost', port), Server)
        print("Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print ("Closing web server")
        server.socket.close()

if __name__ == '__main__':
    main()    



