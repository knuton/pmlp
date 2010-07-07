#-----------------------------------------------------------------# 
#
# Name:		PMLP_beta.py
# Purpose: 	generate a simple song
#
# Version: 	06.07.2010
#
#-----------------------------------------------------------------# 

#from pudb import set_trace

import music21.corpus
import music21.stream

import corpus.persistence
from statistics import ngram
from statistics import frequency
from tools import logger, music42
import copy

import sys, random, warnings

#-----------------------------------------------------------------# 
# Methods for training: 

# getparts() creates a list that contains all part-names (instruments) that occur in a list of songs
# ATTENTION!!! This also parses the corpus  
def getParts(songlist):
	partlist = []
	for elem in songlist:
		song = music21.corpus.parseWork(elem) 
		bigCorpus.append(song) # save time later 
		parts = [part.id for part in song]
		partlist.append(parts)
	return partlist


# removes strange (and empty) integers from the list of instruments
def removeInts(partlist):
	for list in partlist: 
		for elem in list: 
			if isinstance(elem, int):  
				list.remove(elem)
	return partlist

# 3d list to 2d list (all elements in one big list - no lists in lists)
def flattenList(list_with_lists): 
	list_without_lists = []
	for list in list_with_lists:
		for elem in list: 
			list_without_lists.append(elem)
	return list_without_lists

# remove all instruments you don't want to train on
def finalInstruments(flatlist):
	final_instruments = []
	freqdist = frequency.FrequencyDistribution(flatlist)
	border = int(freqdist.relativeFrequency(freqdist.top)/2*100)
	for elem in freqdist.samples():
		if freqdist[elem] >= border: 
			final_instruments.append(elem)
	return final_instruments


#-----------------------------------------------------------------# 
# start
 

#composer = 'beethoven'
composer = 'bach'
#composer = 'mozart'

n = 6

global bigCorpus 
bigCorpus = []
"""

#-----------------------------------------------------------------# 
# load leading-instrument copus or create it if it isn't there 
leading_ngrams = corpus.persistence.load('leading', composer)


if not leading_ngrams: 
	
	#-----------------------------------------------------------------# 
	# some necessary preperations
	
	# create a songlist:
	Songlist = music21.corpus.getComposer(composer, 'xml')[0:25]

	# get all instruments that are used in the songs of Songlist
	# and parse bigCorpus
	all_instruments = getParts(Songlist)
	#print bigCorpus
	
	# remove strange ints
	all_instruments = removeInts(all_instruments)
	
	# flatten list
	all_instruments = flattenList(all_instruments)

	# determine leading instrument
	instrumentFreqDist = frequency.FrequencyDistribution(all_instruments)
	topInstrument = instrumentFreqDist.top

	# determine which instruments will be used for training
	final_instruments = finalInstruments(all_instruments)

	# remove leading instrument because it gets special treatment
	final_instruments.remove(topInstrument)

	# parse all songs (only uncomment if you didn't use the getParts method before)
	#bigCorpus = [music21.corpus.parseWork(xmlScore) for xmlScore in Songlist]
	
	#-----------------------------------------------------------------# 

	# create leading_ngrams
	flatLeading = [score.getElementById(str(topInstrument)).flat for score in bigCorpus if score.getElementById(str(topInstrument))]
	
	leading_ngrams = []
	
	for leading in flatLeading: 
		
		leadingNotes = leading.notes
		if len(leadingNotes) < n:
			continue
		for i in range(0, len(leadingNotes) - n):
			# THIS IS NECESSARY MAGIC!
			lNT = leadingNotes[i:i+n]
			[note for note in lNT]
			# EOM
			#noteNGram = ngram.NoteNGram(lNT)
			#leading_ngrams.append((noteNGram.sequence[0:n-1], noteNGram.sequence[n-1]))
			leading_ngrams.append(ngram.NoteNGram(lNT))
			
			
	corpus.persistence.dump('leading', composer, leading_ngrams)
	
	corpus.persistence.dump('all_instruments', composer, all_instruments)
	corpus.persistence.dump('topInstrument', composer, topInstrument)
	corpus.persistence.dump('final_instruments', composer, final_instruments)
	corpus.persistence.dump('instrumentFreqDist', composer, instrumentFreqDist)
	
	
#print leading_ngrams

#-----------------------------------------------------------------# 
# try loading ngramlists of other instruments


other_ngramlists = corpus.persistence.load('others', composer)

if not other_ngramlists: 
	# other_ngramlists is a list that will contain lists of ngrams for all other instruments (not the leading instrument)
	other_ngramlists = []
	for instrument in final_instruments: 
		flatScore =  [score.getElementById(str(instrument)).flat for score in bigCorpus if score.getElementById(str(instrument))]
		other_ngrams = []
		for member in flatScore: 
			memberNotes = member.notes
			if len(memberNotes) < n:
				continue
			for i in range(0, len(memberNotes) - n):
				mNT = memberNotes[i:i+n]
				[note for note in mNT]
				#noteNgram = ngram.NoteNGram(mNT)
				#other_ngrams.append((noteNGram.sequence[0:n-1], noteNGram.sequence[n-1]))
				other_ngrams.append(ngram.NoteNGram(mNT))
		other_ngramlists.append(other_ngrams)
		# or as tuple, containing the name of the instrument
		#other_ngramlists.append(other_ngrams, str(Instrument))
	corpus.persistence.dump('others', composer, other_ngramlists)

print "other_ngramlists"
# training finished
"""
#-----------------------------------------------------------------# 	
# Methods for measure-generation

