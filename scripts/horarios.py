import env

import re

MAIN_PAGE = 'http://www.curitiba.pr.gov.br/Servicos/Transporte/HorarioOnibus/ctba.asp'
re_item_lista = re.compile(u"""<OPTION VALUE='(.*?)'>.*?<FONT .*?>(.*?)</FONT>""",
	re.MULTILINE|re.DOTALL)

def lista_linhas():
	f = env.urlopener.open(MAIN_PAGE)
	s = f.read()
	for cod,nome in re_item_lista.findall(s):
		nome = nome.rstrip()
		yield cod,nome


for cod,nome in lista_linhas():
	print '%s\t%s' % (cod, nome)
