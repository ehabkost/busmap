
import sys, os
import urllib, urllib2
import logging
import pickle
import StringIO
from PIL import Image

from busmap.urbsweb import lista_linhas
from busmap.db import Database

logger = logging.getLogger('busmap.urbsweb.mapa')
dbg = logger.debug


URL_BASE = 'http://urbs-web.curitiba.pr.gov.br/centro/'
GET_COORDS_URL = URL_BASE + '/j_urbs2.asp' # no urljoin, just to keep exactly the same format

INITIAL_X = 674000
INITIAL_Y = 7180000
INITIAL_RAIO = 17000
INITIAL_CL = ''
INITIAL_CLICKPAGE = 'http://urbs-web.curitiba.pr.gov.br/centro/mostraclick.asp'

class MapRegion(object):
    def __init__(self, db, linha, name):
        self.db = db
        self.linha = linha
        self.name = name

    def _keyval(self, field):
        return 'mapdata.%s.%s.%s' % (self.linha, self.name, field)

    def val(self, field):
        """Get a field from a map image

        linha: bus line
        name: image/region name (set when it is saved)
        field: field name (e.g. coord_data, map_image_gif)
        """
        return self.db.get_keyval(self._keyval(field))

    def set_val(self, field, val):
        return self.db.put_keyval(self._keyval(field), val)

    def parse_coord_data(self):
        fields = 'minx','miny','maxx','maxy'
        data = self.val('coord_data')
        for field,val in zip(fields, data.split(';')):
            self.set_val(field, val)

    def image(self):
        img = self.val('map_image_gif')
        f = StringIO.StringIO(img)
        return Image.open(f)

class MapFetcher(object):
    def __init__(self, db):
        self.db = db

    def coords_url(self, cx, cy, raio, ll, cl, ref):
        args = dict(cx='%f' % (cx),
                    cy='%f' % (cy),
                    r='%f' % (raio),
                    ll='%d' % (ll),
                    cl=cl)
        url = '%s?%s' % (GET_COORDS_URL, urllib.urlencode(args))

        # yes, this is wrong, but this is how the original code does it:
        url += '&u='+ref
        return url

    def image_url(self, ll):
        return '%s/mapa/tmp%d.gif' % (URL_BASE, ll)

    def fetch_map(self, linha, x, y, raio):
        """Fetch map data for a bus line

        Returns a coordinate_data,image tuple.
        """
        dbg('downloading map data for linha %s', linha)

        ll = 441950 # arbitrary number. I expect to be able to reuse it on multiple requests
        url = self.coords_url(x, y, raio, ll, linha, URL_BASE)
        dbg('url: %s', url)

        coord_data = urllib2.urlopen(url).read()
        dbg('coord data: %r', coord_data)

        dbg('now will get image from: %s', self.image_url(ll))

        img = urllib2.urlopen(self.image_url(ll))

        return coord_data,img

    def save_map(self, x, y, raio, linha, name):
        data,image = self.fetch_map(linha, x, y, raio)

        self.db.put_keyval('mapdata.%s.%s.coord_data' % (linha, name), data)
        self.db.put_keyval('mapdata.%s.%s.map_image_gif' % (linha, name), image.read())

    def get_initial_map(self, linha):
        dbg('getting initial map for: %s', linha)
        if self.db.has_keyval('mapdata.%s.initial.done' % (linha)):
            dbg('already on db')
            return

        self.save_map(0, 0, 250, linha, 'initial')
        self.db.put_keyval('mapdata.%s.initial.done' % (linha), True)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    persist = sys.argv[1]
    tipolinha = sys.argv[2]

    db = Database('sqlite:///%s' % (persist))

    db.create_tables()

    linhas = db.check_keyval('lista_linhas.%s' % (tipolinha),
            lambda: list(lista_linhas(tipolinha)))

    mf = MapFetcher(db)
    for cod,nome in linhas:
        dbg('will fetch for %s: %s', cod, nome)
        mf.get_initial_map(cod)

        r = MapRegion(db, cod, 'initial')
        r.parse_coord_data()

        i = r.image()
        dbg('img size: %r', i.size)
    db.commit()
