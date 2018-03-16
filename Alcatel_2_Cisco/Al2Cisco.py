######
# Author: Diego S. Gancedo <dgancedo@gmail.com>
# Desc: Script to parse and migrate Alcatel OmniSwitch config files to Cisco Nexus or Catalyst Switches
#

import sys
import re
from pathlib import Path
from operator import itemgetter
import inspect, os


def print_red(message, end = '\n'):
    sys.stderr.write('\x1b[1;31m' + message + '\x1b[0m' + end)
def print_green(message, end = '\n'):
        sys.stdout.write('\x1b[1;32m' + message + '\x1b[0m' + end)
def print_yellow(message, end = '\n'):
        sys.stderr.write('\x1b[1;33m' + message + '\x1b[0m' + end)
def print_blue(message, end = '\n'):
        sys.stdout.write('\x1b[1;34m' + message + '\x1b[0m' + end)
def print_bold(message, end = '\n'):
        sys.stdout.write('\x1b[1;37m' + message + '\x1b[0m' + end)

def print_banner():
    print_blue("                  _  ___    _____  _                        ")       
    print_blue("           /\    | ||__ \  / ____|(_)                       ")
    print_blue("          /  \   | |   ) || |      _  ___   ___  ___        ")
    print_blue("         / /\ \  | |  / / | |     | |/ __| / __|/ _ \       ")
    print_blue("        / ____ \ | | / /_ | |____ | |\__ \| (__| (_) |      ")
    print_blue("       /_/    \_\|_||____| \_____||_||___/ \___|\___/       ")
    print_blue("                                                            ")
    print_yellow("           == Alcatel to Cisco Migration Tool ==          \n")


#default VLAN in Cisco
defaut_vlan = "1"

print_banner()
program_name = sys.argv[0]
arguments = sys.argv[1:]
args = len(arguments)
if args < 2:
    print("Default mode: Linear one to one port migration")
    print("Usage: "+program_name+" [--nexus/--catalyst] (Ominisiwtch Config file)")
    print()
    print("Non lineal Option")
    exit("Usage: "+program_name+" [--nexus/--catalyst] (Ominisiwtch Config file) --nonlinear (Stack_Members)(Numner of Ports)")

if sys.argv[1] != '--nexus':
    if sys.argv[1] != '--catalyst':
        print_red("First argument must be --nexus or --catalyst")
        exit()

    else:
        switch_type='catalyst'

else:
    switch_type='nexus'

