from assembler.formats._template import fileFormatClass


class ELF(fileFormatClass):
    def __init__(self, parameters):
        fileFormatClass.__init__(self, parameters)
        if parameters.verbose:
            print('selected output file format: ELF')

    def generateTemplate(self):
        elfHeader = [0x7f, 0x45, 0x4c, 0x46]
        mode = [0x02]  # 64 bit
        endianess = 0
        if self.parameters.endianess == 'little':
            endianess = [0x01]
        else:
            endianess = [0x00]  # big-endian
        elfVersion = [0x01]  # current version
        osABI = [0x00]  # UNIX - System V

        header = elfHeader + mode + endianess + elfVersion + \
            osABI + [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

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
