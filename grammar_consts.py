# Stores constant variables and static methods for the grammar project

import math

# currently only for punctuation that is "easy to identify"--that is,
# punctuation which shows up as the last character of a word
INTERSENTENCE_PUNCT = ['.', ';', '?', '!']
INTRASENTENCE_PUNCT = [',', '-']
QUOTE_PUNCT = ['"', "'"]
PUNCT = INTERSENTENCE_PUNCT + INTRASENTENCE_PUNCT + QUOTE_PUNCT
ME = ['i', 'i\'m', 'i\'ll', 'i\'ve', 'i\'d']
TERMINAL_WIDTH = 80
# words to exclude while counting bigrams
EXCLUDE = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'yo',
                  'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
                  'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
                  'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
                  'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
                  'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
                  'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
                  'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
                  'with', 'about', 'against', 'between', 'into', 'through', 'during',
                  'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
                  'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
                  'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
                  'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
                  'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
                  's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 've', 'm'])

# increment is how much to add to the dict value
def add_to_dict(dictionary, item, increment=1):
	if (item in dictionary):
		dictionary[item] += increment
	else:
		dictionary[item] = increment

# Makes an ASCII box of width numChars around the input string, if numChars not
# provided, makes a box which fits perfectly around the string with one padding
# space on either side.
# Doesn't support word wrapping, maybe add later.
def box(inputString, numChars=0, justify='center'):
	if (not numChars):
		numChars = len(inputString) + 4
	textWidth = numChars - 4 # -4 for | and spaces
	topBottom = '+' + '-' * (numChars - 2) + '+'
	middle = ''
	# loop setup
	repeat = len(inputString) // textWidth # integer division
	reps = 0
	for i in range(repeat):
		if (inputString[(i + 1) * textWidth - 1:(i + 1) * textWidth]) != ' ':
			inputString = inputString[:(i + 1) * textWidth - 1] + '-' + \
						  inputString[(i + 1) * textWidth - 1:]
		middle += '| ' + inputString[i * textWidth:(i + 1) * textWidth] + ' |\n'
		reps += 1
	remaining = len(inputString) - reps * textWidth
	numSpaces = numChars - remaining - 2 # -2 for | on either side
	if (justify == 'center'):
		middle += '|' + ' ' * math.floor(numSpaces / 2) + inputString + \
				  ' ' * math.ceil(numSpaces / 2)
	elif (justify == 'left'):
		middle += '|' + ' ' + inputString[-remaining:] + ' ' * (numSpaces - 1)
	elif (justify == 'right'):
		middle += '|' + ' ' * (numSpaces - 1) + inputString[-remaining:] + ' '
	else:
		middle = box('You messed up the justify argument, stupid.', numChars)
	middle += '|'
	return topBottom + '\n' + middle + '\n' + topBottom











