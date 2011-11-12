#!/usr/bin/env python

import cProfile
import crawler, searcher_mongo, searcher_sqlite

urlList = ['http://kiwitobes.com/wiki/Programming_language.html']
queryList = ['anything', 'something special', 'what about Google']
eta = 0.14

if __name__ == '__main__':
	try:
		# generate Mongo DB of crawled pages
		C = crawler.crawler()
		C.crawl(urlList)
	except:
		exit(1)
	
	# initialize searcher class using SQLite index for words
	Sql = searcher_sqlite.searcher() 
	Sql.initTables()
	Sql.count(eta) 
	cProfile.run('Sql.buildIndex()')

	# initialize searcher class using MongoDb index for words
	Mdb = searcher_mongo.searcher() 
	Mdb.wordsdb.drop() # kill words index if it exists
	Mdb.count(eta) 
	cProfile.run('Mdb.buildIndex()')

	for string in queryList:
		print '\nsearching Mdb for "'+string+'"'
		cProfile.run('(tokens, results) = Mdb.simpleQuery(string)')
		for r in results: print r

		print '\nsearching Sql for "'+string+'"'
		cProfile.run('(tokens, results) = Sql.simpleQuery(string)')
		for r in results: print r
		