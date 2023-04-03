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
from datetime import timedelta
from collections import namedtuple
from tabulate import tabulate

class SubPackage:
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        self.package_type = package_type
        self.subpackage_length = subpackage_length
        self.subpackage_type = subpackage_type
        self.subpackage_data = subpackage_data

    # Implements class factory pattern to create subpackage objects at runtime,
    @classmethod
    def create_subpackage(cls, package_type, subpackage_data, subpackage_length, subpackage_type):
        subclasses = {
            (16, 0): RobotModeData,
            (16, 1): JointData,
            (16, 2): ToolData,
            (16, 3): MasterBoardData,
            (16, 4): CartesianInfo,
            (16, 5): KinematicsInfo,
            (16, 6): ConfigurationData,
            (16, 7): ForceModeData,
            (16, 8): AdditionalInfo,
            (16, 9): CalibrationData,
            (16, 10): SafetyData,
            (16, 11): ToolCommunicationInfo,
            (16, 12): ToolModeInfo,
            (16, 13): SingularityInfo
        }
        subclass = subclasses.get((package_type, subpackage_type))

        if subclass:
            return subclass(
                package_type,
                subpackage_data,
                subpackage_length,
                subpackage_type
            )
        else:
            return UnknownSubPackage(
                package_type,
                subpackage_data,
                subpackage_length,
                subpackage_type
            )

    def decode_subpackage_variables(self):
        unpacked_data = struct.unpack(
            self.format_string,
            self.subpackage_data[5:self.subpackage_length]
        )
        subpackage_variables = self.Structure._make(unpacked_data)

        return subpackage_variables

    def __str__(self):
        # Create a list of tuples containing variable names and their corresponding values
        variables = [
            (name, getattr(self.subpackage_variables, name))
            for name in self.subpackage_variables._fields
        ]

        # Use the tabulate library to create a table with the variable names and values
        table = tabulate(
            variables,
            headers=["Variable", "Value"],
            tablefmt="grid"
        )

        # Return the formatted table as a string
        return f"{self.subpackage_name}:\n{table}\n\n"


