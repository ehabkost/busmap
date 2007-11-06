# -* coding: utf-8 -*-

import botoweb

from botoweb import cgimain
from botoweb.handlers import *
from botoweb.printing import *

from botoutils.i18n import *

from busmap import dias

class BusmapHandler:
	def handle_args(self, env):
		self.env = env

class ListaLinhas(HtmlPageHandler, BusmapHandler):
	def title(self):
		return i18n(u'Linhas')
	
	def htmlbody(self):
		yield rh('<h1>%s</h1>') % (ui18n('Linhas de Ônibus'))
		yield rh('<ul>')
		c = self.env.db.cursor()
		c.exec_select('linhas', ['shortname', 'nome'], order='nome')
		for short,name in c.fetchall():
			if not short or not name: continue
			yield rh('<li><a href="%slinhas/%s">%s</a>') % (self.env.cgipath, us(short), us(name))
		yield rh('</ul>')
		c.close()

class MostraLinha(HtmlPageHandler, BusmapHandler):
	def initialize(self):
		sname = self.req.relpath

		c = self.env.db.cursor()
		try:
			r = c.select_onerow('linhas', ['id', 'nome'], 'shortname=%s', [sname])
			if not r:
				raise Exception("Linha <%s> não existe" % (sname))

			self.idlinha = r[0]
			self.nomelinha = r[1]
		finally:
			c.close()

	def title(self):
		return us('Linha: %s' % (self.nomelinha))

	def morehead(self):
		yield rh('<link rel="stylsheet" type="text/css" href="%shorario.css" />' % (self.env.rootpath))

	def htmlbody(self):
		c1 = self.env.db.cursor()
		c2 = self.env.db.cursor()
		yield rh('<h1>Linha: %s</h1>' % (us(self.nomelinha)))
		try:
			c1.execute("select hs.id,pt.nome,hs.dia,hs.apartir from \
				horsets as hs left join pontos pt on pt.id=hs.idponto \
				where idlinha=%s \
				order by pt.nome,hs.dia", [self.idlinha])
			lastpt = None
			for idhs,ponto,dia,apartir in c1.fetchall():
				c2.exec_select('horarios', ['hora', 'special'],
					'idset=%s', [idhs], order='hora')
				#FIXME: nome ponto
				if ponto <> lastpt:
					if lastpt is not None:
						yield rh('</div>')  # ponto
					yield rh('<div class="ponto">')
					yield rh('<h2>Ponto: %s</h2>') % (us(ponto))
				#FIXME: destacar dia de hoje
				yield rh('<div class="dia">') 
				yield rh('<h3>Dia: %s</h3>') % (us(dias.desc_dia(dia)))
				yield rh('<div class="hor">')
				for hora,sp in c2.fetchall():
					if sp: p,s = '<b>', '</b>'
					else: p,s = '',''
					yield rh(' %s%s%s ') % (rh(p), us(hora), rh(s))
				yield rh('</div>') # hor
				yield rh('</div>') # dia
				lastpt = ponto
		finally:
			c1.close()
			c2.close()

m = multiplexHandler
c = classHandler

handler = m({
	'linhas':m({
			'':c(ListaLinhas),
		},
		c(MostraLinha)),
},
UnknownHandler)

import busmap.env as env
import sys
cgimain.main(sys.argv, handler, env)
