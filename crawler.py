"""
Crawler infrastructure for a search engine.
"""
import pymongo
import re, urllib2, urlparse
from BeautifulSoup import BeautifulSoup

def tokenize(string):
	"""Tokenizes a string, returning a list (of strings).
	Algorithm: 
	(1) split the string along whitespace, numeric, and selected punctuation; 
	(2) squash all subsequent non-alphanumeric. 
	"""
	R1 = re.compile(r'[\d\s-]+')
	R2 = re.compile(r'\W+')
	tokens = []
	for s1 in re.split(R1, string) :
		s2 = re.sub(R2, '', s1)
		if s2 == '' : 
			continue
		tokens.append(s2.lower())
	return tokens

class crawler:
	"""Crawler for indexing webpages by recursively crawling links.
	The data is saved in a MongoDB collection named '[prefix]_index'. Each record consists of: 
	(1) the 'url', 
	(2) a list of 'links', and 
	(3) a list of 'words' obtained by tokenizing the text of the page.  
	"""
	def __init__(self, dbPrefix='test'):
		self._conn = pymongo.Connection()
		indexName = '_'.join([dbPrefix,'index'])
		print "main index: database collection '"+indexName+"'"
		self._indexcol = self._conn[indexName]
		self.indexdb = self._indexcol[indexName]
		
	def __del__(self):
		self._conn.disconnect()

	def getTextString(self, soup):
		"""Returns the text (string) element from an html node; if there is none, the node is recursively crawled and all text is concatenated.
		"""
		# strange issue: some web pages yield a soup where the 'string' 
		# attribute is entirely absent.
		if not hasattr(soup, 'string'):
			return ''
		elif soup.string == None:
			return '\n'.join([self.getTextString(t) for t in soup.contents])
		else:
			return soup.string.strip()
	
	def crawl(self, urlList, depth=2):
		"""Crawl and index (using breadth first search) a graph of web pages starting from a seed list of urls.
		"""
		for level in range(depth):
			urlQueue = []
			for url in urlList :
				print url
				# test whether it's already in the database
				if self.indexdb.find({'url': url}).count() :
					print ' ** already indexed'
					continue
				
				try:
					c = urllib2.urlopen(url)
				except urllib2.URLError:
					print ' ** could not be loaded'
					continue
			
				if c.headers.type not in ['text/html', 'text/plain'] :
					print ' **', c.headers.type, '** skipping'
					continue
				
				soup = BeautifulSoup(c.read())
		
				text = self.getTextString(soup.body)
				words = tokenize(text)
				
				links = []
				# links are the 'href' attributes of an <a> tag. 
				for link in soup.findAll('a') :
					if 'href' in dict(link.attrs) :			
						u = urlparse.urljoin(url, link['href'])
						if u.find("'") != -1:
							print ' ** ignoring', u
							continue
						# ignore any anchor components 
						u = u.split('#')[0]
						links.append(u)
						# if the url is not indexed, add to queue
						if self.indexdb.find({'url': u}).count() :
							continue
						urlQueue.append(u)
				
				rec = {'url':url, 'links':links, 'words':words}
				self.indexdb.insert(rec)

			urlList = urlQueue

# include unit tests out of laziness...
import unittest

class testTools(unittest.TestCase):
	"""Unit tests for tokenizer and crawler.getTextString."""
	src_ = 'http://kiwitobes.com/wiki/Programming_language.html'

	def setUp(self):
		curl = urllib2.urlopen(testTools.src_)
		self.soup_ = BeautifulSoup(curl.read())
		self.C = crawler()

	def tearDown(self):
		pass
		# self.C.indexdb.drop()

	def test_getTextString(self):
		print self.C.getTextString(self.soup_)
	
	def test_tokenize(self):
		string = self.C.getTextString(self.soup_)
		print '\t'.join(tokenize(string))
	
	def test_crawl(self):
		self.C.crawl([testTools.src_], 2)

class testCrawl(unittest.TestCase):
	"""Unit tests for crawler.crawl()."""

	def setUp(self):
		self.C = crawler()

	def tearDown(self):
		pass
		# self.C.indexdb.drop()

	def test_crawl(self):
		self.C.crawl([testTools.src_], 2)

if __name__ == '__main__':
	unittest.main()

