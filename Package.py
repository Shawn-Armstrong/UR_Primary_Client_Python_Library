import struct
from collections import namedtuple

class Package:
    def __init__(self, robot_data):
        self.length = self.get_package_length(robot_data)
        self.type = self.get_package_type(robot_data)
        self.robot_data = robot_data
        if self.type == 16:
            self.read_subpackages(robot_data)

    def get_package_length(self, robot_data) -> int:
        package_length = struct.unpack('>I', robot_data[0:4])[0]
        return package_length
    
    def get_package_type(self, robot_data) -> int:
        package_type = struct.unpack('>B', robot_data[4:5])[0]
        return package_type
    
    def read_subpackages(self, robot_data):

        # current_position = 5

        # while current_position < len(robot_data):

        subpackage_length = struct.unpack('>I', robot_data[5:9])[0]
        subpackage_type = struct.unpack('>B', robot_data[9:10])[0]
        subpackage_data = robot_data[5:subpackage_length+5]

        if self.type == 16:
            new_subpackage = SubPackage.create_subpackage(subpackage_data, subpackage_length, subpackage_type)
    
class SubPackage:
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        self.subpackage_length = subpackage_length
        self.subpackage_type = subpackage_type
        self.subpackage_data = subpackage_data
    
    @classmethod
    def create_subpackage(cls, subpackage_data, subpackage_length, subpackage_type):
        subclasses = {0: RobotModeData, 1: JointData}
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

        self.subpackage_name = "Robot Mode Data"
        self.subpackage_variables = self.decode_subpackage_variables()
    
    def decode_subpackage_variables(self):
        format_string = '>Q????????BdddB' # Variable data types within RobotModeData from UR spec.
        unpacked_data = struct.unpack(format_string, self.subpackage_data[5:self.subpackage_length])
        subpackage_variables = RobotModeDataStructure._make(unpacked_data)
        return subpackage_variables

JointData = namedtuple("JointData", [
    "q_actual",
    "q_target",
    "qd_actual",
    "I_actual",
    "V_actual",
    "T_motor",
    "jointMode"
])
    
    

   
