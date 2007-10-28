pontos = [
	# Oyapock com:
	# Agamenon
	( (-25.438178,-49.237332),
	  (7185396.7, 677299.1),
	),
#	# Joao Pontoni
#	( (-25.436822,-49.238276),
#	  (7185549, 677206.5),
#	),
#	# Sao Jose
#	( (-25.434177,-49.239532),
#	  (7185845.4, 677086.7),
#	),
#	# Reinaldino
#	( (-25.430728,-49.24039),
#	  (7186222.6, 677007.1),
#	),


	# XV de novembro com:
	# Dr. Faivre
	( (-25.427482,-49.262202),
	  (7186620.4,674822.4)
	),


	# Kennedy com rep. argentina:
	( (-25.47776,-49.292157),
	  (7181088.38,671741.51)
	),

	# Mamoré c/ Júlio Perneta
#	( (-25.416958,-49.287543),
#	  (7187819.5365,672277.8169122152),
#	),

	# nsa aparecida c/ mario tourinho
	( (-25.449359,-49.304581),
	  (7184244.5365,670515.5712763075),
	),
]

def dif(a,b):
	return a[0]-b[0],a[1]-b[1]

def r(t):
	return float(t[0])/t[1]

for dim in 0,1:
	ratios = []
	for i in range(len(pontos)):
		for j in range(len(pontos)):
			if i == j: continue

			p1 = pontos[i]
			p2 = pontos[j]

			dg = p1[0][dim]-p2[0][dim]
			dc = p1[1][dim]-p2[1][dim]

			r = float(dg)/dc
			ratios.append(r)
			#print dg
			#print dc
			#print '-'
			#print '---'

	mi = min(ratios)
	ma = max(ratios)
	avg = sum(ratios)/len(ratios)
	dif = max(map(lambda v: abs(avg-v), ratios))

	print '   avg: %.20f   (%.20f - %.20f)' % (avg, mi, ma)
	print 'maxdif: %.20f' % (dif)
	print 'error: %.1f%%' % (dif*100/avg)
	print '-----------'
