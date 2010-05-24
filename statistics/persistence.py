import os
import pickle

def dump(dataType, corpusName, data):
	""" Dumps a melody analysis of a certain corpus to `dumps/<corpusName>_<dataType>.p`.
	
	>>> data = "test"
	>>> dump('melody', 'nonsense', data)
	True
	"""
	try:
		with open(_pathForDump(corpusName, dataType), 'w') as f:
			try:
				pickle.dump(data, f)
				return True
			except pickle.PicklingError:
				print "%s can not be pickled." % (data) # TODO logger
				return False
	except IOError:
		# TODO logger.log("Couldn't open file for writing.")
		return False

def load(dataType, corpusName):
	""" Loads a melody analysis for corpus.
	
	>>> dump('melody', 'nonsense', 'test')
	True
	>>> load('melody', 'nonsense')
	'test'
	>>> load('melody', 'not_present') == None
	True
	"""
	try:
		with open(_pathForDump(corpusName, dataType), 'r') as f:
			try:
				return pickle.load(f)
			except pickle.UnpicklingError:
				print "%s's %s can not be unpickled." % (corpusName, dataType) # TODO logger
				return None
			except EOFError:
				# Previous write of dump failed.
				return None
	except IOError:
		# TODO logger.log("Couldn't open file for reading.")
		return None

def _pathForDump(corpusName, dataType):
	return '%s/dumps/%s_%s.p' % (os.path.dirname(__file__), corpusName, dataType)
	

if __name__ == "__main__":
	import doctest
	doctest.testmod()
