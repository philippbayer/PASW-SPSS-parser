#!/usr/bin/python3

# argparse for command-line options
import argparse, sys

class Measurement:
	''' A measurement as predicted by PASW
			dis_1 is the predicted group
			dis1_1, dis2_1.. are the probabilities for the group-prediction'''
	allMeasurements = []
	def __init__(self, dis_1, dis1_1, dis2_1, dis3_1, dis4_1, sample_id, list_of_snps, list_of_snp_names):
		self.dis_1 = dis_1
		self.dis1_1 = dis1_1
		self.dis2_1 = dis2_1
		self.dis3_1 = dis3_1
		self.dis4_1 = dis4_1
		self.sample_id = sample_id
		self.list_of_snps = list_of_snps
		allMeasurements.append(self)
	
	def getProbabilityGroup(self):
		return self.dis_1

	def getHighestProbability(self):
		return max(self.dis1_1, self.dis2_1, self.dis3_1, self.dis4_1)

	def getAllMeasurements(self):
		return allMeasurements
		
def getFileName():
	''' get the command-line options, return the filename'''
	parser = argparse.ArgumentParser(description ="Parse SPSS/PASW tab-delimited output")
	parser.add_argument("filename", metavar="file", type=str, help="name of the SPSS/PASW output-file")

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

def getFormatOfOutput(line):
	''' takes a list of all lines in the file to be parsed, looks at the first line
	and returns the relevant fields '''
	line = line.split("\t")
	fielddict = {}
	fielddict["startOfSNPList"] = 1
	fielddict["endOfSNPList"] = line.index("Skincolour")
	fielddict["dis_1"] = line.index("Dis_1")
	fielddict["dis1_1"] = line.index("Dis1_1")
	fielddict["dis2_1"] = line.index("Dis2_1")
	fielddict["dis3_1"] = line.index("Dis3_1")
	fielddict["dis4_1"] = line.index("Dis4_1\n")
	print(fielddict)

def main():
  # get the filename
	toparsename = getFileName()
  # get all lines of the file in one big list
	linelist = tryToOpenFile(toparsename).readlines()
	fields = getFormatOfOutput(linelist[0])

main()
