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

// fix height of content
function fixContentHeight() {
    var navbar= $("div[data-role='navbar']:visible"),
        content = $("div[data-role='content']:visible:visible"),
        footer = $("div[data-role='footer']:visible"),
        viewHeight = $(window).height(),
        contentHeight = viewHeight - navbar.outerHeight() - footer.outerHeight();

    if (content.outerHeight() !== contentHeight) {
        //contentHeight = viewHeight - footer.outerHeight();
        content.height(contentHeight);
    }

    if (window.map && window.map instanceof OpenLayers.Map) {
        map.updateSize();
    }
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
            //var height = $("div[data-role='content']:visible:visible").outerHeight();
            //$(this.el).height(height)
            this.map = new OpenLayers.Map({ 
                div: "answerListMapContainer",
                projection: new OpenLayers.Projection("EPSG:900913"),
                displayProjection: new OpenLayers.Projection("EPSG:4326"),
                numZoomLevels: 18,
                tileManager: new OpenLayers.TileManager(),
            });
            this.map.addControls([
                new OpenLayers.Control.TouchNavigation({dragPanOption: { enableKinetic: true}})
            ]);
            
            var osm = new OpenLayers.Layer.OSM();
            var boxes  = new OpenLayers.Layer.Vector( "Boxes" );
            var ol_wms = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                    "http://vmap0.tiles.osgeo.org/wms/vmap0?", {layers: 'basic'} );
            this.map.addLayers([osm]);

            minLat = minLong = Number.MAX_VALUE;
            maxLat = maxLong = -Number.MAX_VALUE;
            this.entryBounds = [];
	    for (i in entries) {
                entry = entries[i];
                ext = entry["bounds"];

                minLat = Math.min(minLat, ext[0]);
                maxLat = Math.max(maxLat, ext[2]);
                minLong = Math.min(minLong, ext[1]);
                maxLong = Math.max(maxLong, ext[3]);                            

                bounds = OpenLayers.Bounds.fromArray(ext, true);
                bounds = bounds.transform(this.map.displayProjection, this.map.getProjectionObject());
                box = new OpenLayers.Feature.Vector(bounds.toGeometry());
                boxes.addFeatures([box]);
                this.entryBounds[i] = bounds.clone();
                //selectorButton = new OpenLayers.Control.Button({ trigger: function () { this.map.zoomToExtent(this.entryBounds[i]); }});
                //this.map.addControl(selectorButton);
                var me = this;                

                $("#footer").append($("<input type='radio' name='place' value='"+i+"'>"+entry["key"]+"</input>").click(
                    function () { 
                        me.map.zoomToExtent(me.entryBounds[this.value]); 
                    }
                ));
            }
            this.map.addLayers([boxes]);

            bounds = OpenLayers.Bounds.fromArray([minLong, minLat, maxLong, maxLat]);
            bounds.transform(this.map.displayProjection, this.map.getProjectionObject());

            //this.map.addControl(new OpenLayers.Control.LayerSwitcher());
            
            window.map = this.map;
            fixContentHeight(); 
            this.map.zoomToExtent(bounds);

        }
    });
    
    window.answerListMap = new AnswerListMap();
    //$("#answerListMapContainer").live("resize", function () { fixContentHeight(); });
    //$(window).bind("resize", function () { activityGraph.render(); });
$(window).bind("orientationchange resize pageshow", fixContentHeight);
$("#plus").live('click', function(){
    map.zoomIn();
});

$("#minus").live('click', function(){
    map.zoomOut();
});


});
