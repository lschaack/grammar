# Bigram model courtesy of old assignment from Dr. Jordan Boyd-Graber
import sys
import warnings
import random
import numpy.random as nrandom
import nltk
import grammar_consts as gc
import argparse
import pickle
from scipy import zeros
from scipy.stats import chisquare
from collections import Counter

# Automatically processes on initialization
class GrammarProcessor(object):
	def __init__(self, inputString, senTree, min_unigram=10, max_unigram=300):
		self.inputString = inputString
		self.counts = Counter() 			# counts of unigrams
		self.min_unigram = min_unigram		# min word observations before accepted in self.bigrams
		self.max_unigram = max_unigram		# max ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		self.begin_counts = Counter() 		# counts of unigrams which begin bigrams
		self.total = 0						# sum of every word count in counts
		self.bigrams = dict()				# counts of bigrams
		self.starters = dict()				# from sentence-starting words to probability
		self.tags = dict()					# from word to list of strings representing corresponding POS
		self.default = dict() 				# inverse tags now, from POS to words
		self.root = senTree 				# starting node of the sentence parse tree
		# for verification of chosen text, formatting visibility:
		print(gc.box('Sample text: ' + inputString[0:500] + '...', gc.TERMINAL_WIDTH, justify='left'))
		self.process()

	# start with empty sentence
	# 	going word by word:
	# 	add word to counts, ignore punctuation, add to sentence
	# 	if in intersentence punct:
	# 		set flag
	# 		add next word to starters
	# 		finalize sentence
	def process(self):
		startWords = dict()
		sentences = list()
		tokens = self.inputString.split()
		nextIsStarter = 1 # first word starts the first sentence
		sentence = ''
		for token in tokens:
			sentence += token
			if (token in gc.INTERSENTENCE_PUNCT):
				sentences.append(sentence)
				self.add_to_tree(sentence)
				sentence = ''
				nextIsStarter = 1
			else:
				sentence += ' '
				if (nextIsStarter):
					gc.add_to_dict(startWords, token)
					nextIsStarter = 0
				if (token not in gc.PUNCT):
					self.counts[token] += 1
		self.total = sum(self.counts.values())
		self.starters = self.get_prob_dict(startWords)
		self.process_bigrams(sentences)

	def add_to_tree(self, sentence):
		tokens = sentence.split() 
		tagged = nltk.pos_tag(tokens)
		currNode = self.get_root()
		for tag in tagged:
			self.add_tag(tag[0], tag[1])
			if (tag[1] not in self.default.keys()): # make sure an entry exists for the tag
				self.default[tag[1]] = dict()
			gc.add_to_dict(self.default[tag[1]], tag[0])
			currNode.insert(tag[1])
			currNode = currNode.branches[tag[1]] # get next node in tree

	def process_bigrams(self, sentences):
		# assert already processed 
		prev = ''
		bigramCounts = dict()
		for sentence in sentences:
			tokens = sentence.split()
			for token in tokens:
				if (prev): # and prev not in gc.PUNCT and word not in gc.PUNCT):
					gc.add_to_dict(bigramCounts, (prev, token))
					gc.add_to_dict(self.begin_counts, prev)
				prev = token
		self.bigrams = self.score_bigrams(bigramCounts)

	def score_bigrams(self, bigramCounts):
		scored = dict()
		for bigram in bigramCounts:
			maxCount = max(self.counts[bigram[0]], self.counts[bigram[1]])
			minCount = min(self.counts[bigram[0]], self.counts[bigram[1]])
			if any(x in gc.EXCLUDE for x in bigram):
				scored[bigram] = 1.0
			else:
				obs, ex = self.observed_and_expected(bigramCounts, bigram)
				scored[bigram] = self.chisquare_pvalue(obs, ex)
		return scored

	def observed_and_expected(self, bigramCounts, bigram):
		obs = zeros((2, 2))
		obs[0][0] = bigramCounts.get((bigram[0], bigram[1]), 0) # num both
		obs[0][1] = self.begin_counts[bigram[0]] - bigramCounts.get((bigram[0], bigram[1]), 0) # 2 w/o 1
		obs[1][0] = self.counts[bigram[0]] - bigramCounts.get((bigram[0], bigram[1]), 0) # 1 w/o 2
		obs[1][1] = self.total # num all

		# compute observed values
		total = sum(sum(val) for val in obs)
		row1 = sum(val for val in obs[0])
		row2 = sum(val for val in obs[1])
		col1 = obs[0][0] + obs[1][0]
		col2 = obs[0][1] + obs[1][1]

		# compute expected values
		ex = zeros((2, 2))
		ex[0][0] = (row1 * col1) / total
		ex[0][1] = (row1 * col2) / total
		ex[1][0] = (row2 * col1) / total
		ex[1][1] = (row2 * col2) / total

		return obs, ex

	def chisquare_pvalue(self, obs, ex):
		with warnings.catch_warnings():
			warnings.simplefilter('ignore')
			not_needed, pval = chisquare(obs, ex, 2, axis=None)
			return pval

	def add_tag(self, word, pos):
		if (word in self.tags.keys()):
			if (pos not in self.tags[word]):
				self.tags[word].append(pos)
		else:
			self.tags[word] = [pos]

	def grab_bigrams(self, prev, choice):
		result = dict()
		for key in self.bigrams.keys():
			# if prev matches the first word in bigram and following is correct POS (choice):
			if (key[0] == prev and choice in self.tags[key[1]]):
				 # weight bigrams heavily by frequency, + 1 for no division by 0
				gc.add_to_dict(result, key[1], (1 - self.bigrams[key]) * 1000 + 1)
		return result

	# get common element between chosen word and options, from jamylak's answer at:
	# https://stackoverflow.com/questions/16118621/first-common-element-from-two-lists/16118989#16118989
	# returns common element or None if none found, method entirely for readability
	def grab_common_element(self, first, second):
		return next((a for a in second if a in first), None)

	def choose_default(self, options):
		possibilities = dict()
		for option in options:
			possibilities.update(self.default[option])
		return possibilities

	# choose from any word which started a sentence in the original text
	def choose_start(self):
		return nrandom.choice(list(self.starters.keys()), p=list(self.starters.values()))

	# given a dictionary from any key to number values, returns a dictionary from
	# same keys to calculated probabilities as values 
	def get_prob_dict(self, dictionary):
		total = sum(dictionary.values())
		if (total == 0):
			print(dictionary)
		result = dict()
		for key in dictionary.keys():
			result[key] = dictionary[key] / total
		return result

	# probabilistically generates full sentence based on observed text
	def generate(self, node):
		gen = ''
		nextWord = self.choose_start()
		while (node.branches): # while the current node still has branches to traverse
			gen += nextWord + ' '
			options = {option: node.branches[option].freq for option in node.branches.keys()}
			options = self.get_prob_dict(options)

			# choose a POS from the tree based on frequency
			choice = nrandom.choice(list(options.keys()), p=list(options.values()))
			possibilities = {word: 1 for word in self.default[choice]}
			additions = self.grab_bigrams(nextWord, choice)
			# if (additions):
			# 	print('Used some bigram counts: ' + nextWord + ' --> ' + str(additions))
			possibilities.update(additions) # maybe at some point check if this is getting used
			prob_poss = self.get_prob_dict(possibilities)

			# chooses from all possibilities based on associated probabilities
			nextWord = nrandom.choice(list(prob_poss.keys()), p=list(prob_poss.values()))
			pos = self.grab_common_element(set(self.tags[nextWord]), options)
			node = node.branches[pos]
		return gen

	# get methods
	def get_starters(self):
		return self.starters

	def get_default(self):
		return self.default

	def get_counts(self):
		return self.counts

	def get_tags(self):
		return self.tags

	def get_root(self):
		return self.root

