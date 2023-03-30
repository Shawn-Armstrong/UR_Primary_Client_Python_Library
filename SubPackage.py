import struct
from collections import namedtuple
from tabulate import tabulate

class SubPackage:
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        self.subpackage_length = subpackage_length
        self.subpackage_type = subpackage_type
        self.subpackage_data = subpackage_data

    @classmethod
    def create_subpackage(cls, subpackage_data, subpackage_length, subpackage_type):
        subclasses = {0: RobotModeData, 1: JointData, 2: ToolData, 3: MasterBoardData, 4: CartesianInfo, 7: ForceModeData,
                      8: AdditionalInfo, 9: CalibrationData, 10: SafetyData, 11: ToolCommunicationInfo, 12: ToolModeInfo, 13: SingularityInfo}
        subclass = subclasses.get(subpackage_type)

        if subclass:
            return subclass(subpackage_data, subpackage_length, subpackage_type)
        else:
            return cls(subpackage_data, subpackage_length, subpackage_type)
        
    def __str__(self):
        # Create a list of tuples containing variable names and their corresponding values
        variables = [(name, getattr(self.subpackage_variables, name)) for name in self.subpackage_variables._fields]

        # Use the tabulate library to create a table with the variable names and values
        table = tabulate(variables, headers=["Variable", "Value"], tablefmt="grid")

        # Return the formatted table as a string
        return f"{self.subpackage_name}:\n{table}\n\n"


class RobotModeData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Robot Mode Data"
        self.subpackage_variables = self.decode_subpackage_variables()
        

    def decode_subpackage_variables(self):
        format_string = '>Q????????BdddB'
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = RobotModeDataStructure._make(unpacked_data)
        return subpackage_variables


class JointData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Joint Data"
        self.subpackage_variables = self.decode_subpackage_variables()

    def decode_subpackage_variables(self):

        format_string = '>dddffffB'
        first_joint_byte = 5
        last_joint_byte = 46
        joint_data_list = []

        for i in range(6):

            # Decode data for ith joint
            unpacked_data = struct.unpack(format_string, self.subpackage_data[first_joint_byte:last_joint_byte])
            ith_joint = JointDataStructure._make(unpacked_data)

            # Add ith joint to list
            joint_data_list.append(ith_joint)

            first_joint_byte = last_joint_byte
            last_joint_byte += 41

        return joint_data_list
    
    def __str__(self):
        # Convert each namedtuple to a dictionary and store them in a list
        subpackage_variables_dicts = [joint_data._asdict() for joint_data in self.subpackage_variables]

        # Extract the column headers (variable names) from the first dictionary
        headers = ["Joint"] + list(subpackage_variables_dicts[0].keys())

        # Convert the list of dictionaries to a list of lists for tabulate
        rows = [[f"Joint {i+1}"] + list(joint_data.values()) for i, joint_data in enumerate(subpackage_variables_dicts)]

        # Use tabulate to format the table
        table = tabulate(rows, headers=headers, tablefmt="grid")

        # Return the formatted string
        return f"{self.subpackage_name}:\n{table}\n\n"


class CartesianInfo(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Cartesian Info"
        self.subpackage_variables = self.decode_subpackage_variables()

    def decode_subpackage_variables(self):
        format_string = '>dddddddddddd'
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = CartesianInfoStructure._make(unpacked_data)
        return subpackage_variables

class CalibrationData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Calibration Data"
        self.subpackage_variables = self.decode_subpackage_variables()

    def decode_subpackage_variables(self):
        format_string = '>dddddd'
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = CalibrationDataStructure._make(unpacked_data)
        return subpackage_variables


class MasterBoardData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Master Board Data"
        self.subpackage_variables = self.decode_subpackage_variables()

    def decode_subpackage_variables(self):
        format_string = '>IIBBddBBddffffBBB'
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:68])

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
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Tool Data"
        self.subpackage_variables = self.decode_subpackage_variables()

    def decode_subpackage_variables(self):
        format_string = '>BBddfBffB'
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = ToolDataStructure._make(unpacked_data)
        return subpackage_variables


class ForceModeData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Force Mode Data"
        self.subpackage_variables = self.decode_subpackage_variables()

    def decode_subpackage_variables(self):
        format_string = '>ddddddd'
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = ForceModeDataStructure._make(unpacked_data)
        return subpackage_variables


class AdditionalInfo(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Additional Info"
        self.subpackage_variables = self.decode_subpackage_variables()

    def decode_subpackage_variables(self):
        format_string = '>B??B'
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = AdditionalInfoStructure._make(unpacked_data)
        return subpackage_variables


class SafetyData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Safety Data"
        self.subpackage_variables = SafetyDataStructure(Message="Subpackage is for internal UR operations; nothing to see here.")
    

class ToolCommunicationInfo(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Tool Communication Info"
        self.subpackage_variables = self.decode_subpackage_variables()

    def decode_subpackage_variables(self):
        format_string = '>?IIIff'
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = ToolCommunicationInfoStructure._make(unpacked_data)
        return subpackage_variables


class ToolModeInfo(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Tool Mode Info"
        self.subpackage_variables = self.decode_subpackage_variables()

    def decode_subpackage_variables(self):
        format_string = '>BBB'
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = ToolModeInfoStructure._make(unpacked_data)
        return subpackage_variables


class SingularityInfo(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Singularity Info"
        self.subpackage_variables = self.decode_subpackage_variables()

    def decode_subpackage_variables(self):
        format_string = '>BB'
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = SingularityInfoStructure._make(unpacked_data)
        return subpackage_variables


########################### NAMED TUPLES ###########################


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