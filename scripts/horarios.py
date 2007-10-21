import env

import re

MAIN_PAGE = 'http://www.curitiba.pr.gov.br/Servicos/Transporte/HorarioOnibus/ctba.asp'
def url_horario(cod):
	return 'http://www.curitiba.pr.gov.br/Servicos/Transporte/HorarioOnibus/HorariosOnibusUrbano.asp?LINHA='+cod

re_item_lista = re.compile(u"""<OPTION VALUE='(.*?)'>.*?<FONT .*?>(.*?)</FONT>""",
	re.MULTILINE|re.DOTALL)

def lista_linhas():
	print 'Fetching main page...'
	f = env.urlopener.open(MAIN_PAGE)
	s = f.read()
	for cod,nome in re_item_lista.findall(s):
		nome = nome.rstrip()
		print 'Found list item: %s:%s' % (cod, nome)
		yield cod,nome


def get_horarios(cod):
	print 'Getting schedules for %s' % (cod)
	f = env.urlopener.open(url_horario(cod))
	return f.read()

fl = open('linhas.txt', 'w')
linhas = list(lista_linhas())
for cod,nome in linhas:
	fl.write('%s\t%s\n' % (cod, nome))
	fl.flush()
fl.close()

for cod,nome in linhas:
	hor = get_horarios(cod)

	fh = open('hor/%s.html' % (cod), 'w')
	fh.write(hor)
	fh.close()
