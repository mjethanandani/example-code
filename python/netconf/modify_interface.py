import libyang
from ncclient import manager

# Connect to a device
# Device information
hostname = '10.25.4.8'
username = 'root'
password = 'arrcus'
port = 10830  # Default NETCONF port

# Establish NETCONF session
with manager.connect(
    host=hostname,
    port=port,
    username=username,
    password=password,
    hostkey_verify=False,  # Set to True to enable host key verification
    # device_params={'name': 'junos'},  # Device-specific parameters if required
    timeout=100,  # Connection timeout
) as m:
    # Perform NETCONF operations
    # For example, retrieve the device capabilities
    capabilities = m.server_capabilities
    print("Device Capabilities:")
    for cap in capabilities:
        print(cap)

    # Retrieve the configuration using NETCONF
    response = m.get_config(source='running')

    # Parse XML response
    xml_response = response.data_xml

    # Use libyang to process the configuration data
    ctx = libyang.Context('/Users/mahesh/git/arrcus/arrcus_sw/build/ned/packages/arcos-5.2.1-EFT2-nc-1.7/src/yang')
    data = ctx.parse_data_mem(xml_response, "xml", no_state=True)

    # Print the configuration data
    print("Configuration:")
    print(data.print_mem("xml", with_siblings=True))

# Create a context
ctx = libyang.Context('/Users/mahesh/git/arrcus/arrcus_sw/build/ned/packages/arcos-5.2.1-EFT2-nc-1.7/src/yang')

# Load the module
module_path = 'openconfig-interfaces'
module = ctx.load_module(module_path)

if module is None:
    print(f"Failed to load YANG module: {module_path}")
    ctx.destroy()
    exit(1)

# Use the loaded module
# Perform operations using the loaded module, such as validation or data retrieval

# Find the interfaces container in the module
interfaces_container = module.find_path("/interfaces")

if interfaces_container is None:
    print("Interfaces container not found in the module")
    ctx.destroy()
    exit(1)

# Iterate over the child elements of the interfaces container
print("Interfaces:")
for interface in interfaces_container.children:
    if interface.nodetype() == libyang.YANG_NT_CONTAINER and interface.name() == "interface":
        interface_name = interface.find_path("name")
        if interface_name is not None and interface_name.is_value_set():
            print(interface_name.value())



# Clean up and destroy the context when done
ctx.destroy()
