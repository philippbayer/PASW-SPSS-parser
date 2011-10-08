#!/usr/bin/python3

# argparse for command-line options
import argparse, sys

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
