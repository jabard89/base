#!/usr/bin/python
# Begin stats.py
"""Module for statistics.

Originally written by Jesse Bloom, 2004.
Expanded and maintained by D. Allan Drummond, 2004-2007."""
#
import re, math, os, string, listrank, random
#---------------------------------------------------------------------------------
class StatsError(Exception):
    """Statistics error."""

class Histogram:
	bins = [0]
	min_val = 0.0
	max_val = 1.0
	bin_width = 1.0
	extras = []

	def init(self,min_val,max_val,n_bins):
		assert n_bins > 0
		self.bins = [0]*n_bins
		self.min_val = min_val
		self.max_val = max_val
		self.bin_width = (max_val-min_val)/float(n_bins)
		self.extras = []

	def getBin(self, x):
		b = -1
		try:
			b = int((x-self.min_val)/self.bin_width)
		except TypeError:
			raise TypeError, "Value '%s' is not of usable type" % x
		return b

	def validBin(self, b):
		return b >= 0 and b < len(self.bins)

	def add(self, x):
		b = self.getBin(x)
		if self.validBin(b):
			self.bins[b] += 1
		else:
			self.extras.append(x)

	def printMe(self):
		print "%s" % self

	def __str__(self):
		rep = ''
		rep += "bin\tbin.mid\tcount\n"
		# Don't print empty bins on tails
		bin_min = None
		bin_max = None
		i = 0
		for b in self.bins:
			if b>0 and not bin_min:
				if i>0:
					bin_min = i-1
				else:
					bin_min = 0
				break
			i += 1
		i = len(self.bins)
		for b in self.bins[::-1]:
			if b>0 and not bin_max:
				if i<len(self.bins):
					bin_max = i+1
				else:
					bin_max = i
			i -= 1
		if not bin_min:
			bin_min = 0
		if not bin_max:
			bin_max = len(self.bins)

		for i in range(bin_min,bin_max):
			bin_mid = self.min_val + self.bin_width*(i+0.5)
			rep += "%d\t%f\t%d\n" % (i, bin_mid, self.bins[i])
		#if i < len(self.bins)-1:
		#	print self.bins[i+1]
		if len(self.extras)>0:
			rep += "# Extras: %s\n" % (' '.join(['%s'%s for s in self.extras]),)
		return rep

	def total(self):
		return sum(self.bins) + len(self.extras)


class Summary:
	def __init__(self):
		self.mean = None
		self.median = None
		self.sd = None
		self.se = None
		self.variance = None
		self.n = None
		self.sum = None

	def __str__(self):
		if self.n == 0:
			return "no data"
		else:
			return "mean = %1.2E, var = %1.2E, N = %d" % (self.mean, self.variance, self.n)


class Accumulator:
	def __init__(self, store=False):
		self.sum = 0.0
		self.sum_sq = 0.0
		self.n = 0
		self.store = store
		if self.store:
			self.data = []

	def add(self, x):
		self.sum += x
		self.sum_sq += x*x
		self.n += 1
		if self.store:
			self.data.append(x)

	def getMean(self):
		mean = 0.0
		if self.n > 0:
			mean = self.sum/self.n
		return mean

	def getMedian(self):
		res = None
		if self.store and self.n>0:
			res = Median(self.data)
		return res

	def getVariance(self):
		if self.n == 1:
			return 0.0
		if self.n < 1:
			return None
		mu = self.getMean()
		return (1.0/(self.n-1.0))*(self.sum_sq - self.n*mu*mu)

	def getSum(self):
		return self.sum

	def getN(self):
		return self.n

	def getSD(self):
		if self.n == 1:
			return 0.0
		if self.n < 1:
			return None
		return math.sqrt(self.getVariance())

	def getSE(self):
		if self.n == 1:
			return 0.0
		if self.n < 1:
			return None
		return self.getSD()/math.sqrt(self.n)

	def getData(self):
		res = None
		if self.store:
			res = self.data
		return res

	def getSummary(self):
		s = Summary()
		s.mean = self.getMean()
		s.n = self.getN()
		s.variance = self.getVariance()
		if not s.variance is None:
			s.sd = math.sqrt(s.variance)
			s.se = s.sd/math.sqrt(s.n)
		s.sum = self.getSum()
		s.median = self.getMedian()
		return s

def correctPValue(p_values, method="BH"):
	# DAD: implement
	adjusted_p_values = p_values[:]
	'''
	if method == "BH":
		p_values.sort(decreasing=True)

		#i <- n:1
		#o <- order(p, decreasing = TRUE)
		#ro <- order(o)
		#pmin(1, cummin(n/i * p[o]))[ro]
	'''
	return adjusted_p_values

