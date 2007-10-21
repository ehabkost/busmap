import horarios

import sys

fl = sys.stdout
for cod,nome in horarios.lista_linhas():
	fl.write('%s\t%s\n' % (cod, nome))
	fl.flush()
fl.close()
