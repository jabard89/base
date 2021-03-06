#! python

import sys, os, math, datetime, time
from argparse import ArgumentParser
import util, biofile, translate

# pK values from http://helixweb.nih.gov/emboss/html/iep.html
# pI code from Peter Collingridge, http://www.petercollingridge.co.uk/sites/files/peter/predictPI.txt

class ProteinProperties(object):
	def __init__(self):
		self.pKa     = {'D':3.9, 'E':4.3, 'H':6.1, 'C':8.3, 'Y':10.1, 'K':10.67, 'R':12, 'N-term':8, 'C-term':3.1}
		self.charges = {'D':-1,  'E':-1,  'H':1,  'C':-1,  'Y':-1,   'K':1,    'R':1,  'N-term':1, 'C-term':-1}
		#self.charges = {'D':-1, 'E':-1, 'H':1, 'K':1, 'R':1, 'N-term':1, 'C-term':-1}
		self.hydrophobicity_scales = {}
		# Hack so that we can store scale information in a file -- need better way to store.
		dir_path = os.path.dirname(os.path.realpath(__file__))
		inf = open(os.path.expanduser(dir_path+"/../data/hydrophobicity-scales.txt"),'r')
		tab = util.readTable(inf)
		scales = tab.header[1:]
		for scale in scales:
			self.hydrophobicity_scales[scale.replace('.','-')] = dict(zip(tab.col('aa'), tab.col(scale)))
		# Molecular weights of the amino acids in Da, not residues; subtract 18 for residue weight
		self.mw = {'A': 89.09, 'C': 121.16, 'E': 147.13, 'D': 133.10, 'G': 75.07, 'F': 165.19, 
			'I': 131.18, 'H': 155.16, 'K': 146.19, 'M': 149.21, 'L': 131.18, 'N': 132.12, 'Q': 146.15, 
			'P': 115.13, 'S': 105.09, 'R': 174.20, 'T': 119.12, 'W': 204.23, 'V': 117.15, 'Y': 181.19,
			'B': 132.61, 'Z': 146.64}
		inf.close()

	def _aminoAcidCharge(self, amino_acid, pH):
		proportion = 1 / (1 + 10**(pH - self.pKa[amino_acid]))
		res = None
		if self.charges[amino_acid] == 1:
			res = proportion
		else:
			res = proportion-1.0 # more clearly, -1 * (1-proportion)
		return res

	def getCharge(self, sequence, pH, include_termini=True):
		protein_charge = 0.0
		if include_termini:
			protein_charge += self._aminoAcidCharge('N-term', pH) + self._aminoAcidCharge('C-term', pH)
		for aa in self.charges.keys():
			protein_charge += sequence.count(aa) * self._aminoAcidCharge(aa, pH)
		return protein_charge

	# Molecular weight in daltons
	def getMolecularWeight(self, sequence):
		# Remove water from amino acids; add back in for full protein.
		h2o = 18.0153
		weight = sum(self.mw[aa]-h2o for aa in sequence)+h2o
		return weight
	

	def getIsoelectricPoint(self, sequence, tolerance=1e-4):
		min_pH, max_pH = 3, 13
		done = False
		n_iterations = 0
		max_iterations = 1000
		# Binary search for the pH at which the net charge is within the specified tolerance around zero.
		while not done and n_iterations<max_iterations:
			mid_pH = 0.5 * (max_pH + min_pH)
			protein_charge = self.getCharge(sequence, mid_pH)
			if protein_charge > tolerance:
				min_pH = mid_pH
			elif protein_charge < -tolerance:
				max_pH = mid_pH
			else:
				done = True
			n_iterations += 1
		return mid_pH

	def getHydrophobicityScale(self, scale):
		return self.hydrophobicity_scales[scale]
	
	def getHydrophobicity(self, sequence, scale='Kyte-Doolittle'):
		hyd_scale = self.hydrophobicity_scales[scale]
		hyd = 0.0
		n = 0
		res = 0
		for aa in hyd_scale.keys():
			naa = sequence.count(aa)
			hyd += naa*hyd_scale[aa]
			n += naa
		if n > 0:
			res = hyd/n
		return res
	
	def getComposition(self, sequence, normalize=False, aas=translate.AAs()):
		#aas = translate.AAs()
		if aas is None:
			aas = ''
		#seq_aas = aas + ''.join(sorted(list(set([aa for aa in sequence if not aa in aas]))))
		aa_counts = [(aa,sequence.count(aa)) for aa in aas]
		res = aa_counts
		if normalize:
			tot = float(sum([c for (aa,c) in aa_counts]))
			if tot>0.0:
				res = [(aa,c/tot) for (aa,c) in aa_counts]
			else:
				res = [(aa,c) for (aa,c) in aa_counts]
		return res
	
	def getLength(self, sequence, stopchr="*", gapchr="-"):
		# If there's a "*" -- usual way to put in a stop codon -- should we just report the length up to the stop?
		# Let's do that.
		if stopchr in sequence:
			seq = sequence[0:sequence.rfind(stopchr)]
		else:
			seq = sequence
		res = len(seq.replace(gapchr,''))
		return res

	def _count_vector(self, sequence, aas_list):
		res = [self.count(sequence, aas) for aas in aas_list]
		return res

	def count(self, sequence, aas):
		the_count = 0
		for aa in sequence:
			if aa in aas:
				the_count += 1
		return the_count

	def counts(self, sequence, aas_list):
		res = [self.count(sequence, aas) for aas in aas_list]
		return res

	def _nearestDistances(self, sequence, aas):
		"""Compute distances between aas."""
		# Get positions of each amino acid in the specified class
		positions = [xi for (xi,aa) in enumerate(sequence) if aa in aas]
		# Compute distances
		distances = [positions[i]-positions[i-1] for i in range(1,len(positions))]
		return distances

	def nearestDistances(self, sequence, aas_list):
		res_dict = {}
		for aas in aas_list:
			res_dict[aas] = self._nearestDistances(sequence, aas)
		return res_dict

	def _allDistances(self, sequence, aas):
		"""Compute distances between aas."""
		# Get positions of each amino acid in the specified class
		positions = [xi for (xi,aa) in enumerate(sequence) if aa in aas]
		# Compute all pairwise distances
		distances = []
		for xi in range(len(positions)-1):
			for xj in range(xi+1,len(positions)):
				distances.append(positions[xj]-positions[xi])
		return distances

	def allDistances(self, sequence, aas_list):
		res_dict = {}
		for aas in aas_list:
			res_dict[aas] = self._allDistances(sequence, aas)
		return res_dict

	def motif(self, sequence, aa_classes, symbol_map=chr):
		aa_dict = {}
		for (xi,aas) in enumerate(aa_classes):
			for aa in aas:
				aa_dict[aa] = ord('a')+xi
		mot = ''
		for aa in sequence:
			try:
				mot += symbol_map(aa_dict[aa])
			except KeyError:
				pass
		return mot

