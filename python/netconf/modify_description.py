from ncclient import manager
 import xmltodict
 import json
 # Connection Parameters
 device = {
 }
# Interface Configuration Change
 interface_name = "ma1" # Replace with your interface name
 interface_type = "ethernetCsmacd"
 new_description = "Updated via NETCONF - ERT Testing - ert user"
 config_template = f"""
   <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
 """
"host": "10.196.21.42", # Replace with the correct IP
"port": 830,
"username": "ert",
"password": "",
"hostkey_verify": False
 <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
   <interface>
     <name>{interface_name}</name>
       <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">{interface_type}</type>
       <description>{new_description}</description>
   </interface>
 </interfaces>
 </config>
14
 
 
# Establish a NETCONF Session
 with manager.connect(**device) as m:
 # Sending Configuration Change to Candidate Configuration
 response = m.edit_config(target="candidate", config=config_template)
 print(response)
 # Committing the Change
 commit_response = m.commit()
 print(commit_response)
 # Optional: Retrieve and Print the Current Configuration
 # filter = f"""
 # <filter>
 # <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
 # <interface>
 # <name>{interface_name}</name>
 # </interface>
 # </interfaces>
 # </filter>
# """
Exhibit 8. Changing the Description Field for the "ma1" Interface with a Python Script
 current_config = m.get_config(source="running")
 config_dict = xmltodict.parse(str(current_config))
 print(json.dumps(config_dict, indent=4))