nonlinear = 0
if args > 2:
    if sys.argv[3] == '--nonlinear':
        nonlinear = 1

        if args > 3:   
            stack_members=sys.argv[4]

        else:
            exit()

        if args > 4:
            stack_ports=sys.argv[5]

        else:
            exit()

    else:
        exit()

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

        elif re.search("interfaces \d{1,3}\/\d{1,3} (alias) ", line):
            port = line.split(' ')[1]
            description = line.split(' ')[3]
            description = description.replace('"','')
            description = description.replace(" ",'_')

            if any(d['Port'] == port for d in int_config):
                for d in int_config:

                    if d['Port'] == port:
                        update= {'Description': description}
                        d.update(update)

            else:
                dictionary = {'Port': port,'Description': description, 'Status': '', 'vlan_list': '', 'vlan_type': ''}
                int_config.append(dict(dictionary))

        if re.search("^vlan (\d{1,4}) port default ", line):
            vlan_member_port = line.split(' ')[4]
            vlan_member_id = line.split(' ')[1]
            vlan_member_type = "Untagged"

            if any(d['Port'] == vlan_member_port for d in int_config):
                for d in int_config:

                    if d['Port'] == port:
                        update= {'vlan_list': vlan_member_id, 'vlan_type': vlan_member_type}
                        d.update(update)

            else:
                dictionary = {'Port': vlan_member_port,'Description': '', 'Status': '', 'vlan_list': vlan_member_id, 'vlan_type': vlan_member_type}
                int_config.append(dict(dictionary))

        if re.search("^vlan \d{1,4} members port", line):
            vlan_member_port = line.split(' ')[4]
            vlan_member_type = line.split(' ')[5]
            vlan_member_id = line.split(' ')[1]

            if len(vlan_member_port.split('/')) == 3:
                if nonlinear == 0:
                    print_red("\t\tPort naming style not supported in linear migration, you must use --nonlinear [stack members] [ports]") 
                    print()
                    print()
                    exit()

                if re.search('-', vlan_member_port):
                    port_switch=vlan_member_port.split('/')[-3]
                    port_module=vlan_member_port.split('/')[-2]
                    port_range=vlan_member_port.split('/')[-1]
                    start_port=port_range.split('-')[0]
                    end_port=port_range.split('-')[1]

                    for i in range(int(start_port),int(end_port)+1):
                        vlan_member_port=port_switch+"/"+port_module+"/"+str(i)

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
            else:
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

        if re.search("^vlan \d{1,4} 802\.1q ", line):
            vlan_member_port = line.split(' ')[3]
            vlan_member_type = "tagged"
            vlan_member_id = line.split(' ')[1]

            if any(d['Port'] == port for d in int_config):
                for d in int_config:
                    if d['Port'] == vlan_member_port:
                        if d["vlan_list"] is not '':                           
                            vlan_member_id2 = d["vlan_list"] + ", " + vlan_member_id
                            update= {'vlan_list': vlan_member_id2, 'vlan_type': vlan_member_type}

                        else:
                        
                            update= {'vlan_list': vlan_member_id, 'vlan_type': vlan_member_type}

                        d.update(update)
            else:
                dictionary = {'Port': port,'Description': '', 'Status': '', 'vlan_list': vlan_member_id, 'vlan_type': vlan_member_type}
                int_config.append(dict(dictionary))

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

        if  re.search("^vlan \d{1,4} enable name", line):
            vlan_id=line.split(' ')[1]

            if len(line.split(' ')) > 5:
                for i in range(4,len(line.split(' '))):
                    if 'vlan_name' in locals():
                        vlan_name=vlan_name + "_" + line.split(' ')[i]

                    else:
                        vlan_name=line.split(' ')[i]

            else:
                vlan_name=line.split(' ')[4]

            vlan_name = vlan_name.replace('"','')
            vlan_name = vlan_name.replace(" ",'_')
            dictionary = {'Vlan': vlan_id,'Name': vlan_name, 'Status': 'enable' }
            vlan_config.append(dict(dictionary)) 

    print("\tConfiguration resume:")
    print("\t\tConfigured Vlans: ", end='')
    print_green(str(len(vlan_config)))
    print("\t\tConfigured Ports: ", end='')
    print_green(str(len(int_config)))
    print()
    
    cisco_config_file = os.path.dirname(os.path.abspath(alcatel_config_file)) + "/cisco_config_" + os.path.basename(alcatel_config_file)
    file = open(cisco_config_file,'w')

    file.write("conf t\n")

    for d in sorted(vlan_config, key=lambda r: (int(r['Vlan']))):

        if switch_type == 'nexus':
            file.write("vlan " + d["Vlan"] + "\n")
            file.write(" Description " + d["Name"] + "\n")

            if d["Status"] == "enable":
                file.write("  no shutdown\n")

            else:
                file.write("  shutdown\n")

            file.write("!\n")

        else:
            file.write("vlan " + d["Vlan"]+ "\n")
            file.write(" Name " + d["Name"]+ "\n" )

            if d["Status"] == "enable":
                file.write("  no shutdown\n")

            else:
                file.write("  shutdown\n")

            file.write("\n")

    print("\tCisco config file generated on: ", end='')
    print_blue(os.path.dirname(os.path.abspath(alcatel_config_file)))
    print("\tCisco config file name: cisco_config_", end='')
    print_blue(os.path.basename(alcatel_config_file))
    print()

    if nonlinear == 1:
        current_port = 1
        current_module = 1

    for d in sorted(int_config, key=lambda r: (int(r['Port'].split('/')[0]),int(r['Port'].split('/')[1]))):
        if switch_type == 'nexus':
            int_type = "Ethernet"

        else:
            int_type = "GigabitEthernet"

        if nonlinear == 1:
            file.write("Interfece " + int_type + " " + str(current_module) + "/" + str(current_port)+ "\n")

            if current_port == stack_ports: 
                stack_members = stack_members + 1
                current_port = 1

            update = {'NewPort': str(current_module) + "/" + str(current_port) }
            d.update(update)
            current_port = current_port + 1

        else:
            file.write("Interfece " + int_type + " " + d["Port"] + "\n")

        file.write("  description \"" + d["Description"] + "\""+ "\n")

        if d["vlan_type"] == "tagged":
            file.write("  switchport mode trunk\n")
            file.write("  switchport trunk allowed port vlan " + d["vlan_list"]+ "\n")

        else:
            if d["vlan_list"] == '':
                file.write("  switchport mode access\n")
                file.write("  siwtchport access vlan " + defaut_vlan + "\n")

            else:
                file.write("  switchport mode access\n")
                file.write("  siwtchport access vlan " + d["vlan_list"] + "\n")
                
        file.write("  " + d["Status"]+ "\n")
        file.write("!\n")
        file.close

    if nonlinear == 1:
        cisco_cabling_file = os.path.dirname(os.path.abspath(alcatel_config_file)) + "/cabling_guide_" + os.path.basename(alcatel_config_file)
        file = open(cisco_cabling_file,'w')
        print()
        print_yellow("\tNon linear migration detected. printing clabling guide")
        print()
        print("\tCabling guide generated on: ", end='')
        print_blue(os.path.dirname(os.path.abspath(alcatel_config_file))) 
        print("\tCabling name: cabling_guide_", end='')
        print_blue(os.path.basename(alcatel_config_file))
        print()

        file.write("Cabling Guide for " + os.path.basename(alcatel_config_file) + "\n")
        file.write("\n")
        file.write("\tOld Switch:\t-->\tNew Switch\n")

        for d in sorted(int_config, key=lambda r: (int(r['NewPort'].split('/')[0]),int(r['NewPort'].split('/')[1]))):
            file.write("\t" + d["Port"] + "\t\t-->\t" + d["NewPort"]+"\n")

        file.close

    del int_config[:]
    del vlan_config[:]
    
else:
    print_red("The file "+sys.argv[2]+" Could not be opened")
