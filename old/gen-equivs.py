#!/usr/bin/python

import equivs

import sys

try:
	for e in equivs.equivs[sys.argv[1]]:
		print '<a href="%s%s.htm">%s</a>' % (sys.argv[2],e,e)
except:
	sys.exit(1)