#---------
def statsSummary(numlist):
	n = len(numlist)
	if n < 1:
		return None
	if n == 1:
		return (1, numlist[0], 0.0, 0.0)
	sum1 = sum2 = 0.0
	n = 0.0
	for x in numlist:
		assert isinstance(x, int) or isinstance(x, float)
		sum1 += x
		sum2 += x * x
		n += 1.0
	var = (1.0/(n-1.0))*(sum2 - (1/n)*sum1*sum1)
	if var < 0.0:
		var = 0.0 # Can happen, but only due to numerical problems
	m = sum1/n
	#print sum1, sum2, n, m, var
	sd = math.sqrt(var)
	se = sd/math.sqrt(n)
	return (n, m, sd, se)

def StatsSummary(numlist):
	return statsSummary(numlist)

#----------------------------------------------------------------------------
def StatsSummary2(numlist):
    """Returns summary one-variable statistics for a list of numbers.

    Call is: '(mean, median, sd, n) = StatsSummary2(numlist)'
    Any entries of 'None' or '-' are removed.
    If there are one or zero data points, just returns the number of
    data points rather than the 4-tuple.
    Returns a 4-tuple giving the mean, median, standard deviation, and
    number of data points."""
    n = len(numlist) - numlist.count(None) - numlist.count('-')
    if n <= 1:
		return n
    return (Mean(numlist), Median(numlist), StandardDeviation(numlist), n)
#---------------------------------------------------------------------------------
def Median(numlist):
    """Returns the median of a list of numbers.

    If any entries of the list are 'None' or '-', they are removed first."""
    assert isinstance(numlist, list)
    xlist = []  # make a copy of the list
    for x in numlist:
		if isinstance(x, (int, float)):
			xlist.append(x)
		elif x in [None, '-']:
			pass
		else:
			raise StatsError, "Invalid value of %r in list." % x
    if len(xlist) == 0:
		raise StatsError, "Empty list."
    xlist.sort()
    n = len(xlist)
    if n % 2 == 0: # even length list, average two middle entries
		med = xlist[n / 2] + xlist[n / 2 - 1]
		med = float(med) / 2.0
		return med
    else: # odd length list, get middle entry
		return xlist[n / 2]
#----------------------------------------------------------------------------------
def Mean(numlist):
	"""Returns the mean of a list of numbers.

	If any entries of the list are 'None' or '-', they are removed
	first."""
	mean = 0.0
	n = 0
	for x in numlist:
		assert isinstance(x, (int, float))
		mean += x
		n += 1
	if n <= 0:
		return 0.0
	return mean / float(n)
#----------------------------------------------------------------------------------
def geometricMean(numlist):
	"""Returns the geometric mean of a list of numbers.

	If any entries of the list are 'None' or '-', they are removed
	first."""
	if len(numlist)==0:
		raise StatsError, "Empty list."
	mean = 0.0
	log_sum = 0.0
	n = 0
	for x in numlist:
		if x in [None, '-']:
			continue
		assert isinstance(x, (int, float))
		if x > 0:
			log_sum += math.log(x)
			n += 1
	if n == 0:
		# Can happen if only entry is zero.
		return 0.0
	return math.exp(log_sum / float(n))
#----------------------------------------------------------------------------------
def weightedMean(numlist, weights):
	"""Returns the weighted mean of a list of numbers.

	If any entries of the list are 'None' or '-', they are removed
	first."""
	wxsum = 0.0
	wsum = 0.0

	assert len(numlist) == len(weights)

	for (x,w) in zip(numlist, weights):
		wxsum += x*w
		wsum += w
	if wsum == 0.0:
		return 0.0
	return wxsum/wsum

#--------------------------------------------------------------------------------
def Variance(numlist):
	"""Returns the sample variance of a list of numbers.
	If length is <2, then variance = 0."""
	sum1 = sum2 = 0.0
	n = 0.0
	for x in numlist:
		assert isinstance(x, int) or isinstance(x, float)
		sum1 += x
		sum2 += x * x
		n += 1.0
	if n < 2.0:
		return 0.0
	var = (1.0/n)*(sum2 - (1/n)*sum1*sum1)
	if var < 0.0: # Due to numerical problems only!
		var = 0.0
	return var
#-------------------------------------------------------------------------------
def sampleVariance(numlist):
	"""Returns the sample variance of a list of numbers.
	If length is <2, then variance = 0."""
	sum1 = sum2 = 0.0
	n = 0.0
	for x in numlist:
		assert isinstance(x, int) or isinstance(x, float)
		sum1 += x
		sum2 += x * x
		n += 1.0
	if n < 2.0:
		return 0.0
	var = (1.0/(n+1.0))*(sum2 - (1/n)*sum1*sum1)
	if var < 0.0: # Due to numerical problems only!
		var = 0.0
	return var
