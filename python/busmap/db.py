import dbutil.db
from dbutil.defs import *

def new_db(**kwargs):
	return dbutil.db.new_dbsession(kwargs)



f_linhas = [
	('id',      'int(20)', PRIMARY_KEY|AUTOINC),
	('iditi',   'varchar(16)',   CAN_NULL),
	('idhor',   'varchar(16)',   CAN_NULL),
	('shortname','varchar(32)',  CAN_NULL|INDEXME),
	('nome',    'varchar(32)',   INDEXME),
]
# 'KEY `locateimport` (`uso`, `tipo`, `bairro`)'

f_pontos = [
	('id',      'int(20)', PRIMARY_KEY|AUTOINC),
	('idmapa',  'varchar(16)',   CAN_NULL),
	('nome',    'varchar(32)',   INDEXME),
]

f_ruas = [
	('id',      'int(20)', PRIMARY_KEY|AUTOINC),
	('iditi',    'varchar(16)', INDEXME|CAN_NULL),
	('nome',    'varchar(64)',  0),
]

f_horsets = [
	('id',      'int(20)',      PRIMARY_KEY|AUTOINC),
	('idlinha', 'int(20)',      0),
	('idponto', 'int(20)',      0),
	('dia',     'int(20)',      0),
	('apartir', 'varchar(16)',  0),
]

f_horarios = [
	('idset',   'int(20)',      0),
	('hora',    'char(5)',      0),
	('special', 'tinyint(1)',   0),
]

i_horarios = [
	('sethora', ('idset', 'hora'))
]

f_itinerarios = [
	('idlinha',  'int(20)',     0),
	('seq',      'int(20)',     0),
	('idrua',    'int(20)',     0),
]

i_itinerarios = [
	('linhaseq', ('idlinha', 'seq')),
]

tables = [
	('linhas', f_linhas,  []),
	('pontos', f_pontos,  []),
	('ruas', f_ruas,    []),
	('horsets',   f_horsets, []),
	('horarios', f_horarios, i_horarios),
	('itinerarios', f_itinerarios, i_itinerarios),
]

def create_tables(c):
	for name,fields,indexes in tables:
		c.def_table(name, fields, indexes)


if __name__ == '__main__':
	import dbutil.creator
	import busmap.env
	import sys
	db = busmap.env.db
	destruct = False
	if len(sys.argv) > 1 and sys.argv[1] == '-f':
		destruct = True
	c = dbutil.creator.DatabaseCreator(db, destruct)
	c.prepare()
	create_tables(c)
