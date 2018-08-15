#!/usr/bin/python3
import sys

def displayHelp():
  print('Correct usage:\n' + sys.argv[0] + ' fileToOpen')
  exit(0)

class ParametersError(Exception):
  pass

class InitialParameters:
     
  def __init__(self, parameters):
    # dictionary in format nameOfParameter:typeOfAdditionalParameterRequired
    self.extendedParameters = {
      '-i' : self.setInputFile,
      '-o' : self.setOutputFile
    }

    self.standaloneParameters = {
      '--quiet' : self.setQuiet,
      '-v' : self.setVerbose,
      '--verbose' : self.setVerbose,
      '-h' : self.help,
      '--help' : self.help
    }

    self.processNameame = parameters[0]
    self.parameters = {
      'inputFile' : sys.stdin,
      'outputFile' : sys.stdout,
      'help' : False,
      'quiet' : False,
      'verbose' : False
    }
    
    self.additionalParameterPending = None
    for parameter in parameters[1:]:
      self.processParameter(parameter)
    if self.additionalParameterPending is not None:
      raise ParameterException('Expected additional parameter after: ' + additionalParameterPending[0])

  def processParameter(self, parameter):
    if self.additionalParameterPending is not None:
      self.fillParameter(parameter)
      return True
    if parameter not in self.extendedParameters:
      if parameter not in self.standaloneParameters:
        raise ParametersError( parameter + ' is not an allowed parameter to the assembler' )
      else:
        self.setStandaloneParameter(parameter)
        return True  
    self.setupForParameter(parameter)
    return True
    
  def fillParameter(self, parameter):
    self.additionalParameterPending(parameter)
    self.additionalParameterPending = None
    return True

  def setupForParameter(self, parameter):
    self.additionalParameterPending = self.extendedParameters[parameter]

  def setStandaloneParameter(self, parameter):
    if self.standaloneParameters[parameter] is None:
      raise ParameterException('Parameter ' + parameter + ' not allowed')
    self.standaloneParameters[parameter]()
    return True

  def setInputFile(self, parameter):
    self.parameters['inputFile'] = open(parameter, 'r')
    return True

  def setOutputFile(self, parameter):
    self.parameters['outputFile'] = open(parameter, 'w')
    return True

  def setQuiet(self):
    self.parameters['quiet'] = True

  def setVerbose(self):
    self.parameters['verbose'] = True

  def help(self):
    self.parameters['help'] = True

  def printParameters(self):
    print(self.parameters)
    
initialParameters = InitialParameters(sys.argv)
initialParameters.printParameters()
