import struct
from collections import namedtuple

class Package:
    def __init__(self, robot_data):
        self.length = self.get_package_length(robot_data)
        self.type = self.get_package_type(robot_data)
        self.robot_data = robot_data
        self.subpackage_list = []
        if self.type == 16:
            self.read_subpackages(robot_data)
        print(f"Number of subpackages: {len(self.subpackage_list)}")

    def get_package_length(self, robot_data) -> int:
        package_length = struct.unpack('>I', robot_data[0:4])[0]
        return package_length
    
    def get_package_type(self, robot_data) -> int:
        package_type = struct.unpack('>B', robot_data[4:5])[0]
        return package_type
    
    def read_subpackages(self, robot_data):

        current_position = 5
        total = 0
        print(self.length)
        while current_position < len(robot_data):
            subpackage_length = struct.unpack('>I', robot_data[current_position:current_position+4])[0]
            subpackage_type = struct.unpack('>B', robot_data[current_position+4:current_position+5])[0]
            total += subpackage_length
            subpackage_data = robot_data[current_position:subpackage_length+current_position]
            # print(f"subpackage_length={subpackage_length}, subpackage_type={subpackage_type}")
            if subpackage_type in (0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 13):
                
                new_subpackage = SubPackage.create_subpackage(subpackage_data, subpackage_length, subpackage_type)
                self.subpackage_list.append(new_subpackage)

            
            current_position += subpackage_length
        
        print(f"TOTAL: {total}\n###############################")


class SubPackage:
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        self.subpackage_length = subpackage_length
        self.subpackage_type = subpackage_type
        self.subpackage_data = subpackage_data
    
    @classmethod
    def create_subpackage(cls, subpackage_data, subpackage_length, subpackage_type):
        subclasses = {0: RobotModeData, 1: JointData, 2: ToolData, 3: MasterBoardData, 4: CartesianInfo, 7: ForceModeData, 8: AdditionalInfo, 9: CalibrationData, 10: SafetyData, 11: ToolCommunicationInfo, 12: ToolModeInfo, 13: SingularityInfo}
        subclass = subclasses.get(subpackage_type)
        
        if subclass:
            return subclass(subpackage_data, subpackage_length, subpackage_type)
        else:
            return cls(subpackage_data, subpackage_length, subpackage_type)

class RobotModeData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Robot Mode Data"
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def decode_subpackage_variables(self):
        format_string = '>Q????????BdddB' # Variable data types within RobotModeData from UR spec.
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = RobotModeDataStructure._make(unpacked_data)
        return subpackage_variables


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

class JointData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Joint Data"
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def decode_subpackage_variables(self):

        format_string = '>dddffffB' # Variable data types within RobotModeData from UR spec.
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

class CartesianInfo(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Cartesian Info"
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def decode_subpackage_variables(self):
        format_string = '>dddddddddddd' # Variable data types within RobotModeData from UR spec.
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = CartesianInfoStructure._make(unpacked_data)
        return subpackage_variables

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

class CalibrationData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Calibration Data"
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def decode_subpackage_variables(self):
        format_string = '>dddddd' # Variable data types within RobotModeData from UR spec.
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = CalibrationDataStructure._make(unpacked_data)
        return subpackage_variables

CalibrationDataStructure = namedtuple("CalibrationDataStructure", [
    "Fx",
    "Fy",
    "Fz",
    "Frx",
    "Fry",
    "Frz"
])

class MasterBoardData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Master Board Data"
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def decode_subpackage_variables(self):
        format_string = '>IIBBddBBddffffBBB' # Variable data types within RobotModeData from UR spec.
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
   
class ToolData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Tool Data"
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def decode_subpackage_variables(self):
        format_string = '>BBddfBffB' # Variable data types within RobotModeData from UR spec.
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = ToolDataStructure._make(unpacked_data)
        return subpackage_variables

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

class ForceModeData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Force Mode Data"
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def decode_subpackage_variables(self):
        format_string = '>ddddddd' # Variable data types within RobotModeData from UR spec.
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = ForceModeDataStructure._make(unpacked_data)
        return subpackage_variables

ForceModeDataStructure = namedtuple("ForceModeDataStructure", [
    "Fx",
    "Fy",
    "Fz",
    "Frx",
    "Fry",
    "Frz",
    "robotDexterity"
])

class AdditionalInfo(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        self.subpackage_name = "Additional Info"
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def decode_subpackage_variables(self):
        format_string = '>B??B' # Variable data types within RobotModeData from UR spec.
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = AdditionalInfoStructure._make(unpacked_data)
        return subpackage_variables

AdditionalInfoStructure = namedtuple("AdditionalInfoStructure", [
    "tpButtonState",
    "freedriveButtonEnabled",
    "IOEnabledFreedrive",
    "reserved"
])

class SafetyData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Safety Data"
        self.subpackage_variables = "Subpackage is for internal UR operations; nothing to see here."

class ToolCommunicationInfo(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Tool Communication Info"
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def decode_subpackage_variables(self):
        format_string = '>?IIIff' # Variable data types within RobotModeData from UR spec.
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = ToolCommunicationInfoStructure._make(unpacked_data)
        return subpackage_variables

ToolCommunicationInfoStructure = namedtuple("ToolCommunicationInfo", [
    "toolCommunicationIsEnabled",
    "baudRate",
    "parity",
    "stopBits",
    "RxIdleChars",
    "TxIdleChars"
])

class ToolModeInfo(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Tool Mode Info"
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def decode_subpackage_variables(self):
        format_string = '>BBB' # Variable data types within RobotModeData from UR spec.
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = ToolModeInfoStructure._make(unpacked_data)
        return subpackage_variables

ToolModeInfoStructure = namedtuple("ToolModeInfoStructure", [
    "outputMode",
    "digitalOutputModeOutput0",
    "digitalOutputModeOutput1"
])

class SingularityInfo(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)
        self.subpackage_name = "Singularity Info"
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def decode_subpackage_variables(self):
        format_string = '>BB' # Variable data types within RobotModeData from UR spec.
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = SingularityInfoStructure._make(unpacked_data)
        return subpackage_variables

SingularityInfoStructure = namedtuple("SingularityInfoStructure", [
    "singularitySeverity",
    "singularityType"
])