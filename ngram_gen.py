# Class name and much of __init__ and count methods taken from:
# http://www.decontextualize.com/teaching/dwwp/topics-n-grams-and-markov-chains/
import sys
import random
import numpy.random as nrandom
import argparse

class NGramCounter(object):
	# n is the n in ngrams
	# address is the string address of the text file to be counted
	def __init__(self, n, address):
		self.n = n
		self.ngrams = dict()
		self.default = dict() # count of 1-grams
		self.starters = dict()
		# currently only for punctuation that is "easy to identify" that is,
		# shows up as the last character of a word
		self.cap_punct = ['.', ';', '?', '!']
		self.no_cap_punct = [',']
		self.punct = self.cap_punct + self.no_cap_punct
		# count ngrams and store count of individual words in default
		self.count(address)

	def count(self, address):
		with open(address) as file:
			lines = file.readlines()
			for line in lines:
				tokens = line.lower().strip().split()
				# check for punctuation and split on that too, also simultaneously populate self.default
				for token in tokens:
					i = tokens.index(token)
					self.check_punct(tokens, token, i)
					# populate default dictionary, unrelated to above punctuation splitting
					self.add_to_dict(self.default, token)
				# populate self.ngrams 
				for i in range(len(tokens) - self.n + 1):
					gram = tuple(tokens[i:(i + self.n)])
					self.add_to_dict(self.ngrams, gram)

	# given previous word in the output, returns probabilistically chosen next word
	def generate(self, prev):
		if (prev in self.cap_punct):
			return self.choose_start() # this is Theta(n) expensive, reduce later
		else:
			possibilities = dict()
			for key in self.ngrams.keys():
				if (key[0] == prev):
					self.add_to_dict(possibilities, key[1])
			# if there are no possibilities, use default array contain individual counts of each word instead
			if (not possibilities):
				possibilities = self.default
			# create probability array to pass to numpy sample function
			total = sum(possibilities.values())
			probs = []
			for value in possibilities.values():
				probs.append(value / total)
			# chooses from all possibilities based on associated probabilities
			next_word = nrandom.choice(list(possibilities.keys()), p=probs)
			return next_word

	# choose from any word which started a sentence in the original text
	def choose_start(self):
		total = sum(self.starters.values())
		probs = []
		for value in self.starters.values():
			probs.append(value / total)
		start = nrandom.choice(list(self.starters.keys()), p=probs)
		return start.title() # ensure correct capitalization

	# checks for punctuation at given index and handles token splitting if something is found
	def check_punct(self, tokens, token, i):
		# make sure not checking punctuation, otherwise infinite loop
		if (tokens[i][-1:] in self.punct and len(token) > 1): 
			# use cap_punct to identify which words start a sentence and with what frequency
			if (tokens[i][-1:] in self.cap_punct):
				# check if appropriate index exists
				if (len(tokens) > i + 1):
					self.add_to_dict(self.starters, tokens[i + 1]) 
			# break into two grams (so ['becomes,'] --> ['becomes', ','])
			tokens.insert(i + 1, (tokens[i])[-1:])
			tokens[i] = (tokens[i])[:-1]
			# add punctuation to default dictionary
			self.add_to_dict(self.default, tokens[i + 1])

	def add_to_dict(self, dict, item):
		if (item in dict):
			dict[item] += 1
		else:
			dict[item] = 1

	def get_ngrams(self):
		return self.ngrams

	def get_default(self):
		return self.default

	def get_starters(self):
		return self.starters

	def get_punct(self):
		return self.punct

# produce parse tree assuming every sentence seen is correct
# eventual flow:
#	looks for stored grammar file, fills one out if nonexistent
#		* -o or --overwrite option to regenerate file even if it exists
#	grammar is combination of ngrams, default dicts, and associated parse tree
#	perhaps take huge sample of stories/speeches/etc. from many authors as a
#		basis for comparison, then use chi-squared test to create especially
#		'given author-y' sentences which leverage deviation from average use of
#		English language.
#	so, eventually, essentially separate big processor which I can make more
#		efficient

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('filepath')
	parser.add_argument('-n', '--ngram', type=int, default=3,
						help='Number of _grams to read, 2 = bigram, 3 = trigram, etc.')
	parser.add_argument('-l', '--length', type=int, default=10,
						help='Number of words to generate')
	parser.add_argument('-r', '--repeat', type=int, default=10,
						help='Number of phrases of length l to generate')
	args = parser.parse_args()

	test_grams = NGramCounter(args.ngram, args.filepath)
	ngrams = test_grams.get_ngrams()
	for ngram in ngrams.keys():
		count = ngrams[ngram]
		if (count > 1):
			print(' '.join(ngram) + ": " + str(count))
	print('num unique words: ' + str(len(test_grams.get_default()))) # num unique 

	# create phrases/sentences
	length = args.length
	punct = test_grams.get_punct()
	for i in range(args.repeat):
		title_length = length
		word = test_grams.choose_start()
		title = word
		for j in range(title_length):
			next_word = test_grams.generate(word)
			# make sure it looks pretty
			if next_word in punct:
				title += next_word
			else:
				title += ' ' + next_word
			word = next_word
		print(title)

	# some good ones:
	# Poe Autogenerator
	# The Conqueror Worm Man
	# An Enigma Frenchman Wears His Discovery Song

	# King Autogenerator 
	# Danse Macabre Goes to the Dome Movies
	# Memoir of Bad
	# the Choo-Choo	

	# Innsmouth full text:
	# Church Green, the night wore this space before eight o’clock coach and do
	# 	that brier-choked railway station and shadowed seaport of the second
	#	room—bolt the firemen would not complete. Walking softly to overcome
	#	their first to him I groped my own great-great-grandfather? Well, then, boy?