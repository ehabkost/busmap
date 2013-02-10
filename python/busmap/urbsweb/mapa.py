
import sys, os, random
import urllib, urllib2
import logging
import pickle
import StringIO
from PIL import Image

from busmap.urbsweb import lista_linhas
from busmap.db import Database

logger = logging.getLogger('busmap.urbsweb.mapa')
dbg = logger.debug
warn = logger.warning


URL_BASE = 'http://urbs-web.curitiba.pr.gov.br/centro/'
GET_COORDS_URL = URL_BASE + '/j_urbs2.asp' # no urljoin, just to keep exactly the same format

INITIAL_X = 674000
INITIAL_Y = 7180000
INITIAL_RAIO = 17000
INITIAL_CL = ''
INITIAL_CLICKPAGE = 'http://urbs-web.curitiba.pr.gov.br/centro/mostraclick.asp'

class DataDir:
    def __init__(self, path):
        self.path = path

    def _file_for_key(self, key):
        return os.path.join(self.path, key)

    def get(self, key, unpickle=True):
        f = self.getfile(key)
        if f is None:
            return None
        v = f.read()
        if unpickle:
            v = pickle.loads(v)
        return v

    def getfile(self, key):
        """Open value as file, for reading"""
        path = self._file_for_key(key)
        if not os.path.exists(path):
            return None
        return open(path, 'r')

    def put(self, key, val, pickleit=True):
        if pickleit:
            val = pickle.dumps(val)
        path = self._file_for_key(key)
        return open(path, 'w').write(val)

class MapRegion(object):
    def __init__(self, datadir, linha, name):
        self.datadir = datadir
        self.linha = linha
        self.name = name

    def _key_for_field(self, field):
        return 'mapdata.%s.%s.%s' % (self.linha, self.name, field)

    def val(self, field, unpickle=True):
        """Get a field from a map image

        linha: bus line
        name: image/region name (set when it is saved)
        field: field name (e.g. coord_data, map_image_gif)
        """
        return self.datadir.get(self._key_for_field(field), unpickle)

    def set_val(self, field, val, pickleit=True):
        return self.datadir.put(self._key_for_field(field), val, pickleit)

    def parse_coord_data(self):
        fields = 'minx','miny','maxx','maxy'
        data = self.val('coord_data', unpickle=False)
        for field,val in zip(fields, data.split(';')):
            val = float(val)
            self.set_val(field, val)
        self.set_val('debug.width', str(self.width()), pickleit=False)
        self.set_val('debug.height', str(self.height()), pickleit=False)

    def width(self):
        return self.val('maxx')-self.val('minx')

    def height(self):
        return self.val('maxy')-self.val('miny')

    def image(self):
        f = self.datadir.getfile(self._key_for_field('map_image.gif'))
        return Image.open(f)

