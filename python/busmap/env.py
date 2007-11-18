
import busmap.db

import urllib2
url_opener = urllib2.build_opener()

db = busmap.db.new_db(host='socdb.raisama.net',
		    db='bus', user='bus',
		    passwd='bu555')


# the paths MUST end in /
cgipath = '/cgi-bin/bus.cgi/'
rootpath = '/bus/'
