window.AnswerListMap = Backbone.View.extend({
    el: "#answerListMapContainer",
    
    initialize: function (answerKey, center) {
        _.bindAll(this, "render");
        
        this.answerLists = new AnswerListCollection([],{ "key": answerKey });
        this.answerLists.bind("reset", this.render);
        this.answerLists.fetch();
        this.center = center;
    },
    
    render: function () {
        var entries = this.answerLists.at(0).get("value");
        this.map = new OpenLayers.Map({ 
            div: "answerListMapContainer",
            projection: new OpenLayers.Projection("EPSG:900913"),
            displayProjection: new OpenLayers.Projection("EPSG:4326"),
            numZoomLevels: 18,
            tileManager: new OpenLayers.TileManager(),
//            fractionalZoom: true
        });
        this.geolocate = new OpenLayers.Control.Geolocate({
                bind:false,
                geolocationOptions: {
                    enableHighAccuracy: false,
                    maximumAge: 0,
                    timeout: 7000
                }
            });

        this.map.addControls([
            new OpenLayers.Control.TouchNavigation({dragPanOption: { enableKinetic: true}}),
            this.geolocate
        ]);
  /*      
geolocate.events.register("locationupdated",geolocate,function(e) {
    vector.removeAllFeatures();
    var circle = new OpenLayers.Feature.Vector(
        OpenLayers.Geometry.Polygon.createRegularPolygon(
            new OpenLayers.Geometry.Point(e.point.x, e.point.y),
            e.position.coords.accuracy/2,
            40,
            0
        ),
        {},
        style
    );
    vector.addFeatures([
        new OpenLayers.Feature.Vector(
            e.point,
            {},
            {
                graphicName: 'cross',
                strokeColor: '#f00',
                strokeWidth: 2,
                fillOpacity: 0,
                pointRadius: 10
            }
        ),
        circle
    ]);
    if (firstGeolocation) {
        map.zoomToExtent(vector.getDataExtent());
        pulsate(circle);
        firstGeolocation = false;
        this.bind = true;
    }
});
*/
        var osm = new OpenLayers.Layer.OSM();
        var boxes  = new OpenLayers.Layer.Vector( "Boxes" );
        var pointsLayer = new OpenLayers.Layer.Vector("Points");
        this.map.addLayers([osm]);

        minLat = minLong = Number.MAX_VALUE;
        maxLat = maxLong = -Number.MAX_VALUE;
        this.entryBounds = [];
        var j = 0;
        for (i in entries) {
            entry = entries[i];
            ext = entry["bounds"];
            if (ext) {
                if (typeof ext[0] !== "number") {
                    for (b in ext) {
                        r = ext[b];

                        minLat = Math.min(minLat, r[0]);
                        maxLat = Math.max(maxLat, r[2]);
                        minLong = Math.min(minLong, r[1]);
                        maxLong = Math.max(maxLong, r[3]);
        
                        bounds = OpenLayers.Bounds.fromArray(r, true);
                        bounds = bounds.transform(this.map.displayProjection, this.map.getProjectionObject());
                        box = new OpenLayers.Feature.Vector(bounds.toGeometry());
                        boxes.addFeatures([box]);
                        this.entryBounds[j] = bounds.clone();
                        var me = this;
                        var radioButton = $("<input type='radio' name='place' value='"+j+"' id='place"+j+"' />");
                        $("#footer").append(radioButton.click(
                            function () {
                                me.map.zoomToExtent(me.entryBounds[this.value]);
                            }
                        ));
                        $("#footer").append($("<label for='place"+j+"'>"+entry["key"]+"</label>"));
                        j++;
                    }
                } else {
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
                    var radioButton = $("<input type='radio' name='place' value='"+j+"' id='place"+j+"' />");
                    $("#footer").append(radioButton.click(
                        function () { 
                            me.map.zoomToExtent(me.entryBounds[this.value]); 
                        }
                    ));
                    $("#footer").append($("<label for='place"+j+"'>"+entry["key"]+"</label>"));
                    j++;
                }
            }
            points = entry["points"];

            if (points) {
                for (pointIndex in points) {
                    var point = points[pointIndex];

                    minLat = Math.min(minLat, point[0]);
                    maxLat = Math.max(maxLat, point[0]);
                    minLong = Math.min(minLong, point[1]);
                    maxLong = Math.max(maxLong, point[1]);

                    pointGeometry = new OpenLayers.Geometry.Point(point[1], point[0]);
                    pointGeometry = pointGeometry.transform(this.map.displayProjection, this.map.getProjectionObject());
                    pointVector = new OpenLayers.Feature.Vector(pointGeometry);
                    pointsLayer.addFeatures([pointVector]);
                }
            }
        }
        this.map.addLayers([boxes,pointsLayer]);
        
        this.updateSize();
        //if (this.center) {
        //    minLong = this.center[1] - 0.001;
        //    maxLong = this.center[1] + 0.001;
        //    minLat = this.center[0] - 0.001;
        //    maxLat = this.center[0] + 0.001;
        //}
        if (minLong < Number.MAX_VALUE && maxLong > -Number.MAX_VALUE && !this.center) {
            bounds = OpenLayers.Bounds.fromArray([minLong, minLat, maxLong, maxLat]);
            bounds.transform(this.map.displayProjection, this.map.getProjectionObject());
            this.map.zoomToExtent(bounds);
        } else if (this.center) {
            //center = new OpenLayers.Geometry.Point(this.center[1], this.center[0]);
            center = new OpenLayers.LonLat(this.center[1], this.center[0]);
            center.transform(this.map.displayProjection, this.map.getProjectionObject());
            this.map.setCenter(center, 18);
            //this.map.setCenter(new OpenLayers.LonLat(this.center[1], this.center[0]), 10);
        }

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
