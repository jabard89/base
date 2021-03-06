import sys, os, math, string, random, argparse
import cai, translate, util, biofile

if __name__=='__main__':
	parser = argparse.ArgumentParser(description="Assay/optimize codon sequences", usage="%(prog)s [options]")
	parser.add_argument(dest="sequence", default="", help="sequence to be assayed/optimized")
	parser.add_argument("-o", "--out", dest="out_fname", default=None, help="output filename")
	parser.add_argument("-r", "--reverse-translate", dest="reverse_translate", action="store_true", help="interpret sequences as amino acids, and convert back to codons?")
	parser.add_argument("-a", "--avoid", dest="avoid_sequence", action="store_true", help="avoid the codons in the provided sequence?")
	parser.add_argument("--species", dest="species", default="scer", help="species for identifying optimal codons")
	parser.add_argument("--min-ra", dest="min_rel_adapt", type=float, default=1.0, help="minimum relative adaptiveness for optimization")
	parser.add_argument("-s", "--seed", dest="seed", type=int, default=111, help="random-number generator seed")
	parser.add_argument("-p", "--optimize", dest="optimize", action="store_true", default=False, help="optimize the codons?")
	options = parser.parse_args()

	# Fetch sequence
	seq = options.sequence
	
	random.seed(options.seed)

	# Start up output
	info_outs = util.OutStreams([sys.stdout])
	data_outs = util.OutStreams()
	multi_outs = util.OutStreams([info_outs, data_outs])
	if not options.out_fname is None:
		outf = file(options.out_fname,'w')
		data_outs.addStream(outf)
	else:
		data_outs.addStream(sys.stdout)

	# Read sequences from a FASTA file?
	fname = os.path.expanduser(seq)
	if os.path.isfile(fname):
		(headers, seq_list) = biofile.readFASTA(fname)
		seqs = zip(headers,seq_list)
		info_outs.write("# Read {0:d} sequences from {1}\n".format(len(seqs), fname))
	else:
		seqs = [("command-line input",seq.upper())]
		info_outs.write("# Read sequence L={:d} from standard input\n".format(len(seqs[0][1])))

	# If reverse-translation is desired, do it.
	if options.reverse_translate:
		new_seqs = []
		for (h,s) in seqs:
			rev_trans_seq = translate.reverseTranslate(s)
			new_seqs.append((h,rev_trans_seq))
		seqs = new_seqs

	# Obtain gene sequence using only optimal codons
	info_outs.write("# Using optimal codons for {}\n".format(options.species))
	opt_codons = cai.getOptimalCodons(options.species)
	relad_dict = cai.getRelativeAdaptivenessValues(options.species)
	cai_fxn = cai.getCAIFunction(options.species)
	# DAD: cai.getCAI takes only log-transformed relative adaptiveness values.
	# Here, knowing that some values are == 0, add half of the minimum nonzero value.
	# Should be using some sort of better estimator!
	min_relad_value = 0.5 * min([v for v in relad_dict.values() if v>0.0])
	for k in relad_dict.keys():
		if relad_dict[k] <= 0.0:
			relad_dict[k] = min_relad_value
	ln_relad_dict = dict([(k,math.log(v)) for (k,v) in relad_dict.items()])

	# Assay the provided sequences
	for (id, seq) in seqs:
		line = "{0} Fop = {1:.4f}, CAI = {2:.4f}, GC = {3:.2f}\n".format(id, cai.getFop(seq, opt_codons), cai_fxn(seq), cai.getGC(seq))
		info_outs.write(line)

	# If optimization is desired, do it.
	if options.optimize:
		info_outs.write("# Optimizing sequences...\n")
		gc = translate.geneticCode(rna=False)
		codons = {}
		opt_codon_dict = dict([(gc[c],c) for c in opt_codons])
		opt_codon_dict['W'] = 'TGG'
		opt_codon_dict['M'] = 'ATG'

		opt_headers = []
		opt_seqs = []
		# optimize the codon sequences
		for (id, seq) in seqs:
			orig_codons = [c for c in translate.codons(seq)]
			prot_seq = translate.translate(seq)
			if not prot_seq is None:
				for aa in translate.AAs():
					codons[aa] = [c for c in translate.getCodonsForAA(aa, rna=False) if relad_dict[c] >= options.min_rel_adapt]
				opt_seq = ''
				for (aai, aa) in enumerate(prot_seq):
					#opt_seq += opt_codon_dict[aa] #random.choice(codons[aa])
					codons_to_choose_from = codons[aa]
					# If avoiding codons and we have a choice, eliminate the avoided codon.
					if options.avoid_sequence and len(codons_to_choose_from)>1:
						try:
							codons_to_choose_from.remove(orig_codons[aai])
						except ValueError: # codon to be avoided not among codon choices anyway
							pass
					opt_seq += random.choice(codons_to_choose_from)
				assert translate.translate(opt_seq) == prot_seq
				header_line = "{0} Fop = {1:.4f}, CAI = {2:.4f}, GC = {3:.2f}".format(id, cai.getFop(opt_seq, opt_codons), cai_fxn(opt_seq), cai.getGC(opt_seq))
				info_outs.write("# Optimized {}\n".format(header_line))
				opt_headers.append(header_line)
				opt_seqs.append(opt_seq)
		out_seqs = opt_seqs
		out_headers = opt_headers
		biofile.writeFASTA(out_seqs, data_outs, headers=out_headers)
	elif options.reverse_translate: # Write out sequences but don't optimize
		(out_headers,out_seqs) = zip(*seqs)
		biofile.writeFASTA(out_seqs, data_outs, headers=out_headers)


	if not options.out_fname is None:
		info_outs.write("# Wrote {0} optimized sequences to {1}\n".format(len(opt_seqs), options.out_fname))
		outf.close()


