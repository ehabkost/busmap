# -*- coding: utf-8 -*

import horarios, linhas, env, dias


def get_linha_hor(idhor, nome):
	c = env.db.cursor()

	# look for id horario
	r = c.select_onerow('linhas', ['id'], 'idhor=%s', [idhor])
	if r:
		c.close()
		return r[0]

	# not found. look for a similar name, but with no idhor set
	r = c.select_onerow('linhas', ['id'], 'idhor is null and nome=%s', [nome])
	if r:
		id = r[0]
		# found. set idhor
		c.execute('update linhas set idhor=%s where id=%s',
			[idhor, id])
		c.close()
		return id

	# not found. insert a new record
	c.insert_one('linhas', idhor=idhor, nome=nome)
	id = c.lastrowid
	c.close()
	return id

def get_ponto_hor(nome):
	c = env.db.cursor()
	r = c.select_onerow('pontos', ['id'], 'nome=%s', nome)
	if r:
		c.close()
		return r[0]

	# not found
	c.insert_one('pontos', nome=nome)
	id = c.lastrowid
	c.close()
	return id

def fetch_horarios(idhor, nome):
	c = env.db.cursor()

	idlinha = get_linha_hor(idhor, nome)

	c.execute('delete from hs, h \
		using horsets hs, horarios h \
		where hs.idlinha=%s and h.idset=hs.id',
		[idlinha])

	html = horarios.get_horarios_html(idhor)
	for pto,dia,apartir,horas in horarios.parse_hor_html(html):
		print 'ponto: %s, dias: %s' % (pto, dia)
		idponto = get_ponto_hor(pto)
		d = dias.id_dias(dia)
		c.insert_one('horsets', idlinha=idlinha, idponto=idponto,
			dia=d, apartir=apartir)
		idset = c.lastrowid
		for sp,h in horas:
			c.insert_one('horarios',
				idset=idset, hora=h, special=sp)

	c.close()

def fetch_hor_all():
	for cod,nome in horarios.lista_linhas():
		print 'Fetching %s:%s' % (cod, nome)
		fetch_horarios(cod, nome)

if __name__ == '__main__':
	#fetch_horarios('022', u'INTER 2 (Horário)')
	fetch_hor_all()
