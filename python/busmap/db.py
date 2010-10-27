import cPickle as pickle

from sqlalchemy.types import BLOB
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, UniqueConstraint
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref, sessionmaker
from sqlalchemy.orm.exc import NoResultFound

import logging
logger = logging.getLogger('busmap.urbsweb.mapa')
dbg = logger.debug


Base = declarative_base()

class MiscKeyVal(Base):
    """Useful for simple key->value storage

    Don't abuse it. Use just for quickly testing stuff
    """
    __tablename__ = 'misc_keyval'

    key = Column(String, primary_key=True)
    type = Column(String) # a type, to allow easier filtering
    value = Column(BLOB)



class Database:
    def __init__(self, url):
        self.engine = create_engine(url)
        self.session = sessionmaker(bind=self.engine)()

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    # session shortcuts:
    def add(self, *args):
        return self.session.add(*args)
    def commit(self):
        return self.session.commit()
    def query(self, *a, **kw):
        return self.session.query(*a, **kw)


    def _keyval_query(self, key):
        return self.query(MiscKeyVal).filter_by(key=key)

    # Misc key/val funcs:
    def _put_keyval(self, type, key, value):
        dbg('storing keyval: type: %r, key: %r, value: %r', type, key, value)
        q = self._keyval_query(key)
        existing = q.first()
        if existing is not None:
            kv = existing
        else:
            kv = MiscKeyVal(key=key, type=type)
            self.add(kv)
        kv.value = value
        #self.commit()
        return kv

    def put_keyval(self, key, obj):
        val = pickle.dumps(obj)
        type = key.split('.')[0]
        self._put_keyval(type, key, val)

    def _get_keyval(self, key, default=None):
        dbg('fetching keyval: key: %r', key)
        kv = self._keyval_query(key).first()
        if kv is not None:
            dbg('keyval found: %r', kv)
            return kv.value
        dbg('keyval not found')
        return default

    def has_keyval(self, key):
        return self._keyval_query(key).count() > 0

    def get_keyval(self, key, default=None):
        v = self._get_keyval(key)
        if v is None:
            return default

        obj = pickle.loads(str(v))
        return obj

    def check_keyval(self, key, fn):
        v = self.get_keyval(key)
        if v is None:
            v = fn()
            self.put_keyval(key, v)
        return v

### OLD DEPRECATED DB CODE BEGIN

### I reinvented the wheel. I will use sqlalchemy instead

import dbutil.db
from dbutil.defs import *


def new_db(**kwargs):
	return dbutil.db.new_dbsession(kwargs)



f_linhas = [
	('id',      'int(20)', PRIMARY_KEY|AUTOINC),
	('iditi',   'varchar(16)',   CAN_NULL|INDEXME),
	('idhor',   'varchar(16)',   CAN_NULL|INDEXME),
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

### OLD DEPRECATED DB CODE END
