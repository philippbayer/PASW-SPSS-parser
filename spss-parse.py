#!/usr/bin/python

# argparse for command-line options
import argparse, sys
import numpy as np
from neurolab.core import Train, Trainer, TrainStop
import neurolab as nl

class TrainLM(Train):
    ''' The training class using Levenberg-Marquardt and the neurolab-package'''
    def __init__(self, net, input, target, **kwargs):
        self.net = net
        self.input = input
        self.target = target
        self.kwargs = kwargs
        self.x = tool.np_get_ref(net)
        self.full_output = ()
    
    def fcn(self, x):
        self.x[:] = x
        output = net.sim(self.input)
        err = self.error(self.net, self.input, self.target, output)
        try:
            self.epochf(err, self.net)
        except TrainStop:
            pass
        return (self.target-output).flatten()
        
    def __call__(self, net, input, target):
        from scipy.optimize import leastsq
        #from scipy.optimize.minpack import error
        
        self.full_output = leastsq(func=self.fcn, x0=self.x.copy(), 
                                    maxfev=self.epochs)

class Measurement:
    ''' A measurement as predicted by PASW/SPSS
    dis_1 is the predicted group
    dis1_1, dis2_1.. are the probabilities for the group-prediction
    '''
    # class-variable, an array containing all measurements
    allMeasurements = []
    def __init__(self, dis_1, dis1_1, dis2_1, dis3_1, dis4_1, sample_id, list_of_snps):
        self.predicted_group = dis_1
        self.list_of_probabilities = [transformStrToInt(dis1_1),  transformStrToInt(dis2_1), transformStrToInt(dis3_1),  transformStrToInt(dis4_1)] 
        self.sample_id = sample_id
        self.list_of_snps = list_of_snps
        Measurement.allMeasurements.append(self)

    def getProbabilityGroup(self):
        return self.predicted_group

    def getHighestProbability(self):
        returnstuff = max(self.list_of_probabilities)
        if returnstuff == " ":
            return 0
        else:
            return float(returnstuff)

    def getAllMeasurements(self):
        return Measurement.allMeasurements

    def getSampleID(self):
        return self.sample_id

    def getAllSNPs(self):
        return self.list_of_snps

    def inspect(self):
        return [self.predicted_group, self.list_of_probabilities, self.sample_id, self.list_of_snps]

def transformStrToInt(string):
    ''' Transforms the way small numbers are presented in SPSS/PASW to the way Python wants them'''
    if type(string) == str and "E" in string:
        number = float(string[0:string.index("E")])
        exponent = int(string[string.index("E")+1:len(string)])
        return number*(10**exponent)
    else:
        return string

def getArguments():
    ''' get the command-line options, return the filename'''
    parser = argparse.ArgumentParser(description ="Parse SPSS/PASW tab-delimited output")
    parser.add_argument("filename", metavar="file", type=str, help="name of the SPSS/PASW output-file")
    parser.add_argument("-p",  type=float, default = 0, help="Cut-off probability - measurements with probability < prob will not be included")

    args = parser.parse_args()
    return args

def tryToOpenFile(toparsename):
    ''' try to open the file and return the object, print IOError else'''
    try:
            return open(toparsename, "r")
    except IOError:
            print("Error: can't seem to open or find the file.")
            sys.exit()
    except:
            print("Something weird went wrong")
            sys.exit()
            raise

def getFormatOfOutput(line):
    ''' takes a list of all lines in the file to be parsed, looks at the first line
    and returns the relevant fields '''
    line = line.replace("\n","").split("\t")
    fielddict = {}
    fielddict["startOfSNPList"] = 1
    fielddict["endOfSNPList"] = line.index("Skincolour") # THIS IS GOING TO BE A PROBLEM
    fielddict["dis_1"] = line.index("Dis_1")
    fielddict["dis1_1"] = line.index("Dis1_1")
    fielddict["dis2_1"] = line.index("Dis2_1")
    fielddict["dis3_1"] = line.index("Dis3_1")
    fielddict["dis4_1"] = line.index("Dis4_1")
    if "Dis5_1" in line:
            fielddict["dis5_1"] = line.index("Dis5_1")
    return fielddict

def parse_file(fields, linelist, cutoff):
    ''' Go through the entire file, create measurement-objects '''
    linecounter = 1
    list_of_measurements = []
    # look at all lines
    while linecounter < len(linelist):
            currentLine = linelist[linecounter].replace("\n", "").split("\t")
            sample_id = currentLine[0]
            if len(currentLine) != 1: # some lines only contain a \n, we don't need these
                    m = Measurement(currentLine[fields["dis_1"]], currentLine[fields["dis1_1"]], currentLine[fields["dis2_1"]],currentLine[fields["dis3_1"]], currentLine[fields["dis4_1"]], sample_id, currentLine[1:fields["endOfSNPList"]], )
                    # we also don't need measurements whose probability is lower than the user specified
                    # as this might lead to overfitting
                    if m.getHighestProbability() < cutoff:
                        print >> sys.stderr, "Measurement %s is not going to be included" %m.getSampleID()
                    else:
                        list_of_measurements.append(m)
            linecounter += 1
    return list_of_measurements

def clean_list(list_of_measurements):
    ''' go through the list of measurements, kick out elements with missing stuff '''
    # going over a copy of the list because else counters get confused by removing elements
    for m in list(list_of_measurements):
        if m.getProbabilityGroup() == " ":
            print >> sys.stderr, "Sample-ID %s is incomplete, removing" %m.getSampleID()
            list_of_measurements.remove(m)
        
    return list_of_measurements

def main():
    ''' The main-method - which calls all other methods'''
    # get the filename
    args = getArguments()
    toparsename = args.filename
    # get all lines of the file in one big list
    # should be replaced by "for line in file", .readlines() is quite memory-hungry
    linelist = tryToOpenFile(toparsename).readlines()
    fields = getFormatOfOutput(linelist[0])
    list_of_measurements = parse_file(fields, linelist, args.p)
    list_of_measurements = clean_list(list_of_measurements)
    trainlm = Trainer(TrainLM)
    # now go and create 1 ANN for each Measurement
    # create ANN with 2 inputs, 4 outputs, 2 layers
    net = nl.net.newff([[-1, 1],[1, 4]], [3,1])
    # set to use Levenberg-Marquardt
    net.trainf=trainlm
    # inp is a numpy-array containing all SNPS (-1: 1) reshaped to 2D
    inp = np.array()
    # tar contains the actual group (somewhere between 1 and 4)
    tar = np.array()
    for m in list_of_measurements:
        # now go and append each m to the inp-ndarray
        # current approach computationally expensive, makes more sense to initialize the
        # arrays beforehand with the right size and then go and replace 

        # inp = np.array(m.getAllSNPs()).reshape(len(m.getAllSNPs())/2,2)
        # tar = np.array([m.getProbabilityGroup(),m.getProbabilityGroup()]).reshape(1,2)


    # got everything, time to train the ANN
    err = net.train(inp, tar, epochs=150, show=10, goal=0.02)


main()
