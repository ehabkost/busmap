# -*- coding: utf-8 -*-

DIAS = (
	(0, u'Dias úteis'),
	(1, u'Sábados'),
	(2, u'Domingo / Feriado'),
)

d_cod2dia = dict([(c,n) for c,n in DIAS])
d_dia2cod = dict(DIAS)

def id_dias(s):
	return d_dia2cod[s]

def desc_dia(cod):
	return d_cod2dia[cod]