#-------------------------------------------------------------------------------
def StandardDeviation(numlist):
    """Returns the sample standard deviation of a list of numbers.

    If any entries of the list are 'None' or '-', they are removed first."""
    v = Variance(numlist)
    #print v
    return math.sqrt(v)
#-------------------------------------------------------------------------------
def sampleStandardDeviation(numlist):
    """Returns the sample standard deviation of a list of numbers.

    If any entries of the list are 'None' or '-', they are removed first."""
    v = sampleVariance(numlist)
    #print v
    return math.sqrt(v)
#-------------------------------------------------------------------------------
def Kendalls_Tau(xlist, ylist):
    """Calculates Kendall's tau non-parametric correlation between two variables.

    The input data is given in the two lists 'xdata' and 'ydata' which should be
    of the same length.  If entry i of either list is 'None', this entry is
    disregarded in both lists.
    Returns Kendall's partial tau, the one-tailed P-value, and the number of
    data points as a tuple: (tau, P, N).
    Includes a correction for ties.
    Based on Gibbons, JD, "Nonparametric measures of association",
    Sage University Papers, pg 15 (1983)."""
    if len(xlist) != len(ylist):
		raise StatsError, "Data sets have different lengths."
    xdata = []
    ydata = []
    for i in range(len(xlist)):
		if xlist[i] != None and ylist[i] != None:
			xdata.append(xlist[i])
			ydata.append(ylist[i])
    assert len(xdata) == len(ydata)
    assert len(xdata) <= len(xlist) - xlist.count(None)
    assert len(ydata) <= len(ylist) - ylist.count(None)
    assert len(ydata) >= len(ylist) - xlist.count(None) - ylist.count(None)
    if len(xdata) == 0:
		raise StatsError, "No valid data entries."
    n = len(xdata)
    # compute the number of concordant and discordant pairs
    conc = disc = 0.0 # concordant and discordant pairs
    for i in range(n): # loop over all pairs
		xi = xdata[i]
		yi = ydata[i]
		for j in range(i + 1, n):
			xd = xi - xdata[j]
			yd = yi - ydata[j]
			prod = xd * yd
			if prod == 0.0: # this is a tie
				continue
			elif prod > 0.0:
				conc += 1
			else:
				disc += 1
    # compute the tie correction: sum(t * t - t)
    xcopy = []
    ycopy = []
    for i in range(n):
		xcopy.append(xdata[i])
		ycopy.append(ydata[i])
    xties = yties = 0.0
    while xcopy:
		xi = xcopy[0]
		t = xcopy.count(xi)
		xties = xties + t * t - t
		while xcopy.count(xi) > 0:
			xcopy.remove(xi)
    while ycopy:
		yi = ycopy[0]
		t = ycopy.count(yi)
		yties = yties + t * t - t
		while ycopy.count(yi) > 0:
			ycopy.remove(yi)
    # Compute tau
    n = float(n)
    denom = math.sqrt((n * n - n - xties) * (n * n - n - yties))
    try:
        tau = 2.0 * (conc - disc) / denom
    except ZeroDivisionError:
		raise StatsError, "Too few entries: %r." % n
    # Compute P-value
    z = 3.0 * tau * math.sqrt(n * (n - 1.0)) / math.sqrt(2.0 * (2.0 * n + 5.0))
    prob = Prob_Z(z)
    return (tau, prob, int(n))

#-------------------------------------------------------------------------------
def Prob_Z(z):
	p = Complementary_Error_Function(z / math.sqrt(2.0))/2.0
	return p
	#if z < 0.0:
	#	return 1-p
	#else:
	#	return p
