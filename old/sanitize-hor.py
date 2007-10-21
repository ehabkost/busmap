#!/usr/bin/python

import sys, re, glob

import equivs

for fn in glob.glob('raw/hor/*.htm'):
	print fn
	cod = re.match('raw/hor/(.*)\.htm',fn).group(1)
	re_hor = re.compile('[0-9]+:[0-9]+')

	out = open('pages/hor/%s.htm' % (cod),'w')
	for e in equivs.equivs['hor/%s' % (cod)]:
		print 'equiv:',e
		out.write('<a href="../%s.htm">%s</a><br>\n' % (e,e))
	out.write('<pre>\n')
	for l in open(fn,'r').xreadlines():
		l = l.strip()

		l = re.sub('</TR>','\n',l)
		l = re.sub('<(/|)[^>]+>','',l)
		l = re.sub('&nbsp;',' ',l)
		l = re.sub(' +',' ',l)
		l = l.strip(' ')
		if l == '': continue
		if not re_hor.match(l):
			l = l+'\n'
		l = re_hor.sub(lambda x: ' %s ' % x.group(0),l)

		out.write(l)
	out.write('</pre>\n')

