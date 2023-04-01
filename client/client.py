'''
BSD 3-Clause License

Copyright (c) 2023, Shawn Armstrong

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import socket
from package import Package
from package_writer import PackageWriter
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Client for receiving robot data")
parser.add_argument("-i", "--ip_address", default=socket.gethostbyname(socket.gethostname()), help="IP address of the robot (default: local IP address)")
parser.add_argument("-m", "--max_reports", type=int, default=10, help="Maximum number of reports to write (default: 10)")

args = parser.parse_args()

HOST = args.ip_address
PORT = 30001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
    
    clientSocket.settimeout(4)
    try:
        clientSocket.connect((HOST, PORT))
    except socket.timeout as e:
        print(f"Timeout error: {e}")
    except socket.error as e:
        print(f"Could not connect to {HOST}:{PORT} Error: {e}")

    writer = PackageWriter(args.max_reports)
    i = 0
    while True:

        robot_data = clientSocket.recv(4096)
        new_message = Package(robot_data)
        
        writer.append_package_to_file(new_message)
            
        
    





