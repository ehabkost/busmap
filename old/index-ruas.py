#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import glob, re, string


def remove_acento(s):
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
	return unicode(s, 'iso-8859-1').translate(d)
	
# import equivs

dr = {}
dc = {}

re_prefix = re.compile("""^(R|AV|TV|CJ|ROD|VD|AL|EST|LRG|VL|TERMINAL|PRAÇA|TERM\. DE|TERM)\.* *""")

for l in open('lista-itin.txt','r').xreadlines():
	(cod,nome) = l.split(' ',1)
	dc[cod] = nome

for fn in glob.glob('pages/iti/*.htm'):
	cod = re.match('pages/iti/(.*)\.htm',fn).group(1)
	f = open(fn,'r')
	onpre = 0
	added = {}
	for l in f.xreadlines():
		l = l.strip()
		if not l: continue
		if l == '<pre>':
			onpre = 1
			continue
		if l == '</pre>': break
		if not onpre: continue

		if not re_prefix.match(l):
			print "No match: ",l


		key = re_prefix.sub('',l)
		if added.has_key(key): continue

		if not dr.has_key(key):
			dr[key] = (l,[])
		dr[key][1].append(cod)
		added[key] = 1

kl = dr.keys()
kl.sort()

filelist = string.lowercase + string.digits
files={}
for c in filelist:
	fn = 'index%c.htm' % (c)
	files[c] = (fn, open('pages/ruas/'+fn,'w'))

files[''] = ('index.htm', open('pages/ruas/index.htm','w'))
for fn,f in files.values():
	f.write('<html><body>\n')
	for c in filelist:
		fn = 'index%c.htm' % (c)
		f.write('<a href="%s">%c</a>|' % (fn, c))
	f.write('<br>\n')
	

codrua = 0
for k in kl:
	(nome,list) = dr[k]
	fnome = nome.replace(k,'<b>%s</b>' % (k) )
	codrua += 1

	f = open('pages/ruas/%d.htm' % (codrua), 'w')
	f.write('<html><body>\n')
	f.write('<h1>%s</h1>\n' % (fnome))
	f.write('<ul>\n')
	for c in list:
		f.write('<li><a href="../iti/%s.htm">%s</a></li>\n' % (c, dc[c]))
	f.write('</ul>\n')
	f.write('</body></html\n')
	f.close()

	inicial = remove_acento(k[0]).lower()
	fr = files[inicial][1]
	fr.write('<a href="%d.htm">%s</a><br>' % (codrua, fnome))

for fn,f in files.values():
	f.write('</html></body>\n')
