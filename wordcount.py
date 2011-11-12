"""
Parent class for the searcher classes in each module, providing the basic interface
for determining stop words in the dataset.
"""
import pymongo
from crawler import tokenize

class wordcount:
	"""The class is should be initialized with a collection '[prefix]_index' produced by the crawler class [see crawler.py].
	wordcount.blackList is the list of most frequent words 
	"""

	def __init__(self, dbPrefix='test'):
		self._mdbcon = pymongo.Connection()		
		indexName = '_'.join([dbPrefix,'index'])
		print "main index: database collection '"+indexName+"'"
		self._indexcol = self._mdbcon[indexName]
		self.indexdb = self._indexcol[indexName]
		
		self._frequencyMap = {}
		self.blackList = []
	
	def __del__(self):
		self._mdbcon.disconnect()
	
	def count(self, eta=0.1):
		"""Counts the frequencies of all words in indexdb.
		All relative frequencies, freq/max_freq, in the interval (eta,1] correspond to highly common words, and these are stored in self.blackList on exit.
		"""
		self._frequencyMap = {}
		max_count = 0
		# get cursor of JSON structures {'words':["et","ce","tera",...]}
		cursor = self.indexdb.find({}, {'words':1})
		for jsobj in cursor:
			for w in jsobj['words']:
				self._frequencyMap[w] = 1 + self._frequencyMap.get(w, 0)
		
		freqSpec = self._frequencyMap.values()
		freqSpec.sort()
		max_freq = freqSpec[-1]
		self.blackList = []
		# for each value in the upper segment of the frequency spectrum
		# find all words with matching frequency and append these to the list.
		for freq in freqSpec:
			if freq <= max_freq * eta:
				continue
			for (w, f) in self._frequencyMap.items():
				if f == freq:
					self.blackList.append(w)	
		self.showList()
	
	def showList(self):
		"""Displays the contents of self.blackList with frequencies."""
		if len(self._frequencyMap) == 0:
			print 'the list is empty; initialize with the count() method.'
			return 
		print 'blacklist words by frequency:'
		for word in self.blackList :
			freq = self._frequencyMap.get(word, 0)
			print '%6d\t%s' % (freq, word)

# include unit tests out of laziness...
import unittest

class testAll(unittest.TestCase):
	"""Unit tests for the wordcount class."""
	eta = 0.15

	def setUp(self):
		self.C = wordcount()

	def tearDown(self):
		pass

	def test_set(self):
		self.C.count(testAll.eta)
	
	def test_show(self):
		self.C.showList()
	
if __name__ == '__main__':
	unittest.main()

	