from assembler.formats._template import fileFormatClass
from assembler.formats.elfConstants import *

class elfException(Exception):
    pass

class ELF(fileFormatClass):
    def __init__(self, parameters):
        fileFormatClass.__init__(self, parameters)
        if parameters.verbose:
            print('selected output file format: ELF')
        self.setupStaticProperties()
        self.setDefault()

    def raiseConfigError(self, what, value, allowedValues):
        raise elfException("Incorrect " + what + ": " + str(value) + ". Allowed values: " + str(allowedValues))

    def setupStaticProperties(self):
        self.e_ident = [0x7f, 0x45, 0x4c, 0x46] # .ELF
        self.elfVersion = [EV_CURRENT]
        self.osABI = [ELFOSABI_SYSV]
        self.osABIVersion = [0x00]

    def setElfClass(self, elfClass):
        ''' Sets object file class (e_ident[EI_CLASS])
        '   Possible options:
        '   - ELF_CLASS32 - 32-bit ##TODO
        '   - ELF_CLASS64 - 64-bit
        '''
        allowedValues = [ELF_CLASS64]
        if elfClass in allowedValues:
            self.ei_class = [elfClass]
        else:
            self.raiseConfigError("ELF class", elfClass, allowedValues)

    def setEndianess(self, endianess):
        ''' Sets endianess of the resulting file data structures
        '   Possible options:
        '   - ELF_DATA2LSB - little-endian
        '   - ELF_DATA2MSB - big-endian ##TODO
        '''
        allowedValues = [ELF_DATA2LSB]
        if endianess in allowedValues:
            self.endianess = [endianess]
        else:
            self.raiseConfigError("endianess mode", endianess, allowedValues)

    def setDefault(self):
        self.setElfClass(ELF_CLASS64)
        self.setEndianess(ELF_DATA2LSB)


    def generateTemplate(self):
        mode = [ELF_CLASS64]  # 64 bit
        endianess = 0
        if self.parameters.endianess == 'little':
            self.setEndianess(ELF_DATA2LSB)
        else:
            self.setEndianess(ELF_DATA2MSB)  # big-endian

        header = self.e_ident + self.ei_class + self.endianess + self.elfVersion + \
            self.osABI + self.osABIVersion + [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        executableType = [0x02, 0x00]  # executable file
        architecture = [0x3e, 0x00]  # AMD x86-64 architecture
        elfFileFormat = [0x01, 0x00, 0x00, 0x00]  # current version

        self.beforeEntryPoint = header + executableType + architecture + elfFileFormat

        # program header table offset
        pHOffset = [0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00]

        # section header table offset - we don't have yet
        sHOffset = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        flags = [0x00, 0x00, 0x00, 0x00]  # flags - none
        headerSize = [0x40, 0x00]  # header size
        pHEntrySize = [0x38, 0x00]  # program header entry size
        pHEntryNum = [0x01, 0x00]  # one entry in program headers table
        sHEntrySize = [0x00, 0x00]  # section header entry size
        sHEntryNum = [0x00, 0x00]  # no entries in section headers table
        stringTableIndex = [0x00, 0x00]  # no string table

        headerAfterEntry = pHOffset + sHOffset + flags + headerSize + \
            pHEntrySize + pHEntryNum + sHEntrySize + sHEntryNum + stringTableIndex

        segmentType = [0x01, 0x00, 0x00, 0x00]  # Loadable segment
        # Flags - read + write + execute
        segmentFlags = [0x07, 0x00, 0x00, 0x00]
        # offset of the section from the beginning of the file, we load the whole file to the memory
        sectionOffset = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        # place it in the memory at the virtual address 0x00
        virtualAddress = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        # reserved for systems with physical addressing
        physicalAddress = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        # size of the segment in the file (here 1 MB)
        segmentSize = [0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00]
        segmentMemorySize = [0x00, 0x00, 0x10, 0x00,
                             0x00, 0x00, 0x00, 0x00]  # size in the memory
        segmentAlignment = [0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00]  # alignment in the memory

        self.afterEntryPoint = headerAfterEntry + segmentType + segmentFlags + \
            sectionOffset + virtualAddress + physicalAddress + \
            segmentSize + segmentMemorySize + segmentAlignment

        self.org = 0x78

    def addFormatData(self, data, startingAddress):
        # convert address to 64 bytes
        address = int(startingAddress).to_bytes(
            8, byteorder=self.parameters.endianess)
        addressBytes = []
        for byte in address:
            addressBytes += [byte]
        header = self.beforeEntryPoint + addressBytes + self.afterEntryPoint + data
        return header