class Composition(object):
	def __init__(self, aas=translate.AAs()):
		self._aas = aas
		self._comp_dict = dict([(aa,0) for aa in self._aas]) # list of (aa, frequency) tuples
	
	def initFromList(self, tuple_list):
		self._comp_dict = dict(tuple_list)
	
	def initFromSequence(self, seq, normalize=False):
		aas = self._aas
		if aas is None:
			aas = ''
		#seq_aas = aas + ''.join(sorted(list(set([aa for aa in sequence if not aa in aas]))))
		aa_counts = [(aa,seq.count(aa)) for aa in aas]
		comp = aa_counts
		if normalize:
			tot = float(sum([c for (aa,c) in aa_counts]))
			if tot>0.0:
				comp = [(aa,c/tot) for (aa,c) in aa_counts]
		self._comp_dict = dict(comp)

	@staticmethod
	def getComposition(seq, aas=translate.AAs(), normalize=False):
		comp = Composition(aas)
		comp.initFromSequence(seq, normalize)
		return comp

	def items(self):
		return self._comp_dict.items()
	
	def normalize(self):
		tot = float(sum([c for (aa,c) in self._comp_dict.items()]))
		if tot>0.0:
			self._comp_dict = dict([(aa,c/tot) for (aa,c) in self._comp_dict.items()])
	
	def write(self, stream, header=True):
		if header:
			stream.write("aa\tproportion\n")
		for aa in sorted(self._comp_dict.keys()):
			write("{:s}\t{:1.4f}\n".format(aa, self._comp_dict[aa]))
	
	def read(self, stream, header=True):
		tab = util.readTable(stream, header=header)
		for flds in tab.dictrows:
			self._comp_dict[flds['aa']] = flds['proportion']
	
	def __getitem__(self, aa):
		return self._comp_dict[aa]

	def __str__(self):
		s = ""
		for aa in self._aas:
			s += "{:s}: {:1.2f}\n".format(aa, self._comp_dict[aa])
		return s
			