class RobotModeData(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Robot Mode Data"
        self.format_string = '>Q????????BdddB'
        self.Structure = RobotModeDataStructure
        self.subpackage_variables = self.decode_subpackage_variables()
    
    # Override necessary for timestamp conversion.
    def decode_subpackage_variables(self):
        unpacked_data = struct.unpack(
            self.format_string,
            self.subpackage_data[5:self.subpackage_length]
        )

        # Create a new tuple with the updated timestamp
        new_timestamp = timedelta(seconds=unpacked_data[0]/1000000)
        updated_unpacked_data = (new_timestamp,) + unpacked_data[1:]

        # Create the named tuple using the updated unpacked data
        subpackage_variables = self.Structure._make(updated_unpacked_data)

        return subpackage_variables


class JointData(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Joint Data"
        self.format_string = '>dddffffBdddffffBdddffffBdddffffBdddffffBdddffffB'
        self.Structure = JointDataStructure
        field_names = [f'Joint{i+1}_{field}' for i in range(6) for field in JointDataStructure._fields]
        self.FlattenedJointData = namedtuple('FlattenedJointData', field_names)
        self.subpackage_variables = self.decode_subpackage_variables()

    def decode_subpackage_variables(self):
        single_joint_format_string = self.format_string[0:9]
        first_joint_byte = 5
        last_joint_byte = 46
        flattened_data = []

        for i in range(6):

            # Decode data for ith joint
            unpacked_data = struct.unpack(
                single_joint_format_string,
                self.subpackage_data[first_joint_byte:last_joint_byte]
            )

            # Add the unpacked data to the flattened data list
            flattened_data.extend(unpacked_data)

            first_joint_byte = last_joint_byte
            last_joint_byte += 41

        # Create a new named tuple with the flattened data
        flattened_joint_data = self.FlattenedJointData._make(flattened_data)

        return flattened_joint_data

    def __str__(self):
        # Extract the number of joints and fields per joint
        num_joints = 6
        fields_per_joint = len(JointDataStructure._fields)

        # Create the headers for the table
        headers = ["Joint"] + [field for field in JointDataStructure._fields]

        # Prepare the rows for the table
        rows = []
        for i in range(num_joints):
            row = [f"Joint {i+1}"]
            for j in range(fields_per_joint):
                # Get the value of the field for each joint
                row.append(getattr(self.subpackage_variables, f'Joint{i+1}_{JointDataStructure._fields[j]}'))
            rows.append(row)

        # Use tabulate to format the table
        table = tabulate(rows, headers=headers, tablefmt="grid")

        # Return the formatted string
        return f"{self.subpackage_name}:\n{table}\n\n"


class CartesianInfo(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Cartesian Info"
        self.format_string = '>dddddddddddd'
        self.Structure = CartesianInfoStructure
        self.subpackage_variables = self.decode_subpackage_variables()


class CalibrationData(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Calibration Data"
        self.format_string = '>dddddd'
        self.Structure = CalibrationDataStructure
        self.subpackage_variables = self.decode_subpackage_variables()


class MasterBoardData(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Master Board Data"
        self.subpackage_variables = self.decode_subpackage_variables()

    def decode_subpackage_variables(self):
        format_string = '>IIBBddBBddffffBBB'
        unpacked_data = struct.unpack(
            format_string, self.subpackage_data[5:68])

        if unpacked_data[16] == 0:
            unpacked_data += ("Not used", "Not used", "Not used", "Not used")
            format_string = '>IBBB'
            unpacked_data += struct.unpack(format_string, self.subpackage_data[68:])
        else:
            format_string = '>IIFFIBBB'
            unpacked_data += struct.unpack(format_string, self.subpackage_data[68:])

        subpackage_variables = MasterboardDataStructure._make(unpacked_data)
        return subpackage_variables


class ToolData(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Tool Data"
        self.format_string = '>BBddfBffB'
        self.Structure = ToolDataStructure
        self.subpackage_variables = self.decode_subpackage_variables()


class ForceModeData(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Force Mode Data"
        self.format_string = '>ddddddd'
        self.Structure = ForceModeDataStructure
        self.subpackage_variables = self.decode_subpackage_variables()


class AdditionalInfo(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Additional Info"
        self.format_string = '>B??B'
        self.Structure = AdditionalInfoStructure
        self.subpackage_variables = self.decode_subpackage_variables()


class SafetyData(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Safety Data"
        self.subpackage_variables = SafetyDataStructure(
            Message="Subpackage is for internal UR operations; nothing to see here.")


class ToolCommunicationInfo(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Tool Communication Info"
        self.format_string = '>?IIIff'
        self.Structure = ToolCommunicationInfoStructure
        self.subpackage_variables = self.decode_subpackage_variables()


class ToolModeInfo(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Tool Mode Info"
        self.format_string = '>BBB'
        self.Structure = ToolModeInfoStructure
        self.subpackage_variables = self.decode_subpackage_variables()


class SingularityInfo(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Singularity Info"
        self.format_string = '>BB'
        self.Structure = SingularityInfoStructure
        self.subpackage_variables = self.decode_subpackage_variables()


class ConfigurationData(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Configuration Data"
        self.format_string = ">dddddddddddddddddddddddddddddddddddddddddddddddddddddiiii"
        self.Structure = ConfigurationDataStructure
        field_names = self.create_flattened_fields()
        self.Structure = namedtuple('FlattenedConfigurationData', field_names)
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def create_flattened_fields(self):
        field_names = ConfigurationDataStructure._fields
        updated_names = []

        for i in range(1, 7):
            updated_names.append(f"joint_{i}_{field_names[0]}")
            updated_names.append(f"joint_{i}_{field_names[1]}")
        
        for i in range(1, 7):
            updated_names.append(f"joint_{i}_{field_names[2]}")
            updated_names.append(f"joint_{i}_{field_names[3]}")

        for i in range(4, 9):
            updated_names.append(f"{field_names[i]}")
        
        for i in range(1, 7):
            updated_names.append(f"joint_{i}_{field_names[9]}")
        
        for i in range(1, 7):
            updated_names.append(f"joint_{i}_{field_names[10]}")
        
        for i in range(1, 7):
            updated_names.append(f"joint_{i}_{field_names[11]}")

        for i in range(1, 7):
            updated_names.append(f"joint_{i}_{field_names[12]}")
        
        for i in range(13, 17):
            updated_names.append(f"{field_names[i]}")

        return updated_names


class KinematicsInfo(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Kinematics Info"

        # Controller only sends joint info on change; therefore, adjust accordingly.
        if self.subpackage_length == 9:
            self.format_string = ">i"
        else:
            self.format_string = ">iiiiiiddddddddddddddddddddddddi"

        self.Structure = KinematicsInfoStructure


        if self.subpackage_length == 9: # Controller sends no joint info
            self.Structure = namedtuple("KinematicsInfoStructureSingle", ["calibration_status"])
            self.subpackage_variables = self.decode_subpackage_variables()
        else: # Controller sends joint info
            field_names = self.create_flattened_fields()
            self.Structure = namedtuple('FlattenedKinematicsInfo', field_names)
            self.subpackage_variables = self.decode_subpackage_variables()

    def create_flattened_fields(self):
        field_names = KinematicsInfoStructure._fields
        updated_names = []

        #checksum
        for i in range(1, 7):
            updated_names.append(f"joint_{i}_{field_names[0]}")

        #dhetha
        for i in range(1, 7):
            updated_names.append(f"joint_{i}_{field_names[1]}")
        
        #DHa
        for i in range(1, 7):
            updated_names.append(f"joint_{i}_{field_names[2]}")
        
        #Dhd
        for i in range(1, 7):
            updated_names.append(f"joint_{i}_{field_names[3]}")
        
        #Dhalpha
        for i in range(1, 7):
            updated_names.append(f"joint_{i}_{field_names[4]}")
        
        #calibration_status
        updated_names.append(f"{field_names[5]}")

        return updated_names




# Fallback mechanism / graceful degradation
# Implemented to preserve robustness and handle unexpected subpackages
class UnknownSubPackage(SubPackage):
    def __init__(self, package_type, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(package_type, subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = f"UnknownSubPackage type is {subpackage_type} length is {subpackage_length}"
        self.subpackage_variables = UnknownSubPackageStructure(
            Message="Unknown subpackage")

########################### NAMED TUPLES ###########################
UnknownSubPackageStructure = namedtuple("ConfigurationDataStructure", [
    "Message"
])

ConfigurationDataStructure = namedtuple("ConfigurationDataStructure", [
    "jointMinLimit",
    "jointMaxLimit",
    "jointMaxSpeed",
    "jointMaxAcceleration",
    "vJointDefault",
    "aJointDefault",
    "vToolDefault",
    "aToolDefault",
    "eqRadius",
    "DHa",
    "Dhd",
    "DHalpha",
    "DHtheta",
    "masterboardVersion",
    "controllerBoxType",
    "robotType",
    "robotSubType"
])

KinematicsInfoStructure = namedtuple("KinematicsInfoStructure", [
    "checksum",
    "DHtheta",
    "DHa",
    "Dhd",
    "Dhalpha",
    "calibration_status"
])

AdditionalInfoStructure = namedtuple("AdditionalInfoStructure", [
    "tpButtonState",
    "freedriveButtonEnabled",
    "IOEnabledFreedrive",
    "reserved"
])

ToolCommunicationInfoStructure = namedtuple("ToolCommunicationInfoStructure", [
    "toolCommunicationIsEnabled",
    "baudRate",
    "parity",
    "stopBits",
    "RxIdleChars",
    "TxIdleChars"
])

ToolModeInfoStructure = namedtuple("ToolModeInfoStructure", [
    "outputMode",
    "digitalOutputModeOutput0",
    "digitalOutputModeOutput1"
])

SingularityInfoStructure = namedtuple("SingularityInfoStructure", [
    "singularitySeverity",
    "singularityType"
])

RobotModeDataStructure = namedtuple("RobotModeDataStructure", [
    "timestamp",
    "isRealRobotConnected",
    "isRealRobotEnabled",
    "isRobotPowerOn",
    "isEmergencyStopped",
    "isProtectiveStopped",
    "isProgramRunning",
    "isProgramPaused",
    "robotMode",
    "controlMode",
    "targetSpeedFraction",
    "speedScaling",
    "targetSpeedFractionLimit",
    "reserved"
])

ForceModeDataStructure = namedtuple("ForceModeDataStructure", [
    "Fx",
    "Fy",
    "Fz",
    "Frx",
    "Fry",
    "Frz",
    "robotDexterity"
])

SafetyDataStructure = namedtuple("SafetyDataStructure", [
    "Message"
])

ToolDataStructure = namedtuple("ToolDataStructure", [
    "analogInputRange0",
    "analogInputRange1",
    "analogInput0",
    "analogInput1",
    "toolVoltage48V",
    "toolOutputVoltage",
    "toolCurrent",
    "toolTemperature",
    "toolMode"
])

MasterboardDataStructure = namedtuple("MasterboardDataStructure", [
    "digitalInputBits",
    "digitalOutputBits",
    "analogInputRange0",
    "analogInputRange1",
    "analogInput0",
    "analogInput1",
    "analogOutputDomain0",
    "analogOutputDomain1",
    "analogOutput0",
    "analogOutput1",
    "masterBoardTemperature",
    "robotVoltage48V",
    "robotCurrent",
    "masterIOCurrent",
    "safetyMode",
    "InReducedMode",
    "euromap67InterfaceInstalled",
    "euromapInputBits",
    "euromapOutputBits",
    "euromapVoltage24V",
    "euromapCurrent",
    "URSoftwareOnly",
    "operationalModeSelectorInput",
    "threePositionEnablingDeviceInput",
    "URSoftwareOnly2"
])

CalibrationDataStructure = namedtuple("CalibrationDataStructure", [
    "Fx",
    "Fy",
    "Fz",
    "Frx",
    "Fry",
    "Frz"
])

CartesianInfoStructure = namedtuple("CartesianInfoStructure", [
    "X",
    "Y",
    "Z",
    "Rx",
    "Ry",
    "Rz",
    "TCPOffsetX",
    "TCPOffsetY",
    "TCPOffsetZ",
    "TCPOffsetRx",
    "TCPOffsetRy",
    "TCPOffsetRz"
])

JointDataStructure = namedtuple("JointDataStructure", [
    "q_actual",
    "q_target",
    "qd_actual",
    "I_actual",
    "V_actual",
    "T_motor",
    "T_micro",
    "jointMode"
])
