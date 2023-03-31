import socket
import Package as p
import PackageWriter as pw
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

    writer = pw.PackageWriter(3)
    i = 0
    while True:

        robot_data = clientSocket.recv(4096)
        new_message = p.Package(robot_data)
        
        if new_message.type == 16 and i < 5:
           writer.append_package_to_file(new_message)
           i += 1
            
        
    





