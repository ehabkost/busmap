
import sys, os
import urllib, urllib2
import logging
import pickle

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

    def save_map(self, x, y, raio, linha):
        data,image = self.fetch_map(linha, x, y, raio)

        self.db.put_keyval('mapdata.%s.coord_data' % (linha), data)
        self.db.put_keyval('mapdata.%s.map_image_gif' % (linha), image.read())

    def get_initial_map(self, linha):
        dbg('getting initial map for: %s', linha)
        if self.db.has_keyval('mapdata.%s.done' % (linha)):
            dbg('already on db')
            return

        self.save_map(0, 0, 250, linha)
        self.db.put_keyval('mapdata.%s.done' % (linha), True)

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
