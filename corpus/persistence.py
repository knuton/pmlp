# --- Add parent dir to paths for doctest compatiable intra-package imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# --- End of parent loading
import cPickle as pickle
from tools import logger

def dump(dataType, data, *corpusID):
	""" Dumps an analysis of a certain corpus to `dumps/<corpusID>/<dataType>.p`.
	
	>>> data = "test"
	>>> dump('melody', data, 'nonsense')
	True
	
	Test to see which music21 objects cause trouble.
	>>> from music21 import note
	>>> noteData = note.Note('A4')
	>>> dump('melody', noteData, 'weakref')
	True
	>>> restData = note.Rest('half')
	>>> dump('melody', restData, 'weakref')
	True
	
	This (Note and Rest) seems to have worked. Next.
	>>> from music21 import stream
	>>> measureData = stream.Measure()
	
	It works for empty streams.
	>>> dump('melody', measureData, 'weakref')
	True
	
	But not for streams with children.
	# >>> measureData.append(noteData)
	# >>> dump('melody', measureData, 'weakref')
	# True
	
	Boom. But we don't use streams in the Note ngrams. So what's the dealio?
	# >>> noteData.quarterLength = 3
	# >>> dump('melody', noteData, 'weakref')
	# True
	
	OK, got it. Durations seems to be saved as weakrefs, too.
	Avoided the issue by creating "normalized" note objects.
	<http://docs.python.org/library/pickle.html#pickling-and-unpickling-extension-types>
	God save the Queen, pickling is already supported in music21: <http://code.google.com/p/music21/source/browse/trunk/music21/converter.py>
	"""
	try:
		with open(_pathForDump(corpusID, dataType, True), 'w') as f:
			try:
				pickle.dump(data, f)
				return True
			except pickle.PicklingError:
				logger.log("%s can not be pickled." % (data))
				return False
	except IOError:
		logger.log("Couldn't open file for writing.")
		return False

def load(dataType, *corpusID):
	""" Loads an analysis for corpus and data type.
	
	>>> dump('melody', 'test', 'nonsense')
	True
	>>> load('melody', 'nonsense')
	'test'
	>>> load('melody', 'not_present') == None
	True
	"""
	corpusName = os.path.join(*corpusID)
	try:
		with open(_pathForDump(corpusID, dataType), 'r') as f:
			try:
				return pickle.load(f)
			except pickle.UnpicklingError:
				logger.log("%s's %s can not be unpickled." % ('/'.join(corpusName), dataType))
				return None
			except EOFError:
				# Previous write of dump failed.
				logger.log("Removing corrupted dump for %s' %s." % ('/'.join(corpusName), dataType))
				os.remove(_pathForDump(corpusID, dataType))
				return None
	except IOError:
		logger.log("Couldn't open file for reading.")
		return None

def _pathForDump(corpusID, dataType, mkdir = False):
	""" Creates a path for corpus name and data type in the dumps folder. """
	dumpsPath = os.path.join(os.path.dirname(__file__), 'dumps')
	if not os.path.isdir(dumpsPath):
		os.mkdir(dumpsPath)
	for name in corpusID:
		dumpsPath = os.path.join(dumpsPath, name)
		if mkdir and not os.path.isdir(dumpsPath):
			os.mkdir(dumpsPath)
	return os.path.join(dumpsPath, '%s.p' % (dataType,))
	

if __name__ == "__main__":
	import doctest
	doctest.testmod()
