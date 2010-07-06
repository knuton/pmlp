#-----------------------------------------------------------------# 
#
# Name:		PMLP_beta.py
# Purpose: 	generate a simple song
#
# Version: 	04.07.2010
#
#-----------------------------------------------------------------# 

#from pudb import set_trace

import music21.corpus
import music21.stream

import corpus.persistence
from statistics import ngram
from statistics import frequency
from tools import logger, music42

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


composer = 'bach'

n = 3

global bigCorpus 
bigCorpus = []


#-----------------------------------------------------------------# 
# load leading-instrument copus or create it if it isn't there 
leading_ngrams = corpus.persistence.load('leading', composer)


if not leading_ngrams: 
	
	#-----------------------------------------------------------------# 
	# some necessary preperations
	
	# create a songlist:
	Songlist = music21.corpus.getComposer(composer, 'xml')[0:49]

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

# print other_ngramlists
# training finished

#-----------------------------------------------------------------# 	
# Methods for measure-generation

# lengthPermitted checks whether a note (its quarterlength) can be added to a measure or not
# if this is going to be used, having a large alphabet might be necessary so that a note with a permitted length can always be found
def lengthPermitted(note, listofnotes):
	sum = 0
	for elem in listofnotes:
		sum = sum + elem.quarterLength	
	sum = sum + note.quarterLength
	if sum <= 4: 
		return True
	else: 
		return False

# MeasureFull checks whether a measure is full or not
def MeasureFull(notelist): 
	sum = 0
	for note in notelist: 
		sum = sum + note.quarterLength
	if sum == 4: 
		return True
	else: 	
		return False

# 
def makeLenCompatible(NewNote, listofnotes):
	# List that contains all quarterlengths up from 1/64 to 1
	allQuarterLengths = [0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5, 0.5625, 0.625, 0.6875, 0.75, 0.8125, 0.875, 0.9375, 1.0, 1.0625, 1.125, 1.1875, 1.25, 1.3125, 1.375, 1.4375, 1.5, 1.5625, 1.625, 1.6875, 1.75, 1.8125, 1.875, 1.9375, 2.0, 2.0625, 2.125, 2.1875, 2.25, 2.3125, 2.375, 2.4375, 2.5, 2.5625, 2.625, 2.6875, 2.75, 2.8125, 2.875, 2.9375, 3.0, 3.0625, 3.125, 3.1875, 3.25, 3.3125, 3.375, 3.4375, 3.5, 3.5625, 3.625, 3.6875, 3.75, 3.8125, 3.875, 3.9375, 4.0]
	sum = 0
	# collect quarterlengths that occurred in the measure so far 
	previousQuarterLengths = []
	for elem in listofnotes:
		sum = sum + elem.quarterLength
		previousQuarterLengths.append(elem.quarterLength)
	# determine which QLs are possible/compatible
	end = allQuarterLengths.index(4-sum)
	#start = allQuarterLengths.index(4)
	compatibleQuarterLengths = allQuarterLengths[0:end]
	# check which of the previously occurring QLs are compatible
	# and add these QLs to allQLs in order to raise their probability
	for QL in previousQuarterLengths: 
		if QL in compatibleQuarterLengths:
			# copy next line to make probability for previous QLs larger
			compatibleQuarterLengths.append(QL) 
			compatibleQuarterLengths.append(QL) # remove to make the probability smaller
			compatibleQuarterLengths.append(QL) # remove to make the probability smaller
			compatibleQuarterLengths.append(QL) # remove to make the probability smaller
			compatibleQuarterLengths.append(QL) # remove to make the probability smaller
	# choose a compatible QL for the current note
	# higher probability for compatible QLs that occured before
	NewNote.quarterLength = random.choice(compatibleQuarterLengths)
	return NewNote


#-----------------------------------------------------------------# 	
# creativity: 


leading_ngramCFD = corpus.persistence.load('leading_ngramCFD', composer)

if not leading_ngramCFD: 
	# create ngramDistribution for leading corpus
	leading_ngramCFD = frequency.ConditionalFrequencyDistribution([noteNGram.conditionTuple for noteNGram in leading_ngrams])
	
	# store ngramDistribution
	corpus.persistence.dump('leading_ngramCFD', composer, leading_ngramCFD)

# create ngramDistributions for other copora

"""
# try to load otherNgramCFDs or create if it can't be loaded
otherNgramCFDs = corpus.persistence.load('otherNgramCFDs', composer)

if not otherNgramCFDs: 

	otherNgramCFDs = []
	for otherCorpus in other_ngramlists: 

		otherNgramCFD = frequency.ConditionalFrequencyDistribution([noteNGram.conditionTuple for noteNGram in otherCorpus])
	
		otherNgram_CFDs.append(otherNgramCFD)
		
	corpus.persistence.dump('otherNgramCFDs', composer, otherNgramCFDs)
"""	
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