# lengthPermitted checks whether a note (its quarterlength) can be added to a measure or not
# if this is going to be used, having a large alphabet might be necessary so that a note with a permitted length can always be found

"""
def lengthPermitted(note, listofnotes):
	sum = 0
	for elem in listofnotes:
		sum = sum + elem.quarterLength	
	sum = sum + note.quarterLength
	if sum <= 4: 
		return True
	else: 
		return False

def measurelen(notelist): 
	sum = 0 
	for elem in notelist: 
		sum = sum + elem.quarterLength
	return sum

# MeasureFull checks whether a measure is full or not
def MeasureFull(notelist): 
	sum = 0
	for elem in notelist: 
		sum = sum + elem.quarterLength
	if sum == 4: 
		return True
	else: 	
		return False

 
def makeLenCompatible(NewNote, listofnotes, history):
	
	# contains 1/32
	#allQuarterLengths = [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.125, 1.25, 1.375, 1.5, 1.625, 1.75, 1.875, 2.0, 2.125, 2.25, 2.375, 2.5, 2.625, 2.75, 2.875, 3.0, 3.125, 3.25, 3.375, 3.5, 3.625, 3.75, 3.875, 4.0]
	
	# List that contains all quarterlengths up from 1/64 to 1
	allQuarterLengths = [0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5, 0.5625, 0.625, 0.6875, 0.75, 0.8125, 0.875, 0.9375, 1.0, 1.0625, 1.125, 1.1875, 1.25, 1.3125, 1.375, 1.4375, 1.5, 1.5625, 1.625, 1.6875, 1.75, 1.8125, 1.875, 1.9375, 2.0, 2.0625, 2.125, 2.1875, 2.25, 2.3125, 2.375, 2.4375, 2.5, 2.5625, 2.625, 2.6875, 2.75, 2.8125, 2.875, 2.9375, 3.0, 3.0625, 3.125, 3.1875, 3.25, 3.3125, 3.375, 3.4375, 3.5, 3.5625, 3.625, 3.6875, 3.75, 3.8125, 3.875, 3.9375, 4.0]
	
	# contains all Quarterlengths that can be generated 
	
	# fastest possible 1/128
	#possibleQuarterLengths = [0.03125, 0.0625, 0.09375, 0.125, 0.1875, 0.25, 0.375, 0.5, 0.75, 1, 1.5, 2, 3.0, 4]
	
	# fastest possible 1/64
	possibleQuarterLengths = [0.0625, 0.125, 0.1875, 0.25, 0.375, 0.5, 0.75, 1, 1.5, 2, 3.0, 4]
	

	#
	sum = 0
	# collect quarterlengths that occurred in the measure so far 
	for elem in listofnotes:
		sum = sum + elem.quarterLength
	
	shorthistory = (history[-3], history[-2], history[-1])
	historyQLs = []
	for elem in shorthistory: 
		historyQLs.append(elem.quarterLength)
	
	#compatibleQuarterLengths = allQuarterLengths[0:end+1]
	
	possibleCompatibleQLs = []
	for elem in possibleQuarterLengths: 
		if elem <= 4-sum:
			possibleCompatibleQLs.append(elem)
	
	
	# check which of the previously occurring QLs are compatible
	# and add these QLs to allQLs in order to raise their probability
	for QL in historyQLs: 
		if QL in possibleCompatibleQLs:
			# copy next line to make probability for previous QLs larger
			possibleCompatibleQLs.append(QL) 
			possibleCompatibleQLs.append(QL) # remove to make the probability smaller
			possibleCompatibleQLs.append(QL) # remove to make the probability smaller
			possibleCompatibleQLs.append(QL) # remove to make the probability smaller
			possibleCompatibleQLs.append(QL) # remove to make the probability smaller
			possibleCompatibleQLs.append(QL) # remove to make the probability smaller
			possibleCompatibleQLs.append(QL) # remove to make the probability smaller
			possibleCompatibleQLs.append(QL) # remove to make the probability smaller
			possibleCompatibleQLs.append(QL) # remove to make the probability smaller
			possibleCompatibleQLs.append(QL) # remove to make the probability smaller


	# choose a compatible QL for the current note
	# higher probability for compatible QLs that occured before
	if possibleCompatibleQLs:
		NewNote.quarterLength = random.choice(possibleCompatibleQLs)
		print NewNote, NewNote.quarterLength
		return NewNote	
	else:
		return False
		
		#NewNote = generator(history, ngramModel)
		#makeLenCompatible(NewNote, listofnotes, ngramModel, history)


def isTriplet(note):
	
	triplets = [0.020833333333333332, 0.041666666666666664, 0.083333333333333329, 0.16666666666666666, 0.33333333333333331, 0.66666666666666663, 1.3333333333333333]
	if note.quarterLength in triplets: 
		print "found it"
		print note.quarterLength
		return True
	else: 
		return False
"""		


