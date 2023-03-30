import struct
from SubPackage import *
from datetime import datetime

class Package:
    def __init__(self, robot_data):
        self.length = self.get_package_length(robot_data)
        self.type = self.get_package_type(robot_data)
        self.robot_data = robot_data
        self.subpackage_list = []
        self.received_timestamp = datetime.now()

        log = open('debug.log', mode='a')
        if self.type not in (5, 16):
            print(self.type, self.length)
            print(f"type={self.type}, length={self.length}\ndata={self.robot_data}\n\n######################", file=log)

        if self.type == 16:
            self.read_subpackages(robot_data)

    def get_package_length(self, robot_data) -> int:
        package_length = struct.unpack('>I', robot_data[0:4])[0]
        return package_length
    
    def get_package_type(self, robot_data) -> int:
        package_type = struct.unpack('>B', robot_data[4:5])[0]
        return package_type
    
    def read_subpackages(self, robot_data):

        current_position = 5
        while current_position < len(robot_data):

            subpackage_length = struct.unpack('>I', robot_data[current_position:current_position+4])[0]
            subpackage_type = struct.unpack('>B', robot_data[current_position+4:current_position+5])[0]
            subpackage_data = robot_data[current_position:subpackage_length+current_position]

            if subpackage_type in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13):
                new_subpackage = SubPackage.create_subpackage(self.type, subpackage_data, subpackage_length, subpackage_type)
                self.subpackage_list.append(new_subpackage)

            current_position += subpackage_length

    def __str__(self):
        formatted = self.received_timestamp.strftime("%Y-%m-%d, %H:%M:%S.%f")[:-5] 
        string = f"TIME: {formatted}, PACKAGE TYPE: {self.type}, PACKAGE LENGTH: {self.length}\n\n"
        for subpackage in self.subpackage_list:
            string += f"{subpackage}"

        return string
