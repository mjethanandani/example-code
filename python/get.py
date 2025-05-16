#!/usr/bin/env python3

from ncclient import manager
from pprint import pprint
import xmltodict
from ncclient.xml_ import *
import xml.dom.minidom
import sys

# Device connection parameters
device_ip = "10.50.105.37"
device_port = 830
device_username = "root"
device_password = "arrcus"

# Construct the XML request for the <get> operation
get_vlan_request = f"""
  <vlans xmlns="http://openconfig.net/yang/vlan">
    <vlan>
      <state />
    </vlan>
  </vlans>
"""

def main():
    '''
    This function tests the ability to get a configuration over
    NETCONF. It takes one mandatory and three optional arguments.

    .param arg1: the IP address of the NETCONF server
    .param arg2: the port number of the NETCONF server (default 830)
    .param arg3: the username of the account on NETCONF server (default root)
    .param arg4: the password for the username (default 'arrcus')
    .return: None.
    '''
    
    if len(sys.argv) < 2:
      print ("Usage: python get_vlan_config.py host [port username password]")
      sys.exit(1) 
       
    host = sys.argv[1] if len(sys.argv) > 1 else device_ip
    port = sys.argv[2] if len(sys.argv) > 2 else device_port
    username = sys.argv[3] if len(sys.argv) > 3 else device_username
    password = sys.argv[4] if len(sys.argv) > 4 else device_password

    with manager.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            device_params={"name": "default"},
            allow_agent=False,
            look_for_keys=False,
            hostkey_verify=False,
    ) as m:
      # Retrieve the configuration using NETCONF
      response = m.get(filter=('subtree', get_vlan_request))

      # Extract the response as an XML element
      response_xml = response.data_ele
      # Pretty print the XML
      pretty_xml = etree.tostring(response_xml, pretty_print=True).decode()
      print(pretty_xml)

if __name__ == "__main__":
  main()
