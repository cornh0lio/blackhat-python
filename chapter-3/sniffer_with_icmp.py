import os
import struct
import socket
import threading
import time
from netaddr import IPNetwork,IPAddress
from ctypes import *

#host to listen on
host = "192.168.182.128"

#subnet to target
subnet = "192.168.182.0/24"

#magic string we'll check ICMP responses for
magic_message = "PYTHONRULES!"

#our IP header
class IP(Structure):
    _fields_ = [
        ("ihl",             c_ubyte, 4),
        ("version",         c_ubyte, 4),
        ("tos",             c_ubyte),
        ("len",             c_ushort),
        ("id",              c_ushort),
        ("offset",          c_ushort),
        ("ttl",             c_ubyte),
        ("protocol_num",    c_ubyte),
        ("sum",             c_ushort),
        ("src",             c_uint32),
        ("dst",             c_uint32)
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
    
        #map protocol contants to their names
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}

        #human readable IP addresses
        self.src_address = socket.inet_ntoa(struct.pack("<L",self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L",self.dst))

        #human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)
#our ICMP header
class ICMP(Structure):
    _fields_ = [
        ("type",            c_ubyte),
        ("code",            c_ubyte),
        ("checksum",        c_ushort),
        ("unused",          c_ushort),
        ("next_hop_mtu",    c_ushort),
    ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass

#send the magic_message to all the hosts in the defined subnet via UDP
def udp_sender(subnet, magic_message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(magic_message,("%s" % ip, 65212))
            print "sending packet to %s" % ip
        except:
            pass


#linux needs that we specify that we are sniffing ICMP while Windows allows us to sniff
#all the packets
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

#socket option to include the IP headers in our captured packets
sniffer =  socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL,1)

#if the program is running on windows, we ned to send an IOCTL
#to set up promiscuous mode
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

#start sending packets
t = threading.Thread(target=udp_sender, args=(subnet, magic_message))
t.start()

try:
    while True:
        #read in a packet
        raw_buffer = sniffer.recvfrom(65535)[0]
    
        #create an IP header from the first 20 bytes of the buffer
        ip_header = IP(raw_buffer[0:20])
        
        #print out the protocol that was detected and the hosts
        print "Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address)
    
        if ip_header.protocol == "ICMP":
            #calculate where our ICMP packet starts
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]
    
            #create our ICMP structure
            icmp_header = ICMP(buf)

        print "ICMP -> Type %d Code: %d" % (icmp_header.type, icmp_header.code)

        #now check for the TYPE 3 and CODE 3
        if icmp_header.code == 3 and icmp_header.code == 3:
            #make sure host is in our target subnet
            if IPAddress(ip_header.src_address) in IPNetwork(subnet):
                #make sure it has our magic message by checking the first 8 bytes of the datgram that
                #we get with the response
                if raw_buffer[len(raw_buffer)-len(magic_message):] == magic_message:
                    print "Host Up: %s" % ip_header.src_address

#handle CTRL-C
except KeyboardInterrupt:
    #if we're using Windows, turn off promiscuous mode
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


