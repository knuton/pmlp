# Dictionary that contains all midiPrograms and their names
midiAlphabet = {
	1: "Acoustic Grand Piano",
	2: "Bright Acoustic Piano",
	3: "Electric Grand Piano",
	4: "Honky-tonk Piano",
	5: "Electric Piano 1",
	6: "Electric Piano 2",
	7: "Harpsichord",
	8: "Clavinet",
	9: "Celesta",
	10: "Glockenspiel",
	11: "Music Box",
	12: "Vibraphone",
	13: "Marimba",
	14: "Xylophone",
	15: "Tubular Bells",
	16: "Dulcimer",
	17: "Drawbar Organ",
	18: "Percussive Organ",
	19: "Rock Organ",
	20: "Church Organ",
	21: "Reed Organ",
	22: "Accordion",
	23: "Harmonica",
	24: "Tango Accordion",
	25: "Acoustic Guitar (nylon)",
	26: "Acoustic Guitar (steel)",
	27: "Electric Guitar (jazz)",
	28: "Electric Guitar (clean)",
	29: "Electric Guitar (muted)",
	30: "Overdriven Guitar",
	31: "Distortion Guitar",
	32: "Guitar harmonics",
	33: "Acoustic Bass",
	34: "Electric Bass (finger)",
	35: "Electric Bass (pick)",
	36: "Fretless Bass",
	37: "Slap Bass 1",
	38: "Slap Bass 2",
	39: "Synth Bass 1",
	40: "Synth Bass 2",
	41: "Violin",
	42: "Viola",
	43: "Cello",
	44: "Contrabass",
	45: "Tremolo Strings",
	46: "Pizzicato Strings",
	47: "Orchestral Harp",
	48: "Timpani",
	49: "String Ensemble 1",
	50: "String Ensemble 2",
	51: "Synth Strings 1",
	52: "Synth Strings 2",
	53: "Choir Aahs",
	54: "Voice Oohs",
	55: "Synth Voice",
	56: "Orchestra Hit",
	57: "Trumpet",
	58: "Trombone",
	59: "Tuba",
	60: "Muted Trumpet",
	61: "French Horn",
	62: "Brass Section",
	63: "Synth Brass 1",
	64: "Synth Brass 2",
	65: "Soprano Sax",
	66: "Alto Sax",
	67: "Tenor Sax",
	68: "Baritone Sax",
	69: "Oboe",
	70: "English Horn",
	71: "Bassoon",
	72: "Clarinet",
	73: "Piccolo",
	74: "Flute",
	75: "Recorder",
	76: "Pan Flute",
	77: "Blown Bottle",
	78: "Shakuhachi",
	79: "Whistle",
	80: "Ocarina",
	81: "Lead 1 (square)",
	82: "Lead 2 (sawtooth)",
	83: "Lead 3 (calliope)",
	84: "Lead 4 (chiff)",
	85: "Lead 5 (charang)",
	86: "Lead 6 (voice)",
	87: "Lead 7 (fifths)",
	88: "Lead 8 (bass + lead)",
	89: "Pad 1 (new age)",
	90: "Pad 2 (warm)",
	91: "Pad 3 (polysynth)",
	92: "Pad 4 (choir)",
	93: "Pad 5 (bowed)",
	94: "Pad 6 (metallic)",
	95: "Pad 7 (halo)",
	96: "Pad 8 (sweep)",
	97: "FX 1 (rain)",
	98: "FX 2 (soundtrack)",
	99: "FX 3 (crystal)",
	100: "FX 4 (atmosphere)",
	101: "FX 5 (brightness)",
	102: "FX 6 (goblins)",
	103: "FX 7 (echoes)",
	104: "FX 8 (sci-fi)",
	105: "Sitar",
	106: "Banjo",
	107: "Shamisen",
	108: "Koto",
	109: "Kalimba",
	110: "Bag pipe",
	111: "Fiddle",
	112: "Shanai",
	113: "Tinkle Bell",
	114: "Agogo",
	115: "Steel Drums",
	116: "Woodblock",
	117: "Taiko Drum",
	118: "Melodic Tom",
	119: "Synth Drum",
	120: "Reverse Cymbal",
	121: "Guitar Fret Noise",
	122: "Breath Noise",
	123: "Seashore",
	124: "Bird Tweet",
	125: "Telephone Ring",
	126: "Helicopter",
	127: "Applause",
	128: "Gunshot"
}

# and the other way around
midiNameAlphabet = dict((v,k) for k, v in midiAlphabet.iteritems())

def isMidiProgram(number):
	""" Returns a boolean value corresponding to the number being a valid midi program. """
	try:
		return int(number) in midiAlphabet
	except:
		return False

# Instrument categories:
# "{Category: [midiPrograms], ...}"
# might be useful for generation later
# example: 
# if instrument in instrumentGroups["Bass"]:
#	print "its a Bass-Instrument"
#	generate a bass-like part...
#
# We could also turn this into a reverse lookup table programmatically if we
# were to use it often.
instrumentGroups = {
	"Piano":[1,2,3,4,5,6,7,8],
	"Chromatic Percussion":[9,10,11,12,13,14,15,16],
	"Organ":[17,18,19,20,21,22,23,24], 
	"Guitar":[25,26,27,28,29,30,31,32],
	"Bass":[33,34,35,36,37,38,39,40],
	"Strings":[41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56],
	"Brass":[57,58,59,60,61,62,63,64],
	"Reed":[65,66,67,68,69,70,71,72],
	"Pipe":[73,74,75,76,77,78,79,80],
	"Synth Lead":[81,82,83,84,85,86,87,88],
	"Synth Pad":[89,90,91,92,93,94,95,96],
	"Synth Effects":[97,98,99,100,101,102,103,104],
	"Ethnic":[105,106,107,108,109,110,111,112],
	"Percussive":[113,114,115,116,117,118,119],
	"Sound effects":[120,121,122,123,124,125,126,127,128]
}

for group, members in (("melody", ["Piano", "Strings", "Pipe", "Guitar", "Organ", "Brass"]), ("rhythm", ["Chromatic Percussion", "Percussive", "Bass"])):
	instrumentGroups[group] = reduce(
		lambda x,y: x+y,
		map(lambda x: instrumentGroups[x], members)
	)