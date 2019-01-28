import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = ('localhost', 12001)
sock.settimeout(1)

seq_number = 1
while seq_number < 11:
	start = time.time()
	message = 'Ping ' + str(seq_number) + " " + str(start)
	try:
		sent = sock.sendto(message.encode(), server_addr)
		print("Sent " + message)
		data,server= sock.recvfrom(4096)
		data = data.decode()
		print("Received " + data)
		end = time.time();
		elapsed = end - start
		print("RTT is " + str(elapsed) + " seconds\n")
	except socket.timeout:
		print("Ping " + str(seq_number) + " Requested Time out\n")
	seq_number = seq_number + 1

print("closing socket")
sock.close()