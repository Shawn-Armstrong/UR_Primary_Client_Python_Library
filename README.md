# UR Primary Client Python Library

### Overview
This client is designed to connect to a Universal Robots' e-series cobot via the primary client interface. It receives messages, deserializes them into a human readable format, and writes the content to files.

### Demo
Program demonstrates client curating robot state messages.
  
<kbd>![decode_demo](https://user-images.githubusercontent.com/80125540/229012953-e81e12a9-4dad-45cc-80f6-3fb1eacd7df2.gif)</kbd>

## Usage

### Requirements 
- Python
- Git
- UR e-series model, simulated or physical, running PolyScope version 5.9 or newer.

### Simulator Options
- [VirtualBox simulator](https://gist.github.com/Shawn-Armstrong/bbb2615abd917efc958c7fce714b0d46#ur-simulator-setup)
- Docker simulator setup
  - With docker installed run the following command then navigate to http://localhost:6080/ using Google Chrome.
      
    ```Console
    docker run -it -e ROBOT_MODEL=UR3e -p 30001:30001 -p 30002:30002 -p 30004:30004 -p 6080:6080 --name ur3e_container universalrobots/ursim_e-series
    ```
### Setup

1. Identify your cobot's IP address in the Hamburger menu within PolyScope. 
   - If using docker, then you'll use your host machine's IPv4 
     
   <kbd>![ip_address](https://user-images.githubusercontent.com/80125540/229017434-1d4e4241-bd24-475d-9559-85d4e1724d7f.gif)</kbd>

2. Clone this repository into a directory of your choice with the following command:
     
   ```Console
   git clone https://github.com/Shawn-Armstrong/UR_Primary_Client_Python_Library.git
   ```
3. Curate packages by navigating inside the cloned directory `/client` from a console and running the following command:
   
   ```Console
   python client.py ip_address=YOUR_IP_ADDRESS max_reports=NUMBER_YOU_WANT_TO_CAPTURE_PER_PACKAGE
   ```

### Output & Behavior
The client captures a specified number of packages, `max_reports`, for each package type and writes them to the end of their corresponding text files within the output directory. When the `max_reports` limit for a specific package type has been reached, the client will remove the oldest entry and add the newest incoming entry, maintaining a rolling buffer of the most recent packages. At the beginning of each execution, the text files are cleared to ensure a fresh start. The program can be terminated with a keyboard interrupt: <kbd>ctrl</kbd> + <kbd>c</kbd> .

Default program arguments are as follows:
  - `--max_reports=10`
  - `--ip_address=<local ip address>`

### Custom Reports
To enable custom reports, run `client.py --custom_report`. When enabled, the client will track every variable listed in `watch_list.txt` and report it in the `../output/custom_report.txt` file. Each variable should be on a separate line within the file and spelled exactly as they appear in their related output package file. Custom reports capture a specified number of entries, `max_reports`, in a single table. When a new entry is added, the oldest entry will be discarded if the table has reached its maximum capacity. Every entry contains the last observed value; if a value has yet to be received, its corresponding field in the table will remain empty. At the beginning of each execution `custom_report.txt` is cleared to ensure a fresh start. 
  
## Implementation Details

### Technical Overview
Universal Robots provides a primary client interface, allowing external devices to connect with the cobot's software and facilitate the exchange of communication messages. The cobot's software periodically sends out serialized messages containing robot state information as outlined in their primary / secondary specification. In short, a sent message consists of a hexadecimal string representing binary data, with robot parameters encoded within it. These strings are divided into sections, with the first section called the "package," starting at byte 0 and all subsequent sections being "subpackages."

This client is specifically designed to receive these messages, deserialize them, and write the content to files. The client's implementation consists of four main components: `client.py`, `package.py`, `subpackage.py`, and `packagewriter.py`.

#### `client.py`
This is the entry point of the program. It connects with the cobot, receives messages and uses them to instantiate a `Package` object. Afterwards, a `PackageWriter` object writes the `Package` to a file.

#### `package.py`
This file defines the `Package` class. In principle, this is a container class designed to create, store and manage `SubPackages` also leveraging the relationship between them. `Package` employs a class factory pattern defined in `SubPackage` to instantiate `SubPackage` objects.. 

#### `subpackage.py`
This file defines the `SubPackage` class and its subclasses. `SubPackage` implements an inheritance hierarchy where every subclass is a subpackage defined in the primary / secondary specification. The hierarchy is designed around named tuples to facilitate table construction while taking advantage of polymorphism.

#### `packagewriter.py`
This file defines the `PackageWriter` class, which is essentially a writer class that utilizes data from `Package` objects to write to files. The class streamlines file handling by maintaining a separate text file for each package type defined in the specification and writing corresponding `Package` objects to the appropriate file.

## Development

### Notices
- This client was developed using a simulated e-series UR3e running PolyScope 5.13. As it is in the early stages of development, its results should be treated with caution and skepticism.
- Currently, only robot state messages are supported.

### Unit Tests
- Directory `test` contains unit tests used to support test driven development. 

### Future Features
- [ ] Implement package type 20.
- [ ] Implement a method of filtering variables.
- [ ] Implement unit tests.

### Bugs
- [ ] While deserializing a Robot State Message, package type 16, an unknown subpackage type 14 was observed.
  - There may be a potential logic error in class `Package` function `read_subpackages()`.
  - There may be an undocumented subpackage.