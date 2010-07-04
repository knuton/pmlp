class StateError(Exception):
	""" Notifies about an object method being called in the wrong state. """
	
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return str(self.value)

class Trainer:
	""" Oversees the training on a collection of MusicXML files. """
	
	def __init__(self, collection = []):
		""" Creates the trainer. """
		self._successful = False
	
	def run(self):
		""" Starts the training. """
		self._successful = True
		return True
	
	def _getResults(self):
		""" Return the results of the training run. """
		if not self._successful:
			raise StateError("no results available yet")
	
	results = property(_getResults,
	doc = """ Return the results obtained by training or loaded from dump.
	
	Throws StateError if no results have been computed yet.
	
	>>> coach = Trainer()
	>>> coach.results
	Traceback (most recent call last):
		...
	StateError: no results available yet
	>>> coach.run()
	True
	>>> coach.results
	""")

if __name__ == '__main__':
	import doctest
	doctest.testmod()
            
    