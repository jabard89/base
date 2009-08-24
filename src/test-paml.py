#! /usr/local/bin/python

import sys, os, math, string, random, pickle
import paml, newick

if __name__=="__main__":
	seqs = ["TTGGCTAATATCAAATCAGCTAAGAAGCGCGCCATTCAGTCTGAAAAGGCTCGTAAGCACAACGCAAGCCGTCGCTCTATGATGCGTACTTTCATCAAGAAAGTATACGCAGCTATCGAAGCTGGCGACAAAGCTGCTGCACAGAAAGCATTTAACGAAATGCAACCGATCGTGGACCGTCAGGCTGCTAAAGGTCTGATCCACAAAAACAAAGCTGCACGTCATAAGGCTAACCTGACTGCACAGATCAACAAACTGGCT", \
			"TTGGCTAATATCAAATCAGCTAAGAAGCGCGCCGTTCAGTCTGAAAAGGCTCGTAAGCACAACGCAAGCCGTCGCTCTATGATGCGTACTTTCATCAAGAAAGTATACGCAGCTATCGAAGCTGGCGACAAAGCTGCTGCACTGAAAGCATTTAACGAAATGCAACCGATCGTGGACCGTCAGGCTGCTAAAGGTCTGATCCACAAAAACAAAGCTGCACGTCATAAAGCTAACCTGACTGCACAGATCAACAAACTGGCT", \
			"TTG---AATATCAAATCAGCTAAGAAGCGC------CAGTCTGTAAAGGCTCGTACGCACAACGGAAGCCGTCGATCTATGATGCGTAGTTTCATCAAGAAAGTATACGCAGCTTTCGAAGCTGGCGACAAGGCTGCTGCACAGAAAGCATTTAACGAAATGCAACCGATCGTAGACCGTCAGGCTGCTTTAGGTCTGATCCACAAAAACAAAGCTGACCGTCATAAAGCTAACCGGACTGCACAGATCAATTTACTGACT", \
			"TTG---AATATCAAATCAGCTAAGAAGCGC------CAGTCTGTAAAGGCTCGTACGCACAACGCAAGCCGTCGCTCTATGATGCGTACTTTCATCAAGAAAGTATACGCAGCTATCGAAGCTGGCGACAAAGCTGCTGCACTGAAAGCATTTAACGAAATGCAACCGATCGTGGACCGTCAGGCTGCTAAAGGTCTGATCCACAAAAACAAAGCTGACCGTCATAAAGCTAACCGGACTGCACAGATCAATTTACTGACT"]
	tree_string = "((s1,s2),s3,s4);"
	t = newick.tree.parseTree(tree_string)
	cm = paml.CodeML()
	opts = cm.getModelOptions("FMutSel-F")
	br = paml.getBranchRates(seqs, t, options=opts)
	