if __name__=='__main__':
	parser = ArgumentParser() #usage="%prog [-i fasta] [-s sequence]")
	parser.add_argument("-o", "--out", dest="out_fname", default=None, help="output filename")
	parser.add_argument("-i", "--in", dest="in_fname", default=None, help="input FASTA filename")
	parser.add_argument("-s", "--seq", dest="sequence", default=None, help="input sequence")
	parser.add_argument("-t", "--translate", dest="translate", action="store_true", default=False, help="translate the input sequences?")
	parser.add_argument("-b", "--begin", dest="begin_aa", type=int, default=1, help="beginning amino acid (1-based)")
	parser.add_argument("-e", "--end", dest="end_aa", type=int, default=None, help="ending amino acid (1-based, inclusive)")
	parser.add_argument("-x", "--exclude", dest="exclude", action="store_true", default=False, help="exclude rather than include begin/end region?")
	parser.add_argument("-a", "--aas", dest="aas", default=None, help="amino acids for frequency counts")
	parser.add_argument("-g", "--degap", dest="degap", action="store_true", default=False, help="remove gaps before applying begin/end coordinates?")
	parser.add_argument("-q", "--query", dest="query", default=None, help="specific sequence identifier to query")
	parser.add_argument("-m", "--merge", dest="merge", action="store_true", default=False, help="merge all sequences together?")
	parser.add_argument("--hydrophobicity-scale", dest="hydrophobicity_scale", type=str, default='Hopp-Woods', help="which hydrophobicity scale to use (Kyte-Doolittle, Hopp-Woods, Cornette, Eisenberg, Rose, Janin, Engelman-GES)")
	parser.add_argument("--pH", dest="pH", type=float, default=7.2, help="pH for charge determination")
	#parser.add_argument("-r", "--report", dest="report", action="store_true", default=False, help="write long report per protein?")
	options = parser.parse_args()
	
	info_outs = util.OutStreams(sys.stdout)
	data_outs = util.OutStreams()

	# Start up output
	if not options.out_fname is None:
		outf = open(options.out_fname,'w')
		data_outs.addStream(outf)
	else:
		# By default, write to stdout
		data_outs.addStream(sys.stdout)


	# Write out parameters
	data_outs.write("# Run started {}\n".format(util.timestamp()))
	data_outs.write("# Command: {}\n".format(' '.join(sys.argv)))
	data_outs.write("# Parameters:\n")
	optdict = vars(options)
	for (k,v) in optdict.items():
		data_outs.write("#\t{k}: {v}\n".format(k=k, v=v))
	
	pp = ProteinProperties()
	aas = None
	if not options.aas is None:
		if options.aas.lower() == 'all':
			aas = translate.AAs()
		else:
			aas = [aa for aa in options.aas]
	
	# Single sequence?
	if not options.sequence is None:
		headers = ['Input']
		seqs = [options.sequence]
	else:
		if not options.in_fname is None:
			fname = os.path.expanduser(options.in_fname)
			#print(fname)
			(headers,seqs) = biofile.readFASTA(open(fname, 'r'))
		else:
			info_outs.write("# No sequence or file provided; exiting\n")
			sys.exit()
		#print("# Found", len(seqs), "sequences")
		#print("# Found", len(headers), "headers")
	
	'''
	if options.report: # Write a long report per protein
		for (hdr, seq) in zip(headers,seqs):
			if options.degap:
				seq = seq.replace('-','')
			if not options.end_aa is None and options.end_aa<= len(seq):
				seq = seq[0:options.end_aa]
			#print options.end_aa, options.begin_aa
			seq = seq[options.begin_aa:]
			outs.write("length = {:d}\n".format(pp.getLength(seq)))
			pI = pp.getIsoelectricPoint(seq, tolerance=1e-4)
			outs.write("pI = {0}\n".format(pI))
			outs.write("charge at pH {0:1.1f} = {1:1.2f}\n".format(options.pH, pp.getCharge(seq, options.pH)))
			outs.write("charge at pH=pI = {:1.2f}\n".format(pp.getCharge(seq, pI)))
			scale = 'Kyte-Doolittle'
			outs.write("hydrophobicity ({}) = {:1.2f}\n".format(scale, pp.getHydrophobicity(seq, scale)))
			outs.write("composition:\n\taa\tcount\tproportion\n")
			for (aa,ct) in pp.getComposition(seq):
				outs.write("\t{}\t{}\t{:1.2f}\n".format(aa,ct,float(ct)/len(seq)))
	else: # Write compact
	'''
	
	data_outs.write("orf\tlength\tcharge\tpI\thydrophobicity")
	if not aas is None:
		data_outs.write("\t"+"\t".join(["f.{}".format(aa) for aa in aas])) # fractions
		data_outs.write("\t"+"\t".join(["n.{}".format(aa) for aa in aas])) # numbers
	data_outs.write("\n")
	if options.merge:
		data_outs.write("# Merging {:d} sequences into one\n".format(len(seqs)))
		seqs = [''.join(seqs)]
		headers = ["merged"]
	gap = '-'
	for (h,seq) in zip(headers,seqs):
		if options.query:
			if not options.query in h:
				continue
		if options.translate:
			seq = translate.translateRaw(seq)
		if options.degap:
			seq = seq.replace(gap,'')
		if not options.exclude:
			if not options.end_aa is None and options.end_aa <= len(seq):
				seq = seq[0:(options.end_aa)]
			seq = seq[(options.begin_aa-1):]
		else: # Exclude the sequence
			assert options.end_aa < len(seq)
			assert options.begin_aa < options.end_aa
			seq = seq[0:(options.begin_aa-1)] + seq[(options.end_aa):]
		degapped_seq = seq.replace(gap,"")
		line = "#{}\n{}\t{:d}\t{:1.4f}\t{:1.4f}\t{:1.4f}".format(h, biofile.firstField(h), pp.getLength(degapped_seq), pp.getCharge(degapped_seq, options.pH), pp.getIsoelectricPoint(degapped_seq), pp.getHydrophobicity(degapped_seq))
		if not aas is None:
			counts = Composition()
			counts.initFromSequence(degapped_seq)
			freqs = Composition()
			freqs.initFromSequence(degapped_seq)
			freqs.normalize()
			line += '\t' + '\t'.join(["{:1.4f}".format(freqs[aa]) for aa in aas]) + '\t' + '\t'.join(["{:d}".format(counts[aa]) for aa in aas])
		data_outs.write(line + '\n')
		#print("# Wrote line\n")
	if not options.out_fname is None:
		outf.close()

	
