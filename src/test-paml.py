#! /usr/local/bin/python

import sys, os, math, string, random, pickle
import paml, newick, translate, geneutil, muscle, biofile

def test001():
	print "** Test 001 **"
	seqs = ["TTGGCTAATATCAAATCAGCTAAGAAGCGCGCCATTCAGTCTGAAAAGGCTCGTAAGCACAACGCAAGCCGTCGCTCTATGATGCGTACTTTCATCAAGAAAGTATACGCAGCTATCGAAGCTGGCGACAAAGCTGCTGCACAGAAAGCATTTAACGAAATGCAACCGATCGTGGACCGTCAGGCTGCTAAAGGTCTGATCCACAAAAACAAAGCTGCACGTCATAAGGCTAACCTGACTGCACAGATCAACAAACTGGCT", \
			"TTGGCTAATATCAAATCAGCTAAGAAGCGCGCCGTTCAGTCTGAAAAGGCTCGTAAGCACAACGCAAGCCGTCGCTCTATGATGCGTACTTTCATCAAGAAAGTATACGCAGCTATCGAAGCTGGCGACAAAGCTGCTGCACTGAAAGCATTTAACGAAATGCAACCGATCGTGGACCGTCAGGCTGCTAAAGGTCTGATCCACAAAAACAAAGCTGCACGTCATAAAGCTAACCTGACTGCACAGATCAACAAACTGGCT", \
			"TTG---AATATCAAATCAGCTAAGAAGCGC------CAGTCTGTAAAGGCTCGTACGCACAACGGAAGCCGTCGATCTATGATGCGTAGTTTCATCAAGAAAGTATACGCAGCTTTCGAAGCTGGCGACAAGGCTGCTGCACAGAAAGCATTTAACGAAATGCAACCGATCGTAGACCGTCAGGCTGCTTTAGGTCTGATCCACAAAAACAAAGCTGACCGTCATAAAGCTAACCGGACTGCACAGATCAATTTACTGACT", \
			"TTG---AATATCAAATCAGCTAAGAAGCGC------CAGTCTGTAAAGGCTCGTACGCACAACGCAAGCCGTCGCTCTATGATGCGTACTTTCATCAAGAAAGTATACGCAGCTATCGAAGCTGGCGACAAAGCTGCTGCACTGAAAGCATTTAACGAAATGCAACCGATCGTGGACCGTCAGGCTGCTAAAGGTCTGATCCACAAAAACAAAGCTGACCGTCATAAAGCTAACCGGACTGCACAGATCAATTTACTGACT"]
	tree_string = "(s4,(s1,s2),s3);"
	seq_labels=["s1","s2","s3","s4"]
	rate_tree = newick.tree.parseTree(tree_string)
	opts = paml.CodeML().getModelOptions("FMutSel-F")
	opts["RateAncestor"] = "1"
	cm = paml.CodeML("codon", opts)
	cm.loadSequences(seqs, seq_labels, tree_string)
	cm.run()
	cm.putBranchRatesOnTree(seq_labels, rate_tree)
	nodes = rate_tree.nodes
	def dNdist(x):
		return x.branch_rate.dn

	for i in range(len(nodes)-1):
		for j in range(i+1,len(nodes)):
			dist = nodes[i].measureFrom(nodes[j], dNdist)
			print nodes[i].name, nodes[j].name, dist
	print rate_tree
	print newick.tree.parseTree("%s" % rate_tree)

	cm.putAncestralSequencesOnTree(seq_labels, rate_tree)
	for n in rate_tree.nodes:
		print n.name, translate.translate(n.sequence)

