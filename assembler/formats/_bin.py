from assembler.formats._template import fileFormatClass


class BIN(fileFormatClass):
    def __init__(self, parameters):
        fileFormatClass.__init__(self, parameters)
        if parameters.verbose:
            print('selected output file format: BIN')

    def generateTemplate(self):
        self.org = 0

    def addMiscStructures(self, sections, data):
        return data