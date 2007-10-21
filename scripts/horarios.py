import env

import re, sys, thread, time

def dbg(msg):
	#print msg
	pass

MAIN_PAGE = 'http://www.curitiba.pr.gov.br/Servicos/Transporte/HorarioOnibus/ctba.asp'
def url_horario(cod):
	return 'http://www.curitiba.pr.gov.br/Servicos/Transporte/HorarioOnibus/HorariosOnibusUrbano.asp?LINHA='+cod

re_item_lista = re.compile(u"""<OPTION VALUE='(.*?)'>.*?<FONT .*?>(.*?)</FONT>""",
	re.MULTILINE|re.DOTALL)

def lista_linhas():
	dbg('Fetching main page...')
	f = env.urlopener.open(MAIN_PAGE)
	s = f.read()
	for cod,nome in re_item_lista.findall(s):
		nome = nome.rstrip()
		dbg('Found list item: %s:%s' % (cod, nome))
		yield cod,nome


def get_horarios_html(cod):
	#print 'Getting schedules for %s' % (cod)
	f = env.urlopener.open(url_horario(cod))
	return f.read()

re_ponto = re.compile("""Ponto:(.*?)- (.*?)</small>.*?partir de: (.*?)</small>.*?<table.*?<table.*?>(.*?)</table>.*?</table>""", re.IGNORECASE|re.MULTILINE|re.DOTALL)
re_horario = re.compile("""<font .*?>(|<b><u>)([0-9]*:[0-9]*)""", re.IGNORECASE)

def parse_hor_html(html):
	def parse_ponto(s):
		for bold,h in re_horario.findall(s):
			b = len(bold) > 0
			yield b,h
		
	for ponto,dias,apartir,hor in re_ponto.findall(html):
		ponto = ponto.strip()
		dias = dias.strip()
		yield ponto,dias,apartir,parse_ponto(hor)

if __name__ == '__main__':
	fetch_lock = thread.allocate_lock()

	def fetch_horarios(cod, nome):
		global fetch_count, errors

		try:
			try:
				html = get_horarios_html(cod)

				fh = open('hor/%s.html' % (cod), 'w')
				fh.write(html)
				fh.close()

				fh = open('hor/%s.txt' % (cod), 'w')
				for pto,dias,apartir,horas in parse_hor_html(html):
					fh.write("Ponto: %s - %s\nValido a partir de: %s\n\n" \
							% (pto,dias,apartir))
					for sp,h in horas:
						if sp: bold='*'
						else: bold=''
						fh.write("%s%s " % (bold, h))
					fh.write("\n\n\n")
				fh.close()
			except Exception,e:
				errors.append( (cod, nome, e) )
				raise
		finally:
			change_fetch_count(-1)

	def change_fetch_count(d):
		global fetch_count
		fetch_lock.acquire()
		fetch_count += d
		fetch_lock.release()
		
	def wait_fetch_count(c):
		global fetch_count
		while True:
			fetch_lock.acquire()
			ct = fetch_count
			fetch_lock.release()

			if ct <= c: break
			print '\r%d          ' % (ct),
			time.sleep(0.1)

	fl = open('linhas.txt', 'w')
	linhas = list(lista_linhas())
	for cod,nome in linhas:
		fl.write('%s\t%s\n' % (cod, nome))
		fl.flush()
	fl.close()

	fetch_count = 0
	errors = []

	for cod,nome in linhas:
		print 'Waiting...'
		wait_fetch_count(250)
		print 'Starting thread for %s:%s' % (cod, nome)
		change_fetch_count(1)
		thread.start_new_thread(fetch_horarios, (cod, nome))

	wait_fetch_count(0)

	print repr(errors)