def completeMeasure(part, lenCount):
	rest = music21.note.Rest()
	if lenCount < 4: 
		rest.quarterLength = 4 - lenCount
		part.append(rest)
		return part
	elif lenCount == 4: 
		rest.quarterLength = 4 
		part.append(rest)
		return part


		
	

#-----------------------------------------------------------------# 	
# creativity: 


leading_ngramCFD = corpus.persistence.load('leading_ngramCFD', composer)

if not leading_ngramCFD: 
	# create ngramDistribution for leading corpus
	leading_ngramCFD = frequency.ConditionalFrequencyDistribution([noteNGram.conditionTuple for noteNGram in leading_ngrams])
	
	# store ngramDistribution
	corpus.persistence.dump('leading_ngramCFD', composer, leading_ngramCFD)

# create ngramDistributions for other copora


# try to load otherNgramCFDs or create if it can't be loaded
otherNgramCFDs = corpus.persistence.load('otherNgramCFDs', composer)

if not otherNgramCFDs: 

	otherNgramCFDs = []
	for otherCorpus in other_ngramlists: 

		otherNgramCFD = frequency.ConditionalFrequencyDistribution([noteNGram.conditionTuple for noteNGram in otherCorpus])
	
		otherNgramCFDs.append(otherNgramCFD)
		
	corpus.persistence.dump('otherNgramCFDs', composer, otherNgramCFDs)

# determine an alphabet: 
# so far it is only for leading corpus (we should add other corpora/notes from other corpora too e.g. by creating an alphabet from all corpora and eliminating copies)
alphabet = leading_ngramCFD.sampleSpace

# generate a new note (if possible based on its probability given a certain history)

def generator(realHistory, ngramCFD):
	
	normalizedHistory = music42.normalizeNotes(realHistory)
	
	if ngramCFD[normalizedHistory].top:
		return music42.denormalizeNote(ngramCFD[normalizedHistory].fuzztop, realHistory)
	
	# if nothing is found take a random note
	logger.log("Failed to find random choice for history %s" % (normalizedHistory,))
	return random.choice(alphabet)
	