#-------------------------------------------------------------------------------
def Kendalls_Tau2(xlist, ylist):
    """Calculates Kendall's tau non-parametric correlation between two variables.

    The input data is given in the two lists 'xdata' and 'ydata' which should be
    of the same length.  If entry i of either list is 'None', this entry is
    disregarded in both lists.
    Returns Kendall's partial tau, the one-tailed P-value, and the number of
    data points as a tuple: (tau, P, N).
    Includes a correction for ties.
    Based on Numerical Recipes in C."""
    if len(xlist) != len(ylist):
		raise StatsError, "Data sets have different lengths."
    xdata = xlist
    ydata = ylist
    #for i in range(len(xlist)):
	#	if xlist[i] != None and ylist[i] != None:
	#		xdata.append(xlist[i])
	#		ydata.append(ylist[i])
    assert len(xdata) == len(ydata)
    #assert len(xdata) <= len(xlist) - xlist.count(None)
    #assert len(ydata) <= len(ylist) - ylist.count(None)
    #assert len(ydata) >= len(ylist) - xlist.count(None) - ylist.count(None)
    if len(xdata) == 0:
		raise StatsError, "No valid data entries."
    n = len(xdata)
    # compute the number of concordant and discordant pairs
    conc = disc = 0.0 # concordant and discordant pairs
    nx = ny = 0.0
    updown = 0
    for i in range(n): # loop over all pairs
		xi = xdata[i]
		yi = ydata[i]
		if xi and yi:
			for j in range(i + 1, n):
				if xdata[j] and ydata[j]:
					xd = xi - xdata[j]
					yd = yi - ydata[j]
					prod = xd * yd
					if prod != 0:
						nx += 1
						ny += 1
						if prod > 0:
							updown += 1
						else:
							updown -= 1
					else:
						if xd != 0:
							nx += 1
						if yd != 0:
							ny += 1
    # Compute tau
    n = float(n)
    denom = math.sqrt(nx*ny)
    try:
        tau = float(updown) / denom
    except ZeroDivisionError:
		raise StatsError, "Too few entries: %r." % n
    # Compute P-value
    z = 3.0 * tau * math.sqrt(n * (n - 1.0)) / math.sqrt(2.0 * (2.0 * n + 5.0))
    prob = Prob_Z(z)
    return (tau, prob, int(n))
#----------------------------------------------------------------------------------
def Kendalls_Partial_Tau(xdata, ydata, zdata):
    """Computes Kendall's partial tau of two variables controlling for a third.

    The correlation is between 'xdata' and 'ydata' controlling for 'zdata'.
    The data is given in lists that must be of the same length.
    Returns partial tau as a scalar number.
    Based on Gibbons JD, "Nonparametric measures of associations",
    Sage University Papers, pg 49 (1983)."""
    if not len(xdata) == len(ydata) == len(zdata):
		raise StatsError, "Data sets have different lengths."
    txy = Kendalls_Tau(xdata, ydata)[0]
    tyz = Kendalls_Tau(ydata, zdata)[0]
    txz = Kendalls_Tau(xdata, zdata)[0]
    partial_tau = (txy - txz * tyz) / math.sqrt((1 - txz * txz) * (1 - tyz * tyz))
    return partial_tau
#------------------------------------------------------------------------------
def pearsonCorrelation(x, y):
	"""Computes the Pearson linear correlation between two data sets.

    Call is '(r, p, n) = PearsonCorrelation(xdata, ydata)'
	The input data is given in the two lists 'xdata' and 'ydata' which
	should be
	of the same length.  If entry i of either list is 'None', this
	entry is
	disregarded in both lists.
	Returns Pearson's correlation coefficient, the two-tailed P-value,
	and the number of data points as a tuple '(r, p, n)'."""
	sum_sq_x = 0
	sum_sq_y = 0
	sum_coproduct = 0
	mean_x = x[0]
	mean_y = y[0]
	if len(x) != len(y):
		raise StatsError, "Data sets are of different lengths."
	n = len(x)
	for i in range(1,n):
		sweep = i / (i+1.0)
		delta_x = x[i] - mean_x
		delta_y = y[i] - mean_y
		sum_sq_x += delta_x * delta_x * sweep
		sum_sq_y += delta_y * delta_y * sweep
		sum_coproduct += delta_x * delta_y * sweep
		mean_x += delta_x / (i+1.0)
		mean_y += delta_y / (i+1.0)
	pop_sd_x = math.sqrt( sum_sq_x / n )
	pop_sd_y = math.sqrt( sum_sq_y / n )
	cov_x_y = sum_coproduct / n
	r = cov_x_y / (pop_sd_x * pop_sd_y)
	z = math.fabs(r) * math.sqrt(n) / math.sqrt(2.0)
	p = Prob_Z(z)
	if not (0.0 <= p <= 1.0):
		raise StatsError, "Invalid P-value of %r." % r
	return (r, p, n)

def PearsonCorrelation(xdata, ydata):
	return pearsonCorrelation(xdata, ydata)

def test_pearsonCorrelation():
	eps = 1e-6
	nv = 100
	for i in range(100):
		nv = random.randint(10,1000)
		add = random.random()
		x = [random.random() for xi in range(nv)]
		y = [random.random()+add*x[xi] for xi in range(nv)]
		(r,p,n) = PearsonCorrelation(x,y)
		(r2,p2,n2) = pearsonCorrelation2(x,y)
		print nv, r, r2
	return True
