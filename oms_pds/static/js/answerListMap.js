window.AnswerListMap = Backbone.View.extend({
    el: "#answerListMapContainer",
    
    initialize: function (answerKey, center, containerId, autoResize) {
        _.bindAll(this, "render", "renderPlaces");        

        if (containerId) {
            this.containerId = containerId;
            this.el = "#" + containerId;
        } else {
            this.containerId = "answerListMapContainer";
        }

        this.autoResize = autoResize;
        this.center = center;
        this.render();
        this.answerLists = new AnswerListCollection([],{ "key": answerKey });
        this.answerLists.bind("reset", this.renderPlaces);
        this.answerLists.fetch();
    },
    
    render: function () {
        this.map = new OpenLayers.Map({ 
            div: this.containerId,
            projection: new OpenLayers.Projection("EPSG:900913"),
            displayProjection: new OpenLayers.Projection("EPSG:4326"),
            numZoomLevels: 18,
            tileManager: new OpenLayers.TileManager(),
            controls: [
                new OpenLayers.Control.Zoom(),
                new OpenLayers.Control.TouchNavigation({dragPanOption: { enableKinetic: true}})
            ]
//            fractionalZoom: true
        });

//        this.map.addControls([
//            new OpenLayers.Control.TouchNavigation({dragPanOption: { enableKinetic: true}}),
//        ]);  
        var osm = new OpenLayers.Layer.OSM();
        this.boxes  = new OpenLayers.Layer.Vector( "Boxes" );
        this.pointsLayer = new OpenLayers.Layer.Vector("Points");

        this.map.addLayers([osm, this.boxes, this.pointsLayer]);
        if (this.center) {
            this.setCenter(this.center, 18);
        }
        if (this.autoResize) {
            this.updateSize();
        }
    },
    
    addBoxWithRadioButton: function (ext, entry, j, keyFields) {
        var bounds = OpenLayers.Bounds.fromArray(ext, true);
        bounds = bounds.transform(this.map.displayProjection, this.map.getProjectionObject());
        var box = new OpenLayers.Feature.Vector(bounds.toGeometry());
        this.boxes.addFeatures([box]);
        this.entryBounds[j] = bounds.clone();
        var me = this;
        var radioButton = $("<label for='place"+j+"'>"+entry["key"]+"</label><input type='radio' data-mini='true' name='place' value='"+j+"' id='place"+j+"' />");
        keyFields.controlgroup("container").append(radioButton.click(
            function () {
                me.map.zoomToExtent(me.entryBounds[this.value]);
             }
        ));
        $(radioButton[1]).checkboxradio();
    },

    renderPlaces: function () {
        var entries = (this.answerLists && this.answerLists.length > 0)? this.answerLists.at(0).get("value"):[];

        var minLat = minLong = Number.MAX_VALUE;
        var maxLat = maxLong = -Number.MAX_VALUE;
        var footer = $("#footer");//$("<div data-role='footer'></div>");
        var keyFields = $("<fieldset data-role='controlgroup' data-type='horizontal' data-mini='true'></fieldset>").controlgroup();
        footer.append(keyFields);
        this.entryBounds = [];
        var j = 0;
        for (i in entries) {
            var entry = entries[i];
            var ext = entry["bounds"];
            if (ext) {
                if (typeof ext[0] !== "number") {
                    for (b in ext) {
                        r = ext[b];

                        minLat = Math.min(minLat, r[0]);
                        maxLat = Math.max(maxLat, r[2]);
                        minLong = Math.min(minLong, r[1]);
                        maxLong = Math.max(maxLong, r[3]);
                        this.addBoxWithRadioButton(r, entry, j, keyFields); 
                        j++;
                    }
                } else {
                    minLat = Math.min(minLat, ext[0]);
                    maxLat = Math.max(maxLat, ext[2]);
                    minLong = Math.min(minLong, ext[1]);
                    maxLong = Math.max(maxLong, ext[3]);                            
                    this.addBoxWithRadioButton(ext, entry, j, keyFields);
                    j++;
                }
            }

            footer.appendTo("#pageDiv").toolbar({ position: "fixed" });

            points = entry["points"];

            if (points) {
                for (pointIndex in points) {
                    var point = points[pointIndex];

                    minLat = Math.min(minLat, point[0]);
                    maxLat = Math.max(maxLat, point[0]);
                    minLong = Math.min(minLong, point[1]);
                    maxLong = Math.max(maxLong, point[1]);
                    
                    this.addPoint(point);
                }
            }
        }
        
        if (minLong < Number.MAX_VALUE && maxLong > -Number.MAX_VALUE && !this.center) {
            bounds = OpenLayers.Bounds.fromArray([minLong, minLat, maxLong, maxLat]);
            bounds.transform(this.map.displayProjection, this.map.getProjectionObject());
            this.map.zoomToExtent(bounds);
        } else if (this.center) {
            this.setCenter(this.center, 18);
        }
        if (this.autoResize) {
            this.updateSize();
        }
    },
    
    addPoint: function (point) {
        var pointGeometry = new OpenLayers.Geometry.Point(point[1], point[0]);
        pointGeometry = pointGeometry.transform(this.map.displayProjection, this.map.getProjectionObject());
        var pointVector = new OpenLayers.Feature.Vector(pointGeometry);
        this.pointsLayer.addFeatures([pointVector]);
    },
   
    setCenter: function (latLong, zoom, plot) {
        this.center = latLong;
        var center = new OpenLayers.LonLat(this.center[1], this.center[0]);
        center.transform(this.map.displayProjection, this.map.getProjectionObject());
        this.map.setCenter(center, 18);
        if (plot) {
            this.addPoint(latLong);
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
   
//        console.log("view, content, navbar, footer, outer"+viewHeight+","+contentHeight+","+navbar.outerHeight()+","+footer.outerHeight()+","+content.outerHeight());
         
        if (content.outerHeight() !== contentHeight) {
            content.height(contentHeight);
        }
    
        if (this.map && this.map instanceof OpenLayers.Map) {
            this.map.updateSize();
        }
    }
    
});
