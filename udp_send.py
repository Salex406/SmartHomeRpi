import socket

UDP_IP = "255.255.255.255"
UDP_PORT = 1113

def send(msg):
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	try:
		sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))
	except socket.timeout:
		print("Socket timeout")
		pass
	except socket.error:
		print("Socket error")	
		pass

