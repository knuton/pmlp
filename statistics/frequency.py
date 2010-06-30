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
	
	def samples(self, sortFn = None):
		""" Returns a list of all samples.
		
		>>> newFreak = FrequencyDistribution(['a', 'b', 'b', 'c'])
		>>> newFreak.samples()
		['a', 'c', 'b']
		>>> newFreak.samples(lambda x,y: cmp(x,y))
		['a', 'b', 'c']
		"""
		samples = self._frequencies.keys()
		if sortFn:
			samples.sort(sortFn)
		return samples
	
	def table(self):
		""" Prints a table of the frequency distribution. """
		return '\n'.join([str(sample) + ' ' + str(self[sample]) for sample in self.samples()])
	
	def _getTop(self):
		""" Returns the top occuring sample. """
		if len(self._frequencies) == 0:
			return None
		return self.samples(lambda x,y: cmp(self._frequencies[y], self._frequencies[x]))[0]
	
	top = property(_getTop,
	doc = """ Returns the top occuring sample.
	
	>>> newFreak = FrequencyDistribution()
	>>> newFreak.top
	>>> newFreak = FrequencyDistribution(['a', 'b', 'b', 'c'])
	>>> newFreak.top
	'b'
	""")
	
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
	
	def __len__(self):
		""" Return number of seen sample types. 
		
		>>> newFreak = FrequencyDistribution(['a', 'b', 'b', 'c'])
		>>> len(newFreak)
		3
		"""
		return len(self._frequencies)
	
	def __iter__(self):
		""" Returns an iterator over the samples. """
		self.samples.__iter__()

class ConditionalFrequencyDistribution:
	""" Conditional frequency distribution for any objects. """
	
	def __init__(self, conditionSamplePairs = []):
		""" Create new conditional frequency distribution from sequence of
		sequence type objects, where the first item is the condition and the
		latter items are its samples.
		
		>>> newCFD = ConditionalFrequencyDistribution()
		"""
		self._conditions = collections.defaultdict(FrequencyDistribution)
		
		[self.seenOnCondition(pair[0], pair[1]) for pair in conditionSamplePairs if self._checkConditionSamplePair(pair)]
	
	def _checkConditionSamplePair(self, pair):
		""" Checks wether pair is indeed a pair and throws an exception if it isn't.
		
		>>> newCFD = ConditionalFrequencyDistribution()
		>>> newCFD._checkConditionSamplePair([])
		Traceback (most recent call last):
		ValueError: Condition-sample sequences need to have one condition and one sample (sequence).
		"""
		if len(pair) == 2:
			return True
		raise ValueError('Condition-sample sequences need to have one condition and one sample (sequence).')
	
	def expected(self, condition):
		""" Returns the most probable next value. 
		
		>>> newCFD = ConditionalFrequencyDistribution([('a', 'b'), ('a', 'b'), ('a', 'c')])
		>>> newCFD.expected('a')
		'b'
		"""
		return self[condition].top
	
	def seenOnCondition(self, condition, sample):
		""" Sees a sample for a certain condition, that is, for that condition's frequency distribution. 
		
		>>> newCFD = ConditionalFrequencyDistribution()
		>>> newCFD.seenOnCondition('a', 'b')
		>>> newCFD.conditions
		['a']
		>>> newCFD['a'].total
		1
		"""
		self[condition].seen(sample)
	
	def _getConditions(self):
		""" Returns the number of total sample tokens. """
		return self._conditions.keys()
    
	conditions = property(_getConditions,
	doc = """ Returns a list of all conditions.
    
	>>> newCFD = ConditionalFrequencyDistribution([('a', 'b'), ('b', 'c')])
	>>> newCFD.conditions
	['a', 'b']
	""")
	
	def _getTotal(self):
		""" Returns the number of total sample tokens. """
		return reduce(lambda x,y: x + y.total, self._conditions.values(), 0)
	
	total = property(_getTotal,
	doc = """ Returns the number of total sample tokens.
	
	>>> emptyCFD = ConditionalFrequencyDistribution()
	>>> emptyCFD.total
	0
	>>> newCFD = ConditionalFrequencyDistribution([['a', 'b'], ['b', 'c']])
	>>> newCFD.total
	2
	""")
	
	def __len__(self):
		""" Return number of seen conditions. 
		
		>>> newCFD = ConditionalFrequencyDistribution([['a', 'b'], ['b', 'c']])
		>>> len(newCFD)
		2
		"""
		return len(self._conditions)
	
	def __getitem__(self, condition):
		""" Returns the frequency distribution for the provided condition. 
		
		>>> newCFD = ConditionalFrequencyDistribution([('a', 'b'), ('b', 'c')])
		>>> newCFD['b'].samples()
		['c']
		"""
		return self._conditions[condition]

if __name__ == '__main__':
	import doctest
	doctest.testmod()