#------------------------------------------------------------------------------
def PartialPearsonCorrelation(xdata, ydata, zdata):
	"""Computes the Pearson linear correlation between two data sets controlling for a third set.

    Call is '(r, p, n) = PartialPearsonCorrelation(xdata, ydata, zdata)'
	The input data is given in the two lists 'xdata' and 'ydata' which
	should be of the same length.
	Returns Pearson's partial correlation coefficient, the two-tailed P-value,
	and the number of data points as a tuple '(r, p, n)'."""
	try:
		(rxy, dummy, n) = PearsonCorrelation(xdata, ydata)
		(ryz, dummy, n) = PearsonCorrelation(ydata, zdata)
		(rxz, dummy, n) = PearsonCorrelation(xdata, zdata)
		r = (rxy - ryz*rxz)/math.sqrt((1-ryz**2)*(1-rxz**2))
	except ZeroDivisionError:
		raise StatsError, "Standard deviation is zero."
	if not (-1.0000000001 <= r <= 1.000000001):
		raise StatsError, "Invalid correlation coefficient of %r." % r
	t = r*math.sqrt((n-3)/(1-r*r))
	z = t
	p = Prob_Z(z)
	if not (0.0 <= p <= 1.0):
		raise StatsError, "Invalid P-value of %r." % r
	return (r, p, n)
#------------------------------------------------------------------------------
def SpearmanRankCorrelation(xdata, ydata, ties="average"):
	"""Computes the nonparametric Spearman rank correlation between two data sets."""
	xranks = listrank.rank(xdata, ties=ties)
	yranks = listrank.rank(ydata, ties=ties)
	return PearsonCorrelation(xranks, yranks)

def rank(xdata, ties="average"):
	return listrank.rank(xdata, ties)

#------------------------------------------------------------------------------

def factorial(n):
	if n <= 1:
		return 1
	else:
		return n*factorial(n-1)

__factorial_cache = []
__max_factorial_cache = 100
for n in range(__max_factorial_cache):
	__factorial_cache.append(factorial(n))

def logFactorial(n):
	if n < __max_factorial_cache:
		return math.log(__factorial_cache[n])

	# Gosper's approximation to the factorial; much more accurate than Stirling's.
	res_approx = n*math.log(n)-n+math.log(math.sqrt((2*n+1/3.0)*math.pi))
	#res_exact = sum([math.log(i+1) for i in range(0,n)])
	return res_approx

def logChoose(n,k):
	#num = sum([math.log(i+1) for i in range(n-k,n)])
	#denom = log_factorial(k)
	#return num - denom
	return logFactorial(n) - (logFactorial(k)+logFactorial(n-k))

def logBinom(n,k,p):
	if p <= 0.0 or p == 1.0:
		raise StatsError, "Log factorial for p <= 0, %f" % p
	if p > 1.0:
		raise StatsError, "Log factorial for p > 1, %f" % p

	lc = logChoose(n,k)
	log_p = math.log(p)
	return lc + k*log_p + (n-k)*math.log(1.0-p)


def binomialTest(k, n, p = 0.5, exact = False):
	"""Computes the exact probability for a binomial process to produce at least
	k successes in n tries given binomial proportion p.

	Call is p = binomialTest(k, n, p=0.5, exact = False)
	Conditions are 0 < k <= n and n > 0.  If n*p and n*(1-p) > 30, a normal
	approximation is used.  Use 'exact = True' to force an exact calculation."""
	assert(k <= n)
	assert(k >= 0 and n > 0)
	n = int(n)
	k = int(k)
	p_value = 1.0

	# Trivial cases where p = 0 or p = 1
	if p == 0.0:  # Must then have k = 0
		if k > 0:
			return 0.0
		else:
			return 1.0
	if p == 1.0:  # Must then have k = n
		if k <= n:
			return 1.0

	if k == 0:
		# Probability of at least zero successes is 1
		p_value = 1.0
	elif k == n:
		# Probability of all successes
		p_value = p**n
	else:
		if not exact and n*p > 30 and n*(1-p) > 30:
			# Use normal approximation
			mu = n*p
			sd = math.sqrt(n*p*(1-p))
			z = (k-mu)/sd
			if z < 0.0:
				p_value = 1-Prob_Z(z)
			else:
				p_value = Prob_Z(z)
		else:
			p_value = p**n # The last term in the sum
			for j in range(k,n):
				# Compute logarithm of (n choose j) p^j (1-p)^ (n-j), the
				# binomial probability.  Use logarithm to avoid overflow
				# problems with potentially enormous factorials.
				log_p = logChoose(n,j) + j*math.log(p) + (n-j)*math.log(1-p)
				p_value += math.exp(log_p)
			if p_value > 1.0:
				p_value = 1.0
	return p_value
