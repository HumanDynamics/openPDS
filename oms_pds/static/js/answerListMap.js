$(function () {
    window.AnswerList = Backbone.Model.extend({});
    
    window.AnswerListCollection = Backbone.Collection.extend({
        model: AnswerList,
        urlRoot: ANSWERLIST_API_URL,
        
        fetch: function (options) {
            options || (options = {});
            options.data || (options.data = {});
            filterMapping = { "key": ANSWERLIST_KEY }
            options.data = _.extend(options.data, filterMapping);
            
            return Backbone.Collection.prototype.fetch.call(this,options);
        }
    });
    function deg_rad(ang) {
        return ang * (Math.PI/180.0)
    }
    function merc_x(lon) {
        var r_major = 6378137.000;
        return r_major * deg_rad(lon);
    }
    function merc_y(lat) {
        if (lat > 89.5)
            lat = 89.5;
        if (lat < -89.5)
            lat = -89.5;
        var r_major = 6378137.000;
        var r_minor = 6356752.3142;
        var temp = r_minor / r_major;
        var es = 1.0 - (temp * temp);
        var eccent = Math.sqrt(es);
        var phi = deg_rad(lat);
        var sinphi = Math.sin(phi);
        var con = eccent * sinphi;
        var com = .5 * eccent;
        con = Math.pow((1.0-con)/(1.0+con), com);
        var ts = Math.tan(.5 * (Math.PI*0.5 - phi))/con;
        var y = 0 - r_major * Math.log(ts);
        return y;
    }
    function merc(x,y) {
        return [merc_x(x),merc_y(y)];
    }
    window.AnswerListMap = Backbone.View.extend({
        el: "#answerListMapContainer",
        
        initialize: function () {
            _.bindAll(this, "render");
            
            this.answerLists = new AnswerListCollection();
            this.answerLists.bind("reset", this.render);
            this.answerLists.fetch();
        },
        
        render: function () {
            var entries = this.answerLists.at(0).get("value");

            this.map = new OpenLayers.Map("answerListMapContainer");
            var osm = new OpenLayers.Layer.OSM();
            var boxes  = new OpenLayers.Layer.Boxes( "Boxes" );
            var ol_wms = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                    "http://vmap0.tiles.osgeo.org/wms/vmap0?", {layers: 'basic'} );
	    for (i in entries) {
                entry = entries[i];
                ext = entry["bounds"];
                mercator = merc(ext[1], ext[0])
                ext[0] = mercator[0]
                ext[1] = mercator[1]
                mercator = merc(ext[3], ext[2])
                ext[2] = mercator[2]
                ext[3] = mercator[3]
                
                bounds = OpenLayers.Bounds.fromArray(ext);
                box = new OpenLayers.Marker.Box(bounds);
                box.events.register("click", box, function (e) {
                    this.setBorder("yellow");
                });
                boxes.addMarker(box);
            }
            this.map.addLayers([osm,boxes]);
            this.map.baseLayer = osm; 
            this.map.addControl(new OpenLayers.Control.LayerSwitcher());
            this.map.zoomToMaxExtent();

        }
    });
    
    window.answerListMap = new AnswerListMap();
    //$(window).bind("resize", function () { activityGraph.render(); });
});
