#!/usr/bin/python

# Argparse for command-line options
# Sys to access filesystem-functions
import argparse, sys
# Numpy for nparrays
import numpy as np
# Neurolab for ANN
from neurolab.core import Train, Trainer, TrainStop
import neurolab as nl

import pylab as plt

class TrainLM(Train):
    
    def __init__(self, net, input, target, **kwargs):
        self.net = net
        self.input = input
        self.target = target
        self.kwargs = kwargs
        self.x = nl.tool.np_get_ref(net)
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
        
        self.full_output = leastsq(func=self.fcn, x0=self.x.copy(), maxfev = self.epochs)

class Measurement:
    ''' A measurement as predicted by PASW/SPSS
    dis_1 is the predicted group
    dis1_1, dis2_1.. are the probabilities for the group-prediction
    '''
    # class-variable, an array containing all measurements
    def __init__(self, dis_1, list_of_probabilities, sample_id, list_of_snps):
        self.predicted_group = float(dis_1)
        self.list_of_probabilities = transformStrToInt(list_of_probabilities)
        self.sample_id = sample_id
        self.list_of_snps = list_of_snps

    def getProbabilityGroup(self):
        return self.predicted_group

    def getHighestProbability(self):
        returnstuff = max(self.list_of_probabilities)
        if returnstuff == " " or returnstuff == "":
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

def makeFloat(a_list):
    ''' iterates over all elements of a list, returns copy of list with all elements as floats '''
    ''' warning: breaks with elements like "005E15" '''
    output_list = []
    for element in a_list:
        output_list.append(float(element))
    return output_list

def transformStrToInt(string_list):
    ''' Transforms the way small numbers are presented in SPSS/PASW to the way Python wants them'''
    return_list = []
    for string in string_list:
        # when there's an E in the string, it's a tiny number
        if type(string) == str and "E" in string:
            # example: 16E005 to 16*10^5
            number = float(string[0:string.index("E")])
            exponent = int(string[string.index("E")+1:len(string)])
            return_list.append( number*(10**exponent))
        else:
            return_list.append( float(string))
    return return_list

def getArguments():
    ''' get the command-line options, return the filenames and probability (optional)'''
    parser = argparse.ArgumentParser(description ="Parse SPSS/PASW tab-delimited output")
    parser.add_argument("trainfile", metavar="trainfile", type=str, help="Name of the SPSS/PASW output-file")
    parser.add_argument("-p",  type=float, default = 0, help="Cut-off probability - measurements with probability < p won't be included")
    parser.add_argument("testfile", metavar="testfile", type=str, help="Name of the file with SNPs in unknown groups, same format as SPSS/PASW output-file")

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
            raise # always fall back to this exception

def getFormatOfOutput(line):
    ''' takes a list of all lines in the file to be parsed, looks at the first line
    and returns the relevant fields '''
    line = line.replace("\n","").replace("\r","").split("\t")
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
            currentLine = linelist[linecounter].replace("\n", "").replace("\r","").split("\t")
            sample_id = currentLine[0]
            if len(currentLine) != 1: # some lines only contain a \n, we don't need these
                    list_of_probabilities = [currentLine[fields["dis1_1"]], currentLine[fields["dis2_1"]], 
                                            currentLine[fields["dis3_1"]], currentLine[fields["dis4_1"]]]
                    list_of_snps = currentLine[1:fields["endOfSNPList"]]
                    # we don't need measurements with empty elements
                    if currentLine[fields["dis_1"]] == " " or " " in list_of_probabilities or " " in list_of_snps:
                        print >> sys.stderr, "Measurement %s is incomplete, removing" %sample_id
                    # we also don't need measurements whose probability is lower than the user specified
                    elif max(currentLine[fields["dis1_1"]]) < cutoff:
                        print >> sys.stderr, "Measurement %s has too small probability, not going to be included" %sample_id
                    else:
                        list_of_snps = makeFloat(list_of_snps)
                        m = Measurement(currentLine[fields["dis_1"]], list_of_probabilities, sample_id,  list_of_snps )
                        # everything fine, append to list
                        list_of_measurements.append(m)
            linecounter += 1
    return list_of_measurements

def transform_output_list(target):
    """ output must be in the same range as input, e.g. -1 to 1 - but output is between 1 and 4
    therefore: 1 = -1, 2 = -0.33, 3 = 0.33, 4  = 1 """

    new_list  = []
    for element in target:
        if int(element[0]) == 4:
            new_list.append([1])
        elif int(element[0]) == 3:
            new_list.append([0.33])
        elif int(element[0]) == 2:
            new_list.append([-0.33])
        else:
            new_list.append([-1])
    return new_list

print >>sys.stdout, "Starting..."
# get the filename
args = getArguments()
toparsename = args.trainfile
# get all lines of the file in one big list
# should be replaced by "for line in file", .readlines() is quite memory-hungry
linelist = tryToOpenFile(toparsename).readlines()
fields = getFormatOfOutput(linelist[0])
list_of_measurements = parse_file(fields, linelist, args.p)

# how many SNPs do we have?
# all measurements should have the same amount
number_of_measurements = len(list_of_measurements[0].getAllSNPs())

# inp is a list containing all SNPS 
inp = []
# tar contains the actual group for each measurement
tar = []
# now go and append each m to the inp-array
for m in list_of_measurements:
    # current approach computationally expensive, makes more sense to initialize the
    # arrays beforehand with the right size and then fill up
    inp.append(m.getAllSNPs())
    tar.append([m.getProbabilityGroup()])

# make numpy-arrays out of them (for 2D-shape)
#inp = 121*inp
tar =  transform_output_list(tar)
#tar = 121*tar

print >>sys.stdout, "Got all measurements, now creating ANN."
# create ANN - possible inputs range from -1 to 1

# list containing all possible states for all SNPs used in this study
# have to use [1,1] for states that can only be 1 because of dimensionality
possible_states = 43*[[-1,1]] + 3*[[1,1]] + 4*[[-1,1]] + 1*[[1,1]] + 6*[[-1,1]] + 1*[[1,1]]
possible_states = 43*[[-1,4]] + 3*[[1,1]] + 4*[[-1,1]] + 1*[[1,1]] + 6*[[-1,1]] + 1*[[1,1]]
possible_states = np.array(possible_states)
# 58 SNPs (ranging from -1 to 1 OR only 1), 1 layer, 1 possible output
net = nl.net.newff(possible_states,  [2 , 1])
#print("net.co %s" %net.co)
#print("net.ci %s" %net.ci)
# set to use Levenberg-Marquardt
net.trainf= Trainer(TrainLM)
# got everything, time to train the ANN
err = net.train(inp, tar, epochs=3000, show=1000)
print(err)
# training done! time to have a look at the testing file
print >>sys.stdout, "Training is done, now testing."
toparsename = args.testfile
# get all measurements
#linelist = tryToOpenFile(toparsename).readlines()
# now simulate!
out = net.sim(inp)
counter = 0

for element in out:
    print "Input: %s Simulated output: %s " %(inp[counter],element)
    counter += 1

#print(len(err))
#print(len(range(1,len(err)+1)))
"""
plt.plot( range(1,len(err)+1), err) 
plt.xlabel( "Training steps" )
plt.ylabel( "Error probability")
plt.title( "Training of AND function")
plt.show()
"""
print >>sys.stdout, "Done! Have a nice day."

