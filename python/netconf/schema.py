#!/usr/bin/env python3
from ncclient import manager
import lxml

nc_ns = 'urn:ietf:params:xml:ns:netconf:base:1.0'
dirname = "/tmp/yang"
modname = "openconfig-interfaces"

# Connect to the NETCONF device
with manager.connect(host='10.25.4.8', port=830, username='root', password='arrcus', hostkey_verify=False) as m:

    # Use the <get-schema> RPC to retrieve a YANG module/schema
    schema_filter = """
        <filter>
            <netconf-get-schema xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring">
                <identifier>openconfig-interfaces.yang</identifier>
                <version>2016-12-22</version>
                <format>yang</format>
            </netconf-get-schema>
        </filter>
    """

    schema_request = """
        <rpc message-id="101"
        xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <get-schema xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring">
                <filter>
                    <identifier>openconfig-interfaces.yang</identifier>
                </filter>
            </get-schema>
        </rpc>
    """
    schema_reply = m.dispatch(lxml.etree.fromstring(schema_request))
    
    # Now, you can work with the parsed schema to extract specific information
    # such as the schema hierarchy, data models, data types, etc.
    # Extract the YANG module data from the response as an XML string


    # Print the schema_xml_string
    print(schema_reply)