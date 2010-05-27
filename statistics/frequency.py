import collections

class FrequencyDistribution:
	""" Frequency distribution for any objects. """
	
	def __init__(self, samples = []):
		""" Creates an empty frequency distribution or a filled one, when it is passed an iterable object.
		"""
		# dict for frequencies
		self._frequencies = collections.defaultdict(int)
		# Total number of seen objects
		self._total_tokens = 0
		
		[self.seen(sample) for sample in samples]
	
	def seen(self, sample):
		""" Increase number of seen sample tokens for the provided type. 
		
		Also increases the number of total tokens.
		
		>>> newFreak = FrequencyDistribution()
		>>> len(newFreak)
		0
		>>> newFreak.total
		0
		>>> newFreak.seen('a')
		>>> len(newFreak)
		1
		>>> newFreak.total
		1
		>>> newFreak.seen('a')
		>>> len(newFreak)
		1
		>>> newFreak.total
		2
		"""
		self._frequencies[sample] += 1
		self._total_tokens += 1
	
	def relativeFrequency(self, sample):
		""" Returns the proportion this sample type takes among all sample types.
		
		>>> newFreak = FrequencyDistribution(['a', 'b', 'b', 'c'])
		>>> newFreak.relativeFrequency('a')
		0.25
		>>> newFreak.relativeFrequency('b')
		0.5
		"""
		return float(self[sample])/self.total
		
	def __len__(self):
		""" Return number of seen sample types. 
		
		>>> newFreak = FrequencyDistribution(['a', 'b', 'b', 'c'])
		>>> len(newFreak)
		3
		"""
		return len(self._frequencies)
		
	def _getTotal(self):
		""" Returns the number of total sample tokens. """
		return self._total_tokens
	
	total = property(_getTotal,
	doc = """ Returns the number of total sample tokens.
	
	>>> newFreak = FrequencyDistribution(['a', 'b', 'b', 'c'])
	>>> newFreak.total
	4
	""")
		
	def __getitem__(self, sample):
		""" Returns the number of counted samples equal to the provided sample.
		
		>>> FrequencyDistribution()['not_present']
		0
		"""
		return self._frequencies[sample]

if __name__ == '__main__':
	import doctest
	doctest.testmod()