"""
def generator(realHistory):
	
	normalizedHistory = music42.normalizeNotes(realHistory)
	
	if ngramCFD.expected(normalizedHistory):
		return music42.denormalizeNote(ngramCFD.expectedFuzz(normalizedHistory), realHistory)
	
	# if nothing is found take a random note
	logger.log("Failed to find random choice for history %s" % (normalizedHistory,))
	return random.choice(alphabet)
"""

def randomConcert(leadingModel, otherModels, startsequence, otherStarts, numOfMeasures, filename): 

	# create a score
	s = music21.stream.Score()

	n = len(startsequence)
	
	Lhistory = startsequence
	Lpart = music21.stream.Part()
	
	opartList = []
	
	mCount = 0 
	lenCount = 0 
	
	for elem in startsequence: 
		while lenCount < 4: 
			Lpart.append(elem)
			lenCount += elem.quarterLength
		lenCount -= 4 
		mCount += 1
	
	while mCount < numOfMeasures - 1: 
		while lenCount < 4:
			nextNote = generator(Lhistory, leadingModel)
			Lpart.append(nextNote)
			lenCount += nextNote.quarterLength
			
			#created.append(nextNote)
			print "added note" + str(nextNote)
			Lhistory = Lhistory[1:] + (nextNote,)
			
		print lenCount
		# raise measure count
		mCount += 1
		# reset the length count
		lenCount -= 4 
		print lenCount
		print "mCount" + str(mCount)
		
	Lpart = completeMeasure(Lpart, lenCount)
	
	s.insert(0, Lpart)
	
	for otherStart in otherStarts:
		mCount = 0
		lenCount = 0
		opart = music21.stream.Part()
		for elem in otherStart: 
			while lenCount < 4:
				opart.append(elem)
				lenCount += elem.quarterLength
			lenCount -= 4
			mCount += 1
			
		ohistory = otherStart	
		opartList.append([opart, mCount, lenCount, ohistory])
		
		
	i = 0 
	while i < len(opartList):
	#for i in range(opartList):
		list = opartList[i]
		omodel = otherModels[i]	
		opart = list[0]
		mCount = list[1]
		lenCount = list[2]
		ohistory = list[3]
		
		
		while mCount < numOfMeasures - 1: 
			while lenCount < 4:
				nextNote = generator(ohistory, omodel)
				opart.append(nextNote)
				lenCount += nextNote.quarterLength
			
				#created.append(nextNote)
				print "added note" + str(nextNote)
				ohistory = ohistory[1:] + (nextNote,)
			
			print lenCount
		
			# raise measure count
			mCount += 1
			# reset the length count
			lenCount -= 4 
			print lenCount
			print "mCount" + str(mCount)
		
		
		opart = completeMeasure(opart, lenCount)
		s.show()
		s.insert(opart)
		i = i + 1
		print "instrument complete"
		
	# show score
	s.show()
	
	# store new song in musicXML file
	s.write('musicxml', 'output/'+ str(filename) + '.xml')