# Turns a multi-line file into one long line with splits on punctuation.
class Formatter(object):
	def __init__(self, address):
		file = open(address)
		lines = file.readlines()
		file.close()
		self.formatted = self.format_lines(lines)

	def format_lines(self, lines):
		final = ''
		for line in lines:
			tokens = line.lower().strip().split()
			# check for punctuation and split on that
			for i, token in enumerate(tokens):
				self.check_punct(tokens, i)
			# add tokens in the form of a line to a string
			newLine = ' '.join(tokens)
			final += newLine + ' '
		return final

	def check_punct(self, tokens, i):
		tokens[i] = tokens[i].replace('“', '"')
		tokens[i] = tokens[i].replace('”', '"')
		tokens[i] = tokens[i].replace('‘', '\'')
		tokens[i] = tokens[i].replace('’', '\'')
		# these are all different, they just look the same in a monospace font...
		tokens[i] = tokens[i].replace('‒', ' ‒ ')
		tokens[i] = tokens[i].replace('–', ' – ')
		tokens[i] = tokens[i].replace('—', ' — ')
		tokens[i] = tokens[i].replace('―', ' ― ')
		tokens[i] = tokens[i].replace('[', '')
		tokens[i] = tokens[i].replace(']', '')
		# here, eventually actually handle quotes instead of just getting rid of them
		tokens[i] = tokens[i].strip('\'')
		tokens[i] = tokens[i].strip('\"')
		# make sure not checking punctuation, otherwise infinite loop
		if (tokens[i][-1:] in gc.PUNCT and len(tokens[i]) > 1):
			# break into two grams (so ['becomes,'] becomes ['becomes', ','])
			tokens.insert(i + 1, (tokens[i])[-1:])
			tokens[i] = (tokens[i])[:-1]

	def get_formatted(self):
		return self.formatted