#------------------------------------------------------------------------------
def WilcoxonTest(list1, list2):
	"""Computes the Wilcoxon signed-rank probability that list1's median differs
	from list2's by the observed amount."""
	p_value = 1.0
	assert(len(list1)==len(list2))
	diffs = [b-a for (a,b) in zip(list1, list2)]
	ranks = zip([math.fabs(d) for d in diffs], range(1,len(diffs)+1))
	ranks.sort()
	W = 0.0
	for i in range(len(diffs)):
		if diffs[i] > 0:
			W += ranks[i][1]
	#print "#", W
	n = len(list1)
	mean = n*(n+1)/4.0
	stdev = math.sqrt(n*(n+1)*(2*n+1)/6.0)
	if stdev > 0:
		Z = (W - mean)/stdev
	else:
		if Median(list1) < Median(list2):
			return 0.0
		else:
			return 1.0
	p_value = Prob_Z(Z)
	return p_value

#------------------------------------------------------------------------------
def Means_Differ(pop1, pop2):
	(n1, m1, sd1, se1) = StatsSummary(pop1)
	(n2, m2, sd2, se2) = StatsSummary(pop2)
	denom = math.sqrt(se1**2 + se2**2) #sd1**2/n1 + sd2**2/n2)
	p = 1.0
	if denom > 0.0:
		z = (m1-m2)/denom
		p = Prob_Z(z)
	else: # No variance -- so just check if means differ
		if m1 != m2:
			p = 0.0
		else:
			p = 1.0
	if not (-1e-6 <= p <= 1.0+1e-6):
		raise StatsError, "Invalid P-value of %r." % p
	return p

#------------------------------------------------------------------------------
def Complementary_Error_Function(z):
    """Calculates the error function of z.

    The complementary error function of z is defined as:
    erfc(z) = 2 / sqrt(pi) * integral(e^(t^2) dt) where the integral
    is from z to infinity.
    Can be used to calculate cumulative normal probabilities: given a
    distribution with mean m and standard deviation s,
    the probability of observing x > m  when x > 0 is:
    P = 0.5 * erfc((x - m) / (s * sqrt(2)))
    Calculated according to Chebyshev fitting given by Numerical Recipes
    in C, page 220-221."""
    x = math.fabs(z)
    t = 1.0 / (1.0 + 0.5 * x)
    ans = t * math.exp(-x * x - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))))
    return ans
#--------------------------------------------------------------------------------
def Poisson(n, k):
    """Returns the Poisson probability of observing a number.

    'Poisson(n, k)' takes as input an integer n >= 0 and a real number k >= 0.0.
    Returns p, the probability of getting n counts when the average outcome
    is k, according to the Possion distribution.  Returns 'None' if there is
    an error."""
    p = math.exp(-k) * math.pow(k, n) / float(Factorial(n))
    assert 0.0 <= p <= 1.0, "Error, value of p is invalid probability: " + str(p)
    return p
#---------------------------------------------------------------------------
def Factorial(n):
    """Returns the factorial of an integer."""
    x = 1
    for i in range(1, n + 1):
		x *= i
    return x
#----------------------------------------------------------------------------------
def Choose(n, k):
	num = 1
	for i in range(n-k+1, n+1):
		num *= i
	den = Factorial(k)
	return num/den

def powerSet(s):
    d = dict(zip((1<<i for i in range(len(s))), (set([e]) for e in s) ))
    subset = set()
    yield subset
    for i in range(1, 1<<len(s)):
        subset = subset ^ d[i & -i]
        yield subset

def generateChoices(seqin,k):
	'''returns a generator which returns combinations of argument sequences without replacement
	for example generateChoices((1,2,3),2) returns a generator; calling the next()
	method on the generator will return [1,2], [1,3], [2,3] and the
	StopIteration exception.  This will not create the whole list of
	combinations in memory at once.'''
	def rloop(seqin, comb, k):
		'''recursive looping function'''
		if k>0:                   # any more sequences to process?
			for i in range(len(seqin)):
				item = seqin[i]
				newcomb=comb+[item]     # add next item to current combination
				# call rloop w/ remaining seqs, newcomb
				for item in rloop(seqin[(i+1):],newcomb,k-1): # remove this and previous items from consideration
					yield item          # seqs and newcomb
		else:                           # processing last sequence
			yield comb                  # comb finished, add to list
	return rloop(seqin,[],k)

