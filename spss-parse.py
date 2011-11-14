#!/usr/bin/python

# argparse for command-line options
import argparse, sys

class Measurement:
    ''' A measurement as predicted by PASW
    dis_1 is the predicted group
    dis1_1, dis2_1.. are the probabilities for the group-prediction
    '''
    # class-variable, an array containing all measurements
    allMeasurements = []
    def __init__(self, dis_1, dis1_1, dis2_1, dis3_1, dis4_1, sample_id, list_of_snps):
        self.predicted_group = dis_1
        self.list_of_probabilities = [dis1_1,  dis2_1,  dis3_1,  dis4_1] 
        self.sample_id = sample_id
        self.list_of_snps = list_of_snps
        Measurement.allMeasurements.append(self)

    def getProbabilityGroup(self):
        return self.predicted_group

    def getHighestProbability(self):
        return max(self.dis1_1, self.dis2_1, self.dis3_1, self.dis4_1)

    def getAllMeasurements():
        return Measurement.allMeasurements

    def inspect(self):
        return [self.predicted_group, self.list_of_probabilities, self.sample_id, self.list_of_snps]

def getFileName():
    ''' get the command-line options, return the filename'''
    parser = argparse.ArgumentParser(description ="Parse SPSS/PASW tab-delimited output")
    parser.add_argument("filename", metavar="file", type=str, help="name of the SPSS/PASW output-file")
    parser.add_argument("--p", metavar="probability", type=int, default = 0, help="Cut-off probability - measurements with probability < prob will not be included")

    args = parser.parse_args()
    toparsename = args.filename
    return toparsename

def tryToOpenFile(toparsename):
    ''' try to open the file and return the object, print IOError else'''
    try:
            return open(toparsename, "r")
    except IOError:
            print("Error: can't seem to open or find the file.")
            sys.exit()
    except:
            print("Something went wrong, dunno lol")
            sys.exit()
            raise

def getFormatOfOutput(line):
    ''' takes a list of all lines in the file to be parsed, looks at the first line
    and returns the relevant fields '''
    line = line.replace("\n","").split("\t")
    fielddict = {}
    fielddict["startOfSNPList"] = 1
    fielddict["endOfSNPList"] = line.index("Skincolour")
    fielddict["dis_1"] = line.index("Dis_1")
    fielddict["dis1_1"] = line.index("Dis1_1")
    fielddict["dis2_1"] = line.index("Dis2_1")
    fielddict["dis3_1"] = line.index("Dis3_1")
    fielddict["dis4_1"] = line.index("Dis4_1")
    if "Dis5_1" in line:
            fielddict["dis5_1"] = line.index("Dis5_1")
    return fielddict

def parse_file(fields, linelist, list_of_measurements):
    ''' Go through the entire file, create measurement-objects '''
    linecounter = 1
    # look at all lines
    while linecounter < len(linelist):
            currentLine = linelist[linecounter].replace("\n", "").split("\t")
            sample_id = currentLine[0]
            if len(currentLine) != 1: # some lines only contain a \n
                    m = Measurement(currentLine[fields["dis_1"]], currentLine[fields["dis1_1"]], currentLine[fields["dis2_1"]],currentLine[fields["dis3_1"]], currentLine[fields["dis4_1"]], sample_id, currentLine[1:fields["endOfSNPList"]], )
                    list_of_measurements.append(m)
            linecounter += 1
    return list_of_measurements

def clean_list(list_of_measurements):
    for element in list_of_measurements:
        print(element.inspect())
    return list_of_measurements

def main():
    # get the filename
    toparsename = getFileName()
    # get all lines of the file in one big list
    # should be replaced by "for line in file", .readlines() is quite memory-hungry
    linelist = tryToOpenFile(toparsename).readlines()
    fields = getFormatOfOutput(linelist[0])
    list_of_measurements = []
    parse_file(fields, linelist, list_of_measurements)
    list_of_measurements = clean_list(list_of_measurements)


main()
