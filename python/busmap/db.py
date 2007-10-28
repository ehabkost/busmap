import dbutil.db
from dbutil.defs import *

def new_db(**kwargs):
	return dbutil.db.new_dbsession(kwargs)



f_linhas = [
	('id',      'int(20)', PRIMARY_KEY|AUTOINC),
	('iditi',   'varchar(16)',   0),
	('idhor',   'varchar(16)',   0),
]

f_pontos = [
	('id',      'int(20)', PRIMARY_KEY|AUTOINC),
	('idmapa',  'varchar(16)',   0),
	('nome',    'varchar(32)',   0),
]

f_ruas = [
	('id',      'int(20)', PRIMARY_KEY|AUTOINC),
	('iditi',    'varchar(16)',  0),
	('nome',    'varchar(64)',  0),
]

f_horarios = [
	('idlinha', 'int(20)',      0),
	('idponto', 'int(20)',      0),
	('dia',     'int(20)',      0),
	('hora',    'char(4)',      0),
]

f_itinerarios = [
	('idlinhas', 'int(20)',     0),
	('seq',      'int(20)',     0),
	('idrua',    'int(20)',     0),
]

tables = [
	('linhas', f_linhas,  []),
	('pontos', f_pontos,  []),
	('ruas', f_ruas,    []),
	('horarios', f_horarios, []),
	('itinerarios', f_itinerarios, []),
]

def create_tables(c):
	for name,fields,indexes in tables:
		c.def_table(name, fields, indexes)


if __name__ == '__main__':
	import dbutil.creator
	import busmap.env
	db = busmap.env.db
	c = dbutil.creator.DatabaseCreator(db)
	c.prepare()
	create_tables(c)
