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

    def do_HEAD(self):
        self.send_header('Server', self.server_version)
        self.send_header('Date', self.date_time_string(time.time()))
        self.send_header('Content-Length', self.headers.get('Content-Length'))
        self.send_header('Content-Type', self.headers.get('Content-Type'))
        self.end_headers()

        #self.send_header('Accept') -> preguntar que es
                
        #self.send_header('Host', self.client_address)
        #self.send_header('Referer') 
        
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        try:
            file_to_open = open(self.path[1:],'rb').read() # rb lo abre como binario para que las imagenes funcionen
            self.send_response(200)
        except IOError:
            self.send_error('404',"File not found")
        
        _, suffix = path.splitext(self.path)
        
        content_type = self.types_handler.get_type(suffix[1:])
        content_length = len(file_to_open)

        self.send_header('content-Length', content_length)
        self.send_header('content-Type', content_type)
        self.end_headers()

        self.wfile.write(bytes(file_to_open))
    
    def do_POST(self):
        try:
            file_to_open = open(self.path[1:],'rb').read()
            self.send_response(200)
            
            _prefix, suffix = path.splitext(self.path)
            content_type = self.types_handler.get_type(suffix[1:])

            content_length = len(file_to_open)

            self.send_header('Content-Length', content_length)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(bytes(file_to_open))
        
        except:
            pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Se crea un thread cada que hay un request"""

def main():
    port = 80
    try:
        server = ThreadedHTTPServer(('localhost', port), Server)
        print("Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print ("Closing web server")
        server.socket.close()

if __name__ == '__main__':
    main()    



