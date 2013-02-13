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
                bounds = OpenLayers.Bounds.fromArray(ext,true);
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
