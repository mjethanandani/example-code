#!/usr/bin/env python3

import paramiko

# Define SSH parameters
host = '10.25.4.8'
port = 22
username = 'root' 
password = 'arrcus'

# Command to execute
command = "bashcli -c 'show vlan'"

try:
    # Create an SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()  # Load known hosts

    # Connect to the remote host
    ssh_client.connect(host, port, username, password)

    # Execute the command
    stdin, stdout, stderr = ssh_client.exec_command(command)

    # Print the output
    print("Command output:")
    print(stdout.read().decode())

    # Close the SSH connection
    ssh_client.close()

except Exception as e:
    print(f"An error occurred: {str(e)}")
