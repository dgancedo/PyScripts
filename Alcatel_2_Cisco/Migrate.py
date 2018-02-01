######
# Author: Diego S. Gancedo <dgancedo@gmail.com>
# Desc: Script to parse and migrate Alcatel OmniSwitch config files to Cisco Nexus or Catalyst Switches
#
#
# Todo: recognise sintax port 1/1/1 in alcatel, generate non linear config to Cisco
#

import sys
import re
from pathlib import Path

# VLAN default in Cisco
defaut_vlan = "1"

program_name = sys.argv[0]
arguments = sys.argv[1:]
args = len(arguments)
if args < 2:
    print("Usage: "+program_name+" [--nexus/--catalyst] Ominisiwtch Config file")
    exit()
if sys.argv[1] != '--nexus':
    if sys.argv[1] != '--catalyst':
        print("First argument must be --nexus or --catalyst")
        exit()
    else:
        switch_type='catalyst'
else:
    switch_type='nexus'

alcatel_config_file = Path(sys.argv[2])
if alcatel_config_file.is_file():
    input_config_file = open(alcatel_config_file,'r')
    int_config = []
    vlan_config = []

    for line in input_config_file.readlines():
        line = line.strip('\n')
        line = line.strip('\t')

        if re.search('interfaces port ', line):
            port = line.split(' ')[2]
            description = ''
            status = 'no shutdown'

            if re.search('alias', line):
                description = line.split(' ')[4]
                description = description.replace('"','')
                description = description.replace(" ",'_')

            if re.search('admin-state disable', line):
                status = "shutdown" 

            dictionary = {'Port': port,'Description': description, 'Status': status, 'vlan_list': '', 'vlan_type': ''}
            int_config.append(dict(dictionary))   

        if re.search("^vlan \d{1,4} members port", line):
            vlan_member_port = line.split(' ')[4]
            vlan_member_type = line.split(' ')[5]
            vlan_member_id = line.split(' ')[1]

            if re.search('-', vlan_member_port):
                port_module=vlan_member_port.split('/')[-2]
                port_range=vlan_member_port.split('/')[-1]
                start_port=port_range.split('-')[0]
                end_port=port_range.split('-')[1]

                for i in range(int(start_port),int(end_port)+1):
                    vlan_member_port=port_module+"/"+str(i)

                    for d in int_config:

                        if d["Port"] == vlan_member_port:

                            if d["vlan_list"] is not '':                           
                                vlan_member_id2 = d["vlan_list"] + ", " + vlan_member_id
                                update= {'vlan_list': vlan_member_id2, 'vlan_type': vlan_member_type}

                            else:
                                update= {'vlan_list': vlan_member_id, 'vlan_type': vlan_member_type}

                            d.update(update)

            else:

                 for d in int_config:

                    if d["Port"] == vlan_member_port:

                        if d["vlan_list"] is not '':
                            vlan_member_id = d["vlan_list"] + ", " + vlan_member_id

                        update= {'vlan_list': vlan_member_id, 'vlan_type': vlan_member_type}
                        d.update(update)

        if re.search("^vlan (\d{1,4}|\d{1,4}-\d{1,4}) admin-state", line):
            vlan_id=line.split(' ')[1]

            if re.search('-', vlan_id):
                vlan_id_start =  vlan_id.split("-")[0]
                vlan_id_end = vlan_id.split("-")[1]

                for i in range(int(vlan_id_start),int(vlan_id_end)+1):
                    vlan_state=line.split(' ')[3]
                    dictionary = {'Vlan': str(i),'Name': '', 'Status': vlan_state }
                    vlan_config.append(dict(dictionary)) 

            else:
                vlan_state=line.split(' ')[3]
                dictionary = {'Vlan': vlan_id,'Name': '', 'Status': vlan_state }
                vlan_config.append(dict(dictionary)) 

        if re.search("^vlan \d{1,4} name", line):
            vlan_id=line.split(' ')[1]
            vlan_name=line.split(' ')[3]

            for d in vlan_config:

                if d["Vlan"] == vlan_id :
                    vlan_name = vlan_name.replace('"','')
                    vlan_name = vlan_name.replace(" ",'_')
                    update = {'Name': vlan_name }
                    d.update(update)

    #pepe = list(filter(lambda x: x['Vlan'] == '520', vlan_config))
    #pepe = list(filter(lambda x: x['Port'] == '1/20', int_config))
    #print(pepe)


    print("conf t")

    for d in vlan_config:

        if switch_type == 'nexus':
            print("vlan " + d["Vlan"])
            print(" Description " + d["Name"] )

            if d["Status"] == "enable":
                print("  no shutdown")

            else:
                print("  shutdown")
            print("!")

        else:
            print("vlan " + d["Vlan"])
            print(" Name " + d["Name"] )

            if d["Status"] == "enable":
                print("  no shutdown")

            else:
                print("  shutdown")

            print("!")

    for d in int_config:

        if switch_type == 'nexus':
            print("Interface Ethernet " + d["Port"] )

        else:
            print("Interface Gigabitethernet " + d["Port"] )

        print("  description \"" + d["Description"] + "\"")

        if d["vlan_type"] == "tagged":
            print("  switchport mode trunk")
            print("  switchport trunk allowed port vlan " + d["vlan_list"])

        else:

            if d["vlan_list"] == '':
                print("  switchport mode access")
                print("  siwtchport access vlan " + defaut_vlan)

            else:
                print("  switchport mode access")
                print("  siwtchport access vlan " + d["vlan_list"])
                
        print("  " + d["Status"])
        print("!")


    del int_config[:]
    del vlan_config[:]

else:
    print("The file "+sys.argv[2]+" Could not be opened")

    
    
    


