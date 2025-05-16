#!/usr/bin/env python
"""This Python script leverages RESTCONF to:
      - retrieve a list of interfaces on a device
      - ask the user for the interface to configure
      - displays the interface IP information
      - asks user for new IP information
      - updates the IP address on the interface
      - displays the final IP information on the interface

    This script has been tested with Python 3.7, however may work with
    other versions.

    This script targets a RESTCONF Device. To execute this script
    against a different device, update the variables and command-line
    arguments that list the connectivity, management interface, and
    url_base for RESTCONF.

    Requirements:
      Python
        - requests

"""

import json
import requests
import sys
import os
import ipaddress
from argparse import ArgumentParser
from collections import OrderedDict
from getpass import getpass
import urllib3
import logging

# Disable SSL Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup logging
logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

# Identify yang+json as the data formats
headers = {'Content-Type': 'application/yang-data+json',
           'Accept': 'application/yang-data+json'}
ip = {}


# Function to retrieve the list of interfaces on a device
def get_configured_interfaces(url_base, username, password):
    log.info("URL base %s" % url_base)
    
    # this statement performs a GET on the specified url
    try:
        response = requests.get(url_base,
                                auth=(username, password),
                                headers=headers,
                                verify=False
                                )
        response.raise_for_status()
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    # return the json as text
    return response.json()["openconfig-interfaces:interfaces"]["interface"]


# Used to delete the IP address on an interface
def delete_ip_address(url_base, interface, ip, username, password):
    # RESTCONF URL for specific interface
    url = url_base + "/interface={i}/config/".format(i=interface)
    prefix = get_prefix(ip["mask"])

    # Create the data payload to reconfigure IP address
    # Need to use OrderedDicts to maintain the order of elements
    data = OrderedDict([
        ('config', OrderedDict([
            ('name', interface),
            ('type', 'iana-if-type:ethernetCsmacd')
        ])),
        ('subinterfaces', OrderedDict([
            ('subinterface', OrderedDict([
                ('index', 0),
                ('openconfig-if-ip:ipv4', OrderedDict([
                    ('addresses', OrderedDict([
                        ('address', OrderedDict([
                            ('ip', ip["address"]),
                            ('config', OrderedDict([
                                ('ip', ip["address"]),
                                ('prefix-length', prefix)
                            ]))
                        ]))
                    ]))
                ])),
            ]))
        ]))
    ])

    print(json.dumps(data, indent=4, default=str))

    # Use PUT request to update data
    try:
        response = requests.put(url,
                                auth=(username, password),
                                headers=headers,
                                verify=False,
                                json=data
                                )
        response.raise_for_status()
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    print(response.text)


# Retrieve and print the current configuration of an interface
def print_interface_details(url_base, interface, username, password, cidr):
    url = url_base + "/interface={i}".format(i=interface)

    # this statement performs a GET on the specified url
    try:
        response = requests.get(url,
                                auth=(username, password),
                                headers=headers,
                                verify=False
                                )
        response.raise_for_status()
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    intf = response.json()["openconfig-interfaces:interface"]
    # return the json as text
    print("Name: ", intf[0]["name"])
    try:
        netmask = intf[0]["subinterfaces"]["subinterface"][0]["ip"]["addresses"]["address"][0]["config"]["prefix-length"]
        log.info("prefix-length %s" % netmask)
        if cidr:
            nma = ipaddress.ip_address(netmask)
            netmask = str("{0:b}".format(int(nma)).count('1'))
        print("IP Address: ", intf[0]["ietf-ip:ipv4"]["address"][0]["ip"], "/",
              netmask)
    except KeyError:
        print("IP Address: UNCONFIGURED")
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    print()

    return(intf)


# Ask the user to select an interface to configure.  Ensures input is valid and
# NOT the management interface
def interface_selection(interfaces, mgmt_if):
    # Ask User which interface to configure
    sel = input("Which Interface do you want to configure? ")

    # Validate interface input
    # Must be an interface on the device AND NOT be the Management Interface
    while sel == mgmt_if or not sel in [intf["name"] for intf in interfaces]:
        print("INVALID:  Select an available interface.")
        print("          " + mgmt_if + " is used for management.")
        print("          Choose another Interface")
        sel = input("Which Interface do you want to configure? ")

    return(sel)

# Given a netmask, get the prefix length
def get_prefix(mask):
    prefix = sum([bin(int(x)).count('1') for x in mask.split('.')])
    return prefix

# Asks the user to provide an IP address and Mask.
def get_ip_info(cidr):
    # Ask User for IP and Mask
    try:
        if cidr:
            ipa_t = input("What IP address/prefixlen do you want to set? ")
            ipi = ipaddress.ip_interface(ipa_t)
            ip["address"] = ipi.ip.compressed
            ip["prefixlen"] = ipi.prefixlen.compressed
        else:
            ipa_t = input("What IP address do you want to set? ")
            ipi = ipaddress.ip_interface(ipa_t)
            ip["address"] = ipi.ip.compressed
            ipm_t = input("What Subnet Mask do you want to set? ")
            ipm = ipaddress.ip_address(ipm_t)
            ip["mask"] = ipm.compressed
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    return(ip)


def main():
    """
    Simple main method calling our function.
    """

    parser = ArgumentParser(
        prog=sys.argv[0], description='A RESTCONF method to delete bond interface.')
    parser.add_argument('--hostname', '-a', type=str,
                        help='hostname or IP address',
                        default='10.25.4.8')
    parser.add_argument('--username', '-u', type=str,
                        help='username', default='root')
    # Identifies the interface on the device used for management access
    # Used to ensure the script isn't used to update the IP leveraged
    # to manage device
    parser.add_argument('--management_if', '-m', type=str,
                        help='management interface', default='ma1')
    parser.add_argument('--port', '-P', type=int,
                        help='device RESTCONF port', default=8009)
    args = parser.parse_args()

    password = os.getenv('RESTCONF_PASSWORD')
    if password is None:
        password = getpass()

    # Create the base URL for RESTCONF calls

    url_base = "https://{h}:{p}/restconf/data/openconfig-interfaces:interfaces".format(h=args.hostname, p=args.port)

    # Get a List of Interfaces
    interfaces = get_configured_interfaces(url_base, args.username,
                                           password)

    print("The router has the following interfaces: \n")
    for interface in interfaces:
        print("  * {name:25}".format(name=interface["name"]))

    print("")

    # Ask User which interface needs to be deleted.
    selected_interface = interface_selection(interfaces,
                                             args.management_if)
    print(selected_interface)

    # Print Starting Interface Details
    print("Starting Interface Configuration")
    print_interface_details(url_base, selected_interface, args.username,
                            password, args.cidr)

    # As User for IP Address to set
    ip = get_ip_info(args.cidr)

    # Configure interface
    delete_bond_interface(url_base, selected_interface, args.username, password)

    # Print Ending Interface Details
    print("Ending Interface Configuration")
    print_interface_details(url_base, selected_interface, args.username,
                            password, args.cidr)

if __name__ == '__main__':
    sys.exit(main())
