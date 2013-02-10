import sys, os

from busmap.urbsweb.mapa import DataDir, MapRegion
from PIL import Image

import logging
logger = logging.getLogger(__name__)
dbg = logger.debug
warn = logger.warning
info = logger.info

def main(argv):
    loglevel = logging.INFO
    args = []
    i = 0
    while i < len(sys.argv[1:]):
        arg = sys.argv[1+i]
        if arg == '-d':
            loglevel = logging.DEBUG
        else:
            args.append(arg)
        i += 1

    logging.basicConfig(stream=sys.stderr, level=loglevel)
    dirpath = args[0]
    d = DataDir(dirpath)
    ltype = args[1]
    linha = args[2]

    # region-size of the largest image we could imagine building:
    LARGE_IMAGE = 10000.0
    rnames = d.get('linha.%s.all_region_names' % (linha))

    dbg('gathering image sizes...')
    persize = {}
    for rname in rnames:
        r = MapRegion(d, linha, rname)

        img = r.image()
        isize = img.size
        rsize = r.size()
        region_per_pixel = [float(rsize[i])/isize[i] for i in (0,1)]
        pixels_for_bigimage = [int(LARGE_IMAGE/region_per_pixel[i]) for i in (0,1)]
        k = (tuple(pixels_for_bigimage), isize)
        persize.setdefault(k, []).append(rname)

    dbg('looking for best size...')
    # look for best size combination:
    #dbg('sizes: %r', repr(persize))
    bestsize = None
    bestcount = 0
    for size,names in persize.items():
        count = len(names)
        dbg('count for %r: %r', size, count)
        if bestsize is None or count > bestcount:
            bestsize = size
            bestcount = count

    info("best size: %r", bestsize)
    rnames = persize[bestsize]
    pixels_for_bigimage,imgsize = bestsize
    region_per_pixel = [(LARGE_IMAGE/pixels_for_bigimage[i]) for i in (0,1)]
    dbg('region/pixel ratio: %r', region_per_pixel)
    region_for_img = [region_per_pixel[i]*imgsize[i] for i in (0,1)]
    dbg('region size for each image: %r', region_for_img)
    def regions():
        for rname in rnames:
            yield MapRegion(d, linha, rname)

    minx = min([r.val('minx') for r in regions()])
    miny = min([r.val('miny') for r in regions()])
    maxx = max([r.val('maxx') for r in regions()])
    maxy = max([r.val('maxy') for r in regions()])

    dbg('lat/lng ranges: %r-%r (%r), %r-%r (%r)', minx, maxx, maxx-minx, miny, maxy, maxy-miny)
    image_region_size = (maxx-minx, maxy-miny)
    image_pixel_size = [int(image_region_size[i]/region_per_pixel[i]) for i in (0,1)]

    dbg('image pixel size: %r', image_pixel_size)
    img = Image.new('RGB', image_pixel_size)
    for r in regions():
        subimg = r.image()
        # 0,0 (top-left corner) is minx,maxx
        dbg('ranges of image are: %r-%r (%r), %r-%r (%r)', r.val('minx'), r.val('maxx'), r.width(), r.val('miny'), r.val('maxy'), r.height())
        region_offset = (r.val('minx')-minx, maxy-r.val('maxy'))
        dbg('region offset is: %r', region_offset)
        pixel_offset = tuple([int(region_offset[i]/region_per_pixel[i]) for i in (0,1)])
        dbg('pasting at pixel offset: %r', pixel_offset)
        img.paste(subimg, pixel_offset)
    fname = os.path.join(dirpath, '%s-full.png' % (linha))
    img.save(fname, 'png')
    info('saved to: %s', fname)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
