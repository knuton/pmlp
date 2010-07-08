#-----------------------------------------------------------------# 
#
# Name:		PMLP_beta.py
# Purpose: 	generate a simple song
#
# Version: 	08.07.2010
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


### TRAINING ###
### Commented out to keep program from loading/dumping both ngrams AND CFD.
### Needs to be uncommented for first run.
"""
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
	### all_instruments: Namen der Parts
	### Hier wird auch schon geparst
	all_instruments = getParts(Songlist)
	#print bigCorpus
	
	# remove strange ints
	### Can be integrated into getParts
	all_instruments = removeInts(all_instruments)
	
	# flatten list
	### Integrate
	all_instruments = flattenList(all_instruments)

	# determine leading instrument
	### Just using FreqDist to find leading (most occurences)
	instrumentFreqDist = frequency.FrequencyDistribution(all_instruments)
	topInstrument = instrumentFreqDist.top

	# determine which instruments will be used for training
	### Use N most occuring instruments
	final_instruments = finalInstruments(all_instruments)

	# remove leading instrument because it gets special treatment
	final_instruments.remove(topInstrument)

	# parse all songs (only uncomment if you didn't use the getParts method before)
	#bigCorpus = [music21.corpus.parseWork(xmlScore) for xmlScore in Songlist]
	
	#-----------------------------------------------------------------# 

	# create leading_ngrams
	### Obtained using the name of the top/leading instrument
	flatLeading = [score.getElementById(str(topInstrument)).flat for score in bigCorpus if score.getElementById(str(topInstrument))]
	
	leading_ngrams = []
	### One trackfrom leading per score
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
	### Names of the instruments
	corpus.persistence.dump('all_instruments', composer, all_instruments)
	corpus.persistence.dump('topInstrument', composer, topInstrument)
	corpus.persistence.dump('final_instruments', composer, final_instruments)
	corpus.persistence.dump('instrumentFreqDist', composer, instrumentFreqDist)
	
	
#print leading_ngrams

#-----------------------------------------------------------------# 
# try loading ngramlists of other instruments

### Load/generate list of ngram lists (one per instrument)

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


### GENERATION ###

### Used to fill up the last measure in generated score with rests,
### so that all parts have the same length.

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



# Takes a note and translates it into cdur if it is not in cdur yet
def makeCdur(note): 
	# clist contains all pitchClasses that occur in cdur
	clist = [0,2,4,5,7,9,11]
	#if note.name not in clist:
	while note.pitchClass not in clist:
		note = note.transpose(-1)
	
	return note
	
	
	
# takes two notes or a list of notes and a note 
def areConflicting(Note1, Note2):
	# conflictlist contains intervals that would produce a conflict
	
	# every note which is 1/2 step above or below produces conflict
	conflictlist = [1,11,13,23,25,35,37,47,49,59,61,71,73,83,85,95,97]
	
	if Note1.isNote and Note2.isNote:
		print "changing interval"
		intval = music21.interval.notesToChromatic(Note1,Note2)
	
		if intval.undirected in conflictlist: 
			return True
		else: 
			return False
	else: 
		return False

	

#-----------------------------------------------------------------# 	
# creativity: 

### Load CFD (leading)

leading_ngramCFD = corpus.persistence.load('leading_ngramCFD', composer)

### Or create CFD (leading)

if not leading_ngramCFD: 
	# create ngramDistribution for leading corpus
	leading_ngramCFD = frequency.ConditionalFrequencyDistribution([noteNGram.conditionTuple for noteNGram in leading_ngrams])
	
	# store ngramDistribution
	corpus.persistence.dump('leading_ngramCFD', composer, leading_ngramCFD)

# create ngramDistributions for other copora

### Load CFD (others)

# try to load otherNgramCFDs or create if it can't be loaded
otherNgramCFDs = corpus.persistence.load('otherNgramCFDs', composer)


### Or create CFD (others)

if not otherNgramCFDs: 

	otherNgramCFDs = []
	for otherCorpus in other_ngramlists: 

		otherNgramCFD = frequency.ConditionalFrequencyDistribution([noteNGram.conditionTuple for noteNGram in otherCorpus])
	
		otherNgramCFDs.append(otherNgramCFD)
		
	corpus.persistence.dump('otherNgramCFDs', composer, otherNgramCFDs)

# determine an alphabet: 
# so far it is only for leading corpus (we should add other corpora/notes from other corpora too e.g. by creating an alphabet from all corpora and eliminating copies)
alphabet = leading_ngramCFD.sampleSpace


### Might want to use separate alphabet for others

# generate a new note (if possible based on its probability given a certain history)

### Pass along CFD (there are several), pass along alphabet (see above)

def generator(realHistory, ngramCFD):
	
	normalizedHistory = music42.normalizeNotes(realHistory)
	
	### Might want to use expected/expectedFuzz
	if ngramCFD[normalizedHistory].top:
		return music42.denormalizeNote(ngramCFD[normalizedHistory].fuzztop, realHistory)
	
	# if nothing is found take a random note
	logger.log("Failed to find random choice for history %s" % (normalizedHistory,))
	return random.choice(alphabet)

topInstrument = corpus.persistence.load('topInstrument', composer)
final_instruments = corpus.persistence.load('final_instruments', composer)


### Might want to pass alphabet(s)

def randomConcert(leadingModel, otherModels, startsequence, otherStarts, numOfMeasures, filename): 

	# create a score
	s = music21.stream.Score()

	### Maybe choose n per instrument

	n = len(startsequence)
	
	### Leading
	Lhistory = startsequence
	Lpart = music21.stream.Part()
	
	
	# alternativ: note in tonart generieren 
	choicelist = [-1, 1]
	opartchecklist = []
	### List of other parts
	opartList = []
	
	mCount = 0 # measure count
	lenCount = 0 # quarter length count
	
	### Only insert start sequence into leading part
	
	while lenCount < 4:
		for elem in startsequence: 
			Lpart.append(elem)
			lenCount += elem.quarterLength
	lenCount -= 4 
	mCount += 1
	
	### Less than parameter value
	while mCount < numOfMeasures - 1: 
		### lenCount might be prefilled, but works measure-wise
		while lenCount < 4:
			nextNote = generator(Lhistory, leadingModel)
			
			if nextNote.isNote: 
				nextNote = makeCdur(nextNote)
			
			Lpart.append(nextNote)
			lenCount += nextNote.quarterLength
			
			#created.append(nextNote)
			print "added note" + str(nextNote)
			Lhistory = Lhistory[1:] + (nextNote,)
			
		# raise measure count
		mCount += 1
		# reset the length count
		lenCount -= 4 
	
	### Fill last "measure" with rests
	Lpart = completeMeasure(Lpart, lenCount)
	### Try to reassign instrument type
	Lpart.id = topInstrument
	
	### Add leading part to score
	s.insert(0, Lpart)
	
	# create startsequences for other parts
	for otherStart in otherStarts:
		mCount = 0
		lenCount = 0
		opart = music21.stream.Part()
		
		while lenCount < 4:
			for elem in otherStart: 
				opart.append(elem)
				lenCount += elem.quarterLength
		lenCount -= 4
		mCount += 1
			
		ohistory = otherStart
		### opart: Track for one instrument
		### mCount: Pass on to generation of remaining
		### lenCount: Pass on to generation of remaining
		### ohistory: History of instrument
		opartList.append([opart, mCount, lenCount, ohistory])
		
		
	i = 0 
	### i runs trough number of instruments
	### Could be turned into
	### for opart, mCount, lenCount, ohistory in opartList:
	while i < len(opartList):
		### Current instrument
		list = opartList[i]
		omodel = otherModels[i] ### Can get alphabet from this
		### Track
		opart = list[0]
		mCount = list[1]
		lenCount = list[2]
		ohistory = list[3]
		
		### Run through measures
		while mCount < numOfMeasures - 1:
			### Create measurewise
			while lenCount < 4:
				nextNote = generator(ohistory, omodel)
				
				if nextNote.isNote: 
					nextNote = makeCdur(nextNote)
				
				
				
				# add note to part
				opart.append(nextNote)
				
				### Either this or makeCdur
				
				"""
				# take new elem from the part (same as nextNote but contains offset information)
				### Now has an offset
				lastelem = opart[-1]
				
				
				# create list to fill with notes that have the same offset as lastelem
				### From all previously generated parts
				sameoffset = []
				
				# take a random choice for changing the pitch (choicelist see above)
				### choicelist = [1, -1]
				choice = random.choice(choicelist)
				
				# search for notes with same offset as lastelem and append them to sameoffset 
				
				# 1. sameoffset in Lpart
				for elem in Lpart:
					if elem.isNote and lastelem.isNote:
						if lastelem.offset in range(elem.offset, (elem.offset + elem.quarterLength)) or elem.offset in range(lastelem.offset, (lastelem.offset + lastelem.quarterLength)):
							lSameOffset = elem
							### No regard for chords up til now
							if elem.isNote:
								sameoffset.append(elem)
				
				# 2. sameoffset in previous parts
				if opartchecklist: 
					for previousPart in opartchecklist: 
						for oelem in previousPart:
							if oelem.isNote and lastelem.isNote:
								if lastelem.offset in range(oelem.offset, (oelem.offset + oelem.quarterLength)) or oelem.offset in range(lastelem.offset, (lastelem.offset + lastelem.quarterLength)):
									if oelem.isNote:
										sameoffset.append(oelem)
										print "append note to opartchecklist"
				
				print "length sameoffset", len(sameoffset)
				if sameoffset:
					
					### Adjustment is alwas for lastelem (the new note)
					
					### As long as there is a conflict between lastelem and any elem from sameoffset
					### randomly go always up or always down with lastelem's pitch, until there is
					### no more conflict.
					
					if len(sameoffset) == 1:
						while areConflicting(sameoffset[0], lastelem):
							#choice = random.choice(choicelist)
							lastelem = lastelem.transpose(choice)
						
					elif len(sameoffset) == 2:
						while areConflicting(sameoffset[0], lastelem) or areConflicting(sameoffset[1], lastelem):
							#choice = random.choice(choicelist)
							lastelem = lastelem.transpose(choice)
					
					elif len(sameoffset) == 3:
						while areConflicting(sameoffset[0], lastelem) or areConflicting(sameoffset[1], lastelem) or areConflicting(sameoffset[2], lastelem):
							#choice = random.choice(choicelist)
							lastelem = lastelem.transpose(choice)
					
					elif len(sameoffset) == 4:
						while areConflicting(sameoffset[0], lastelem) or 	areConflicting(sameoffset[1], lastelem) or areConflicting(sameoffset[2], lastelem) or areConflicting(sameoffset[3], lastelem):
							#choice = random.choice(choicelist)
							lastelem = lastelem.transpose(choice)
					
					elif len(sameoffset) == 5:
						while areConflicting(sameoffset[0], lastelem) or areConflicting(sameoffset[1], lastelem) or areConflicting(sameoffset[2], lastelem) or areConflicting(sameoffset[3], lastelem) or areConflicting(sameoffset[4], lastelem):
							#choice = random.choice(choicelist)
							lastelem = lastelem.transpose(choice)
					
					elif len(sameoffset) == 6:
						while areConflicting(sameoffset[0], lastelem) or areConflicting(sameoffset[1], lastelem) or areConflicting(sameoffset[2], lastelem) or areConflicting(sameoffset[3], lastelem) or areConflicting(sameoffset[4], lastelem) or areConflicting(sameoffset[5], lastelem):
							#choice = random.choice(choicelist)
							lastelem = lastelem.transpose(choice)
					
					elif len(sameoffset) == 7:
						while areConflicting(sameoffset[0], lastelem) or areConflicting(sameoffset[1], lastelem) or areConflicting(sameoffset[2], lastelem) or areConflicting(sameoffset[3], lastelem) or areConflicting(sameoffset[4], lastelem) or areConflicting(sameoffset[5], lastelem) or areConflicting(sameoffset[6], lastelem):
							#choice = random.choice(choicelist)
							lastelem = lastelem.transpose(choice)
						
					elif len(sameoffset) > 7:
						while areConflicting(sameoffset[0], lastelem) or areConflicting(sameoffset[1], lastelem) or areConflicting(sameoffset[2], lastelem) or areConflicting(sameoffset[3], lastelem) or areConflicting(sameoffset[4], lastelem) or areConflicting(sameoffset[5], lastelem) or areConflicting(sameoffset[6], lastelem) or areConflicting(sameoffset[7], lastelem):
							#choice = random.choice(choicelist)
							lastelem = lastelem.transpose(choice)
					
				### lastelem needs to be put back over its old version in the part
				opart[-1] = lastelem
				
				"""
				### For conflict solution
				#lenCount += lastelem.quarterLength
				### For makeCdur
				lenCount += nextNote.quarterLength
				
				### Update history (makeCdur)
				ohistory = ohistory[1:] + (nextNote,)
				### Update history (conflict solution)
				#ohistory = ohistory[1:] + (lastelem,)
		
			### End of while (lenCount < 4)
			# raise measure count
			mCount += 1
			# reset the length count
			lenCount -= 4 
		
		### Fill part with rests
		opart = completeMeasure(opart, lenCount)
		### Add new part to list of parts which could contain conflicting notes
		opartchecklist.append(opart)
		
		s.insert(opart)
		### Just for debugging, because each turn could end in a crash
		s.show()
		i = i + 1
		print "instrument complete"
		
	# label score (experimental)
	s.id = str(filename)
	
	# show score
	s.show()
	
	# store new song in musicXML file
	s.write('musicxml', 'output/'+ str(filename) + '.xml')

### End of randomConcert

# so far start only consists of 2 arbitrary notes
# could be something more sophisticated like a real intro 
start = random.choice(leading_ngramCFD.conditions)
logger.log(start)

# choose a filename
songname = str(composer) + "_" + str(raw_input("Enter a name for the new song: "))

# create a new song 
print "here comes the music"

otherStarts = []
for cfd in otherNgramCFDs: 
	otherStart = random.choice(cfd.conditions)
	otherStarts.append(otherStart)


# create a new concert
### Leading CFD, other CFDs (list), startseq of leading, startseq of others (list), 10 measures, song name
randomConcert(leading_ngramCFD, otherNgramCFDs, start, otherStarts, 10, songname)


#-----------------------------------------------------------------# 
# random song for many parts

