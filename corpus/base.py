import os

import music21.converter

def getCollection(name):
	""" Look in collections folder for subfolder with provided name and return paths to contained XML files.
	
	>>> len(getCollection('beatles')) >= 11
	True
	"""
	dirName = os.path.join(os.path.dirname(__file__), 'collections', name)
	dirListing = [os.path.join(dirName, dirContent) for dirContent in os.listdir(dirName)]
	
	scoreFiles = []
	
	for fileName in dirListing:
		if fileName.endswith('xml'):
			scoreFiles.append(fileName)
	
	return scoreFiles

def parseWork(workName):
	return music21.converter.parse(workName)

if __name__ == '__main__':
	import doctest
	doctest.testmod()