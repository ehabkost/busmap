var map;
var dbg1, dbg2, dbg3, dbg4;

function _loadMap()
{
	map = new GMap2(document.getElementById("map"));
	map.addControl(new GLargeMapControl());
	map.addControl(new GMapTypeControl());
	map.addControl(new GScaleControl());
	//map.addControl(new GOverviewMapControl());

	dbg1 = document.getElementById("debug1");
	dbg2 = document.getElementById("debug2");
	dbg3 = document.getElementById("debug3");
	dbg4 = document.getElementById("debug4");
}

function pstr(latng)
{
	return latng.lat()+','+latng.lng();
}

function setup_index()
{
	function marker(la, lo) {
		var point = new GLatLng(la, lo);
		var m = new GMarker(point, {clickable:false});
		map.addOverlay(m);
	}

	function reloadMarkers()
	{
		var b = map.getBounds();
		var ne = b.getNorthEast();
		var sw = b.getSouthWest();
		var z = map.getZoom();


		// add 50% on each side, to get markers around
		// the visible are, also

		// width and height
		var lats = ne.lat()-sw.lat();
		var lngs = ne.lng()-sw.lng();
		//dbg3.value = lats + ' -- ' + lngs;

		// calculate new bounds:
		var ne2 = new GLatLng(ne.lat()+(lats/4), ne.lng()+(lngs/4));
		var sw2 = new GLatLng(sw.lat()-(lats/4), sw.lng()-(lngs/4));

		//dbg4.value = ne2.lat() + ', '+ne2.lng()+' --- '+sw2.lat()+', '+sw2.lng();

		var sne = pstr(ne2);
		var ssw = pstr(sw2);

		var url = 'http://raisama.net/maps/test.fcgi/getmarkers?ne='+sne+'&sw='+ssw+'&zoom='+z;
		//alert(url);
		dbg1.value = url;
		dbg2.value = "loading...";
		GDownloadUrl(url, function (data, resp) {
			var r = eval('('+data+')');
			dbg2.value = 'loaded '+r.count+' markers';
			map.clearOverlays();
			for (var i = 0; i < r.markers.length; i++) {
				m = r.markers[i];
				marker(m.coord.latitude, m.coord.longitude);
			}
			dbg3.value = r.toomany?"Too many markers":"OK";
		});
	}

	GEvent.addListener(map,"dragend", reloadMarkers);
	GEvent.addListener(map,"zoomend", reloadMarkers);

	map.setCenter(new GLatLng(-25.438090, -49.236154), 9);
	reloadMarkers();

}

function setup_rect()
{
	function binfo(b)
	{
		var ne = b.getSouthWest();
		var sw = b.getNorthEast();
		var w = (ne.lng() - sw.lng())*1000;
		var h = (ne.lat() - sw.lat())*1000;
		var ar = w*h;

		return 'w: '+w+'.  h: '+h+'.  area: '+ar;
	}


	function EditableRect(b) {
		var dmarker_opts = {
			draggable:true,
			clickable:false,
		}

		function rect_poly(p1, p2) {
			var p12 = new GLatLng(p1.lat(), p2.lng());
			var p21 = new GLatLng(p2.lat(), p1.lng());

			return new GPolygon([p1, p12, p2, p21, p1], "#222222", 1, 1, "#0000ff", 0.2);
		}

		var m1, m2;
		var rbounds;
		var rpoly = null;

		function get_counts()
		{
			var ne = m1.getLatLng();
			var sw = m2.getLatLng();

			var sne = pstr(ne);
			var ssw = pstr(sw);
			var url = 'http://raisama.net/maps/test.fcgi/imovelcount?ne='+sne+'&sw='+ssw;

			dbg1.value = url;
			dbg2.value = "loading...";
			GDownloadUrl(url, function (data, resp) {
				var r = eval('('+data+')');
				dbg2.value = 'inside: '+r.inside+'. outside: '+r.outside;
			});

		}

		function show_sizes(ctrl)
		{
			dbg3.value = binfo(rbounds);
		}

		function redo_rect()
		{
			rbounds = new GLatLngBounds(m1.getLatLng(), m2.getLatLng());

			if (rpoly) {
				map.removeOverlay(rpoly);
				delete rpoly;
			}
			rpoly = rect_poly(m1.getLatLng(), m2.getLatLng());
			map.addOverlay(rpoly);

			get_counts();
			show_sizes();
		}

		this.change = function(b) {
			var sw = b.getSouthWest();
			var ne = b.getNorthEast();

			m1.setLatLng(sw);
			m2.setLatLng(ne);

			redo_rect();
		}

		function dmarker(point)
		{
			var m = new GMarker(point, dmarker_opts);
			map.addOverlay(m);
			GEvent.addListener(m, "dragend", redo_rect);
			return m;
		}

		m1 = dmarker(b.getSouthWest());
		m2 = dmarker(b.getNorthEast());

		this.m1 = m1;
		this.m2 = m2;
		redo_rect();
	}

	this.adjust_to_bounds = function ()
	{
		this.r.change(map.getBounds());
	}

	var cla = -25.438090;
	var clo = -49.236154;
	var w = 0.1;
	map.setCenter(new GLatLng(cla, clo), 9);

	var sw = new GLatLng(cla-w, clo-w);
	var ne = new GLatLng(cla+w, clo+w);
	var b = new GLatLngBounds(sw, ne);

	this.r = new EditableRect(b);
}

function loadMap() {
	if (GBrowserIsCompatible()) {
		_loadMap();
		return true;
	} else
		return false;
}



//page-specific functions
function index_load() {
	if (loadMap())
		setup_index();
}
