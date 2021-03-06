import collections
import copy
import random

class FrequencyDistribution:
	""" Frequency distribution for any objects. """
	
	def __init__(self, samples = []):
		""" Creates an empty frequency distribution or a filled one, when it is passed an iterable object.
		"""
		# dict for frequencies
		self._frequencies = collections.defaultdict(int)
		self._sampleHeap = []
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
		# If the frequency is 1, the sample hadn't been seen
		if self._frequencies[sample] == 1:
			# Add it to the heap
			self._heappush(sample)
		else:
			self._siftdown(0, self._sampleHeap.index(sample))
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
		['b', 'a', 'c']
		>>> newFreak.samples(lambda x,y: cmp(x,y))
		['a', 'b', 'c']
		"""
		samples = self._sampleHeap
		if sortFn:
			samples = list(samples)
			samples.sort(sortFn)
		return samples
	
	def table(self):
		""" Prints a table of the frequency distribution. """
		return '\n'.join([str(sample) + ' ' + str(self[sample]) for sample in self.samples()])
	
	def _getTop(self):
		""" Returns the top occuring sample. """
		if len(self._sampleHeap) == 0:
			return None
		return self._sampleHeap[0]
	
	top = property(_getTop,
	doc = """ Returns the top occuring sample.
	
	>>> newFreak = FrequencyDistribution()
	>>> newFreak.top
	>>> newFreak = FrequencyDistribution(['a', 'b', 'b', 'c'])
	>>> newFreak.top
	'b'
	""")
	
	def _getFuzztop(self):
		""" Returns one of the top 5 occuring samples with weighted probabilites. """
		if len(self._sampleHeap) == 0:
			return None
		weights = [1.0, 0.8, 0.6, 0.4, 0.2]
		fuzztop = None
		fuzzfreq = -1
		for i in range(0, len(self._sampleHeap[:5])):
			sample = self._sampleHeap[i]
			weightfreq = self.relativeFrequency(sample) * random.uniform(0.0, weights[i])
			if weightfreq > fuzzfreq:
				fuzztop = sample
				fuzzfreq = weightfreq
		return fuzztop

	fuzztop = property(_getFuzztop,
	doc = """ Returns the top occuring sample.

	>>> newFreak = FrequencyDistribution()
	>>> newFreak.fuzztop
	>>> newFreak = FrequencyDistribution(['a', 'b', 'b', 'c', 'd', 'e', 'f'])
	>>> newFreak.fuzztop in ['a', 'b', 'c', 'd', 'e']
	True
	>>> newFreak = FrequencyDistribution(['a', 'a', 'a'])
	>>> newFreak.fuzztop
	'a'
	""")
	
	def topN(self, n):
		""" Returns the top N samples by occurence.
		
		>>> newFreak = FrequencyDistribution()
		>>> newFreak.topN(5)
		[]
		>>> newFreak.seen('a')
		>>> newFreak.topN(5)
		['a']
		>>> newFreak.seen('b')
		>>> newFreak.topN(1)
		['a']
		"""
		if len(self._sampleHeap) == 0:
			return []
		return self._sampleHeap[0:n]
	
	def getByPercentage(self, percentage):
		""" Get all samples that appear at least as often as the given percentage.
		
		>>> newFreak = FrequencyDistribution(['a', 'b', 'b', 'c', 'd', 'e', 'f'])
		>>> newFreak.getByPercentage(5)
		Traceback (most recent call last):
			...
		ValueError: Percentage needs to be between 0 and 1
		>>> newFreak.getByPercentage(0.20)
		['b']
		"""
		if percentage < 0 or percentage > 1:
			raise ValueError('Percentage needs to be between 0 and 1')
		i = 0
		while i < len(self._sampleHeap) and self.relativeFrequency(self._sampleHeap[i]) >= percentage:
			i += 1
		if i > 0:
			return self._sampleHeap[0:i]
		return []
	
	def _getTotal(self):
		""" Returns the number of total sample tokens. """
		return self._total_tokens
	
	total = property(_getTotal,
	doc = """ Returns the number of total sample tokens.
	
	>>> newFreak = FrequencyDistribution(['a', 'b', 'b', 'c'])
	>>> newFreak.total
	4
	""")
	
	#--------------------------------------------------------------------------
	# Heap implementation adapted from Python's heapq module
	# Adapted to use different comparison criteria
	# Adapted to be a maxheap
	
	def _heappush(self, item):
		"""Push item onto heap, maintaining the heap invariant.
		
		>>> newFreak = FrequencyDistribution(['c', 'c', 'c', 'b', 'b', 'a'])
		>>> newFreak._sampleHeap
		['c', 'b', 'a']
		"""
		self._sampleHeap.append(item)
		self._siftdown(0, len(self._sampleHeap)-1)
	
	def _siftdown(self, startpos, pos):
		heap = self._sampleHeap
		newitem = heap[pos]
		# Follow the path to the root, moving parents down until finding a
		# place newitem fits.
		while pos > startpos:
			parentpos = (pos - 1) >> 1
			parent = heap[parentpos]
			if self[newitem] > self[parent]:
				heap[pos] = parent
				pos = parentpos
				continue
			break
		heap[pos] = newitem
	
	def __add__(self, other):
		""" Returns the 'sum' of two frequency distributions.
		
		>>> newFreak = FrequencyDistribution(['a', 'b', 'b', 'c'])
		>>> secondFreak = FrequencyDistribution(['d', 'e'])
		>>> sumFreak = newFreak + secondFreak
		>>> len(newFreak) + len(secondFreak) == len(sumFreak)
		True
		>>> set(newFreak) | set(secondFreak) == set(sumFreak)
		True
		"""
		sumFD = copy.deepcopy(self)
		for sample in other:
			for i in range(0, other[sample]):
				sumFD.seen(sample)
		return sumFD
	
	def __getitem__(self, sample):
		""" Returns the number of counted samples equal to the provided sample.
		
		>>> FrequencyDistribution()['not_present']
		0
		"""
		return self._frequencies[sample]
	
	def __iter__(self):
		""" Returns an iterator over the samples. """
		return self.samples().__iter__()
	
	def __len__(self):
		""" Return number of seen sample types. 
		
		>>> newFreak = FrequencyDistribution(['a', 'b', 'b', 'c'])
		>>> len(newFreak)
		3
		"""
		return len(self._frequencies)

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
	
	def expectedFuzz(self, condition):
		""" Returns one of the most probable next values. """
		return self[condition].fuzztop
	
	def backoff(self, shortCondition):
		""" Backoff and just look for conditions with a suffix like the one provided.
		
		>>> newCFD = ConditionalFrequencyDistribution([('ab', 'd'), ('bb', 'd'), ('cb', 'c'), ('ba', 'f')])
		>>> newCFD.backoff('b').samples()
		['d', 'c']
		"""
		if len(shortCondition) == 0:
			return FrequencyDistribution()
		return reduce(lambda x,y: x+y,
			[self[condition] for condition in self.conditions if condition[len(condition)-len(shortCondition):] == shortCondition],
			FrequencyDistribution()
		)
	
	def backoffExpected(self, shortCondition):
		""" Returns the most probable next value for a condition suffix.
		
		>>> newCFD = ConditionalFrequencyDistribution([('ab', 'd'), ('bb', 'd'), ('cb', 'c'), ('ba', 'f')])
		>>> newCFD.backoffExpected('b')
		'd'
		"""
		return self.backoff(shortCondition).top
	
	def backoffExpectedFuzz(self, shortCondition):
		""" Returns one of the most probable next values for a condition suffix. """
		return self.backoff(shortCondition).fuzztop
	
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
	
	def _getSampleSpace(self):
		""" Returns the combined samples of all conditions. """
		space = set()
		for fd in self._conditions.values():
			space |= set(fd.samples())
		if None in space:
			logger.error('None crept into the samples.')
			space.remove(None)
		return list(space)
	
	sampleSpace = property(_getSampleSpace,
	doc = """ Returns a list of the combined samples of all conditions.
	
	There is no reasonable ordering for this I can think of.
	
	>>> cfd = ConditionalFrequencyDistribution([(1,2),(2,3),(2,4),(2,4)])
	>>> set(cfd.sampleSpace) == set([2,3,4])
	True
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