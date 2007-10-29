# -* coding: utf-8 -*-

import botoweb

from botoweb import handlers,cgimain
from botoweb.printing import *

from botoutils.i18n import *

class BusmapHandler:
	def handle_args(self, env):
		self.env = env

class LinhasHandler(handlers.HtmlPageHandler, BusmapHandler):
	def title(self):
		return i18n(u'Linhas')
	
	def htmlbody(self):
		yield rh('<h1>%s</h1>') % (ui18n('Linhas de Ônibus'))
		yield rh('<ul>')
		c = self.env.db.cursor()
		c.exec_select('linhas', ['shortname', 'nome'], order='nome')
		for short,name in c.fetchall():
			if not short or not name: continue
			yield rh('<li><a href="linhas/%s">%s</a>') % (us(short), us(name))
		yield rh('</ul>')
		c.close()

h = {
	'linhas':LinhasHandler,
}

handler = handlers.multiplexClassHandler(h)

import busmap.env as env
import sys
cgimain.main(sys.argv, handler, env)