def generateCombinations(seqin):
	'''returns a generator which returns combinations of argument sequences
	for example generateCombinations((1,2),(3,4)) returns a generator; calling the next()
	method on the generator will return [1,3], [1,4], [2,3], [2,4] and
	StopIteration exception.  This will not create the whole list of
	combinations in memory at once.'''
	def rloop(seqin,comb):
		'''recursive looping function'''
		if seqin:                   # any more sequences to process?
			for item in seqin[0]:
				newcomb=comb+[item]     # add next item to current combination
				# call rloop w/ remaining seqs, newcomb
				for item in rloop(seqin[1:],newcomb):
					yield item          # seqs and newcomb
		else:                           # processing last sequence
			yield comb                  # comb finished, add to list
	return rloop(seqin,[])


#----------------------------------------------------------------------------------
def __getAVEA(a, b, c, d):
	"""Returns the number of at-risk+outcome cases, expected number, and variance.

	   For i'th level, given risk factor ("exposure") E and outcome ("disease") D, the annotated
	   2x2 contingency table is:

	       |  E  | ~E  | Total
	   -----------------------
	     D | ai  |  bi |  m1i
	   -----------------------
	    ~D | ci  |  di |  m0i
	   -----------------------
	       | n1i | n0i |  ni

	   The Mantel-Haenszel statistic =
	     chi-squared_MH = (A - E(A))^2 / Var(A)
		              A = sum_i a_i         -- Number of disease cases associated with at-risk factor
	               E(A) = sum_i n1i*m1i/ni  -- Expected disease+at-risk cases if no association
	             Var(A) = sum_i n1i*n0i*m1i*m0i/((ni-1)*ni^2)
	"""
	assert(a>-1)
	assert(b>-1)
	assert(c>-1)
	assert(d>-1)
	m1i = a+b
	m0i = c+d
	n1i = a+c
	n0i = b+d
	ni = a+b+c+d
	v = 0.0
	ea = 0.0
	if ni<=1:
		# Avoid divide-by-zero
		ea = n1i*m1i
	else:
		v = n1i*n0i*m1i*m0i/float((ni-1)*ni*ni)
		ea = n1i*m1i/float(ni)
	return (a,v,ea)

def getSummaryMHStats(tables):
	sum_a = 0
	sum_v = 0
	sum_ea = 0
	sum_odds_num = 0
	sum_odds_den = 0

	for table in tables:
		(a1,b1,c1,d1) = table
		ni = float(sum(table))
		# Eliminate tables with ni < 1.0, as these can
		# give undefined variances.
		if ni <= 1.0:
			continue
		(a,v,ea) = __getAVEA(a1,b1,c1,d1)
		sum_a += a
		sum_v += v
		sum_ea += ea
		if ni>0.0:
			sum_odds_num += a1*d1/ni
			sum_odds_den += b1*c1/ni
	return (sum_a, sum_v, sum_ea, sum_odds_num, sum_odds_den)

def MantelHaenszelZ(a1,b1,c1,d1):
	(a,v,ea) = __getAVEA(a1,b1,c1,d1)
	z = __ZStat(a,v,ea)
	p = Prob_Z(z)
	if not (0.0 <= p <= 1.0):
		raise StatsError, "Invalid P-value of %r." % z
	return z, p

def __ZStat(a,v,ea):
	z = 0
	if v>0:
		z = (a-ea)/math.sqrt(v)
	return z

def MantelHaenszelSummaryZ(tables):
	"""Returns the score and overall

	   For i'th level, given risk factor ("exposure") E and outcome ("disease") D, the annotated
	   2x2 contingency table is:

	       |  E  | ~E  | Total
	   -----------------------
	     D | ai  |  bi |  m1i
	   -----------------------
	    ~D | ci  |  di |  m0i
	   -----------------------
	       | n1i | n0i |  ni

	   The Mantel-Haenszel statistic =
	     chi-squared_MH = (A - E(A) -0.5)^2 / Var(A)
		              A = sum_i a_i         -- Number of disease cases associated with at-risk factor
	               E(A) = sum_i n1i*m1i/ni  -- Expected disease+at-risk cases if no association
	             Var(A) = sum_i n1i*n0i*m1i*m0i/((ni-1)*ni^2)
	             0.5 is a continuity correction.

	   Because the contingency table includes information on the direction of association, but
	   the chi-squared statistic destroys this information, the quantity

	       Z = (A-E(A)-0.5)/sqrt(Var(A))

	   is instead returned, along with a probability of this Z-score assuming normality.
	"""
	(sum_a, sum_v, sum_ea, sum_odds_num, sum_odds_den) = getSummaryMHStats(tables)
	if sum_v == 0.0:
		raise StatsError, "Variance of summary M-H tables is zero; can't compute Z or P."
	z = __ZStat(sum_a,sum_v,sum_ea)
	p = Prob_Z(z)
	if not (0.0 <= p <= 1.0):
		raise StatsError, "Invalid P-value of %r (Z=%E)." % (p, z)
	return z, p

