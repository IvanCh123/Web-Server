import socket


#class Server():


#serverHandler = serverHandler()
server = socket.socket()
server.bind(('localhost',80))
server.listen(5)


while True:
	conexion, addr = server.accept()
	print ("Nueva conexion establecida")
	print(addr) 

	peticion = conexion.recv(1024)
	#peticion.decode(encoding='UTF-8')
	print("Peticion")
	print(peticion)
	buffer_vector = peticion.split()#la peticion como vector 
	print(buffer_vector)
	method_Type = buffer_vector[0] #GET, POST, HEAD
	print(method_Type)

	#Estructura, comentado porque no se ha implementado los metodos
	
	# if serverHandler.verifyAccept(buffer_vector) == True #Verifica que el tipo de archivo que se pide y el que viene en el accept concuerden
	# 	if method_Type == "GET":
	# 		serverHandler.do_Get(buffer_vector)
	# 	if method_Type == "POST":
	# 		serverHandler.do_POST(buffer_vector)
	# 	if method_Type == "HEAD":
	# 		serverHandler.do_HEAD(buffer_vector)	

	# else: 
		#se retorna el error 406

	#file = x[1]
	#compare_file = x[8]
	#print(file)
	#print(compare_file)

	#file_extension = file.split(".")
	#compare_file_extension = compare_file.split("/")
	#print(file_extension)
	#print(compare_file_extension)
	#print(file_extension[1])
	#print(compare_file_extension[1])
	respuesta = b"Hola, Solicitud recibida"
	#respuesta = respuesta.encode(encoding='utf-8')
	conexion.send(respuesta)
	conexion.close()



#class serverHandler():
	#verifica si el archivo que se busca esta dentro del accept
	#def verifyAccept(self, buffer):


	#def do_Get(self, buffer):

	#def do_HEAD(self, buffer):

	#def do_POST(self, buffer):
# 	server = Server()



# def main():
# 	server.run()

# main()