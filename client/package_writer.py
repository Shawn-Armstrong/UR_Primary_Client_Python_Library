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

import os
import sys
from collections import deque

class PackageWriter:

    def __init__(self, max_packages):
        self.max_packages = max_packages
        output_directory = "output"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        self.file_paths = [
            (-1, os.path.join(output_directory, "disconnect.txt")),
            (16, os.path.join(output_directory, "robot_state.txt")),
            (20, os.path.join(output_directory, "robot_message.txt")),
            (22, os.path.join(output_directory, "hmc_message.txt")),
            (5, os.path.join(output_directory, "modbus_info_message.txt")),
            (23, os.path.join(output_directory, "safety_setup_broadcast_message.txt")),
            (24, os.path.join(output_directory, "safety_compliance_tolerances_message.txt")),
            (25, os.path.join(output_directory, "program_state_message.txt"))
        ]
        self.package_counts = [(key, 0) for key, _ in self.file_paths]
        self.package_deques = {key: deque(maxlen=self.max_packages) for key, _ in self.file_paths}

        # Clear the content of each file at the beginning of every execution
        for _, file_path in self.file_paths:
            with open(file_path, "w") as file:
                file.write("")

    def append_package_to_file(self, package):
        message_type = package.type
        file_path = None
        for index, (key, path) in enumerate(self.file_paths):
            if key == message_type:
                file_path = path
                # Increment the counter for the matching package type only if the deque is not full
                if len(self.package_deques[key]) < self.max_packages:
                    self.package_counts[index] = (key, self.package_counts[index][1] + 1)
                break

        if file_path:
            self.package_deques[message_type].append(f"{package}\n{'#' * 80}\n")
            with open(file_path, "w") as file:
                for pkg_str in self.package_deques[message_type]:
                    file.write(pkg_str)
        else:
            print(f"Unknown message type: {message_type}")
 
        self.print_package_counts()

    def print_package_counts(self):
        sys.stdout.write("\r")
        sys.stdout.write(f"RECEIVED: {self.package_counts[0][0]}:{self.package_counts[0][1]}, {self.package_counts[1][0]}:{self.package_counts[1][1]}, {self.package_counts[2][0]}:{self.package_counts[2][1]}, {self.package_counts[3][0]}:{self.package_counts[3][1]}, {self.package_counts[4][0]}:{self.package_counts[4][1]}, {self.package_counts[5][0]}:{self.package_counts[5][1]}, {self.package_counts[6][0]}:{self.package_counts[6][1]}, {self.package_counts[7][0]}:{self.package_counts[7][1]}")
        sys.stdout.flush()