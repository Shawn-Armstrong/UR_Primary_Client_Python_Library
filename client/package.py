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
    def __init__(self, robot_data):
        self.length = self.get_package_length(robot_data)
        self.type = self.get_package_type(robot_data)
        self.robot_data = robot_data
        self.subpackage_list = []
        self.received_timestamp = datetime.now()

        # Currently, only robot state messages are implemented.
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
            
            new_subpackage = SubPackage.create_subpackage(self.type, subpackage_data, subpackage_length, subpackage_type)
            self.subpackage_list.append(new_subpackage)

            current_position += subpackage_length

    def __str__(self):
        formatted = self.received_timestamp.strftime("%Y-%m-%d, %H:%M:%S.%f")[:-5] 
        string = f"TIME: {formatted}, PACKAGE TYPE: {self.type}, PACKAGE LENGTH: {self.length}\n\n"
        for subpackage in self.subpackage_list:
            string += f"{subpackage}"

        return string
