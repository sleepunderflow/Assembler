#!/usr/bin/python3
import sys
from assembler import Assembler


def displayHelp():
    print('Correct usage:\n' +
          sys.argv[0] + ' [OPTIONS..]\n\n' +
          'OPTIONS:\n' +
          '\t-i fileName     specify the input file\n' +
          '\t-o fileName     specify the output file\n' +
          '\t-e little/big   specify endianess of the output\n' +
          '\t-h, --help      show this help message and exit\n' +
          '\t-v, --verbose   increase the number of debugging info\n' +
          '\t-f fileType     specify output file type\n' +
          '\n\n' +
          'File Types (to be used with -f)\n' +
          '\tbin             Just compile, no file format\n' +
          '\telf             Make it an ELF64 executable'
          )
    exit(0)


class ParametersError(Exception):
    pass


class processedParameters:
    def __init__(self):
        self.inputFile = sys.stdin
        self.outputFile = sys.stdout
        self.verbose = False
        self.endianess = 'little'
        self.fileFormat = 'bin'


class InitialParameters:

    def __init__(self, cliParameters):
        # dictionary in format nameOfParameter:functionToCallWithAdditionalArgument
        self.extendedParameters = {
            '-i': self.setInputFile,
            '-o': self.setOutputFile,
            '-e': self.setEndianess,
            '-f': self.setFileFormat
        }

        self.standaloneParameters = {
            '-h': displayHelp,
            '--help': displayHelp,
            '-v': self.setVerbose,
            '--verbose': self.setVerbose
        }

        self.processName = cliParameters[0]
        self.parameters = processedParameters()

        self.awaitingArgument = None
        for parameter in cliParameters[1:]:
            self.processParameter(parameter)
        # Check if anything still requires any additional arguments
        if self.awaitingArgument is not None:
            raise ParametersError(
                'Expected additional argument after: ' + self.awaitingArgument[0])

    def processParameter(self, parameter):
        if self.awaitingArgument is not None:
            self.fillArgument(parameter)
            return True
        if parameter not in self.extendedParameters:
            if parameter not in self.standaloneParameters:
                raise ParametersError(
                    parameter + ' is not an allowed parameter to the assembler')
            else:
                self.setStandaloneParameter(parameter)
                return True
        self.initializeExtendedParameter(parameter)
        return True

    def fillArgument(self, parameter):
        self.awaitingArgument(parameter)
        self.awaitingArgument = None
        return True

    def initializeExtendedParameter(self, parameter):
        # set the awaitingArgument to a function reprezenting the expected paramter
        self.awaitingArgument = self.extendedParameters[parameter]

    def setStandaloneParameter(self, parameter):
        if parameter not in self.standaloneParameters:
            raise ParametersError('Unknown parameter: ' + parameter)
        # call the function being assigned to the parameter in the dictionary
        self.standaloneParameters[parameter]()
        return True

    def setInputFile(self, parameter):
        self.parameters.inputFile = open(parameter, 'r')
        return True

    def setEndianess(self, parameter):
        self.parameters.endianess = parameter
        return True

    def setOutputFile(self, parameter):
        self.parameters.outputFile = open(parameter, 'wb')
        return True

    def setVerbose(self):
        self.parameters.verbose = True
        return True

    def setFileFormat(self, parameter):
        allowedParamters = ['bin', 'elf']
        if not parameter in allowedParamters:
            raise ParametersError(parameter + 'is not an accepted file format')
        self.parameters.fileFormat = parameter


def main():
    initialParameters = InitialParameters(sys.argv)

    processor = Assembler.setup(initialParameters.parameters)
    processor.process()
    processor.addMiscStructures()
    processor.write()


if __name__ == "__main__":
    main()

