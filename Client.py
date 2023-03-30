import socket
import Package as p
from pprint import pprint

HOST = socket.gethostbyname(socket.gethostname())
PORT = 30001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
    
    clientSocket.settimeout(4)
    try:
        clientSocket.connect((HOST, PORT))
    except socket.timeout as e:
        print(f"Timeout error: {e}")
    except socket.error as e:
        print(f"Could not connect to {HOST}:{PORT} Error: {e}")

    while True:

        robot_data = clientSocket.recv(4096)
        new_message = p.Package(robot_data)
        print(new_message)
        # string = ""
        # for x in new_message.subpackage_list:
        #     string += f"{x}"
        # log = open("output.txt", "w")
        # print(string, file=log)
    