def test002():
	print "** Test 002 **"
	# Tree remapping
	whole_tree = newick.tree.parseTree("((((scer,spar),smik),sbay),scas);")
	sub_tree = newick.tree.parseTree("((scer,smik),scas);")
	
	# Name nodes on whole tree
	for n in whole_tree.nodes:
		if not n.name:
			leaf_names = [x.name for x in n.leaves]
			leaf_names.sort()
			n.name = '_'.join(leaf_names)
	
	if False:
		# Only need to do this if you want more/other data.
		# Load the genes
		load_fxn = biofile.getIDFunction("vanilla")
		cdna_dicts = {}
		geneutil.readGenomesFromFile(os.path.expanduser("~/research/data/scerevisiae/saccharomyces-files.txt"), os.path.expanduser("~/bio/genomes"), cdna_dicts, 1, load_fxn)

		align_dict = pickle.load(file(os.path.expanduser("~/research/data/scerevisiae/scer-ortholog-alignments.p"),'r'))
		(nal, spec_orf_list, protal) = align_dict["YBR177C"]
		aligned_seqs = {}
		for xi in range(len(spec_orf_list)):
			(spec,orf) = spec_orf_list[xi]
			gene = cdna_dicts[spec][orf]
			prot = protal[xi]
			aligned_gene = muscle.alignGeneFromProtein(gene, prot)
			aligned_seqs[spec] = aligned_gene
		print aligned_seqs

	seq_dict = {'spar': 'ATGTCAGAAGTTTCGAAATGGCCAGCTATCAACCCGTTCCATTGGGGATACAATGGTACTGTTTCACATGTCGTCGGTGAAAATGGTTCCATCAAACTAAATTTAAAAGACAACAAGGAACAGGTTGAATTTGACGAGTTCGTTAACAAATATGTCCCAACGTTGAAGAATGGTGCTCAATTTAAATTGAGTCCTTACTTGTTCACAGGTATTTTGCAAACCCTGTACTTAAATGCTGCTGATTTCTCTAAGAAATTTCCTGTATTCTACGGCAGAGAAATTGTCAAATTCTCGGATAATGGAGTTTGTACCGCTGACTGGCTCATGGATTCCTGGAAGAAGGATTACAAACTCGATCAAAGTACTATGGGTTTCGATAAGAAAAAATTTGGTGAAGACGAGAAGGAGACGCATCCAGAAGGGTGGCCTCGTTTACAACCACGTACAAGGTATCTGAAGGATAATGAATTGGAAAATGTAAGGGAGGTTGATCTGCCCTTAGTAGTTATCCTACATGGTCTTGCTGGTGGTAGTCATGAGCCTATCATAAGATCTCTTGCTGAAAACCTCTCTCGG------AGTGGGAGATTTCAAGTGGTGGTACTAAATACTAGAGGCTGTGCACGTTCTAAAATTACAACCAGAAATTTATTTACGGCTTACCACACAATGGATATTCGTGAATTTTTGCAAAGAGAAAAGGAGAGATATCCAAATAGAAAATTATACGCTGTGGGATGCTCCTTCGGTGCTACGATGTTGGGAAACTATCTGGGAGAAGAAGGCGATAAATCTCCTTTATCTGCAGCTGCTACCCTGTGCAACCCTTGGGATCTTCTCCTTTCGGCACTTAGAATGACCGAGGATTGGTGGTCAAAGACTTTATTTTCCAAAAATATTGCCCAATTCTTAACAAGAACTGTTCAAGTTAATATGGGTGAACTAGGAGTTCCAAATGGCTCCCGTCCTGACCATCCTCCCACAGTCAAGAATCCATCTTACTATATGTTCACACCTGAAAATCTAATAAAGGCAAAAAGCTTTAAATCGAGTCTGGAATTTGATGAATTGTACACTGCGCCTGCTTTAGGCTTCCCAAATGCTATGGAATATTATAAAGCGGCCAGCTCAATAAGCAGAGTTGATACAATTCGGGTTCCTACTCTAGTTATCAATTCAAGGGATGATCCTGTTGTCGGCCCGGATCAA---CCTTACTCAATCGTGGAAAAAAATCCTCGTGTTTTGTATTGTAGAACCGACTTAGGAGGTCATTTAGCTTACCTAGATAAAGACAATAATTCGTGGGCTACCAAGGCGATTGCAGAATTCTTTACTAAGTTTGATGAATTAGTTGTA', \
				'smik': 'ATGTCAGAAGTTTCGAAATGGCCAGCTATCAACCCATTCCATTGGGGATACAATGGTACTGTTTCGCATGTTGTCGGTGAAAATGGTTCCATGAAACTAGGTTTAAAAGATAACAAGGAACAGATTGAATTTGATCAGTTCGTTAACAAATATGTTCCAAGTTTGAAGAATGGTGCTCACTTCAAATTGAGTCCTTACTTGTTCACAGGTATTTTACAAACGTTGTACTTAAACGCTGCAGACTTCTCGAAGAAATTTCCTGTATTTTATGGCAGAGAAATTATCAAATTCTCCGATAATGGAGTTTGCACCGCTGATTGGGTTATGAGCTCCTGGAAGAGGGATTACAAACTCAATCAAAGTACCATGAGCTTTGATAAAAGCAAATTCGACGGAGACGAAAAAGCGACGCATCCAGAAGGATGGCCTCGTTTACAACCACGTACAAGATATTTGAAGGATAATGAGTTAGAGGAGCTCAGAGAAATTGAGCTCCCCTTAGTAGTCATTTTGCATGGACTTGCCGGTGGCAGTCATGAACCGATCATAAGATCTCTTGCTGAAAACCTGTCTCGC------AGCGGGAAATTTCAAGTGGTGGTGCTAAATACCAGAGGTTGTGCACGCTCCAAAATTACAACCAGGAACTTATTCACGGCTTACCACACAATGGATATCCGTGAATTTTTGCAAAGAGAAAATCAAAGACATCCAAACAGAAAGTTATACGCTGTAGGATGTTCTTTTGGTGCCACCATGTTGGGGAATTATCTCGGTGAAGAAGGTGATAAATCACCTTTATCTGCAGCTGCTACCTTATGCAATCCTTGGGACCTTCTCCTTTCAGCGCTTAGAATGACCGAGGATTGGTGGTCAAAAACTTTATTTTCCAAAAATATTGCACAGTTTTTAACAAGAACCGTTCAAGTTAACATGGGTGAACTAGGAGTCCCAAACGGCTCTCATCCCGACCATCCTCCTACAGTAAAAAATCCATCCTACTATATGTTCACCCCTGAAAATTTAATAAAGGCAAAACACTTCAAATCGAGTCTGGAATTCGATGAATTGTATACTGCACCTGCTTTAGGCTTTCCAAATGCAATGGAGTATTATAAAGCAGCTAGCTCAATAAACAGAGTTGCTACAATTAAGGTTCCTACTTTAGTTATCAATTCTAGAGATGATCCTGTTGTCGGCCCAGATCAG---CCTTATTCAATTGTAGAAAAAAACCCTCGTATTTTGTATTGCGGAACCGATTTAGGGGGCCATTTAGCCTACCTAGATAATGACAATAACTCATGGGCAACTAAGGCGATTGCAGAATTCTTTACTAAATTTGATCAACTGGTTGTA', \
				'scas': 'ATGGCTTCACAATCAACATATCCACTCATTAAACCATGGAATTGGGGGTATCACGGAACCGTGACCCAAATTACCAGTAAGGAAGGTACTGTACTCATTCCATTAAAGGACAACAAAGAGGGTATTCCATTAGCAGAATTAGTTTCAAAGAATGTCCCTAGTTTAAAGGATGGTGCTAAGTTTGAGTTGAAACCTTTTTTATTCACTGGTATTTTACAAACTCTGTACCTTGGCGCAGCTGACTTTTCTAAGAAATTCCAAGTCTTTTATGGTAGAGAAATTGTGGAATTCTCAGATACTGGTGTATGTACTGCCGATTGGGTAATGCCATCTTGGAAGCAAAAATATAACTTTAATGAGAAAACATCAACTTTTGACAAGAAAGCATTCGACCTGGACGAAAAAGAAACACATCCAGACAATTGGCCTCGTTTGCAACCTCGTACCAGATACTTAAATGAAAAAGAAATGACGACTATCCACGAGGATGACAGACCATTGGTTGTTTGTTGTCATGGGTTAGCTGGTGGCTCTCACGAACCAATTATCAGATCATTGACTGAAAATCTATCTAAGGTTGGTAATGGGAAATTCCAAGTGGTTGTCCTAAATACTCGTGGCTGTGCACGTTCTAAGATTACTACTCGTAACCTATTTACTGCTTTCCATACTATGGATCTACGTGAATTTGTCAACAGAGAACACCAAAAACATCCTAACAGAAAGATTTATGCCGTTGGATTTTCATTCGGGGGTACAATGTTAGCAAATTATTTAGGAGAAGAAGGTGATAAAACTCCAATTGCATCTGCTGCAGTGTTATGTAACCCGTGGGATATGGTATTATCCGGTATGAAAACGAGAGATGATTTTTGGACAAGAACGCTATTTGCTAAGAATATTACAGATTTCTTGACTAGAATGGTTAAAGTTAATATGGCAGAATTGGAATCTCCAGATGGTTCTAAGCCTGATCACATCCCAACAGTGAAAAATCCATCTTATTATACATTTACCCAAGAAAATTTGGCAAAAGCCAAGGATTTTAAATTAATATCTGACTTTGATGACGTATTTACTGCACCTGCATTGGGTTTCAAAAACGCATTGGAGTACTACGCTGCAGCTGGGTCCATTAACAGACTACCTAATATTAAGATTCCTTTATTAGTTATCAATTCCACTGATGATCCAGTTGTTGGGCCGGATCCAATCCCAAACCATATCATAGATTCAAACAACCACCTACTGCTATGTGAAACCGATATCGGTGGCCATTTGGCATATTTGGATAAAAATAATGATTCATGGTCAACGAACCAAATCGCCAATTATTTCGACAAATTTGATGAAGTGGCATTA', \
				'sbay': 'ATGTCAGAAGTTTCAAAGTGGCCAGCTATTAACCCATTTCATTGGGGGTACAACGGTACAGTTTCACATGTCGTTGGTGGTAATGGTTCTGTGAAGTTAAGCTTGAAGAGCGATAAGGAGCAAGTCGAGTTTGATACGTTTGTTAATAAATATGTCCCGATTCTGAAAAACGGGGCCCATTATAAACTAAGTCCCTACTTGTTCACAGGTATTTTACAAACCCTATACTTGAACGCTGCTGATTTCTCAAAGAAATTTCCCGTATTTTATGGTAGAGAAATCGTCAAGTTCTCGGATGACGGTGTCTGTACTGCTGATTGGGTCATGAACTCTTGGGAAAAGGAATATGATTTCGACCAAAAGACTATGAAATTTGATACGAAGAAGTTTGGCGACGACGAAAAGGCGACGCACCCAGAAGGATGGCCTCGTTTACAACCACGTACGAGGTACCTCAGGGACGAAGAGTTGGAAGAACAGAGAAAAGTAGATCTTCCCCTAGTTATCATCCTCCATGGTCTTGCCGGAGGCAGTCATGAACCAATCATAAGATCCCTAACTGAGAACTTGTCTCGTATCGGCAATGGGAGATTCCAAGTCGTGGTGCTAAACACGAGAGGCTGTGCACGTTCTAAAATCACCACTAGAAACCTATTCACAGCTTACCACACAATGGATATCCGTGAGTTCTTGCAAAGGGAAAAAGAAAGATATCCAAACAGAAAATTATACACTGTAGGGTGCTCTTTCGGGGCTACCATGTTAGCAAACTATTTGGGTGAAGAAGGTGACAAATCACCTGTATCTGCTGCTGTTACGTTATGTAATCCTTGGGATCTTCTTCTTTCGGCACTTAGAATGACTGAAGACTGGTGGTCAAAAACTTTGTTTTCTAAAAATATTGCCCAATTTTTAACAAGAACCGTTCAAGTTAACATGGGCGAATTAGGTGTTCCAAATGGCTCTCGTCCTGACCATACACCTACAGTTAAAAATCCATCTTACTATAAGTTCACACCTGAGAATTTGATGAAGGCAAAGCGCTTTAAGTCGAGTCTCGAATTCGATGAGCTGTACACTGCACCAGCTTTGGGCTTCCCGAATGCTATGGAATATTATAAATCAGCTAGTTCAATCAACAGGGCTGATAAAATCAAGGTTCCTACTTTAGTAATCAATTCTAGAGATGATCCTGTTGTTGGCCCAGACCAA---CCTTATTCATTTGTGGAGAAGAACCCTAATATACTATTCTGTAGAACCGACCTAGGTGGCCATTTAGCCTACCTAGATAGCAACAATGATTCGTGGGTTACAAAGGCGATTTCCGAGTTCTTGAATAAGTTTGAGGAGTTAGTGTTA', 
				'scer': 'ATGTCAGAAGTTTCCAAATGGCCAGCAATCAACCCATTCCATTGGGGATACAATGGTACAGTTTCGCATATTGTCGGTGAAAATGGTTCCATTAAACTCCATTTAAAAGACAACAAGGAGCAAGTTGATTTTGACGAGTTCGCTAACAAATATGTCCCAACGTTGAAGAATGGTGCCCAATTCAAATTGAGTCCTTACTTGTTCACAGGTATTTTGCAAACTTTGTACTTAGGTGCTGCTGATTTCTCTAAGAAATTTCCTGTATTCTACGGCAGGGAAATTGTCAAATTCTCGGATGGTGGAGTTTGCACCGCTGACTGGCTCATAGATTCATGGAAAAAGGATTATGAATTCGATCAAAGTACTACGAGCTTTGATAAAAAAAAATTTGATAAAGACGAGAAGGCGACACATCCAGAAGGATGGCCTCGTTTACAACCACGTACAAGGTACCTGAAAGATAATGAGTTGGAAGAACTACGGGAGGTTGATCTACCCCTAGTAGTTATTCTACATGGTCTTGCTGGTGGTAGTCATGAGCCGATTATAAGATCTCTTGCTGAAAACCTGTCTCGC------AGTGGGAGATTTCAAGTGGTCGTCCTAAATACCAGAGGTTGTGCACGTTCCAAAATTACCACCAGAAATTTATTTACAGCTTATCACACAATGGATATTCGCGAGTTTTTGCAAAGAGAAAAGCAAAGACATCCAGATAGAAAACTATACGCTGTGGGATGCTCTTTTGGTGCTACGATGCTGGCAAACTATCTGGGAGAAGAGGGCGATAAATCACCTTTATCCGCAGCTGCTACTTTGTGCAATCCTTGGGATCTTCTCCTTTCAGCAATTAGGATGAGCCAGGATTGGTGGTCAAGAACTTTATTTTCCAAAAATATTGCGCAATTCTTAACAAGAACCGTTCAGGTTAATATGGGTGAATTAGGAGTTCCAAATGGCTCTCTCCCCGATCATCCTCCCACAGTCAAGAATCCATCTTTCTATATGTTCACGCCTGAAAATCTAATAAAGGCAAAGAGCTTTAAATCGACCCGGGAATTTGATGAAGTGTACACTGCGCCTGCTTTAGGCTTCCCAAATGCTATGGAGTATTATAAAGCGGCCAGCTCAATAAACAGAGTTGATACAATTCGGGTTCCTACCCTTGTTATCAATTCCAGGGATGATCCTGTTGTCGGCCCAGATCAA---CCATACTCAATCGTGGAAAAGAATCCTCGTATTTTGTATTGTAGAACCGATTTAGGTGGTCATTTAGCTTACCTAGATAAAGACAACAACTCGTGGGCTACCAAGGCAATTGCAGAATTTTTCACTAAGTTTGATGAATTAGTCGTA'}
	seq_labels = [x.name for x in sub_tree.leaves]
	seqs = [seq_dict[k] for k in seq_labels]
	# Run PAML
	opts = paml.CodeML().getModelOptions("FMutSel-F")
	opts["RateAncestor"] = "1"
	cm = paml.CodeML("codon", opts)
	cm.loadSequences(seqs, seq_labels, str(sub_tree))
	cm.run()
	cm.putBranchRatesOnTree(seq_labels, sub_tree)
	cm.putAncestralSequencesOnTree(seq_labels, sub_tree)
	
	# Now remap the tree.
	whole_node_dict = dict([(x.name, x) for x in whole_tree.nodes])
	sub_node_dict = dict([(x.name, x) for x in sub_tree.nodes])
	#print whole_node_dict["scer"].getMostRecentCommonAncestor(whole_node_dict["smik"]).name
	
	for i in range(len(seq_labels)-1):
		for j in range(i+1, len(seq_labels)):
			s1 = seq_labels[i]
			s2 = seq_labels[j]
			sub_mrca = sub_node_dict[s1].getMostRecentCommonAncestor(sub_node_dict[s2])
			mrca = whole_node_dict[s1].getMostRecentCommonAncestor(whole_node_dict[s2])
			sub_mrca.name = mrca.name
			print s1, s2, sub_mrca.name
		

if __name__=="__main__":
	test001()
	test002()
	


