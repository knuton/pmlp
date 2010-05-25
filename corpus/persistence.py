import os
import pickle

def dump(dataType, corpusName, data):
	""" Dumps an analysis of a certain corpus to `dumps/<corpusName>_<dataType>.p`.
	
	>>> data = "test"
	>>> dump('melody', 'nonsense', data)
	True
	
	Test to see which music21 objects cause trouble.
	>>> from music21 import note
	>>> noteData = note.Note('A4')
	>>> dump('melody', 'weakref', noteData)
	True
	>>> restData = note.Rest('half')
	>>> dump('melody', 'weakref', restData)
	True
	
	This (Note and Rest) seems to have worked. Next.
	>>> from music21 import stream
	>>> measureData = stream.Measure()
	
	It works for empty streams.
	>>> dump('melody', 'weakref', measureData)
	True
	
	But not for streams with children.
	>>> measureData.append(noteData)
	>>> dump('melody', 'weakref', measureData)
	True
	
	Boom. But we don't use streams in the Note ngrams. So what's the dealio?
	>>> noteData.quarterLength = 3
	>>> dump('melody', 'weakref', noteData)
	True
	
	OK, got it. Durations seems to be saved as weakrefs, too.
	Let us fix this by implementing obj.__reduce__(). Later.
	<http://docs.python.org/library/pickle.html#pickling-and-unpickling-extension-types>
	God save the Queen, pickling is already supported in music21: <http://code.google.com/p/music21/source/browse/trunk/music21/converter.py>
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
	""" Loads an analysis for corpus and data type.
	
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
	""" Creates a path for corpus name and data type in the dumps folder. """
	return os.path.join(os.path.dirname(__file__), 'dumps', '%s_%s.p' % (corpusName, dataType))
	

if __name__ == "__main__":
	import doctest
	doctest.testmod()
