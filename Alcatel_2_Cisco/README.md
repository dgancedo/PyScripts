This script is designed to simplify in the task of migrate ports and vlans only, no advanced configuration are migrated
The script use Python 3+

USAGE: python al2cisco.py [ --catalyst | --nexus ] /path/to/alcatel_config.file

The script generate a cisco style config file in the same path of the original file with the naming cisco_config_+orginal_file_name

Also the script support the migration for the alcatel switches with the interface naming X/Y/Z but you need to specify the parameter --nonlinear and specyfy the number of stack or modules in the destination system and the ports of modules, in example:

python al2cisco.py [ --catalyst | --nexus ] /path/to/alcatel_config.file --nonlinear 2 48

when nonlinear option is used a cabling guide is generated with the relation of the original port with the new one


