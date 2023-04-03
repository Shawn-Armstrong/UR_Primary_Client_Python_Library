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

import struct
from subpackage import *
from datetime import datetime

class Package:
    """
    A class representing a package in robot data communication.
    
    This class is designed to parse and manage the information contained
    within a package received from a Universal Robots' e-series cobot. It
    deserializes the package's robot data, extracts the package type, and
    processes its subpackages. 

    Attributes:
        length (int): The length of the package.
        type (int): The type of the package.
        robot_data (str): A hexadecimal string representing binary data with
                          robot parameters encoded as packages and subpackages.
        subpackage_list (list): A list containing the processed subpackage objects.
        received_timestamp (datetime): A timestamp representing when the package was received.

    Methods:
        get_package_length: Extract the package length from the given robot data.
        get_package_type: Extract the package type from the given robot data.
        read_subpackages: Deserialize and process subpackages within the robot data.
        get_subpackage: Retrieve a specific subpackage from the subpackage list by name.
        __str__: Generate a report for the package object, including its subpackages.
    """

    def __init__(self, robot_data):
        self.length = self.get_package_length(robot_data)
        self.type = self.get_package_type(robot_data)
        self.robot_data = robot_data
        self.subpackage_list = []
        self.received_timestamp = datetime.now()

        # Currently, only robot state messages are implemented.
        if self.type == 16:
            self.read_subpackages(robot_data)

    def get_package_length(self, robot_data: str) -> int:
        """
        Extract the package length from the given robot data.
        
        Args:
            robot_data (str): A hexadecimal string representing binary data with robot parameters
                            encoded as packages and subpackages.
                            
        Returns:
            int: The length of the package as an integer.
        """
        package_length = struct.unpack('>I', robot_data[0:4])[0]
        return package_length

    def get_package_type(self, robot_data: str) -> int:
        """
        Extract the package type from the given robot data.
        
        Args:
            robot_data (str): A hexadecimal string representing binary data with robot parameters
                            encoded as packages and subpackages.
                            
        Returns:
            int: The type of the package as an integer.
        """
        package_type = struct.unpack('>B', robot_data[4:5])[0]
        return package_type

    
    def read_subpackages(self, robot_data) -> None:
        """
        Read subpackages from the given robot data and append them to the subpackage_list.

        This function iterates through the robot_data, which is a hexadecimal string
        representing binary data containing robot parameters encoded as a package consisting of
        subpackages. It uses the factory class pattern to create SubPackage instances at runtime
        and appends them to the subpackage_list.

        Args:
            robot_data (str): A hexadecimal string representing binary data with robot parameters
                            encoded as packages and subpackages.
        """
        current_position = 5 # First 5 bytes already decoded.
        while current_position < len(robot_data):

            subpackage_length = struct.unpack('>I', robot_data[current_position:current_position+4])[0]
            subpackage_type = struct.unpack('>B', robot_data[current_position+4:current_position+5])[0]
            subpackage_data = robot_data[current_position:subpackage_length+current_position]
            
            new_subpackage = SubPackage.create_subpackage(self.type, subpackage_data, subpackage_length, subpackage_type)
            self.subpackage_list.append(new_subpackage)

            current_position += subpackage_length

    def get_subpackage(self, target_subpackage_name):
        """
        Retrieve a subpackage object from the package's subpackage_list based on its name.
        
        Args:
            target_subpackage_name (str): The name of the subpackage to be retrieved.
            
        Returns:
            SubPackage: The subpackage object with the matching name, if found; otherwise, None.
        """
        for subpackage in self.subpackage_list:
            if subpackage.subpackage_name == target_subpackage_name:
                return subpackage
        return None
    
    def __str__(self) -> str:
        """
        Generate a string for the Package object, including tables for all its SubPackage objects.
        
        The string includes the package's arrival timestamp, package type, package length, and a table
        for each subpackage displaying its data.
        
        Returns:
            str: A formatted string representing the package report with tables for all subpackages.
        """
        formatted = self.received_timestamp.strftime("%Y-%m-%d, %H:%M:%S.%f")[:-5] 
        string = f"TIME: {formatted}, PACKAGE TYPE: {self.type}, PACKAGE LENGTH: {self.length}\n\n"
        for subpackage in self.subpackage_list:
            string += f"{subpackage}"

        return string

