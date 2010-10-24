import logging
import urllib2
import re

logger = logging.getLogger('busmap.urbsweb.main')
dbg = logger.debug

def url_lista(tipo):
	return "http://urbs-web.curitiba.pr.gov.br/centro/conteudo_lista_linhas.asp?l='%s'" % (tipo)

re_item = re.compile("""<option value='(.*?)'>(.*?)</option>""")
def lista_linhas(tipo):
	dbg('Listando linhas (%s)...', tipo)
	f = urllib2.urlopen(url_lista(tipo))
	s = f.read()
	for cod,nome in re_item.findall(s):
		dbg('Linha: %s:%r', cod, nome)
		yield cod, nome.decode('iso-8859-1')
