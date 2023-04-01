# test_subpackage.py

import struct
import unittest
from client.subpackage import *

class TestRobotModeData(unittest.TestCase):

    def create_test_data(self, format_string, subpackage_type):
    
        data = b''
        num_count = 0
        
        # Creates test data
        # Numeric values are given monotonically increasing values starting with 0 at index 0
        # Bools are given true
        for char in format_string[1:]:
            if char in ('Q', 'q', 'L', 'l', 'I', 'i', 'H', 'h', 'B', 'b', 'd'):
                packed_data = struct.pack(f'>{char}', num_count)
                num_count += 1
                data += packed_data
            elif char == '?':
                data += struct.pack('>?', True)
            else:
                raise ValueError(f"Invalid format string character: {char}")
                
        
        # Encodes subpackage type and subpackage_length
        size = len(data)+5
        data = struct.pack('>IB', size, subpackage_type) + data
        
        return data

    def test_decode_subpackage_variables(self):
        
        # Define test data
        package_type = 16
        format_string = '>Q????????BdddB'
        subpackage_type = 0
        subpackage_data = self.create_test_data(format_string, subpackage_type)
        subpackage_length = len(subpackage_data)
        
        # Create RobotModeData instance
        robot_mode_data = RobotModeData(package_type, subpackage_data, subpackage_length, subpackage_type)

        # Call decode_subpackage_variables on the separate instance and save result
        result = robot_mode_data.decode_subpackage_variables()

        # Define expected result
        values = (0, True, True, True, True, True, True, True, True, 1, 2.0, 3.0, 4.0, 5)
        expected_result = RobotModeDataStructure._make(values)

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()