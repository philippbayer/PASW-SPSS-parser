#!/usr/bin/python3

# argparse for command-line options
import argparse, sys

class Measurement:
	''' A measurement as predicted by PASW
			dis_1 is the predicted group
			dis1_1, dis2_1.. are the probabilities for the group-prediction'''
	def __init__(self, dis_1, dis1_1, dis2_1, dis3_1, dis4_1, sample_id):
		self.dis_1 = dis_1
		self.dis1_1 = dis1_1
		self.dis2_1 = dis2_1
		self.dis3_1 = dis3_1
		self.dis4_1 = dis4_1
		self.sample_id = sample_id
	
	def getProbabilityGroup(self):
		return self.dis_1

	def getHighestProbability(self):
		return max(self.dis1_1, self.dis2_1, self.dis3_1, self.dis4_1)
		
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

def main():
	toparsename = getFileName()
	for line in tryToOpenFile(toparsename):
		print(line)


main()
