######
# Author: Diego S. Gancedo <dgancedo@gmail.com>
# Desc: Script to connect nexus switches over ssh and execute a command passed the script generate an output file using the hostname of the switch + the command
# Requirements: Netmiko
######

import sys, getopt, os, getpass
from netmiko import ConnectHandler


def main(argv):
   user = ''
   password = ''
   switch = ''
   command = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["user=","password=","switch=","command="])
   except getopt.GetoptError:
      print('ShowCollector.py --user <username> --password <ask|password> --switch <hostname|IP|list separated with ","|file.txt> --command <"command">')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('ShowCollector --user <username> --password <ask|password> --switch <hostname|IP|list separated with ","|file.txt> --command <"command">')
         sys.exit()
      elif opt in ("--user"):
         user = arg
      elif opt in ("--password"):
         if arg == 'ask':
            password = getpass.getpass()
         else:
            password = arg
      elif opt in ("--switch"):
         switch = arg
      elif opt in ("--command"):
         command = arg
   return user,password,switch,command

if __name__ == "__main__":
   values=main(sys.argv[1:])
   if values[0] != "" and values[1] != "" and values[2] != "" and values[3] !="":
      switches = []
      if ".txt" in values[2]:
         s = open(values[2],'r')
         for line in s:
            switches.append(line.replace("\n",""))
      elif "," in values[2]:
         switches = values[2].split(",")
      else:
         switches.append(values[2])
      for switch in switches:
         net_connect = ConnectHandler(device_type='cisco_nxos', ip=switch, username=values[0], password=values[1]) 
         switchname = net_connect.send_command("show hostname")
         print("Executing "+ values[3] + " on " + switchname)
         show = net_connect.send_command(values[3])
         filename = switchname.replace(" ","_") + values[3].replace(" ", "_") + ".txt"
         f = open(filename,'w')
         f.write(show)
         f.close
         print("File " + filename + " generated with the output")
   else:
      main('-h')  