# randomSong creates a new song (or rather a new Part)
def randomSong(ngramModel, startsequence, numOfMeasures, filename):
	
	
	
	# n is the order of the ngram (e.g. 3)
	# right now it is determined by the length of the startsequence
	n = len(startsequence)
	#n = 3
	#history = startsequence[len(startsequence)-n:len(startsequence)] 
	history = startsequence
	print "First History"
	print history
	
	part = music21.stream.Part()
	#created = []
	
	# measure count
	mCount = 0
	# measurelength sum
	lenCount = 0
	
	# insert startsequence into the part
	for elem in startsequence: 
		while lenCount < 4: 
			part.append(elem)
			lenCount += elem.quarterLength
		lenCount -= 4 
		mCount += 1
		
		"""
		# if the sum of the quarterlength is bigger than 4 
		if lenCount >= 4:
			# reset the length count
			lenCount -= 4 
			# raise measure count
			mCount += 1
		else: 
			#created.append(elem)
			part.append(elem)
			lenCount += elem.quarterLength
		"""
	# create rest of the song
	#while len(part.getElementsByClass(music21.stream.Measure)) < numOfMeasures:
	while mCount < numOfMeasures - 1: 
		while lenCount < 4:
			nextNote = generator(history, ngramModel)
			part.append(nextNote)
			lenCount += nextNote.quarterLength
			
			#created.append(nextNote)
			print "added note" + str(nextNote)
			history = history[1:] + (nextNote,)
			
		print lenCount
		
		# raise measure count
		mCount += 1
		# reset the length count
		lenCount -= 4 
		print lenCount
		print "mCount" + str(mCount)
		
	
	# fill up last measure with rests
	part = completeMeasure(part, lenCount)
	
        """
		if lenCount >= 4:
			print lenCount
			# reset the length count
			lenCount -= 4 
			# raise measure count
			mCount += 1
			print lenCount
			print "mCount" + str(mCount)
		else:
			nextNote = generator(history, ngramModel)
			part.append(nextNote)
			#created.append(nextNote)
			print "added note" + str(nextNote)
			history = history[1:] + (nextNote,)
			lenCount += elem.quarterLength
        """		

	# create a music21 part
	"""	
	part = music21.stream.Part()
	for elem in created: 
		part.append(elem)
	
	sNew = music21.stream.Stream()
	for elem in created:
		sNew.append(elem)
		
	sNew.show()

	"""
	
#	detaerc = []
#	for elem in created: 
#		detaerc.insert(0, elem)
	
#	part2 = music21.stream.Part()
#	for elem in detaerc: 
#		part2.append(elem)
	
	# create a score
	#s = music21.stream.Score()
	
	# insert part into score
	#s.insert(0, part)
	#s.insert(0, part)
	#s.show()
	#b = s[0].getMeasureRange(1,5)
	#b.show()

	
	# show score
	part.show()
	
	# store new song in musicXML file
	part.write('musicxml', 'output/'+ str(filename) + '.xml')
				
	
# so far start only consists of 2 arbitrary notes
# could be something more sophisticated like a real intro 
start = random.choice(leading_ngramCFD.conditions)
logger.log(start)

# choose a filename
songname = str(composer) + "_" + str(raw_input("Enter a name for the new song: "))

# create a new song 
print "here comes the music"
#randomSong(leading_ngramCFD, start, 20, songname)

otherStarts = []
for cfd in otherNgramCFDs: 
	otherStart = random.choice(cfd.conditions)
	otherStarts.append(otherStart)



# create a new concert
randomConcert(leading_ngramCFD, otherNgramCFDs, start, otherStarts, 10, songname)


#-----------------------------------------------------------------# 
# random song for many parts
"""
def randomSong(leadingModel, leadingStartsequence, listOfModels, listOfStartsequences, numOfMeasures, filename):
	# n is the order of the ngram (e.g. 3)
	#n = len(startsequence)
	n = 3
	#history = startsequence[len(startsequence)-n:len(startsequence)] 
	leadingHistory = startsequence
	print "First History"
	print leadingHistory
	# create a list to fill with new measures
	leading_generated = []
	others_generated = []

	i = 0 
	while i <= numOfMeasures: 
		measure = []
		# filling the measure
		while not MeasureFull(measure):
			nextNote = generator(history, leadingModel)
			# check whether note fits into the measure
			
			#while not lengthPermitted(nextNote, measure):
			#	nextNote = generator(history)
			
			# make length of the next note compatible if it isn't 
			if not lengthPermitted(nextNote, measure):
				nextNote = makeLenCompatible(nextNote, measure)
			
			measure.append(nextNote)	
			# update history
			history = history[1:] + (nextNote,)
			
		# add measure to song
		generated.append(measure)
		i = i + 1
			
	# create a music21 part
	leadingPart = music21.stream.Part()
	
	for measure in generated:
		m = music21.stream.Measure()
		
		# create measure
		for note in measure: 
			m.append(note)
			
		# append measure to part
		leadingPart.append(m)
	# create a score
	s = music21.stream.Score()
	# insert part into score
	s.insert(0, leadingPart)
	# show score
	s.show()

"""

