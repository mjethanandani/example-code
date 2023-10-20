#!/usr/bin/env python3

from ncclient import manager
from pprint import pprint
import xmltodict
from ncclient.xml_ import *
import xml.dom.minidom
import sys

# Device connection parameters
device_ip = "127.0.0.1"
device_port = 830
device_username = "root"
device_password = "arrcus"

# Edit function
config_element = """
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" 
        xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="http://openconfig.net/yang/interfaces">
    <interface>
      <name>swp1</name>
      <config>
        <description>This the first front panel interface.</description>
      </config>
    </interface>
  </interfaces>
</config>
"""
# Define the NETCONF RPC operation
rpc_operation = """
<get-diff xmlns="http://yang.arrcus.com/arcos/system">
  <encoding>XML</encoding>
</get-diff>
"""

def main():
    '''
    This function tests the ability to generate a NETCONF diff using the rpc <get-diff>
    supported by Arrcus devices. It first creates a candidate config, by modifying the
    modifying the description for the ma1 interface, and then uses it to issue a rpc request for <get-diff>
    go get the NETCONF server to generate the diff between the running configuration,
    and the candidate configuration. It expects a couple of parameters including

    .param arg1: the IP address of the NETCONF server
    .param arg2: the port number of the NETCONF server (default 830)
    .param arg3: the username used to contact the NETCONF server (default 'root')
    .param arg4: the password to be used along with the username (default 'arrcus')
    .return: None
    '''
    if len(sys.argv) < 2:
      print ("Usage: python netconf_diff.py host [port username password]")
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
      conf = m.edit_config(target='candidate', config=to_ele(config_element))
      print(conf)
      # Send the RPC operation and print the response
      response = m.dispatch(to_ele(rpc_operation))
      print(xml.dom.minidom.parseString(str(response.xml)).toprettyxml())
        

if __name__ == "__main__":
    main()
