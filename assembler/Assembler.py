from enum import Enum
from collections import namedtuple
import string
from assembler.formats._bin import BIN
from assembler.formats._elf import ELF


class AssemblerException(Exception):
    pass


def setup(initialParameters):
    processor = Processor(initialParameters)
    processor.tokenize()
    if initialParameters.verbose:
        print('TOKENS:\n')
        print("{: <8} {: <25} {}\n".format(
            'LINE', 'TYPE', 'VALUE'))
        for token in processor.tokens:
            token.print()
        print()

    return processor


class tokenInfo:
    def __init__(self, type, value):
        self.value = value
        self.type = type


class TYPES(Enum):
    UNKNOWN = -1
    COMMA = 0
    INT = 1
    STRING = 2
    INSTRUCTION = 3
    LABEL = 4


class Token:
    def __init__(self, value, lineNumber, bypass = False):
        self.setFunctionAssignments()
        info = self.getTokenInfo(value)
        self.type = info.type
        self.value = info.value
        self.lineNumber = lineNumber

    def print(self):
        print("{: <8} {: <25} {}".format(
            self.lineNumber, self.type, self.value))

    def setFunctionAssignments(self):
        self.typeFunctions = [
            self.checkComma,
            self.checkNumber,
            self.checkString,
            self.checkLabel,
            self.checkInstruction
        ]

    def getTokenInfo(self, value):
        for type in self.typeFunctions:
            verifiedType = type(value)
            if (verifiedType != None):
                return verifiedType

        return tokenInfo(TYPES.UNKNOWN, value)

    def checkComma(self, value):
        if len(value) == 1 and value[0] == ',':
            return tokenInfo(TYPES.COMMA, ',')
        return None

    def checkNumber(self, value):
        variant = 'dec'
        if len(value) > 2 and value[0:2] == '0x':
            variant = 'hex'

        digits = ''
        finalValue = -1

        if variant == 'dec':
            for character in value:
                if character in string.digits:
                    digits += character
                else:
                    return None
            finalValue = int(digits)

        elif variant == 'hex':
            for character in value[2:]:
                if character in string.hexdigits:
                    digits += character
                else:
                    return None
            finalValue = int(digits, 16)

        return tokenInfo(TYPES.INT, finalValue)

    def checkString(self, value):
        if len(value) < 2:
            return None
        if(value[0] in '"' and value[-1] == '"'):
            return tokenInfo(TYPES.STRING, value)
        return None

    def checkInstruction(self, value):
        index = 0
        for character in value:
            if index == 0 and character not in string.ascii_letters or \
            (index != 0 and character not in (string.digits + string.ascii_letters)):
                return None
            index += 1

        return tokenInfo(TYPES.INSTRUCTION, value.upper())

    def checkLabel(self, value):
        if len(value) < 2:
            return None
        if(value[0] is '.'):
            for character in value[1:]:
                if character not in string.ascii_letters:
                    break
            return tokenInfo(TYPES.LABEL, value)
        return None


