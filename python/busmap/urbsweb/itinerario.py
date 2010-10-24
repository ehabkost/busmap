import env

import re, urllib

from busmap.urbsweb import *

NORMAL='n'
ESPECIAL='e'

def url_itinerario(cod, nome):
	return "http://urbs-web.curitiba.pr.gov.br/centro/lista_ruas.asp?l=%s&nl=%s" % (cod, urllib.quote(nome))

re_rua = re.compile("""<option value='(.*?)'>(.*?)</option>""")

def get_itinerario(cod, nome):
	print 'Listando ruas para %s:%s' % (cod, nome)
	u = url_itinerario(cod, nome)
	print 'URL: %s' % (u)
	f = env.urlopener.open(u)
	s = f.read()
	for cr,rua in re_rua.findall(s):
		print 'Rua: %s:%s' % (cr,rua)
		yield cr,rua


fl = open('itinerarios.txt', 'w')
linhas = {}
for tipo in NORMAL,ESPECIAL:
	linhas[tipo] = list(lista_linhas(tipo))
	for cod,nome in linhas[tipo]:
		fl.write('%s\t%s\n' % (cod,nome))
fl.close()

errors=[]
for tipo in NORMAL,ESPECIAL:
	for cod,nome in linhas[tipo]:
		fi = open('iti/%s.txt' % (cod), 'w')
		try:
			iti = list(get_itinerario(cod, nome))
			for cr,rua in iti:
				fi.write('%s\t%s\n' % (cr, rua))
			fi.close()
		except:
			print 'Erro em %s:%s' % (cod,nome)
			errors.append( (cod,nome) )


if errors:
	print 'ERROS:'
	print repr(errors)
