# currently only for punctuation that is "easy to identify"--that is,
# punctuation which shows up as the last character of a word
INTERSENTENCE_PUNCT = ['.', ';', '?', '!']
INTRASENTENCE_PUNCT = [',']
QUOTE_PUNCT = ['"', "'"]
PUNCT = INTERSENTENCE_PUNCT + INTRASENTENCE_PUNCT + QUOTE_PUNCT
ME = ['i', 'i\'m', 'i\'ll', 'i\'ve', 'i\'d']

def add_to_dict(dictionary, item):
	if (item in dictionary):
		dictionary[item] += 1
	else:
		dictionary[item] = 1
	