import sys
import urllib2
import string
import re

from busmap.urbsweb.mapa import DataDir

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

    dpath = args[0]
    dd = DataDir(dpath)
    cookie = dd.get('negen_cookie', unpickle=False)
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', cookie))


    tosearch = string.lowercase
    for q in tosearch:
        reply = dd.get('negen/getLinhas/%s/response' % (q), False)
        if reply is None:
            reply = opener.open('http://www.urbs.curitiba.pr.gov.br/PORTAL/tabelahorario/negen/getLinhas.php?q=%').read()
            dd.put('negen/getLinhas/%s/response' % (q), reply, False)
        dbg('reply: %r', reply)

        matches = re.findall(r"option value='(.*?)'.*?>(.*?)<", reply)
        dbg('matches: %r', matches)
        for l,name in matches:
            dd.put('negen/getLinha/%s/nome.txt' % (l), name, False)
            l,v,cor = l.split(',')
            dbg('querying for getLinha: %r, %r, %r' % (l, v, cor))
            reply = dd.get('negen/getLinha/%s,%s,%s/response' % (l, v, cor), False)
            if reply is None:
                url = 'http://www.urbs.curitiba.pr.gov.br/PORTAL/tabelahorario/negen/getLinha.php?l=%s&v=%s&cor=%s' % (l, v, cor)
                dbg('url: %r', url)
                reply = opener.open(url).read()
                dd.put('negen/getLinha/%s,%s,%s/response' % (l, v, cor), reply, False)
            dbg('reply: %r', reply)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
