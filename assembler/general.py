def setup(initialParameters):
    processor = Processor(initialParameters)
    processor.tokenize()
    for token in processor.tokens:
        token.print()


class Token:
    def __init__(self, type, value, lineNumber):
        self.type = type
        self.value = value
        self.lineNumber = lineNumber

    def print(self):
        print(self.type, self.value, self.lineNumber)


class Processor:
    def __init__(self, initialParameters):
        self.parameters = initialParameters
        self.lines = []
        self.tokens = []

        self.readInputFile()

    def tokenize(self):
        for i in range(len(self.lines)):
            self.parse(i, self.lines[i])

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
        while position < lineLength and line[position] not in '\t \n':
            text += line[position]
            position += 1
        if text != '':
            token = Token('?', text, lineNumber)
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
