#!/usr/bin/env python3

from ncclient import manager
from pprint import pprint
import xmltodict
from ncclient.xml_ import *
import xml.dom.minidom
import sys

# Device connection parameters
device_ip = "10.25.4.8"
device_port = 830
device_username = "root"
device_password = "arrcus"

cfg_hostname = """
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" 
        xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <system xmlns="http://openconfig.net/yang/system">
    <config>
      <hostname>leaf2</hostname>   
    </config>
  </system>
</config>
"""

cfg_loopback0_description = """
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" 
        xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="http://openconfig.net/yang/interfaces">
    <interface>
      <name>eth0</name>
      <config>
        <description>This is management interface</description>
      </config>
    </interface>
  </interfaces>
</config>
"""

def main():
    '''
    This function tests the ability to edit a configuration over
    NETCONF. It takes one mandatory and three optional arguments.

    .param arg1: the IP address of the NETCONF server
    .param arg2: the port number of the NETCONF server (default 830)
    .param arg3: the username of the account on NETCONF server (default root)
    .param arg4: the password for the username (default 'arrcus')
    .return: None.
    '''
    
    if len(sys.argv) < 2:
      print ("Usage: python edit_config.py host [port username password]")
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
        with m.locked("candidate"):
            m.edit_config(
                target="candidate", config=cfg_hostname, default_operation="merge"
            )
            m.edit_config(
                target="candidate",
                config=cfg_loopback0_description,
                default_operation="merge",
            )
            m.commit()

if __name__ == "__main__":
  main()
