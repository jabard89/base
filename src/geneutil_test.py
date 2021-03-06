import time, os, random, string, sys, math, traceback, unittest
import geneutil


class test001(unittest.TestCase):
	def test_longest_run(self):
		"""Longest run testcases"""
		self.assertTrue(geneutil.longestRun('AAAAA','A')==5)
		self.assertTrue(geneutil.longestRun('AAATAA','A',1)==6)
		self.assertTrue(geneutil.longestRun('AAATTAA','A',1)==3)
		self.assertTrue(geneutil.longestRun('AAATTAA','A',2)==7)
		self.assertTrue(geneutil.longestRun('TAAATAA','A',1)==6)
		self.assertTrue(geneutil.longestRun('TAAATAAT','A',1)==6)

	def test_longest_run_mult(self):
		"""Longest run testcases with more than one target"""
		self.assertTrue(geneutil.longestRun('QQQQN','QN')==5)
		self.assertTrue(geneutil.longestRun('QQANNQ','QN',1)==6)
		self.assertTrue(geneutil.longestRun('QQNPPQ','QN',1)==3)
		self.assertTrue(geneutil.longestRun('QQQAANN','QN',2)==7)
		self.assertTrue(geneutil.longestRun('ANQNQAN','QN',1)==6)
		self.assertTrue(geneutil.longestRun('ANQNQANP','QN',1)==6)
	
	def test_max_sliding_count(self):
		"""Max Sliding Count testcases"""
		self.assertTrue(geneutil.maxSlidingCount('AAAAA','A')==5)
		self.assertTrue(geneutil.maxSlidingCount('AAAAA','Q')==0)
		self.assertTrue(geneutil.maxSlidingCount('AAATAA','A')==4)
		self.assertTrue(geneutil.maxSlidingCount('AAATTAA','A')==3)
		self.assertTrue(geneutil.maxSlidingCount('MMMMMMMMMMABCABCABCDM','M',10)==10)
		self.assertTrue(geneutil.maxSlidingCount('MMMMMMMMMMABCABCABCDM','C',10)==3)

class test002(unittest.TestCase):
	def test_gapped_find(self):
		"""Gapped-find testcases"""
		self.assertTrue(geneutil.gappedFind('AAASS--SAA','SSS')==3)
		self.assertTrue(geneutil.gappedFind('AAASS--SAA','SSSS')==-1)
		#print geneutil.gappedFind('AAASS--SAA','SSS',start=False)
		self.assertTrue(geneutil.gappedFind('AAASS--SAA','SSS',start=False)==8)
		self.assertTrue(geneutil.gappedFind('AAASSxxSAA','SSS',start=False)==-1)
		self.assertTrue(geneutil.gappedFind('AAASSxxSAA','SSS',start=False,gap='x')==8)

class test003(unittest.TestCase):
	def test_gapped_index(self):
		seq1 = '----AAAA'
		seq2 = 'A---AA'
		self.assertTrue(geneutil.getGappedIndex(seq1, 3)==7)
		self.assertTrue(geneutil.getGappedIndex(seq2, 2)==5)

class test004(unittest.TestCase):
	def test_entropy(self):
		"""Entropy of a homopolymer"""
		seq1 = 'AAAA'
		res = geneutil.sequenceEntropy(seq1)
		self.assertAlmostEqual(res.entropy,0.0)
		self.assertTrue(res.counts['A']==4)
	def test_max_entropy(self):
		"""Maximum possible entropy"""
		seq1 = 'ACDEFGHIKLMNPQRSTVWY'
		res = geneutil.sequenceEntropy(seq1,base=20)
		self.assertAlmostEqual(res.entropy,1.0)
		for aa in seq1:
			self.assertTrue(res.counts[aa]==1)

if __name__=="__main__":
	unittest.main(verbosity=2)
