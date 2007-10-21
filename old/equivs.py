#!/usr/bin/python

equivs = {}

f = open('equivs.txt','r')
for l in f.xreadlines():
	l = l.strip()
	eqs = l.split(':')
	for i in eqs:
		equivs[i] = []
		for j in eqs:
			if i != j:
				equivs[i].append(j)
