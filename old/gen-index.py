#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import re
def make_key(s):
	d = {192: u'A', 193: u'A', 194: u'A', 195: u'A', 196: u'A', 197: u'A',
	     199: u'C', 200: u'E', 201: u'E', 202: u'E', 203: u'E', 204: u'I',
	     205: u'I', 206: u'I', 207: u'I', 209: u'N', 210: u'O', 211: u'O',
	     212: u'O', 213: u'O', 214: u'O', 216: u'O', 217: u'U', 218: u'U',
	     219: u'U', 220: u'U', 221: u'Y', 224: u'a', 225: u'a', 226: u'a',
	     227: u'a', 228: u'a', 229: u'a', 231: u'c', 232: u'e', 233: u'e',
	     234: u'e', 235: u'e', 236: u'i', 237: u'i', 238: u'i', 239: u'i',
	     241: u'n', 242: u'o', 243: u'o', 244: u'o', 245: u'o', 246: u'o',
	     248: u'o', 249: u'u', 250: u'u', 251: u'u', 252: u'u', 253: u'y',
	     255: u'y'}
	s = unicode(s, 'iso-8859-1').translate(d)
	s = re.sub('( |[^a-zA-Z0-9])+',' ',s)
	return s

d = {}
for file,type,format in [ ('onibuses.txt','Horário','hor/%s.htm'),
			  ('lista-itin.txt','Itinerário','iti/%s.htm') ]:
	f = open(file,"r")
	for l in f.xreadlines():
		l = l.strip()
		(cod,nome) = l.split(' ',1)
		key = make_key(nome)
		fn = format % (cod)
		if not d.has_key(key):
			d[key] = (nome,[])
		d[key][1].append( (type,fn) )
	f.close()

listanomes = d.keys()
listanomes.sort()

f = open('pages/index.htm','w')
f.write('<html>\n<body>\n')
for nome in listanomes:
	f.write(d[nome][0])
	for type,fn in d[nome][1]:
		f.write(' <a href="%s">%s</a>' % (fn,type))
	f.write('<br>\n')
f.write('</html>\n</body>\n')
f.close()
