######
# Author: Diego S. Gancedo <dgancedo@gmail.com>
# Desc: Script to parse and migrate Alcatel OmniSwitch config files to Cisco Nexus VXLAN VTEP
#

import sys
import re
from pathlib import Path
from operator import itemgetter
import inspect, os


base_vxlan = sys.argv[2]
vrf_name = "L3-VXLAN-Routing-BCRA"
mcast_grp = "224.1.1.3"
add_vlans = "1679, 1682, 1684-1686"
program_name = sys.argv[0]
arguments = sys.argv[1:]
args = len(arguments)
searched_vlan = sys.argv[3]
int_uplink = sys.argv[4]
alcatel_config_file = Path(sys.argv[1])
if alcatel_config_file.is_file():
    input_config_file = open(alcatel_config_file,'r')
    for line in input_config_file.readlines():
        line = line.strip('\n')
        line = line.strip('\t')
        if re.search('ip interface ', line):
            vlan_ip = line.split(' ')[4]
            vlan_mask = line.split(' ')[6]
            vlan_id = line.split(' ')[8]
            edificio = vlan_id[0]
            piso = vlan_id[-1]
            if vlan_id== searched_vlan:
                print("conf t")
                print("vlan " + vlan_id)
                print("  vn-segment " + base_vxlan + vlan_id)
                print("!")
                print("interface Vlan" + vlan_id)
                print("  vrf member " + vrf_name)
                print("  description \"Edificio " + edificio + " Piso " + piso + "\"")
                print("  no shutdown")
                print("  no ip redirects")
                print("  ip address " + vlan_ip + "/" + vlan_mask)
                print("  fabric forwarding mode anycast-gateway")
                print("!")
                print("interface nve1")
                print("  member vni " + base_vxlan + vlan_id)
                print("  suppress-arp")
                print("  mcast-group "+ mcast_grp)
                print("!")
                print("evpn")
                print("  vni " + base_vxlan + vlan_id)
                print("  rd auto")
                print("  route-target import auto")
                print("  route-target export auto")
                print("!")
                print("interface " + int_uplink)
                print("  port-channel " + vlan_id + " mode active")
                print("  no shutdown")
                print("interface po " + vlan_id)
                print("  vpc " + vlan_id)
                print("  switchport mode trunk")
                print("  switchport trunk allowed vlan add " + vlan_id)
                print("  switchport trunk allowed vlan add " + add_vlans)
                print("  no shutdown")
                print("!")
 