def MantelHaenszelOddsRatio(tables):
	"""Returns the score and overall

	   For i'th level, given risk factor ("exposure") E and outcome ("disease") D, the annotated
	   2x2 contingency table is:

	       |  E  | ~E  | Total
	   -----------------------
	     D | ai  |  bi |  m1i
	   -----------------------
	    ~D | ci  |  di |  m0i
	   -----------------------
	       | n1i | n0i |  ni

	   The Mantel-Haenszel odds ratio =
	     chi-squared_MH = X/Y
		              X = sum_i a_i*d_i/n_i
	                  Y = sum_i b_i*c_i/n_i
	"""
	(sum_a, sum_v, sum_ea, sum_odds_num, sum_odds_den) = getSummaryMHStats(tables)
	#print (sum_a, sum_v, sum_ea, sum_odds_num, sum_odds_den)
	if sum_odds_den==0:
		raise StatsError, "Denominator of odds ratio is zero; can't compute M-H odds ratio."
	else:
		odds_ratio = sum_odds_num/sum_odds_den
	return odds_ratio


class MHVarResult:
	"""Class for storing results of Mantel-Haenszel variance computation"""
	odds_ratio = None
	var_odds_ratio = None
	ln_odds_ratio = None
	var_ln_odds_ratio = None
	n_tables = None
	n_counts = None

def MantelHaenszelOddsRatioVariance(tables):
	"""Returns the Robins et al. variance phi_US(W) for Mantel-Haenszel odds ratio W, per
	   Robins et al. Biometrics June 42:311-323 (1986).

	       |    E    |   ~E    | Total
	   -------------------------------
	     D |   X_k   |   Y_k   |  t_k
	   -------------------------------
	    ~D | n_k-X_k | m_k-Y_k |  N_k - t_k
	   -------------------------------
	       |   n_k   |   m_k   |  N_k

		Var_US(W) = [sum_k P_k R_k/2R_t^2 + sum_k (P_k S_k + Q_k R_k)/(2 R_t S_t) + sum_k Q_k S_k/2S_t^2] (W)^2

		where

			P_k = (X_k + m_k - Y_k)/N_k
			Q_k = (Y_k + n_k - X_k)/N_k
			R_k = X_k(m_k - Y_k)/N_k
			S_k = Y_k(n_k - X_k)/N_k
			R_t  = sum_k R_k
			S_t  = sum_k S_k
			odds ratio = R_t / S_t

		Raises StatsError if either R_t or S_t = 0.
	"""
	N_t = 0
	R_t = 0
	S_t = 0
	sum_PR = 0.0
	sum_PS = 0.0
	sum_QR = 0.0
	sum_QS = 0.0
	n_tables = 0
	for table in tables:
		(X_k, Y_k, n_k_X_k, m_k_Y_k) = table
		N_k = float(X_k + Y_k + n_k_X_k + m_k_Y_k)
		if N_k <= 0:
			continue
		n_tables += 1
		P_k = (X_k + m_k_Y_k)/N_k
		Q_k = (Y_k + n_k_X_k)/N_k
		R_k = X_k*m_k_Y_k/N_k
		S_k = Y_k*n_k_X_k/N_k
		# Accumulate
		sum_PR += P_k * R_k
		sum_PS += P_k * S_k
		sum_QR += Q_k * R_k
		sum_QS += Q_k * S_k
		N_t += N_k
		R_t += R_k
		S_t += S_k
	# Now compute M-H odds ratio and variance
	if S_t <= 0.0:
		raise StatsError, "Denominator of odds ratio is zero; can't compute M-H odds ratio or variance."
	odds_ratio = R_t / S_t
	if R_t <= 0.0:
		raise StatsError, "Denominator R_t <= 0; can't compute M-H odds ratio variance."
	var_odds_ratio = (sum_PR/(2*R_t**2.0) + (sum_PS + sum_QR)/(2*R_t*S_t) + sum_QS/(2*S_t**2.0)) * odds_ratio**2.0

	res = MHVarResult()
	res.odds_ratio = odds_ratio
	res.ln_odds_ratio = math.log(odds_ratio)
	res.var_odds_ratio = var_odds_ratio
	# From Robins et al. 1986, bottom p.312
	res.var_ln_odds_ratio = var_odds_ratio/odds_ratio**2.0
	res.n_tables = n_tables
	res.n_counts = N_t
	return res

if __name__ == "__main__":
	test_pearsonCorrelation()

# End stats.py