class MapFetcher(object):
    def __init__(self, datadir):
        self.datadir = datadir
        self.ll = random.randint(0, 999999) # our 'session identifier'

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

        url = self.coords_url(x, y, raio, self.ll, linha, URL_BASE)
        dbg('url: %s', url)

        c = urllib2.urlopen(url)
        coord_data = c.read()
        c.close()
        dbg('coord data: %r', coord_data)

        iurl = self.image_url(self.ll)
        dbg('now will get image from: %s', iurl)

        img = urllib2.urlopen(iurl)

        return coord_data,img

    def save_map(self, x, y, raio, linha, name):
        data,image = self.fetch_map(linha, x, y, raio)

        self.datadir.put('mapdata.%s.%s.coord_data' % (linha, name), data, pickleit=False)
        self.datadir.put('mapdata.%s.%s.map_image.gif' % (linha, name), image.read(), pickleit=False)

    def get_map_if_missing(self, linha, name, x, y, raio, force=False):
        dbg('getting map[%s] for: %s', name, linha)
        done = self.datadir.get('mapdata.%s.%s.done' % (linha, name))
        dbg('done? %r', done)
        if done and not force:
            dbg('already on db')
        else:
            self.save_map(x, y, raio, linha, name)
            self.datadir.put('mapdata.%s.%s.done' % (linha, name), True)
        r = self.get_mapregion(linha, name)
        r.parse_coord_data()
        if r.val('has_busline') is None:
            i = r.image()
            has_bus = self._image_has_busline(i)
            r.set_val('has_busline', has_bus)
        return r

    def get_mapregion(self, linha, name):
        return MapRegion(self.datadir, linha, name)

    def get_initial_map(self, linha):
        return self.get_map_if_missing(linha, 'initial', 0, 0, 250)

    def _color_is_busline(self, c):
        return ord(c[0]) < 0x08 and ord(c[1]) < 0x08 and ord(c[2]) > 0xf0

    def _image_has_busline(self, i):
        assert i.mode == 'P'
        ptype,pdata = i.palette.getdata()
        dbg('ptype: %r', ptype)
        assert ptype == 'RGB'
        valid_colors = set()
        for pi in range(len(pdata)/3):
            if self._color_is_busline(pdata[3*pi:3*pi+3]):
                valid_colors.add(pi)
        dbg('colors: %r', valid_colors)
        if len(valid_colors) > 1:
            raise Exception("too many valid colors, sorry")
        for pixel in i.getdata():
            if pixel in valid_colors:
                return True
        return False

    def fetch_subregions(self, region, recursion_level, results):
        dbg('region size: %r, %r', region.width(), region.height())
        if not region.val('has_busline'):
            dbg('no bus line found on image, skipping')
            return
        name = region.name
        linha = region.linha
        width = region.width()
        height = region.height()
        if width > height:
            size = width
        else:
            size = height

        centerx = region.val('minx') + (width / 2)
        centery = region.val('miny') + (height / 2)

        MIN_RAIO = 100

        minmax = ('min', 'max')
        maxmin = ('max', 'min')
        for xr,opx in minmax,maxmin:
            for yr,opy in minmax,maxmin:
                # xr,yr = corner we want
                # opx,opy = opposite corner
                x = region.val('%sx' % (xr))
                y = region.val('%sy' % (yr))
                cx = (x + centerx) / 2
                cy = (y + centery) / 2
                raio = int((height / 4) * 1.05) # 5% tolerance
                if raio < MIN_RAIO:
                    dbg('fixing raio: %r', raio)
                    raio = MIN_RAIO
                    recursion_level = 0
                subname = 'submap.%f.%f.%d' % (cx, cy, raio)
                dbg('subname: %r', subname)
                sr = self.get_map_if_missing(linha, subname, cx, cy, raio)
                dbg('subregion size: %r, %r', sr.width(), sr.height())
                if sr.val('maxx') < cx or sr.val('minx') > cx or \
                   sr.val('maxy') < cy or sr.val('miny') > cy:
                    warn('image missed the center!')
                cornerx = sr.val('%sx' % (opx))
                cornery = sr.val('%sy' % (opy))
                results.append(sr)
                if recursion_level > 0:
                    self.fetch_subregions(sr, recursion_level - 1, results)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    datapath = sys.argv[1]
    tipolinha = sys.argv[2]
    linha = None
    if len(sys.argv) > 3:
        linha = sys.argv[3]

    datadir = DataDir(datapath)

    linhaskey = 'lista_linhas.%s' % (tipolinha)
    linhas = datadir.get(linhaskey)
    if linhas is None:
        linhas = list(lista_linhas(tipolinha))
        datadir.put(linhaskey, linhas)

    mf = MapFetcher(datadir)
    for cod,nome in linhas:
        if linha is not None and linha <> cod:
            continue
        dbg('will fetch for %s: %s', cod, nome)
        r = mf.get_initial_map(cod)

        regions = [r]
        mf.fetch_subregions(r, 5, regions)

        rnames = [r.name for r in regions]
        datadir.put('linha.%s.all_region_names' % (cod), rnames)
