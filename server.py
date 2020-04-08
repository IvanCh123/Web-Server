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
	method_Type = buffer_vector[8] #GET, POST, HEAD
	file_Open = buffer_vector[1]

	print(method_Type)
	file_open_String = file_Open.decode("utf-8")
	if file_open_String == "/":
		file_open_String = "/index.html"
	accept_clause = method_Type.decode("utf-8")
	print(accept_clause)
	print(file_open_String)
	file_type_buffer = file_open_String.split(".")
	file_type = file_type_buffer[1]

	#si el string es mas largo
	if file_type.find('?') != -1:
		file_trueType = file_type.split("?")
		file_type = file_trueType[0]
	accept_buffer = accept_clause.split("/")
	accept_type = accept_buffer[1]
	print(accept_type)
	print(file_type)

	if accept_type == "*":
		print("200Ok")
	else:
		if accept_type != file_type:
			print("Error 406")
		else: 
			print("200OK")	 	

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

# print(self.headers['Accept'])#borrar todo desde aqui
# own_headers = self.headers['Accept'].split("/")
# print(own_headers)