# idea from http://www.openbookproject.net/thinkcs/python/english2e/ch21.html
# tree with each node containing:
#	a string representing a part of speech (POS)
# 	a frequency representing num times that particular POS has been seen at that location in a sentence
#	a dictionary from POS strings to other SentenceTree nodes
# idea is: use as parse tree representing every sequence of P(s)OS seen in a text and with what freq.
class SentenceTree(object):
	def __init__(self, data = 'START', freq = 1):
		self.data = data
		self.freq = freq
		self.branches = dict()

	def insert(self, pos): # pos = part of speech
		if (self.branches.get(pos)):
			node = self.branches[pos]
			node.freq += 1
		else:
			self.branches[pos] = SentenceTree(data = pos)

	# different name convention for different print usage, making Java method comparison
	def toString(self, level = 0):
		ret = '.' * level + repr(self.data) + ': '+ str(self.freq) + '\n'
		if (True): # (level < 10):
			for branch in self.branches.values():
				ret += branch.toString(level + 1)
		return ret

	def __str__(self):
		return ('{' + 'data = ' + str(self.data) + ', freq = ' + str(self.freq) + '}')

	def __repr__(self):
		return '<tree node representation>'

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('filepath')
	parser.add_argument('-o', '--outname', default='output',
						help='Filename for output, so -o=innsmouth will write to ./processed/innsmouth.pkl')
	args = parser.parse_args()

	print(gc.box('Formatting...', gc.TERMINAL_WIDTH))
	# eventually check if valid filepath
	formatter = Formatter(args.filepath)
	formatted = formatter.get_formatted()
	senTree = SentenceTree() # root of final sentence tree

	print(gc.box('Processing...', gc.TERMINAL_WIDTH))
	processor = GrammarProcessor(formatted, senTree)
	print(gc.box('Number of unique words: ' + str(len(processor.get_counts())), 
			gc.TERMINAL_WIDTH, justify='right'))
	# print(processor.get_root().toString())
	# print(processor.get_starters())
	# print(processor.get_default())
	# print(processor.get_tags())

	# save the object for use by the generator
	with open('./processed/' + args.outname + '.pkl', 'wb') as outpath:
		pickle.dump(processor, outpath)
	print(gc.box('DONE', gc.TERMINAL_WIDTH))