class Processor:
    def __init__(self, initialParameters):
        self.parameters = initialParameters
        self.lines = []
        self.tokens = []
        self.dataBuffer = []
        self.labels = {}
        self.sections = {}
        self.currentAddress = 0

        self.readInputFile()
    
    def addMiscStructures(self):
        self.dataBuffer = self.fileFormat.addMiscStructures(self.sections, self.dataBuffer)

    def tokenize(self):
        self.lines.append('.section .EOF')
        for i in range(len(self.lines)):
            self.parse(i+1, self.lines[i])

    def readInputFile(self):
        for line in self.parameters.inputFile:
            self.lines.append(line)
        self.parameters.inputFile.close()

    def removeStartingWhitespaces(self, line, position, lineLength):
        while position < lineLength and line[position] in '\t \n':
            position += 1
        return position

    def getToken(self, lineNumber, line, position, lineLength):
        text = ''
        parametersDelimiters = '\t\n, '

        # if not at the end of the line check if next argument is not a comma
        if position < lineLength:
            if line[position] == ',':
                text = ','
                position += 1
            elif line[position] in '"\'':
                delimiter = line[position]
                isString = True
                # it's a string, spaces allowed
                parametersDelimiters = '\t\n,'
                text += '"'
                position += 1
            else:
                isString = False

        # if it's not a comma then process argument
        if text != ',':
            # ignore comments
            if position < lineLength and line[position] == '#':
                position = lineLength

            while position < lineLength and line[position] not in parametersDelimiters:
                text += line[position]
                position += 1

                if isString and line[position-1] == delimiter:
                    if (delimiter == '\''):
                        text = text[:-1] + '"'
                    break

        if text != '':
            token = Token(text, lineNumber)
            self.tokens.append(token)

        return position

    def parse(self, lineNumber, line):
        lineLength = len(line)
        if lineLength == 0:
            return False
        position = 0
        while position < lineLength:
            position = self.removeStartingWhitespaces(
                line, position, lineLength)
            position = self.getToken(lineNumber, line, position, lineLength)

    def process(self):
        supportedFormats = {
            'bin': BIN,
            'elf': ELF
        }
        self.fileFormat = supportedFormats[self.parameters.fileFormat](
            self.parameters)
        self.fileFormat.generateTemplate()

        self.currentAddress = self.fileFormat.getOrg()

        self.index = 0
        while self.index < len(self.tokens):
            self.assemble()

        # if file doesn't have .start label specified, set starting address to 0
        try:
            startingPoint = self.labels['.start']
        except KeyError:
            startingPoint = 0

        self.dataBuffer = self.fileFormat.addFormatData(
            self.dataBuffer, startingPoint)

    def write(self):
        if len(self.dataBuffer) == 0:
            raise AssemblerException('Empty write buffer!, nothing to write')
        print("\n\n\n\n")
        print(self.dataBuffer)
        print("\n\n\n\n")
        self.parameters.outputFile.write(bytes(self.dataBuffer))
        self.parameters.outputFile.close()

    def assembleLabel(self, token):
        if token.value == '.section':
            argument = self.tokens[self.index]
            self.sections[argument.value] = self.currentAddress
            print('New section: {0} on address {1}'.format(argument.value, self.currentAddress))
            self.index += 1
            return
        self.labels[token.value] = self.currentAddress
        print(token.value, self.currentAddress)
        return

    def assemble(self):
        token = self.tokens[self.index]
        if token.type != TYPES.INSTRUCTION and token.type != TYPES.LABEL:
            raise AssemblerException('Unexpected token of type {0}, value: {1} in line {2}'.
                format(token.type, token.value, token.lineNumber))

        self.index += 1
        usedArguments = 0

        if token.type == TYPES.LABEL:
            self.assembleLabel(token)
            return

        if token.value == 'DB':
            usedArguments += self.insertValue(1, usedArguments)
        elif token.value == 'DW':
            usedArguments += self.insertValue(2, usedArguments)
        elif token.value == 'DD':
            usedArguments += self.insertValue(4, usedArguments)
        elif token.value == 'DQ':
            usedArguments += self.insertValue(8, usedArguments)
        else:
            raise AssemblerException('unnown exception ' + str(token.value) +
                                     ' in line: ' + str(token.lineNumber))

        self.index += usedArguments

    def insertValue(self, length, offset, recursive=False):
        index = self.index + offset
        argument = self.tokens[index]

        if argument.type == TYPES.STRING:
            counter = 0
            for character in argument.value[1:-1]:
                counter += 1
                self.dataBuffer += bytearray(
                    ord(character).to_bytes(1, byteorder=self.parameters.endianess))
            if counter % length != 0:
                self.dataBuffer += bytearray(int(0).to_bytes(length - counter %
                                                             length, byteorder=self.parameters.endianess))
            self.currentAddress += counter + (length - counter) % length

        elif argument.type == TYPES.INT:
            self.dataBuffer += bytearray(argument.value.to_bytes(
                length, byteorder=self.parameters.endianess))
            self.currentAddress += length

        else:
            raise AssemblerException('Wrong argument type: ' + str(argument.type) +
                                     ', value: ' +
                                     str(argument.value) + ' in line: ' +
                                     str(argument.lineNumber))

        try:
            nextToken = self.tokens[self.index+offset + 1]
            # if next argument is comma then there is another argument waiting to be printed
            if nextToken.type == TYPES.COMMA:
                return self.insertValue(length, offset + 2, True)
        except IndexError:
            pass

        # necessary for correct index calculation
        if recursive:
            return offset + 1

        return 1