# randomSong creates a new song (or rather a new Part)
def randomSong(ngramModel, startsequence, numOfMeasures, filename):
	# n is the order of the ngram (e.g. 3)
	#n = len(startsequence)
	n = 3
	#history = startsequence[len(startsequence)-n:len(startsequence)] 
	history = startsequence
	print "First History"
	print history
	# create a list to fill with new measures
	generated = []

	i = 0 
	while i <= numOfMeasures: 
		measure = []
		# filling the measure
		while not MeasureFull(measure):
			nextNote = generator(history, ngramModel)
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
	
# so far start only consists of 2 arbitrary notes
# could be something more sophisticated like a real intro 
start = random.choice(leading_ngramCFD.conditions)
logger.log(start)

# choose a filename
songname = raw_input("Enter a name for the new song: ")

# create a new song 
print "here comes the music"
randomSong(leading_ngramCFD, start, 2, songname)

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

#-----------------------------------------------------------------# 
# below comes some old generation stuff

"""


# Look for dump of trigrams to save time
trigrams = corpus.persistence.load('melody', 'bach')

n = 3

# Compute if no dump was found
if not trigrams:
	# Load XML
	bachXMLCorpus = music21.corpus.getComposer('bach', 'xml')[0:49]

	# Parse XML
	bachCorpus = [music21.corpus.parseWork(xmlScore) for xmlScore in bachXMLCorpus]

	# Get flattened Soprano parts (ignore scores without Soprano)
	flattenedSopranos = [score.getElementById('Soprano').flat for score in bachCorpus if score.getElementById('Soprano')]

	trigrams = []
	n = 3

	for soprano in flattenedSopranos: #remove
		sopranoNotes = soprano.notes
		if len(sopranoNotes) < n:
			continue
		for i in range(0, len(sopranoNotes) - n):
			# THIS IS NECESSARY MAGIC!
			sNT = sopranoNotes[i:i+n]
			[note for note in sNT]
			# EOM
			noteNGram = ngram.NoteNGram(sNT)
			trigrams.append((noteNGram.sequence[0:n-1], noteNGram.sequence[n-1]))
			
	# Skip for now
	corpus.persistence.dump('melody', 'bach', trigrams)


# ngramDistri is our frequency distribution of ngrams
ngramDistri = frequency.FrequencyDistribution(trigrams)

# determine the alphabet
alphabet = ngramDistri.samples()
print "alphabet"
print alphabet

# generate a new note (if possible based on its probability given a certain history)
def generator(history):
	# generate a random number between 0 and 1
	p = random.random()
	
	# look for a high probability for a trigram given the history and if found return the last note of that trigram
	for c in alphabet: 
		# c is a tuple of this form: ((x,y),z)
		# c[1] = z
		ngram = history, c[1] 
		
		p -= ngramDistri.relativeFrequency(ngram) # p - probability of c given history
		print p 
		print ngramDistri.relativeFrequency(ngram)
		if p <= 0.2: #change the value of p to give more or less importance to training data 
			return c[1]
	
	# if nothing is found take a random note
	warnings.warn("Failed to find random choice with remaining p = %g" % (p))
	alternative = random.choice(alphabet)
	return alternative[1]


# randomSong creates a new song (or rather a new Part)
def randomSong(ngramModel, startsequence, songlength, filename):
	# n is the order of the ngram (e.g. 3)
	#history = startsequence[len(startsequence)-n:len(startsequence)] 
	history = startsequence
	print "First History"
	print history
	
	# create list to fill with new notes
	generated = list(startsequence)
 	
 	# fill the list with new notes
 	for elem in range(songlength): 
	
		# selects random note c with Pr(c|history)
		nextNote = generator(history)
		
		# add new note to list of generated notes
		generated.append(nextNote)
		
		# update history
		# This is only creates a trigram history -> has to be changed if other ngrams are used
		#history = (history[1], nextNote)
		
		history = history[1:n-1] + (nextNote,)
		print "New History"
		print history
		
	# add startsequence to song
	#reversestart = []
	#for elem in startsequence: 
	#	reversestart.insert(0, elem)
	
	#for elem in reversestart:
	#	generated.insert(0, elem)
		

	# create new music21 stream using the generated notes
	# later it would be better to first generate an intro, then some in-between-stuff and finally an outro
	
	#s = music21.stream.Stream()
	#for note in generated:
	#	s.append(note)
	
	
	# this way we can insert different parts as soon as we got more than one 
	a = music21.stream.Part()
	for note in generated:
		a.append(note)
		
	s = music21.stream.Score()
	s.insert(0, a)
		
	# show new song
	#s.show('musicxml')
	
	# store new song in musicXML file
	s.write('musicxml', 'output/'+ str(filename) + '.xml')
	
	# Probleme bisher: 
	# - Kommt mit grossen Liedlaengen nicht klar
	# - Kuemmert sich noch gar nicht um Liedstruktur etc
	# - koennte noch Fehler bei der generate methode geben 
	# - Andere Dinge wie startkey, tempo, instrumente/spuren etc koennte/sollte man auch noch einfuegen
	
# so far start only consists of 2 arbitrary notes
# could be something more sophisticated like a real intro 
starttrigram = alphabet[3]
start = starttrigram[0]
print start

# choose a filename
songname = raw_input("Enter a name for the new song: ")

# create a new song 
randomSong(ngramDistri, start, 100, songname)

"""	
