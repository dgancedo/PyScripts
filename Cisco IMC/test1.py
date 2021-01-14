from functools import partial
import ssl, sys


#ssl.wrap_socket = partial(ssl.wrap_socket, ssl_version=ssl.PROTOCOL_TLSv1)
#ssl._create_default_https_context = ssl._create_unverified_context

from ucsmsdk.ucshandle import UcsHandle

handle = UcsHandle("UCS","USER","PASS")
import certifi
handle.login()
print("Server Name:\tModel:\t\tSerial Number:\tPower State:")

compute_rack_units = handle.query_classid("ComputeRackUnit")
for compute_rack_unit in compute_rack_units:
    serviceprofile = str(compute_rack_unit.assigned_to_dn.split('/')[-1].replace('ls-',''))
    serial = compute_rack_unit.serial
    power_state =compute_rack_unit.oper_power
    model = compute_rack_unit.model

    print(serviceprofile + "\t" + model + "\t" + serial + "\t" + power_state)
    


compute_blade_units = handle.query_classid("ComputeBlade")
for compute_blade_unit in compute_blade_units:
    serviceprofile = str(compute_blade_unit.assigned_to_dn.split('/')[-1].replace('ls-',''))
    serial = compute_blade_unit.serial
    power_state =compute_blade_unit.oper_power
    model = compute_blade_unit.model

    print(serviceprofile + "\t" + model + "\t" + serial + "\t" + power_state)

    #print(compute_blade_unit)

handle.logout()

