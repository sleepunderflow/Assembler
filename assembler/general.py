from enum import Enum
from collections import namedtuple
import string


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


class Token:
    def __init__(self, value, lineNumber):
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
        for character in value:
            if character not in string.ascii_uppercase:
                return None

        return tokenInfo(TYPES.INSTRUCTION, value)


class Processor:
    def __init__(self, initialParameters):
        self.parameters = initialParameters
        self.lines = []
        self.tokens = []
        self.dataBuffer = []

        self.readInputFile()

    def tokenize(self):
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
        self.index = 0
        while self.index < len(self.tokens):
            self.assemble()

    def write(self):
        if len(self.dataBuffer) == 0:
            raise AssemblerException('Empty write buffer!, nothing to write')
        for data in self.dataBuffer:
            self.parameters.outputFile.write(data)
        self.parameters.outputFile.close()

    def assemble(self):
        index = self.index
        token = self.tokens[index]
        if token.type != TYPES.INSTRUCTION:
            raise AssemblerException('Unexpected token of type ' + str(token.type) +
                                     ', value: ' +
                                     str(token.value) + ' in line: ' +
                                     str(token.lineNumber))

        self.index += 1

        usedArguments = 0

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
                self.dataBuffer.append(
                    ord(character).to_bytes(1, byteorder=self.parameters.endianess))
            if counter % length != 0:
                self.dataBuffer.append(
                    int(0).to_bytes(length - counter % length, byteorder=self.parameters.endianess))

        elif argument.type == TYPES.INT:
            self.dataBuffer.append(argument.value.to_bytes(
                length, byteorder=self.parameters.endianess))

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
