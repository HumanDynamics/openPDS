$(function () {
    window.AnswerList = Backbone.Model.extend({});
    
    window.AnswerListCollection = Backbone.Collection.extend({
        model: ActivityByHour,
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

            this.map = new OpenLayers.Map("map");
            var ol_wms = new OpenLayers.Layer.WMS( "OpenLayers WMS", "http://vmap0.tiles.osgeo.org/wms/vmap0?", {layers: 'basic'} );
            var boxes  = new OpenLayers.Layer.Boxes( "Boxes" );
            
            for (i in entries) {
                entry = entries[i];
                ext = entries["bounds"];
                bounds = OpenLayers.Bounds.fromArray(ext);
                box = new OpenLayers.Marker.Box(bounds);
                box.events.register("click", box, function (e) {
                    this.setBorder("yellow");
                });
                boxes.addMarker(box);
            }
            
            map.addLayers([ol_wms, boxes]);
            map.addControl(new OpenLayers.Control.LayerSwitcher());
            map.zoomToMaxExtent();

        }
    });
    
    window.answerListMap = new AnswerListMap();
    //$(window).bind("resize", function () { activityGraph.render(); });
});
