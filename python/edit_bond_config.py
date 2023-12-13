#!/usr/bin/env python3

from ncclient import manager
from pprint import pprint
import xmltodict
from ncclient.xml_ import *
import xml.dom.minidom
import sys
import argparse

# Device connection parameters
device_ip = "10.27.204.29"
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

cfg_management_description = """
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" 
        xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="http://openconfig.net/yang/interfaces">
    <interface>
      <name>ma1</name>
      <config>
        <description>This is management interface</description>
      </config>
    </interface>
  </interfaces>
</config>
"""

cfg_bond = """
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" 
        xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="http://openconfig.net/yang/interfaces">
	<interface>
	  <name>bond102</name>
	  <subinterfaces>
	    <subinterface>
	      <index>5101</index>
	      <config>
		<enabled>true</enabled>
		<index>5101</index>
		<name>bond102.5101</name>
	      </config>
	      <ipv4
		  xmlns="http://openconfig.net/yang/interfaces/ip">
		<config>
		  <enabled>false</enabled>
		</config>
	      </ipv4>
	      <ipv6
		  xmlns="http://openconfig.net/yang/interfaces/ip">
		<config>
		  <enabled>false</enabled>
		</config>
	      </ipv6>
	      <vlan
		  xmlns="http://openconfig.net/yang/vlan">
		<ingress-mapping>
		  <config>
		    <vlan-stack-action>POP</vlan-stack-action>
		  </config>
		</ingress-mapping>
		<match>
		  <double-tagged>
		    <config>
		      <inner-vlan-id>832</inner-vlan-id>
		      <outer-vlan-id>931</outer-vlan-id>
		    </config>
		  </double-tagged>
		</match>
		<egress-mapping>
		  <config>
		    <vlan-id>931</vlan-id>
		    <vlan-stack-action>PUSH-SWAP</vlan-stack-action>
		    <tpid
			xmlns:oc-vlan-types="http://openconfig.net/yang/vlan-types">oc-vlan-types:TPID_0X8100
		    </tpid>
		    <inner-vlan-id
			xmlns="http://yang.arrcus.com/arcos/openconfig/vlan/augments">832
		    </inner-vlan-id>
		  </config>
		</egress-mapping>
	      </vlan>
	      <qos
		  xmlns="http://yang.arrcus.com/arcos/interface/qos">
		<service-tablemaps
		    xmlns="http://yang.arrcus.com/arcos/interface/qos/service-tablemap">
		  <service-tablemap>
		    <direction>INGRESS</direction>
		    <config>
		      <direction>INGRESS</direction>
		      <name>tc0</name>
		    </config>
		  </service-tablemap>
		</service-tablemaps>
		<service-policies
		    xmlns="http://yang.arrcus.com/arcos/interface/qos/service-policy">
		  <service-policy>
		    <direction>INGRESS</direction>
		    <config>
		      <direction>INGRESS</direction>
		      <name>1000M-L2</name>
		    </config>
		  </service-policy>
		  <service-policy>
		    <direction>EGRESS</direction>
		    <config>
		      <direction>EGRESS</direction>
		      <name>1000M-L2</name>
		    </config>
		  </service-policy>
		</service-policies>
	      </qos>
	    </subinterface>
	  </subinterfaces>
	</interface>
  </interfaces>
</config>
"""

class EditConfig():

    def bond(self, m):
        with m.locked("candidate"):
            m.edit_config(
                target="candidate",
                config=cfg_hostname,
                default_operation="merge"
            )
            m.edit_config(
                target="candidate",
                config=cfg_bond,
                default_operation="merge",
                test_option="test-then-set",
                error_option="rollback-on-error",
            )
            m.commit(
                confirmed=True,
                timeout=str(20),
                persist=None,
                persist_id=None
            )

def parse_args(sys_args):
    usage = """
    % edit [-h | --help] [options]

    One of the options must be given.
    """
    # Create an instance of the parser
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("-u", "--user", dest="username",
                        default=device_username, help="username")
    parser.add_argument("-p", "--password", dest="password",
                        default=device_password, help="password")
    parser.add_argument("--host", dest="host", default=device_ip,
                      help="NETCONF server hostname")
    parser.add_argument("--port", type=int, dest="port",
                        default=device_port,
                        help="NETCONF server SSH port")
    parser.add_argument("--bond", action='store_true',
                        help="Configure the bond interface")
    args = parser.parse_args()
    return (args)


def main(sys, EditConfig, logger=None):
    '''
    This function tests the ability to edit a configuration over
    NETCONF. It takes one mandatory and three optional arguments.

    .param arg1: the IP address of the NETCONF server
    .param arg2: the port number of the NETCONF server (default 830)
    .param arg3: the username of the account on NETCONF server (default root)
    .param arg4: the password for the username (default 'arrcus')
    .param arg5: test case that needs to be run
    .return: None.
    '''
    
#  if len(sys.argv) < 2:
#      print ("Usage: python edit_config.py host [port username password]
#    sys.exit(1) 

    args = parse_args(sys)
    if logger:
        logger.debug("edit_config.py: about to connect")
    
    try:
        with manager.connect(
                host=args.host,
                port=args.port,
                username=args.username,
                password=args.password,
                device_params={"name": "default"},
                allow_agent=False,
                look_for_keys=False,
                hostkey_verify=False,
        ) as m:
            if args.bond:
                EditConfig.bond(m)
    except Exception as e:
        print("An error occured:", str(e))
            

if __name__ == "__main__":
    editConfig = EditConfig()
    main(sys.argv[1:], editConfig)
