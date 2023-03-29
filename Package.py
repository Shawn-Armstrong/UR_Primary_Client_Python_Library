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

        subpackage_length = struct.unpack('>I', robot_data[5:9])[0]
        subpackage_type = struct.unpack('>B', robot_data[9:10])[0]
        subpackage_data = robot_data[5:subpackage_length+5]

        if self.type == 16:
            new_subpackage = SubPackage.create_subpackage(subpackage_data, subpackage_length, subpackage_type)
            print(new_subpackage.subpackage_variables.isRobotPowerOn)
    
class SubPackage:
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        self.subpackage_length = subpackage_length
        self.subpackage_type = subpackage_type
        self.subpackage_data = subpackage_data
    
    @classmethod
    def create_subpackage(cls, subpackage_data, subpackage_length, subpackage_type):
        subclasses = {0: RobotModeData}
        subclass = subclasses.get(subpackage_type)
        
        if subclass:
            return subclass(subpackage_data, subpackage_length, subpackage_type)
        else:
            return cls(subpackage_data, subpackage_length, subpackage_type)

class RobotModeData(SubPackage):
    def __init__(self, subpackage_data, subpackage_length, subpackage_type):
        super().__init__(subpackage_data, subpackage_length, subpackage_type)

        format_string = '>Q????????BdddB'
        unpacked_data = struct.unpack(format_string, subpackage_data[5:subpackage_length])
        self.subpackage_name = "Robot Mode Data"
        self.subpackage_variables = RobotModeDataStructure._make(unpacked_data)

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

    
    

   
