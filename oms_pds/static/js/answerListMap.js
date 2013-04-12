window.AnswerListMap = Backbone.View.extend({
    el: "#answerListMapContainer",
    
    initialize: function (answerKey) {
        _.bindAll(this, "render");
        
        this.answerLists = new AnswerListCollection([],{ "key": answerKey });
        this.answerLists.bind("reset", this.render);
        this.answerLists.fetch();
    },
    
    render: function () {
        var entries = this.answerLists.at(0).get("value");
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
        var pointsLayer = new OpenLayers.Layer.Vector("Points");
        this.map.addLayers([osm]);

        minLat = minLong = Number.MAX_VALUE;
        maxLat = maxLong = -Number.MAX_VALUE;
        this.entryBounds = [];
        for (i in entries) {
            entry = entries[i];
            ext = entry["bounds"];
            if (ext) {
                minLat = Math.min(minLat, ext[0]);
                maxLat = Math.max(maxLat, ext[2]);
                minLong = Math.min(minLong, ext[1]);
                maxLong = Math.max(maxLong, ext[3]);                            

                bounds = OpenLayers.Bounds.fromArray(ext, true);
                bounds = bounds.transform(this.map.displayProjection, this.map.getProjectionObject());
                box = new OpenLayers.Feature.Vector(bounds.toGeometry());
                boxes.addFeatures([box]);
                this.entryBounds[i] = bounds.clone();
                var me = this;                
    
                $("#footer").append($("<input type='radio' name='place' value='"+i+"'>"+entry["key"]+"</input>").click(
                    function () { 
                        me.map.zoomToExtent(me.entryBounds[this.value]); 
                    }
                ));
            }
            points = entry["points"];

            if (points) {
                for (pointIndex in points) {
                    var point = points[pointIndex];

                    minLat = Math.min(minLat, point[0]);
                    maxLat = Math.max(maxLat, point[0]);
                    minLong = Math.min(minLong, point[1]);
                    maxLong = Math.max(maxLong, point[1]);

                    pointGeometry = OpenLayers.Geometry.Point(point[0], point[1]);
                    pointGeometry = pointGeometry.transform(this.map.displayProjection, this.map.getProjectionObject());
                    pointVector = new OpenLayers.Feature.Vector(pointGeometry);
                    pointsLayer.addFeatures([pointVector]);
                }
            }
        }
        this.map.addLayers([boxes,pointsLayer]);

        bounds = OpenLayers.Bounds.fromArray([minLong, minLat, maxLong, maxLat]);
        bounds.transform(this.map.displayProjection, this.map.getProjectionObject());
        
        this.updateSize();
        this.map.zoomToExtent(bounds);

    },
    
    zoomIn: function () {
        if (this.map) {
            this.map.zoomIn();
        }
    },
    
    zoomOut: function () {
        if (this.map) {
            this.map.zoomOut();
        }
    },
    
    updateSize: function () {
        var navbar= $("div[data-role='navbar']:visible"),
        content = $("div[data-role='content']:visible:visible"),
        footer = $("div[data-role='footer']:visible"),
        viewHeight = $(window).height(),
        contentHeight = viewHeight - navbar.outerHeight() - footer.outerHeight();
    
        if (content.outerHeight() !== contentHeight) {
            content.height(contentHeight);
        }
    
        if (this.map && this.map instanceof OpenLayers.Map) {
            this.map.updateSize();
        }
    }
    
});
