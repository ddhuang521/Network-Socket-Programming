from socket import *
import socket
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2

# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

def checksum(str_):
	# In this function we make the checksum of our packet 
	str_ = bytearray(str_)
	csum = 0
	countTo = (len(str_) // 2) * 2

	for count in range(0, countTo, 2):
		thisVal = str_[count+1] * 256 + str_[count]
		csum = csum + thisVal
		csum = csum & 0xffffffff

	if countTo < len(str_):
		csum = csum + str_[-1]
		csum = csum & 0xffffffff

	csum = (csum >> 16) + (csum & 0xffff)
	csum = csum + (csum >> 16)
	answer = ~csum
	answer = answer & 0xffff
	answer = answer >> 8 | (answer << 8 & 0xff00)
	return answer

def build_packet():
	myChecksum = 0
	myID = os.getpid() & 0xFFFF

	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)

	data = struct.pack("d", time.time())

	myChecksum = checksum(header + data)    
	if sys.platform == 'darwin':
		myChecksum = socket.htons(myChecksum) & 0xffff
	else:
		myChecksum = htons(myChecksum)

	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
	packet = header + data
	return packet

def get_route(hostname):
	timeLeft = TIMEOUT
	for ttl in range(1,MAX_HOPS):
		for tries in range(TRIES):
			destAddr = socket.gethostbyname(hostname)
			
			#Fill in start
			# Make a raw socket named mySocket
			icmp = socket.getprotobyname("icmp")
			mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
			#Fill in end
			
			mySocket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
			mySocket.settimeout(TIMEOUT)
			try:
				d = build_packet()
				mySocket.sendto(d, (hostname, 0))
				t = time.time()
				startedSelect = time.time()
				whatReady = select.select([mySocket], [], [], timeLeft)
				howLongInSelect = (time.time() - startedSelect)

				if whatReady[0] == []: # Timeout
					print ("*    *    * Request timed out.")

				recvPacket, addr = mySocket.recvfrom(1024)
				timeReceived = time.time()
				timeLeft = timeLeft - howLongInSelect
				if timeLeft <= 0:
					print ("*    *    * Request timed out.")

			except socket.timeout:
				continue

			else:
				icmpHeader = recvPacket[20:28]
				request_type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)

				if request_type == 11:
					bytes = struct.calcsize("d")
					timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
					print (" %d   rtt=%.0f ms %s addr %s" % (ttl,(timeReceived -t)*1000, addr[0],socket.getfqdn(addr[0])))
					# using getfadn() to get hostname
				elif request_type == 3:
					bytes = struct.calcsize("d")
					timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
					print (" %d   rtt=%.0f ms %s addr %s" % (ttl,(timeReceived -t)*1000, addr[0],socket.getfqdn(addr[0])))
				elif request_type == 0:
					bytes = struct.calcsize("d")
					timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
					print (" %d   rtt=%.0f ms %s addr %s" % (ttl,(timeReceived -t)*1000, addr[0],socket.getfqdn(addr[0])))
					return
				else:
					print ("error")
					break
			finally:
				mySocket.close()

#print("google.com")
get_route('google.com')
#print("youtube.com")
#get_route('youtube.com')
#print("apple.com")
#get_route('apple.com')
#print("bestbuy.com")
#get_route('bestbuy.com')